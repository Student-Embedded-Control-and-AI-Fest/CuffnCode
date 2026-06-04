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

from hardware_sim import HardwareSimulator, Phase, PHASE_LABELS, SimulationResult
from filters import process_chunk
from signal_analysis import FilterComparison, compare_before_after
from cuffncode_specs import (
    AD620_GAIN,
    ADC_RATE_HZ,
    NOTCH_TARGET_HZ,
    PROJECT_FUNDING,
    PROJECT_TITLE,
    SENSOR_MODEL,
    TLC_OFFSET_V,
)


# Warna tema
BG = "#1a1d23"
PANEL = "#252a33"
ACCENT = "#3d8bfd"
ACTIVE = "#ffc107"
SUCCESS = "#51cf66"
TEXT = "#e9ecef"
MUTED = "#868e96"
WIRE = "#495057"


class CuffnCodeGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CuffnCode — Simulasi Hardware & Paralel")
        self.root.configure(bg=BG)
        self.root.minsize(1400, 900)
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
        header = tk.Frame(self.root, bg=PANEL, pady=10, padx=12)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=f"{PROJECT_TITLE} Simulator",
            font=("Segoe UI", 16, "bold"),
            fg=ACCENT,
            bg=PANEL,
        ).pack(side=tk.LEFT)
        tk.Label(
            header,
            text=f"{PROJECT_FUNDING} | Simulasi software (ref. GitHub CuffnCode)",
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=PANEL,
        ).pack(side=tk.LEFT, padx=12)

        # Toolbar — tombol selalu terlihat (tidak tertutup grafik)
        toolbar = tk.Frame(self.root, bg=PANEL, padx=12, pady=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_start = tk.Button(
            toolbar,
            text="Mulai Simulasi",
            command=self._on_start,
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground="#5c9eff",
            activeforeground="white",
            relief=tk.RAISED,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.btn_start.pack(side=tk.LEFT)

        tk.Button(
            toolbar,
            text="Reset",
            command=self._on_reset,
            font=("Segoe UI", 10),
            bg=WIRE,
            fg=TEXT,
            activeforeground=TEXT,
            relief=tk.RAISED,
            padx=16,
            pady=8,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(toolbar, length=320, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=16)

        tk.Label(
            toolbar,
            text="Klik Mulai Simulasi untuk menjalankan alur hardware + filter",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL,
        ).pack(side=tk.LEFT, padx=8)

        # Log & footer dulu (pack dari bawah) agar tidak ke-push keluar layar
        log_frame = tk.Frame(self.root, bg=BG, padx=10, pady=6)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(log_frame, text="Log proses", font=("Segoe UI", 9, "bold"), fg=MUTED, bg=BG).pack(
            anchor=tk.W
        )
        self.log_box = tk.Text(
            log_frame,
            height=5,
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

        sidebar = tk.Frame(main_row, bg=PANEL, padx=8, pady=8, width=400)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Diagram hardware",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT,
            bg=PANEL,
        ).pack(anchor=tk.W)

        self.canvas = tk.Canvas(sidebar, bg="#0f1115", highlightthickness=0, width=380, height=260)
        self.canvas.pack(pady=4)

        self.phase_title_var = tk.StringVar(value="Siap")
        tk.Label(
            sidebar,
            textvariable=self.phase_title_var,
            font=("Segoe UI", 10, "bold"),
            fg=ACTIVE,
            bg=PANEL,
            wraplength=360,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=2)

        self.phase_var = tk.StringVar(value=PHASE_LABELS[Phase.IDLE])
        tk.Label(
            sidebar,
            textvariable=self.phase_var,
            font=("Segoe UI", 8),
            fg=TEXT,
            bg=PANEL,
            wraplength=360,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        metrics = tk.Frame(sidebar, bg=PANEL)
        metrics.pack(fill=tk.X, pady=6)
        self.pressure_var = tk.StringVar(value="Cuff: — mmHg")
        self.telemetry_var = tk.StringVar(value="AFE: —")
        self.bp_var = tk.StringVar(value="BP (demo): — / — mmHg")
        self.node_var = tk.StringVar(value="Distributed: —")
        for var in (self.pressure_var, self.telemetry_var, self.bp_var, self.node_var):
            tk.Label(metrics, textvariable=var, font=("Consolas", 8), fg=TEXT, bg=PANEL).pack(
                anchor=tk.W
            )

        tk.Label(
            sidebar,
            text="Detail fase",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor=tk.W, pady=(8, 2))

        self.detail_text = tk.Text(
            sidebar,
            height=6,
            bg="#0f1115",
            fg=TEXT,
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=6,
            pady=4,
        )
        self.detail_text.pack(fill=tk.X)
        self.detail_text.config(state=tk.DISABLED)

        self.specs_text = tk.Text(
            sidebar,
            height=5,
            bg="#12151a",
            fg=MUTED,
            font=("Consolas", 7),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=6,
            pady=4,
        )
        self.specs_text.pack(fill=tk.X, pady=4)
        self.specs_text.config(state=tk.DISABLED)
        self._show_phase_detail(Phase.IDLE)

        plot_col = tk.Frame(main_row, bg=PANEL, padx=10, pady=8)
        plot_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            plot_col,
            text="Perbandingan sinyal — SEBELUM vs SESUDAH pemrosesan Host",
            font=("Segoe UI", 12, "bold"),
            fg=ACCENT,
            bg=PANEL,
        ).pack(anchor=tk.W)

        tk.Label(
            plot_col,
            text=(
                f"Atas: SEBELUM (raw + hum {NOTCH_TARGET_HZ:.0f} Hz)  |  "
                f"Bawah: SESUDAH (notch + moving average)"
            ),
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor=tk.W, pady=(0, 6))

        self.fig = Figure(figsize=(10, 6.5), facecolor=PANEL, dpi=96)
        gs = GridSpec(2, 1, figure=self.fig, height_ratios=[1, 1], hspace=0.38)
        self.ax_raw = self.fig.add_subplot(gs[0])
        self.ax_filt = self.fig.add_subplot(gs[1])
        self._style_axes()

        plot_frame = tk.Frame(plot_col, bg=PANEL)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        compare_hdr = tk.Frame(plot_col, bg=PANEL)
        compare_hdr.pack(fill=tk.X, pady=(8, 2))
        tk.Label(
            compare_hdr,
            text="Output: metrik & pengaruh filter",
            font=("Segoe UI", 10, "bold"),
            fg=SUCCESS,
            bg=PANEL,
        ).pack(side=tk.LEFT)

        compare_wrap = tk.Frame(plot_col, bg="#0f1115")
        compare_wrap.pack(fill=tk.BOTH, expand=False, pady=4)

        self.compare_text = tk.Text(
            compare_wrap,
            height=9,
            bg="#0f1115",
            fg=TEXT,
            font=("Consolas", 10),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=10,
        )
        self.compare_text.pack(fill=tk.BOTH, expand=True)
        self.compare_text.config(state=tk.DISABLED)
        self._set_compare_placeholder()

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
            font=("Segoe UI", 9, "bold"),
            tags=("blk", tag),
        )
        if sub:
            self.canvas.create_text(
                x + w // 2,
                y + h // 2 + 12,
                text=sub,
                fill="#333" if active else MUTED,
                font=("Segoe UI", 7),
                tags=("blk", tag),
            )

    def _arrow(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.canvas.create_line(x1, y1, x2, y2, fill=WIRE, width=2, arrow=tk.LAST)

    def _draw_diagram(self) -> None:
        self.canvas.delete("all")
        # Cuff + aktuator (retrofitted pump system)
        self._block("cuff", 30, 30, 95, 48, "Cuff", "manset BP")
        self._block("pump", 25, 108, 78, 40, "DC Pump", "1× micro")
        self._block("valve_a", 115, 108, 58, 40, "Sol-A", "inflate")
        self._block("valve_b", 182, 108, 58, 40, "Sol-B", "deflate")
        self.canvas.create_line(77, 78, 64, 108, fill=WIRE, width=2)
        self.canvas.create_line(77, 78, 144, 108, fill=WIRE, width=2)
        self.canvas.create_line(77, 78, 211, 108, fill=WIRE, width=2)

        if self.sim.pump_on:
            self.canvas.create_oval(95, 125, 115, 145, fill="#ff6b6b", outline="")
        if self.sim.valve_inflate_open:
            self.canvas.create_text(137, 155, text="OPEN", fill=SUCCESS, font=("Segoe UI", 7, "bold"))
        if self.sim.valve_deflate_open:
            self.canvas.create_text(202, 155, text="OPEN", fill=SUCCESS, font=("Segoe UI", 7, "bold"))

        # Rantai sinyal
        y = 200
        self._block("sensor", 25, y, 108, 48, SENSOR_MODEL, "50-100mV FS")
        self._arrow(133, y + 24, 158, y + 24)
        self._block("ad620", 158, y, 88, 48, "AD620", f"G~{AD620_GAIN:.0f}")
        self._arrow(246, y + 24, 268, y + 24)
        self._block("tlc", 268, y, 92, 48, "TLC2272", f"~{TLC_OFFSET_V:.1f}V")
        self._arrow(360, y + 24, 382, y + 24)
        self._block("stm32", 382, y, 108, 48, "STM32F411", "Black Pill")

        self._arrow(436, y + 48, 436, 268)
        self._block("host", 300, 268, 220, 52, "PC Host", f"ADC {ADC_RATE_HZ}Hz sim")

        # Node terdistribusi
        ny = 338
        self._block("node_a", 295, ny, 72, 34, "Node A", "Acquire")
        self._block("node_b", 375, ny, 72, 34, "Node B", "Filter")
        self._block("node_c", 455, ny, 72, 34, "Node C", "BP UI")
        if self.sim.distributed_node:
            nx = {"A": 295, "B": 375, "C": 455}
            x0 = nx.get(self.sim.distributed_node, 360)
            self.canvas.create_rectangle(
                x0 - 2, ny - 2, x0 + 72, ny + 34, outline=SUCCESS, width=3
            )

        # Bar ADC / parallel
        if self.sim.adc_progress > 0:
            self.canvas.create_rectangle(
                395, 248, 395 + int(90 * self.sim.adc_progress), 258, fill=ACCENT, outline=""
            )
            self.canvas.create_text(440, 265, text="ADC", fill=MUTED, font=("Segoe UI", 7))
        if self.sim.parallel_progress > 0:
            self.canvas.create_rectangle(
                345, 332, 345 + int(190 * self.sim.parallel_progress), 342, fill=SUCCESS, outline=""
            )
            self.canvas.create_text(
                440, 348, text="Parallel chunks", fill=MUTED, font=("Segoe UI", 7)
            )

    def _show_phase_detail(self, phase: Phase) -> None:
        info = self.sim.phase_info(phase)
        self.phase_title_var.set(info.title)
        self.phase_var.set(info.short)

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, info.detail)
        self.detail_text.config(state=tk.DISABLED)

        self.specs_text.config(state=tk.NORMAL)
        self.specs_text.delete("1.0", tk.END)
        self.specs_text.insert(tk.END, info.specs)
        self.specs_text.config(state=tk.DISABLED)

    def _update_telemetry_display(self) -> None:
        t = self.sim.telemetry
        if t.sample_count == 0:
            self.telemetry_var.set("AFE: — (jalankan simulasi)")
            return
        self.telemetry_var.set(
            f"Bridge≈{t.bridge_peak_mv:.1f}mV | AD620≈{t.ad620_peak_mv:.0f}mV | "
            f"+offset≈{t.after_offset_v:.2f}V | ADC≈{t.adc_code_peak} | "
            f"{t.sample_count} samp @ {t.fs_hz:.0f}Hz"
        )

    def _style_axes(self) -> None:
        for ax, title, color in (
            (self.ax_raw, f"SEBELUM — Raw (AFE + hum {NOTCH_TARGET_HZ:.0f} Hz)", "#ff6b6b"),
            (self.ax_filt, f"SESUDAH — Filtered (notch + moving avg)", SUCCESS),
        ):
            ax.set_facecolor("#0f1115")
            ax.set_title(title, color=TEXT, fontsize=12, fontweight="bold", pad=10)
            ax.tick_params(colors=MUTED, labelsize=10)
            ax.spines[:].set_color(WIRE)
            ax.set_ylabel("Amplitudo (mV eq.)", color=MUTED, fontsize=10)
            ax.grid(True, color=WIRE, alpha=0.35, linestyle="--")
        self.ax_filt.set_xlabel("Sampel (200 Hz × 10 s)", color=MUTED, fontsize=10)

    def _set_compare_placeholder(self) -> None:
        text = (
            "Jalankan simulasi untuk melihat perbandingan SEBELUM vs SESUDAH.\n\n"
            "SEBELUM  = sinyal dari rantai sensor+AFE (masih ada hum listrik 50 Hz)\n"
            "SESUDAH  = setelah Host: notch 50 Hz + moving average (paralel)\n\n"
            "Panel ini menampilkan metrik & pengaruh terhadap estimasi BP demo."
        )
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert(tk.END, text)
        self.compare_text.config(state=tk.DISABLED)

    def _update_comparison_panel(self, cmp: FilterComparison) -> None:
        self._comparison = cmp
        body = "\n".join(cmp.summary_lines) + "\n\n" + "\n".join(cmp.impact_lines)
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert(tk.END, body)
        # Sorot baris pengaruh
        self.compare_text.tag_configure("impact", foreground=SUCCESS)
        start = body.find("── PENGARUH")
        if start >= 0:
            line = body[:start].count("\n") + 1
            self.compare_text.tag_add("impact", f"{line}.0", tk.END)
        self.compare_text.config(state=tk.DISABLED)

    def _init_plot(self) -> None:
        self.ax_raw.clear()
        self.ax_filt.clear()
        self._style_axes()
        self.plot_canvas.draw_idle()

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
        self._show_phase_detail(Phase.IDLE)
        self.pressure_var.set("Cuff: — mmHg")
        self.telemetry_var.set("AFE: —")
        self.bp_var.set("BP (demo): — / — mmHg")
        self.node_var.set("Distributed: —")
        self.log_box.delete("1.0", tk.END)
        self._comparison = None
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
            self._log("=== CuffnCode — simulasi software (ref. IFAC / GitHub) ===")
            self._log(
                f"Rantai: {SENSOR_MODEL} -> AD620 (G~{AD620_GAIN:.0f}) -> "
                f"TLC2272 (~{TLC_OFFSET_V:.2f}V) -> STM32 -> Host"
            )

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
        info = self.sim.phase_info(phase)
        for line in info.log_lines:
            self._log(line)
        self._draw_diagram()

    def _update_pressure(self, mmhg: float) -> None:
        self.sim.cuff_pressure_mmhg = mmhg
        self.pressure_var.set(f"Cuff: {mmhg:.0f} mmHg (oscillometric sim)")

    def _step_sensor(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[{SENSOR_MODEL}] Bridge peak ≈ {t.bridge_peak_mv:.1f} mV (skala sim)")
        self._log("[Sensor] Impedansi bridge ~4–6 kΩ | FS 50–100 mV (repo)")
        self.root.after(0, self._update_telemetry_display)
        time.sleep(0.7)

    def _step_ad620(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[AD620] Vout ≈ {t.ad620_peak_mv:.0f} mV — G = 1 + 49.4k/470 ≈ {AD620_GAIN:.1f}")
        self.root.after(0, self._update_telemetry_display)
        time.sleep(0.7)

    def _step_tlc(self, result: SimulationResult) -> None:
        t = result.telemetry
        self._log(f"[TLC2272] Level shift → ≈ {t.after_offset_v:.2f} V (divider 47k/56k @ 3.3V)")
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
        self._log(f"[STM32F411] ADC 12-bit @ {ADC_RATE_HZ} Hz — peak code ≈ {t.adc_code_peak}")
        self._log("[STM32] UART/USB ke host untuk algoritma lanjutan (opsional)")
        for k in range(1, 21):
            self.sim.adc_progress = k / 20
            self._draw_on_main()
            time.sleep(0.04)

    def _step_parallel(self, result: SimulationResult) -> None:
        self._log(f"[Host] Notch {NOTCH_TARGET_HZ:.0f} Hz hum killer + moving avg (roadmap repo)")
        chunks = np.array_split(result.raw, 8)
        fs = result.fs
        for i in range(len(chunks)):
            process_chunk((i, chunks[i], fs, 4))
            self.sim.parallel_progress = (i + 1) / len(chunks)
            self._draw_on_main()
            self._log(f"  Pool.map chunk {i + 1}/{len(chunks)} — data parallelism")
            time.sleep(0.12)
        self._log("[Host] Reduce/merge envelope untuk estimasi BP")
        cmp = compare_before_after(result.raw, result.filtered, result.fs)
        self.root.after(0, lambda c=cmp: self._update_comparison_panel(c))
        self.root.after(0, lambda: self._plot_full(result))

    def _step_distributed(self, _r: SimulationResult) -> None:
        nodes = [
            ("A", "Acquisition — batch ADC @ 200 Hz (setara STM32 stream)"),
            ("B", f"Processing — MA + notch {NOTCH_TARGET_HZ:.0f} Hz + peak"),
            ("C", "Storage/UI — simpan & tampilkan SYS/DIA (demo)"),
        ]
        for node, msg in nodes:
            self.sim.distributed_node = node
            self._log(f"[Distributed] Node {node}: {msg}")
            self._draw_on_main()
            time.sleep(0.55)
        self.sim.distributed_node = ""

    def _finish(self, result: SimulationResult) -> None:
        cmp = self._comparison or compare_before_after(result.raw, result.filtered, result.fs)
        self._update_comparison_panel(cmp)
        self.bp_var.set(
            f"BP demo: {cmp.bp_sys_before}/{cmp.bp_dia_before} → "
            f"{cmp.bp_sys_after}/{cmp.bp_dia_after} mmHg"
        )
        self.node_var.set("Distributed: A→B→C selesai")
        self._plot_full(result)
        self._update_telemetry_display()
        self._log(
            f"=== SEBELUM filter: BP demo {cmp.bp_sys_before}/{cmp.bp_dia_before} mmHg ==="
        )
        self._log(
            f"=== SESUDAH filter: BP demo {cmp.bp_sys_after}/{cmp.bp_dia_after} mmHg ==="
        )
        self._log(
            f"Hum {NOTCH_TARGET_HZ:.0f}Hz ↓{cmp.hum_reduction_pct:.1f}% | "
            f"Noise ↓{cmp.noise_reduction_pct:.1f}%"
        )
        self._log("Roadmap repo: PCB KiCad, evaluasi performa, notch 60 Hz")
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
                f"Hum {NOTCH_TARGET_HZ:.0f}Hz power: {c.hum_power_before:.3f}",
                transform=self.ax_raw.transAxes,
                color=MUTED,
                fontsize=9,
                va="top",
            )

        self.ax_filt.plot(t, filt, color=SUCCESS, linewidth=1.2, label="SESUDAH (filtered)")
        if show_legend and self._comparison:
            c = self._comparison
            self.ax_filt.text(
                0.02,
                0.95,
                f"Hum ↓{c.hum_reduction_pct:.0f}% | Noise ↓{c.noise_reduction_pct:.0f}%",
                transform=self.ax_filt.transAxes,
                color=SUCCESS,
                fontsize=9,
                va="top",
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

        self.fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.08, hspace=0.42)
        self.plot_canvas.draw_idle()

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
