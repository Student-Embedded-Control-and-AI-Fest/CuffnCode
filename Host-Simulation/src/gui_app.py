"""
CuffnCode — GUI simulasi hardware + komputasi paralel/terdistribusi.
Jalankan: python gui.py   atau   python src/gui_app.py
"""

from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import ttk

import numpy as np

try:
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec
except ImportError as exc:
    raise SystemExit("Install matplotlib: pip install matplotlib") from exc

from hardware_sim import HardwareSimulator, Phase, SimulationResult
from filters import process_chunk
from signal_analysis import FilterComparison, compare_before_after
from cuffncode_specs import AD620_GAIN, ADC_RATE_HZ, NOTCH_TARGET_HZ, TLC_OFFSET_V


# Warna tema
BG = "#1a1d23"
PANEL = "#252a33"
ACCENT = "#3d8bfd"
ACTIVE = "#ffc107"
SUCCESS = "#51cf66"
TEXT = "#e9ecef"
MUTED = "#868e96"
WIRE = "#495057"
GUIDE_BG = "#1e3a5f"

# Penjelasan langkah simulasi (bahasa sederhana untuk demo kuliah)
STEP_GUIDE: dict[Phase, str] = {
    Phase.IDLE: "Klik «Mulai Demo» di atas. Simulasi ±1 menit.",
    Phase.PUMP_INFLATE: "① Manset diisi udara (pompa + katup isi).",
    Phase.VALVE_HOLD: "② Tekanan ditahan sebentar.",
    Phase.VALVE_DEFLATE: "③ Manset mengempis — sinyal tekanan terekam.",
    Phase.SENSOR_BRIDGE: "④ Sensor MPS20N0040D membaca tekanan (mV).",
    Phase.AFE_AD620: "⑤ Penguat AD620 memperkuat sinyal.",
    Phase.AFE_TLC2272: "⑥ TLC2272 mengatur level tegangan.",
    Phase.STM32_ADC: "⑦ STM32 mengubah sinyal ke digital (ADC).",
    Phase.HOST_PARALLEL: "⑧ PC Host — filter paralel (beberapa core CPU).",
    Phase.HOST_DISTRIBUTED: "⑨ Tiga node: ambil data → filter → tampilkan.",
    Phase.DONE: "✓ Selesai — lihat grafik & tabel di kanan.",
}

# Baris tabel bukti numerik (sebelum / sesudah / perubahan)
PROOF_ROW_KEYS = ("hum", "noise", "rms", "peak", "bp", "samples")


class CuffnCodeGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CuffnCode — Demo IFB 206 (Farhan Kamil)")
        self.root.configure(bg=BG)
        self.root.minsize(1280, 900)
        self.root.geometry("1440x920")

        self.sim = HardwareSimulator()
        self._comparison: FilterComparison | None = None
        self._running = False
        self._wave_idx = 0
        self._anim_after: str | None = None

        self._build_layout()
        self._draw_diagram()
        self._init_plot()

    def _build_layout(self) -> None:
        header = tk.Frame(self.root, bg=PANEL, pady=8, padx=12)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="CuffnCode — Demo IFB 206  ·  Farhan Kamil",
            font=("Segoe UI", 14, "bold"),
            fg=ACCENT,
            bg=PANEL,
        ).pack(side=tk.LEFT)

        toolbar = tk.Frame(self.root, bg=PANEL, padx=12, pady=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_start = tk.Button(
            toolbar,
            text="▶  Mulai Demo",
            command=self._on_start,
            font=("Segoe UI", 12, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground="#5c9eff",
            activeforeground="white",
            relief=tk.RAISED,
            padx=24,
            pady=10,
            cursor="hand2",
        )
        self.btn_start.pack(side=tk.LEFT)

        tk.Button(
            toolbar,
            text="↺  Ulang",
            command=self._on_reset,
            font=("Segoe UI", 10),
            bg=WIRE,
            fg=TEXT,
            activeforeground=TEXT,
            relief=tk.RAISED,
            padx=18,
            pady=10,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=10)

        prog_frame = tk.Frame(toolbar, bg=PANEL)
        prog_frame.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)
        self.progress_pct_var = tk.StringVar(value="Progress: 0%")
        tk.Label(
            prog_frame,
            textvariable=self.progress_pct_var,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT,
            bg=PANEL,
        ).pack(anchor=tk.W)
        self.progress = ttk.Progressbar(prog_frame, length=400, mode="determinate")
        self.progress.pack(anchor=tk.W, fill=tk.X, pady=(4, 0))

        self.step_guide_var = tk.StringVar(value=STEP_GUIDE[Phase.IDLE])
        tk.Label(
            toolbar,
            textvariable=self.step_guide_var,
            font=("Segoe UI", 9),
            fg=ACTIVE,
            bg=PANEL,
            wraplength=520,
            justify=tk.RIGHT,
        ).pack(side=tk.RIGHT, padx=8)

        log_frame = tk.Frame(self.root, bg=BG, padx=10, pady=4)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(
            log_frame,
            text="Catatan langkah",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=BG,
        ).pack(anchor=tk.W)
        self.log_box = tk.Text(
            log_frame,
            height=4,
            bg="#0f1115",
            fg=TEXT,
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.log_box.pack(fill=tk.X)

        # --- Baris utama: diagram kiri | grafik besar kanan ---
        main_row = tk.Frame(self.root, bg=BG)
        main_row.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=6)

        sidebar = tk.Frame(main_row, bg=PANEL, padx=8, pady=6, width=310)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Alur perangkat (kuning = aktif)",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT,
            bg=PANEL,
        ).pack(anchor=tk.W)

        self.canvas = tk.Canvas(sidebar, bg="#0f1115", highlightthickness=0, width=292, height=200)
        self.canvas.pack(pady=4)

        self.phase_title_var = tk.StringVar(value="Menunggu demo")
        tk.Label(
            sidebar,
            textvariable=self.phase_title_var,
            font=("Segoe UI", 10, "bold"),
            fg=ACTIVE,
            bg=PANEL,
            wraplength=290,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(4, 0))

        self.phase_var = tk.StringVar(value=STEP_GUIDE[Phase.IDLE])
        tk.Label(
            sidebar,
            textvariable=self.phase_var,
            font=("Segoe UI", 8),
            fg=TEXT,
            bg=PANEL,
            wraplength=290,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        metrics = tk.Frame(sidebar, bg="#12151a", padx=6, pady=6)
        metrics.pack(fill=tk.X, pady=6)
        tk.Label(
            metrics,
            text="Angka penting",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg="#12151a",
        ).pack(anchor=tk.W)
        self.pressure_var = tk.StringVar(value="Tekanan manset: —")
        self.telemetry_var = tk.StringVar(value="Sensor → ADC: —")
        self.bp_var = tk.StringVar(value="BP simulasi: — / —")
        self.parallel_var = tk.StringVar(value="Filter paralel: —")
        self.node_var = tk.StringVar(value="Node A→B→C: —")
        for var in (
            self.pressure_var,
            self.telemetry_var,
            self.parallel_var,
            self.node_var,
            self.bp_var,
        ):
            tk.Label(
                metrics,
                textvariable=var,
                font=("Segoe UI", 8),
                fg=TEXT,
                bg="#12151a",
                wraplength=280,
                justify=tk.LEFT,
            ).pack(anchor=tk.W, pady=1)

        tk.Label(
            sidebar,
            text="Penjelasan fase",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor=tk.W, pady=(2, 0))
        self.detail_text = tk.Text(
            sidebar,
            height=4,
            bg="#0f1115",
            fg=TEXT,
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=4,
            pady=4,
        )
        self.detail_text.pack(fill=tk.X)

        plot_col = tk.Frame(main_row, bg=PANEL, padx=8, pady=6)
        plot_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            plot_col,
            text="Bukti filter Host: gelombang + angka + analisis",
            font=("Segoe UI", 11, "bold"),
            fg=ACCENT,
            bg=PANEL,
        ).pack(anchor=tk.W)
        tk.Label(
            plot_col,
            text="Merah = sebelum (hum 50 Hz)  ·  Hijau = sesudah  ·  Batang = metrik FFT/statistik",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor=tk.W, pady=(0, 4))

        self.insight_frame = tk.Frame(plot_col, bg=PANEL)
        self.insight_frame.pack(fill=tk.X, pady=(0, 4))
        self._insight_vars: dict[str, tk.StringVar] = {}
        for key, title, color in (
            ("hum", "Hum 50 Hz", "#ff6b6b"),
            ("noise", "Noise", "#ffa94d"),
            ("rms", "RMS", "#74c0fc"),
            ("peak", "Peak", ACCENT),
        ):
            card = tk.Frame(self.insight_frame, bg="#12151a", padx=6, pady=4)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
            tk.Label(card, text=title, font=("Segoe UI", 7), fg=MUTED, bg="#12151a").pack(anchor=tk.W)
            var = tk.StringVar(value="—")
            self._insight_vars[key] = var
            tk.Label(
                card,
                textvariable=var,
                font=("Segoe UI", 9, "bold"),
                fg=color,
                bg="#12151a",
            ).pack(anchor=tk.W)

        proof_tbl_frame = tk.Frame(plot_col, bg="#12151a", padx=4, pady=4)
        proof_tbl_frame.pack(fill=tk.X, pady=(0, 4))
        headers = ("Metrik", "Sebelum", "Sesudah", "Perubahan")
        for c, h in enumerate(headers):
            tk.Label(
                proof_tbl_frame,
                text=h,
                font=("Segoe UI", 8, "bold"),
                fg=MUTED,
                bg="#12151a",
                padx=6,
                pady=4,
            ).grid(row=0, column=c, sticky="w")
        self._proof_cells: dict[str, list[tk.StringVar]] = {
            k: [tk.StringVar(value="—") for _ in range(3)] for k in PROOF_ROW_KEYS
        }
        row_labels = {
            "hum": f"Daya hum {NOTCH_TARGET_HZ:.0f} Hz (FFT ±3 Hz)",
            "noise": "Std dev noise residu",
            "rms": "RMS amplitudo",
            "peak": "Peak envelope",
            "bp": "BP demo (mmHg)",
            "samples": f"Sampel (@ {ADC_RATE_HZ:.0f} Hz)",
        }
        for r, key in enumerate(PROOF_ROW_KEYS, start=1):
            tk.Label(
                proof_tbl_frame,
                text=row_labels[key],
                font=("Segoe UI", 9),
                fg=TEXT,
                bg="#12151a",
                padx=6,
                pady=3,
                anchor="w",
            ).grid(row=r, column=0, sticky="w")
            for c in range(3):
                tk.Label(
                    proof_tbl_frame,
                    textvariable=self._proof_cells[key][c],
                    font=("Consolas", 9),
                    fg=TEXT if c < 2 else SUCCESS,
                    bg="#12151a",
                    padx=6,
                    pady=3,
                    anchor="w",
                ).grid(row=r, column=c + 1, sticky="w")
        proof_tbl_frame.columnconfigure(0, weight=2)
        for c in range(1, 4):
            proof_tbl_frame.columnconfigure(c, weight=1)

        self.fig = Figure(figsize=(10.2, 7.0), facecolor=PANEL, dpi=96)
        gs = GridSpec(3, 1, figure=self.fig, height_ratios=[1, 1, 0.65], hspace=0.38)
        self.ax_raw = self.fig.add_subplot(gs[0])
        self.ax_filt = self.fig.add_subplot(gs[1])
        self.ax_proof = self.fig.add_subplot(gs[2])
        self._style_axes()

        plot_frame = tk.Frame(plot_col, bg=PANEL)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._init_proof_chart()

        tk.Label(
            plot_col,
            text="Analisis & insight (dari FFT + statistik array yang sama)",
            font=("Segoe UI", 9, "bold"),
            fg=SUCCESS,
            bg=PANEL,
        ).pack(anchor=tk.W, pady=(6, 2))
        compare_wrap = tk.Frame(plot_col, bg="#0f1115")
        compare_wrap.pack(fill=tk.BOTH, expand=False)
        self.compare_text = tk.Text(
            compare_wrap,
            height=7,
            bg="#0f1115",
            fg=TEXT,
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=8,
        )
        self.compare_text.pack(fill=tk.BOTH, expand=True)
        self.compare_text.config(state=tk.DISABLED)
        self._set_compare_placeholder()
        self._show_phase_detail(Phase.IDLE)

    def _block(
        self,
        tag: str,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        sub: str = "",
    ) -> None:
        active = tag in self.sim.active_blocks()
        fill = ACTIVE if active else "#2d333b"
        outline = ACCENT if active else WIRE
        self.canvas.create_rectangle(
            x, y, x + w, y + h, fill=fill, outline=outline, width=2, tags=("blk", tag)
        )
        self.canvas.create_text(
            x + w // 2,
            y + h // 2 - (8 if sub else 0),
            text=label,
            fill="#111" if active else TEXT,
            font=("Segoe UI", 7, "bold"),
            tags=("blk", tag),
        )
        if sub:
            self.canvas.create_text(
                x + w // 2,
                y + h // 2 + 10,
                text=sub,
                fill="#333" if active else MUTED,
                font=("Segoe UI", 6),
                tags=("blk", tag),
            )

    def _arrow(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.canvas.create_line(x1, y1, x2, y2, fill=WIRE, width=2, arrow=tk.LAST)

    def _draw_diagram(self) -> None:
        self.canvas.delete("all")
        s = 0.65

        def S(v: int | float) -> int:
            return int(v * s)

        self._block("cuff", S(30), S(30), S(95), S(48), "Manset", "BP")
        self._block("pump", S(25), S(108), S(78), S(40), "Pompa", "")
        self._block("valve_a", S(115), S(108), S(58), S(40), "Katup", "isi")
        self._block("valve_b", S(182), S(108), S(58), S(40), "Katup", "buang")
        self.canvas.create_line(S(77), S(78), S(64), S(108), fill=WIRE, width=2)
        self.canvas.create_line(S(77), S(78), S(144), S(108), fill=WIRE, width=2)
        self.canvas.create_line(S(77), S(78), S(211), S(108), fill=WIRE, width=2)

        if self.sim.pump_on:
            self.canvas.create_oval(S(95), S(125), S(115), S(145), fill="#ff6b6b", outline="")
        if self.sim.valve_inflate_open:
            self.canvas.create_text(
                S(137), S(155), text="OPEN", fill=SUCCESS, font=("Segoe UI", 6, "bold")
            )
        if self.sim.valve_deflate_open:
            self.canvas.create_text(
                S(202), S(155), text="OPEN", fill=SUCCESS, font=("Segoe UI", 6, "bold")
            )

        y = S(200)
        self._block("sensor", S(25), y, S(108), S(48), "Sensor", "mV")
        self._arrow(S(133), y + S(24), S(158), y + S(24))
        self._block("ad620", S(158), y, S(88), S(48), "AD620", "")
        self._arrow(S(246), y + S(24), S(268), y + S(24))
        self._block("tlc", S(268), y, S(92), S(48), "TLC", "")
        self._arrow(S(360), y + S(24), S(382), y + S(24))
        self._block("stm32", S(382), y, S(108), S(48), "STM32", "ADC")

        self._arrow(S(436), y + S(48), S(436), S(268))
        self._block("host", S(300), S(268), S(220), S(52), "PC Host", "paralel")

        ny = S(338)
        self._block("node_a", S(295), ny, S(72), S(34), "A", "")
        self._block("node_b", S(375), ny, S(72), S(34), "B", "")
        self._block("node_c", S(455), ny, S(72), S(34), "C", "")
        if self.sim.distributed_node:
            nx = {"A": S(295), "B": S(375), "C": S(455)}
            x0 = nx.get(self.sim.distributed_node, S(360))
            self.canvas.create_rectangle(
                x0 - 2, ny - 2, x0 + S(72), ny + S(34), outline=SUCCESS, width=2
            )

        if self.sim.adc_progress > 0:
            self.canvas.create_rectangle(
                S(395),
                S(248),
                S(395) + int(S(90) * self.sim.adc_progress),
                S(258),
                fill=ACCENT,
                outline="",
            )
        if self.sim.parallel_progress > 0:
            self.canvas.create_rectangle(
                S(345),
                S(332),
                S(345) + int(S(190) * self.sim.parallel_progress),
                S(342),
                fill=SUCCESS,
                outline="",
            )

    def _show_phase_detail(self, phase: Phase) -> None:
        info = self.sim.phase_info(phase)
        self.phase_title_var.set(info.short)
        self.phase_var.set(STEP_GUIDE.get(phase, info.short))
        self.step_guide_var.set(STEP_GUIDE.get(phase, ""))
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, info.detail)
        self.detail_text.config(state=tk.DISABLED)

    def _update_telemetry_display(self) -> None:
        t = self.sim.telemetry
        if t.sample_count == 0:
            self.telemetry_var.set("Rangkaian sensor→ADC: (jalankan demo)")
            return
        self.telemetry_var.set(
            f"Sensor {t.bridge_peak_mv:.0f} mV → AD620 → ADC kode {t.adc_code_peak} "
            f"({t.sample_count} sampel)"
        )

    def _style_axes(self) -> None:
        for ax, title, color in (
            (
                self.ax_raw,
                f"SEBELUM — masih ada hum listrik {NOTCH_TARGET_HZ:.0f} Hz",
                "#ff6b6b",
            ),
            (self.ax_filt, "SESUDAH — sudah difilter di PC Host", SUCCESS),
        ):
            ax.set_facecolor("#0f1115")
            ax.set_title(title, color=TEXT, fontsize=10, fontweight="bold", pad=6)
            ax.tick_params(colors=MUTED, labelsize=8)
            ax.spines[:].set_color(WIRE)
            ax.set_ylabel("Amplitudo (mV eq.)", color=MUTED, fontsize=10)
            ax.grid(True, color=WIRE, alpha=0.35, linestyle="--")
        self.ax_filt.set_xlabel("Sampel (200 Hz × 10 s)", color=MUTED, fontsize=10)

    def _proof_row_values(
        self, cmp: FilterComparison, n_samples: int
    ) -> dict[str, tuple[str, str, str]]:
        return {
            "hum": (
                f"{cmp.hum_power_before:.4f}",
                f"{cmp.hum_power_after:.4f}",
                f"↓ {cmp.hum_reduction_pct:.1f}%  (bukti FFT)",
            ),
            "noise": (
                f"{cmp.noise_std_before:.4f}",
                f"{cmp.noise_std_after:.4f}",
                f"↓ {cmp.noise_reduction_pct:.1f}%",
            ),
            "rms": (
                f"{cmp.rms_before:.2f}",
                f"{cmp.rms_after:.2f}",
                f"{((cmp.rms_after - cmp.rms_before) / cmp.rms_before * 100):+.1f}%"
                if cmp.rms_before > 1e-9
                else "—",
            ),
            "peak": (
                f"{cmp.peak_before:.2f}",
                f"{cmp.peak_after:.2f}",
                f"{cmp.peak_change_pct:+.1f}%",
            ),
            "bp": (
                f"{cmp.bp_sys_before}/{cmp.bp_dia_before}",
                f"{cmp.bp_sys_after}/{cmp.bp_dia_after}",
                "demo (bukan klinis)",
            ),
            "samples": (
                str(n_samples),
                str(n_samples),
                f"≈ {n_samples / ADC_RATE_HZ:.1f} s data",
            ),
        }

    def _update_proof_panel(self, cmp: FilterComparison, n_samples: int) -> None:
        rows = self._proof_row_values(cmp, n_samples)
        for key in PROOF_ROW_KEYS:
            vals = rows[key]
            for var, val in zip(self._proof_cells[key], vals):
                var.set(val)
        self._insight_vars["hum"].set(
            f"{cmp.hum_power_before:.3f} → {cmp.hum_power_after:.3f}  (↓{cmp.hum_reduction_pct:.0f}%)"
        )
        self._insight_vars["noise"].set(
            f"{cmp.noise_std_before:.3f} → {cmp.noise_std_after:.3f}  (↓{cmp.noise_reduction_pct:.0f}%)"
        )
        self._insight_vars["rms"].set(f"{cmp.rms_before:.1f} → {cmp.rms_after:.1f}")
        self._insight_vars["peak"].set(
            f"{cmp.peak_before:.1f} → {cmp.peak_after:.1f}  ({cmp.peak_change_pct:+.1f}%)"
        )
        self._draw_proof_bars(cmp)

    def _clear_proof_panel(self) -> None:
        for key in PROOF_ROW_KEYS:
            for var in self._proof_cells[key]:
                var.set("—")
        for var in self._insight_vars.values():
            var.set("—")
        self._init_proof_chart()

    def _refresh_canvas(self) -> None:
        if hasattr(self, "plot_canvas"):
            self.plot_canvas.draw_idle()

    def _init_proof_chart(self) -> None:
        self.ax_proof.clear()
        self.ax_proof.set_facecolor("#0f1115")
        self.ax_proof.set_title(
            "Grafik batang: bukti perbandingan angka",
            color=TEXT,
            fontsize=9,
            fontweight="bold",
            pad=6,
        )
        self.ax_proof.tick_params(colors=MUTED, labelsize=7)
        for spine in self.ax_proof.spines.values():
            spine.set_color(WIRE)
        self.ax_proof.text(
            0.5,
            0.5,
            "Jalankan demo untuk perbandingan\nhum, noise, RMS, peak",
            transform=self.ax_proof.transAxes,
            ha="center",
            va="center",
            color=MUTED,
            fontsize=9,
        )
        self._refresh_canvas()

    def _draw_proof_bars(self, cmp: FilterComparison) -> None:
        self.ax_proof.clear()
        self.ax_proof.set_facecolor("#0f1115")
        labels = ["Hum\n50Hz", "Noise", "RMS", "Peak"]
        before = [
            cmp.hum_power_before,
            cmp.noise_std_before,
            cmp.rms_before,
            cmp.peak_before,
        ]
        after = [
            cmp.hum_power_after,
            cmp.noise_std_after,
            cmp.rms_after,
            cmp.peak_after,
        ]
        x = np.arange(len(labels))
        w = 0.35
        b1 = self.ax_proof.bar(x - w / 2, before, w, label="Sebelum", color="#ff6b6b", alpha=0.9)
        b2 = self.ax_proof.bar(x + w / 2, after, w, label="Sesudah", color=SUCCESS, alpha=0.9)
        self.ax_proof.set_xticks(x)
        self.ax_proof.set_xticklabels(labels, color=TEXT, fontsize=8)
        self.ax_proof.set_ylabel("Metrik", color=MUTED, fontsize=7)
        self.ax_proof.set_title(
            "Bukti visual — batang = angka di tabel",
            color=TEXT,
            fontsize=9,
            fontweight="bold",
            pad=6,
        )
        self.ax_proof.legend(loc="upper right", fontsize=7, facecolor=PANEL, labelcolor=TEXT)
        self.ax_proof.tick_params(colors=MUTED, labelsize=7)
        for spine in self.ax_proof.spines.values():
            spine.set_color(WIRE)
        for bars, vals in ((b1, before), (b2, after)):
            for bar, val in zip(bars, vals):
                h = bar.get_height()
                self.ax_proof.text(
                    bar.get_x() + bar.get_width() / 2,
                    h,
                    f"{val:.2f}" if val < 100 else f"{val:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=6,
                    color=TEXT,
                )
        if cmp.hum_reduction_pct > 0:
            self.ax_proof.annotate(
                f"Hum ↓{cmp.hum_reduction_pct:.0f}%",
                xy=(0, max(before[0], after[0])),
                xytext=(0, max(before[0], after[0]) * 1.12),
                ha="center",
                color=SUCCESS,
                fontsize=7,
                fontweight="bold",
            )

    def _format_easy_summary(self, cmp: FilterComparison, n_samples: int) -> str:
        return (
            "═══ ANALISIS (FFT + statistik dari array sinyal yang sama) ═══\n\n"
            f"• Hum 50 Hz: {cmp.hum_power_before:.4f} → {cmp.hum_power_after:.4f} "
            f"(turun {cmp.hum_reduction_pct:.1f}%) — bukti filter notch bekerja.\n\n"
            f"• Noise: std {cmp.noise_std_before:.4f} → {cmp.noise_std_after:.4f} "
            f"(turun {cmp.noise_reduction_pct:.1f}%).\n\n"
            f"• RMS: {cmp.rms_before:.2f} → {cmp.rms_after:.2f} · Peak: "
            f"{cmp.peak_before:.2f} → {cmp.peak_after:.2f} ({cmp.peak_change_pct:+.1f}%).\n\n"
            f"• BP demo: {cmp.bp_sys_before}/{cmp.bp_dia_before} → "
            f"{cmp.bp_sys_after}/{cmp.bp_dia_after} mmHg (bukan klinis).\n\n"
            f"• Data: {n_samples} sampel @ {ADC_RATE_HZ} Hz "
            f"(≈ {n_samples / ADC_RATE_HZ:.1f} s).\n\n"
            "Kesimpulan IFB 206: pemrosesan Host (paralel 8 chunk + node A→B→C) "
            "menekan gangguan tanpa mengubah hardware CuffnCode."
        )

    def _set_compare_placeholder(self) -> None:
        text = (
            "Setelah «Mulai Demo» terisi:\n"
            "• Empat kartu insight (Hum, Noise, RMS, Peak)\n"
            "• Tabel Sebelum / Sesudah / Perubahan (6 baris)\n"
            "• Grafik gelombang + grafik batang\n"
            "• Teks analisis ini (FFT, noise, BP, paralel, distributed)\n\n"
            "Semua angka dari array sinyal yang sama."
        )
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert(tk.END, text)
        self.compare_text.config(state=tk.DISABLED)

    def _update_comparison_panel(
        self, cmp: FilterComparison, n_samples: int = 0
    ) -> None:
        self._comparison = cmp
        if n_samples > 0:
            self._update_proof_panel(cmp, n_samples)
        body = self._format_easy_summary(cmp, n_samples or 0)
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert(tk.END, body)
        self.compare_text.tag_configure("head", foreground=SUCCESS, font=("Segoe UI", 9, "bold"))
        self.compare_text.tag_add("head", "1.0", "1.end")
        self.compare_text.config(state=tk.DISABLED)

    def _init_plot(self) -> None:
        self.ax_raw.clear()
        self.ax_filt.clear()
        self._style_axes()
        self._init_proof_chart()

    def _log(self, msg: str) -> None:
        self.sim.log.append(msg)
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def _set_phase(self, phase: Phase, progress: float | None = None) -> None:
        self.sim.phase = phase
        self._show_phase_detail(phase)
        info = self.sim.phase_info(phase)
        for line in info.log_lines:
            self._log(line)
        if progress is not None:
            self.progress["value"] = progress
        self._draw_diagram()
        self.root.update_idletasks()

    def _on_reset(self) -> None:
        if self._running:
            return
        if self._anim_after:
            self.root.after_cancel(self._anim_after)
            self._anim_after = None
        self.sim.reset()
        self._wave_idx = 0
        self.progress["value"] = 0
        self.progress_pct_var.set("Progress: 0%")
        self._show_phase_detail(Phase.IDLE)
        self.pressure_var.set("Tekanan manset: —")
        self.telemetry_var.set("Rangkaian sensor→ADC: —")
        self.bp_var.set("BP simulasi: — / —")
        self.node_var.set("Node A→B→C: —")
        self.parallel_var.set("Filter paralel: —")
        self.log_box.delete("1.0", tk.END)
        self._comparison = None
        self._clear_proof_panel()
        self._set_compare_placeholder()
        self._draw_diagram()
        self._init_plot()
        self.btn_start.config(state=tk.NORMAL)

    def _on_start(self) -> None:
        if self._running:
            return
        self._running = True
        self.btn_start.config(state=tk.DISABLED)
        self.log_box.delete("1.0", tk.END)
        self.sim.reset()
        threading.Thread(target=self._run_simulation, daemon=True).start()

    def _run_simulation(self) -> None:
        try:
            result = self.sim.prepare_signal(duration_s=10.0)
            self.root.after(0, self._update_telemetry_display)
            self._log("=== Demo dimulai — simulasi software CuffnCode ===")
            self._log("Alur: manset → sensor → penguat → STM32 → PC Host (paralel + 3 node)")

            steps: list[tuple[Phase, float, float, callable | None]] = [
                (Phase.PUMP_INFLATE, 8, 5, self._step_inflate),
                (Phase.VALVE_HOLD, 18, 12, self._step_hold),
                (Phase.VALVE_DEFLATE, 28, 18, self._step_deflate),
                (Phase.SENSOR_BRIDGE, 38, 25, self._step_sensor),
                (Phase.AFE_AD620, 48, 32, self._step_ad620),
                (Phase.AFE_TLC2272, 55, 38, self._step_tlc),
                (Phase.STM32_ADC, 65, 45, self._step_adc),
                (Phase.HOST_PARALLEL, 80, 60, self._step_parallel),
                (Phase.HOST_DISTRIBUTED, 92, 75, self._step_distributed),
                (Phase.DONE, 100, 100, None),
            ]

            for phase, pct, pressure, hook in steps:
                self.root.after(0, lambda p=phase, pc=pct: self._apply_phase(p, pc))
                self.root.after(0, lambda pr=pressure: self._update_pressure(pr))
                if hook:
                    hook(result)
                else:
                    time.sleep(0.45)
                self.root.after(0, self._draw_diagram)

            self.root.after(0, lambda: self._finish(result))
        finally:
            self._running = False
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))

    def _apply_phase(self, phase: Phase, progress: float) -> None:
        """Update UI phase tanpa duplikasi log dari thread."""
        self.sim.phase = phase
        self._show_phase_detail(phase)
        self.progress["value"] = progress
        self.progress_pct_var.set(f"Progress: {progress:.0f}%")
        self.step_guide_var.set(STEP_GUIDE.get(phase, ""))
        info = self.sim.phase_info(phase)
        for line in info.log_lines:
            self._log(line)
        self._draw_diagram()

    def _update_pressure(self, mmhg: float) -> None:
        self.sim.cuff_pressure_mmhg = mmhg
        self.pressure_var.set(f"Tekanan manset: {mmhg:.0f} mmHg (simulasi)")

    def _step_sensor(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[Sensor] Membaca tekanan ≈ {t.bridge_peak_mv:.1f} mV dari manset")
        self.root.after(0, self._update_telemetry_display)
        time.sleep(0.7)

    def _step_ad620(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[AD620] Memperkuat sinyal → ≈ {t.ad620_peak_mv:.0f} mV (gain ~{AD620_GAIN:.0f})")
        self.root.after(0, self._update_telemetry_display)
        time.sleep(0.7)

    def _step_tlc(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[TLC2272] Offset tegangan → ≈ {t.after_offset_v:.2f} V")
        self.root.after(0, self._update_telemetry_display)
        time.sleep(0.7)

    def _step_inflate(self, _result: SimulationResult) -> None:
        self.sim.pump_on = True
        self.sim.valve_inflate_open = True
        self.sim.valve_deflate_open = False
        self._draw_on_main()
        for p in range(0, 190, 19):
            self._update_pressure_on_main(p)
            time.sleep(0.08)
        self.sim.pump_on = False

    def _step_hold(self, _r: SimulationResult) -> None:
        self.sim.valve_inflate_open = False
        self.sim.valve_deflate_open = False
        self._draw_on_main()
        time.sleep(0.6)

    def _step_deflate(self, result: SimulationResult) -> None:
        self.sim.valve_deflate_open = True
        self.sim.valve_inflate_open = False
        self._draw_on_main()
        n = len(result.raw)
        for i in range(0, n, max(1, n // 40)):
            self._wave_idx = i
            pr = 190 - (i / n) * 150
            self._update_pressure_on_main(pr)
            self._plot_slice_on_main(result, i)
            time.sleep(0.05)
        self.sim.valve_deflate_open = False

    def _step_adc(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[STM32] ADC digital — kode puncak ≈ {t.adc_code_peak} ({ADC_RATE_HZ} Hz)")
        self._log("[STM32] Data dikirim ke PC Host untuk filter")
        for k in range(1, 21):
            self.sim.adc_progress = k / 20
            self._draw_on_main()
            time.sleep(0.04)

    def _step_parallel(self, result: SimulationResult) -> None:
        self._log(f"[PC Host] Filter hum {NOTCH_TARGET_HZ:.0f} Hz + rata-rata (paralel)")
        chunks = np.array_split(result.raw, 8)
        fs = result.fs
        for i in range(len(chunks)):
            process_chunk((i, chunks[i], fs, 4))
            self.sim.parallel_progress = (i + 1) / len(chunks)
            self.root.after(
                0,
                lambda n=i + 1, total=len(chunks): self.parallel_var.set(
                    f"Filter paralel: bagian {n}/{total}"
                ),
            )
            self._draw_on_main()
            self._log(f"  → Core memproses bagian sinyal {i + 1} dari {len(chunks)}")
            time.sleep(0.12)
        self._log("[PC Host] Gabung hasil → siap dibaca")
        cmp = compare_before_after(result.raw, result.filtered, result.fs)
        n = len(result.raw)
        self.root.after(0, lambda c=cmp, ns=n: self._update_comparison_panel(c, ns))
        self.root.after(0, lambda: self._plot_full(result))
        self._log(f"[Bukti data] Hum FFT: {cmp.hum_power_before:.4f} → {cmp.hum_power_after:.4f}")
        self._log(f"[Bukti data] Noise std: {cmp.noise_std_before:.4f} → {cmp.noise_std_after:.4f}")
        self._log(f"[Bukti data] Peak: {cmp.peak_before:.2f} → {cmp.peak_after:.2f}")

    def _step_distributed(self, _r: SimulationResult) -> None:
        nodes = [
            ("A", "Mengambil data ADC (seperti dari STM32)"),
            ("B", f"Memfilter sinyal (notch {NOTCH_TARGET_HZ:.0f} Hz)"),
            ("C", "Menyimpan & menampilkan hasil tekanan (demo)"),
        ]
        for node, msg in nodes:
            self.sim.distributed_node = node
            self.root.after(
                0, lambda n=node: self.node_var.set(f"Node terdistribusi: aktif {n}")
            )
            self._log(f"[Node {node}] {msg}")
            self._draw_on_main()
            time.sleep(0.55)
        self.sim.distributed_node = ""

    def _finish(self, result: SimulationResult) -> None:
        cmp = self._comparison or compare_before_after(result.raw, result.filtered, result.fs)
        self._update_comparison_panel(cmp, len(result.raw))
        self.bp_var.set(
            f"BP simulasi: {cmp.bp_sys_before}/{cmp.bp_dia_before} → "
            f"{cmp.bp_sys_after}/{cmp.bp_dia_after} mmHg"
        )
        self.node_var.set("Node A→B→C: selesai ✓")
        self.parallel_var.set("Filter paralel: 8 bagian ✓")
        self._plot_full(result)
        self._update_telemetry_display()
        self._log("=== SELESAI ===")
        self._log(
            f"Hum listrik turun {cmp.hum_reduction_pct:.0f}% | Noise turun {cmp.noise_reduction_pct:.0f}%"
        )
        self._log(
            f"Tekanan simulasi: {cmp.bp_sys_before}/{cmp.bp_dia_before} → "
            f"{cmp.bp_sys_after}/{cmp.bp_dia_after} mmHg (bukan alat medis)"
        )
        self._log("Lihat tabel, grafik batang, kartu insight, dan analisis di panel kanan.")
        self._apply_phase(Phase.DONE, 100)

    def _plot_full(self, result: SimulationResult) -> None:
        self._plot_slice(result, len(result.raw), show_legend=True)

    def _plot_slice(
        self, result: SimulationResult, end: int, show_legend: bool = False
    ) -> None:
        end = min(end, len(result.raw))
        if end < 2:
            return
        t = np.arange(end) / result.fs
        raw = result.raw[:end]
        filt = result.filtered[:end]

        self.ax_raw.clear()
        self.ax_filt.clear()
        self._style_axes()

        self.ax_raw.plot(t, raw, color="#ff6b6b", linewidth=1.2, label="SEBELUM (raw)")
        if show_legend and self._comparison:
            c = self._comparison
            self.ax_raw.text(
                0.02,
                0.95,
                f"DATA: hum={c.hum_power_before:.4f}  peak={c.peak_before:.2f}  rms={c.rms_before:.2f}",
                transform=self.ax_raw.transAxes,
                color="#ff8787",
                fontsize=8,
                va="top",
                family="monospace",
            )

        self.ax_filt.plot(t, filt, color=SUCCESS, linewidth=1.2, label="SESUDAH (filtered)")
        if show_legend and self._comparison:
            c = self._comparison
            self.ax_filt.text(
                0.02,
                0.95,
                f"DATA: hum={c.hum_power_after:.4f} (↓{c.hum_reduction_pct:.0f}%)  "
                f"peak={c.peak_after:.2f}  noise↓{c.noise_reduction_pct:.0f}%",
                transform=self.ax_filt.transAxes,
                color=SUCCESS,
                fontsize=8,
                va="top",
                family="monospace",
            )
            self.ax_filt.axhline(
                c.peak_after,
                color=ACCENT,
                linestyle="--",
                alpha=0.7,
                linewidth=1,
                label=f"Peak envelope {c.peak_after:.1f}",
            )

        if show_legend:
            self.ax_raw.legend(loc="upper right", fontsize=9, facecolor=PANEL, labelcolor=TEXT)
            self.ax_filt.legend(loc="upper right", fontsize=9, facecolor=PANEL, labelcolor=TEXT)

        if show_legend and self._comparison:
            self._draw_proof_bars(self._comparison)
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.92, bottom=0.06, hspace=0.42)
        self._refresh_canvas()

    def _draw_on_main(self) -> None:
        self.root.after(0, self._draw_diagram)

    def _update_pressure_on_main(self, p: float) -> None:
        self.root.after(0, lambda: self._update_pressure(p))

    def _plot_slice_on_main(self, result: SimulationResult, end: int) -> None:
        self.root.after(0, lambda: self._plot_slice(result, end))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass
    app = CuffnCodeGUI(root)
    app.run()


if __name__ == "__main__":
    main()
