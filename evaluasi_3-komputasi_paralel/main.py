"""
CuffnCode - Sistem Kontrol Solenoid Valve & DC Micro-Pump
Evaluasi 3 - IFB 206 Komputasi Paralel
Nama   : senja
NIM    : 152024191
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import multiprocessing
import queue
import time
import random
import math
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# ─────────────────────────────────────────────
#  KOMPUTASI PARALEL — Multiprocessing Worker
# ─────────────────────────────────────────────

def pressure_worker(cmd_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
    """
    Worker process terpisah untuk menghitung tekanan pompa secara paralel.
    Menggunakan multiprocessing agar tidak memblokir GUI thread.
    """
    valve1_open = False
    valve2_open = False
    pump_active = False
    pressure = 0.0
    flow_rate = 0.0

    while True:
        # Baca perintah jika ada
        try:
            cmd = cmd_queue.get_nowait()
            if cmd == "STOP":
                break
            elif cmd == "VALVE1_ON":
                valve1_open = True
            elif cmd == "VALVE1_OFF":
                valve1_open = False
            elif cmd == "VALVE2_ON":
                valve2_open = True
            elif cmd == "VALVE2_OFF":
                valve2_open = False
            elif cmd == "PUMP_ON":
                pump_active = True
            elif cmd == "PUMP_OFF":
                pump_active = False
        except Exception:
            pass

        # Simulasi fisika tekanan
        if pump_active:
            target_pressure = 2.5
            if valve1_open:
                target_pressure -= 0.8
            if valve2_open:
                target_pressure -= 0.6
            pressure += (target_pressure - pressure) * 0.15
            flow_rate = pressure * 0.4 + random.uniform(-0.05, 0.05)
        else:
            pressure *= 0.92
            flow_rate = max(0, flow_rate * 0.85)

        # Tambah noise realistis
        pressure += random.uniform(-0.02, 0.02)
        pressure = max(0.0, min(pressure, 5.0))
        flow_rate = max(0.0, flow_rate)

        result_queue.put({
            "pressure": round(pressure, 3),
            "flow_rate": round(flow_rate, 3),
            "valve1": valve1_open,
            "valve2": valve2_open,
            "pump": pump_active,
            "timestamp": time.time()
        })

        time.sleep(0.1)


# ─────────────────────────────────────────────
#  SIGNAL SIMULATION — Thread untuk Real-time Plot
# ─────────────────────────────────────────────

def signal_simulation_thread(data_buffer: list, lock: threading.Lock, stop_event: threading.Event):
    """
    Thread terpisah untuk menghasilkan sinyal simulasi sensor secara real-time.
    Menggunakan threading agar GUI tetap responsif.
    """
    t = 0
    while not stop_event.is_set():
        # Sinyal gabungan: gelombang + noise
        signal = (
            1.5 * math.sin(2 * math.pi * 0.5 * t) +
            0.5 * math.sin(2 * math.pi * 1.5 * t) +
            random.uniform(-0.1, 0.1)
        )
        with lock:
            data_buffer.append(signal)
            if len(data_buffer) > 200:
                data_buffer.pop(0)
        t += 0.05
        time.sleep(0.05)


# ─────────────────────────────────────────────
#  GUI UTAMA
# ─────────────────────────────────────────────

class CuffnCodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CuffnCode — Sistem Kontrol Valve & Pompa")
        self.geometry("1200x750")
        self.configure(bg="#0d1117")
        self.resizable(True, True)

        # ── State ──
        self.valve1_state = False
        self.valve2_state = False
        self.pump_state   = False

        self.pressure_history  = []
        self.flow_history      = []
        self.time_history      = []
        self.start_time        = time.time()

        self.signal_buffer = []
        self.signal_lock   = threading.Lock()
        self.stop_signal   = threading.Event()

        self.log_lines = []

        # ── Multiprocessing ──
        self.cmd_queue    = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.worker_proc  = multiprocessing.Process(
            target=pressure_worker,
            args=(self.cmd_queue, self.result_queue),
            daemon=True
        )
        self.worker_proc.start()

        # ── Signal thread ──
        self.sig_thread = threading.Thread(
            target=signal_simulation_thread,
            args=(self.signal_buffer, self.signal_lock, self.stop_signal),
            daemon=True
        )
        self.sig_thread.start()

        # ── Build UI ──
        self._build_ui()
        self._start_polling()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg="#161b22", height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  CuffnCode", font=("Courier New", 20, "bold"),
                 fg="#58a6ff", bg="#161b22").pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text="IFB 206 Komputasi Paralel  |  Evaluasi 3",
                 font=("Courier New", 11), fg="#8b949e", bg="#161b22").pack(side="left", padx=8)

        self.clock_lbl = tk.Label(hdr, text="", font=("Courier New", 11),
                                  fg="#3fb950", bg="#161b22")
        self.clock_lbl.pack(side="right", padx=20)
        self._tick_clock()

        # ── Main body ──
        body = tk.Frame(self, bg="#0d1117")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        left  = tk.Frame(body, bg="#0d1117")
        right = tk.Frame(body, bg="#0d1117")
        left.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="y", padx=(10, 0))

        # ── Plots ──
        self._build_plots(left)

        # ── Control Panel ──
        self._build_control_panel(right)

        # ── Log ──
        self._build_log(right)

    def _build_plots(self, parent):
        fig = Figure(figsize=(8, 6), facecolor="#0d1117")
        fig.subplots_adjust(hspace=0.45, left=0.08, right=0.97, top=0.93, bottom=0.08)

        # Plot 1: Tekanan
        self.ax1 = fig.add_subplot(3, 1, 1)
        self.ax1.set_facecolor("#161b22")
        self.ax1.set_title("Tekanan Sistem (bar)", color="#c9d1d9", fontsize=9, pad=4)
        self.ax1.tick_params(colors="#8b949e", labelsize=7)
        for spine in self.ax1.spines.values():
            spine.set_color("#30363d")
        self.line_pressure, = self.ax1.plot([], [], color="#58a6ff", linewidth=1.5)
        self.ax1.set_ylim(0, 5)
        self.ax1.set_xlim(0, 60)
        self.ax1.set_ylabel("bar", color="#8b949e", fontsize=7)
        self.ax1.axhline(y=2.5, color="#f85149", linestyle="--", linewidth=0.8, alpha=0.6)

        # Plot 2: Flow Rate
        self.ax2 = fig.add_subplot(3, 1, 2)
        self.ax2.set_facecolor("#161b22")
        self.ax2.set_title("Flow Rate (L/min)", color="#c9d1d9", fontsize=9, pad=4)
        self.ax2.tick_params(colors="#8b949e", labelsize=7)
        for spine in self.ax2.spines.values():
            spine.set_color("#30363d")
        self.line_flow, = self.ax2.plot([], [], color="#3fb950", linewidth=1.5)
        self.ax2.set_ylim(0, 2)
        self.ax2.set_xlim(0, 60)
        self.ax2.set_ylabel("L/min", color="#8b949e", fontsize=7)

        # Plot 3: Signal Simulasi
        self.ax3 = fig.add_subplot(3, 1, 3)
        self.ax3.set_facecolor("#161b22")
        self.ax3.set_title("Sinyal Sensor (real-time thread)", color="#c9d1d9", fontsize=9, pad=4)
        self.ax3.tick_params(colors="#8b949e", labelsize=7)
        for spine in self.ax3.spines.values():
            spine.set_color("#30363d")
        self.line_signal, = self.ax3.plot([], [], color="#d2a8ff", linewidth=1.2)
        self.ax3.set_ylim(-2.5, 2.5)
        self.ax3.set_ylabel("V", color="#8b949e", fontsize=7)

        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_control_panel(self, parent):
        panel = tk.Frame(parent, bg="#161b22", bd=1, relief="flat",
                         highlightthickness=1, highlightbackground="#30363d")
        panel.pack(fill="x", pady=(0, 8))

        tk.Label(panel, text="KONTROL SISTEM", font=("Courier New", 10, "bold"),
                 fg="#58a6ff", bg="#161b22").pack(pady=(10, 6))

        # ── Gauge frame ──
        gf = tk.Frame(panel, bg="#161b22")
        gf.pack(pady=4)
        self.lbl_pressure = self._gauge(gf, "TEKANAN", "0.000 bar", "#58a6ff")
        self.lbl_flow     = self._gauge(gf, "FLOW", "0.000 L/m", "#3fb950")

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # ── Pump ──
        pump_f = tk.Frame(panel, bg="#161b22")
        pump_f.pack(pady=4)
        tk.Label(pump_f, text="DC MICRO-PUMP", font=("Courier New", 9),
                 fg="#8b949e", bg="#161b22").pack()
        self.btn_pump = tk.Button(
            pump_f, text="▶  PUMP OFF", font=("Courier New", 10, "bold"),
            bg="#21262d", fg="#f85149", activebackground="#30363d",
            activeforeground="#ff7b72", relief="flat", cursor="hand2",
            width=18, pady=5, command=self._toggle_pump
        )
        self.btn_pump.pack(pady=4)

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=14, pady=6)

        # ── Valves ──
        vf = tk.Frame(panel, bg="#161b22")
        vf.pack(pady=4)
        tk.Label(vf, text="SOLENOID VALVES", font=("Courier New", 9),
                 fg="#8b949e", bg="#161b22").grid(row=0, column=0, columnspan=2, pady=(0, 6))

        self.btn_v1 = self._valve_btn(vf, "VALVE 1", row=1, col=0, cmd=self._toggle_valve1)
        self.btn_v2 = self._valve_btn(vf, "VALVE 2", row=1, col=1, cmd=self._toggle_valve2)

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # ── Manual Input ──
        mf = tk.Frame(panel, bg="#161b22")
        mf.pack(pady=4, padx=14, fill="x")
        tk.Label(mf, text="INPUT MANUAL TEKANAN (bar)",
                 font=("Courier New", 8), fg="#8b949e", bg="#161b22").pack(anchor="w")

        inp_row = tk.Frame(mf, bg="#161b22")
        inp_row.pack(fill="x", pady=4)

        self.manual_entry = tk.Entry(inp_row, font=("Courier New", 12),
                                     bg="#21262d", fg="#c9d1d9", insertbackground="#58a6ff",
                                     relief="flat", width=10)
        self.manual_entry.pack(side="left", padx=(0, 6), ipady=4)
        self.manual_entry.insert(0, "1.5")

        tk.Button(inp_row, text="ANALISIS", font=("Courier New", 9, "bold"),
                  bg="#1f6feb", fg="white", activebackground="#388bfd",
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=self._manual_analyze).pack(side="left")

        self.manual_result = tk.Label(mf, text="", font=("Courier New", 9),
                                      fg="#3fb950", bg="#161b22", wraplength=220, justify="left")
        self.manual_result.pack(anchor="w", pady=4)

        tk.Button(panel, text="⟳  RESET DATA", font=("Courier New", 9),
                  bg="#21262d", fg="#8b949e", activebackground="#30363d",
                  relief="flat", cursor="hand2", pady=4,
                  command=self._reset_data).pack(pady=(4, 12))

    def _build_log(self, parent):
        lf = tk.Frame(parent, bg="#161b22", highlightthickness=1,
                      highlightbackground="#30363d")
        lf.pack(fill="both", expand=True)
        tk.Label(lf, text="LOG SISTEM", font=("Courier New", 9, "bold"),
                 fg="#8b949e", bg="#161b22").pack(anchor="w", padx=10, pady=(8, 2))
        self.log_text = tk.Text(lf, font=("Courier New", 8), bg="#0d1117",
                                fg="#3fb950", relief="flat", height=10,
                                state="disabled", wrap="word", insertbackground="#3fb950")
        self.log_text.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────

    def _gauge(self, parent, label, init, color):
        f = tk.Frame(parent, bg="#0d1117", padx=12, pady=8)
        f.pack(side="left", padx=6)
        tk.Label(f, text=label, font=("Courier New", 7), fg="#8b949e", bg="#0d1117").pack()
        lbl = tk.Label(f, text=init, font=("Courier New", 13, "bold"),
                       fg=color, bg="#0d1117", width=11)
        lbl.pack()
        return lbl

    def _valve_btn(self, parent, text, row, col, cmd):
        btn = tk.Button(parent, text=f"⬤  {text}\nCLOSED",
                        font=("Courier New", 8, "bold"),
                        bg="#21262d", fg="#f85149", activebackground="#30363d",
                        relief="flat", cursor="hand2", width=12, pady=6, command=cmd)
        btn.grid(row=row, column=col, padx=5)
        return btn

    def _tick_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime("%H:%M:%S  %d/%m/%Y"))
        self.after(1000, self._tick_clock)

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log_text.config(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        if int(self.log_text.index("end-1c").split(".")[0]) > 200:
            self.log_text.delete("1.0", "50.0")
        self.log_text.config(state="disabled")

    # ──────────────────────────────────────────
    #  CONTROLS
    # ──────────────────────────────────────────

    def _toggle_pump(self):
        self.pump_state = not self.pump_state
        if self.pump_state:
            self.cmd_queue.put("PUMP_ON")
            self.btn_pump.config(text="⏹  PUMP ON", fg="#3fb950", bg="#0d2f16")
            self._log("PUMP → ON  (multiprocess worker aktif)")
        else:
            self.cmd_queue.put("PUMP_OFF")
            self.btn_pump.config(text="▶  PUMP OFF", fg="#f85149", bg="#21262d")
            self._log("PUMP → OFF")

    def _toggle_valve1(self):
        self.valve1_state = not self.valve1_state
        cmd = "VALVE1_ON" if self.valve1_state else "VALVE1_OFF"
        self.cmd_queue.put(cmd)
        state_str = "OPEN" if self.valve1_state else "CLOSED"
        color = "#3fb950" if self.valve1_state else "#f85149"
        bg    = "#0d2f16" if self.valve1_state else "#21262d"
        self.btn_v1.config(text=f"⬤  VALVE 1\n{state_str}", fg=color, bg=bg)
        self._log(f"VALVE 1 → {state_str}")

    def _toggle_valve2(self):
        self.valve2_state = not self.valve2_state
        cmd = "VALVE2_ON" if self.valve2_state else "VALVE2_OFF"
        self.cmd_queue.put(cmd)
        state_str = "OPEN" if self.valve2_state else "CLOSED"
        color = "#3fb950" if self.valve2_state else "#f85149"
        bg    = "#0d2f16" if self.valve2_state else "#21262d"
        self.btn_v2.config(text=f"⬤  VALVE 2\n{state_str}", fg=color, bg=bg)
        self._log(f"VALVE 2 → {state_str}")

    def _manual_analyze(self):
        try:
            val = float(self.manual_entry.get())
        except ValueError:
            self.manual_result.config(text="⚠  Masukkan angka yang valid!", fg="#f85149")
            return

        if val <= 0:
            status = "❌ Tidak ada tekanan"
            color = "#f85149"
        elif val < 1.0:
            status = "⚠  Tekanan terlalu rendah"
            color = "#d29922"
        elif val <= 2.5:
            status = "✅ Tekanan normal"
            color = "#3fb950"
        elif val <= 4.0:
            status = "⚠  Tekanan tinggi — periksa valve"
            color = "#d29922"
        else:
            status = "🚨 OVERPRESSURE! Matikan pompa!"
            color = "#f85149"

        self.manual_result.config(text=f"{status}\n→ {val:.3f} bar", fg=color)
        self._log(f"Analisis manual: {val:.3f} bar — {status.split(' ', 1)[-1]}")

    def _reset_data(self):
        self.pressure_history.clear()
        self.flow_history.clear()
        self.time_history.clear()
        self.start_time = time.time()
        with self.signal_lock:
            self.signal_buffer.clear()
        self._log("Data di-reset.")

    # ──────────────────────────────────────────
    #  POLLING — Ambil data dari multiprocess worker
    # ──────────────────────────────────────────

    def _start_polling(self):
        self._poll()

    def _poll(self):
        # Ambil semua hasil dari queue
        while not self.result_queue.empty():
            try:
                data = self.result_queue.get_nowait()
                t = data["timestamp"] - self.start_time
                self.pressure_history.append(data["pressure"])
                self.flow_history.append(data["flow_rate"])
                self.time_history.append(t)

                # Trim agar tidak terlalu panjang
                if len(self.time_history) > 600:
                    self.pressure_history.pop(0)
                    self.flow_history.pop(0)
                    self.time_history.pop(0)

                # Update gauges
                self.lbl_pressure.config(text=f"{data['pressure']:.3f} bar")
                self.lbl_flow.config(text=f"{data['flow_rate']:.3f} L/m")

                # Warna gauge berdasarkan tekanan
                if data["pressure"] > 4.0:
                    self.lbl_pressure.config(fg="#f85149")
                elif data["pressure"] > 2.5:
                    self.lbl_pressure.config(fg="#d29922")
                else:
                    self.lbl_pressure.config(fg="#58a6ff")

            except Exception:
                pass

        # Update plots
        self._update_plots()
        self.after(150, self._poll)

    def _update_plots(self):
        if len(self.time_history) > 1:
            t = self.time_history
            window = 60
            x_min = max(0, t[-1] - window)
            x_max = max(window, t[-1])

            self.line_pressure.set_data(t, self.pressure_history)
            self.ax1.set_xlim(x_min, x_max)

            self.line_flow.set_data(t, self.flow_history)
            self.ax2.set_xlim(x_min, x_max)

        # Update signal plot
        with self.signal_lock:
            sig = list(self.signal_buffer)
        if len(sig) > 1:
            xs = list(range(len(sig)))
            self.line_signal.set_data(xs, sig)
            self.ax3.set_xlim(0, max(200, len(sig)))

        self.canvas.draw_idle()

    # ──────────────────────────────────────────
    #  CLOSE
    # ──────────────────────────────────────────

    def _on_close(self):
        self.stop_signal.set()
        self.cmd_queue.put("STOP")
        time.sleep(0.2)
        if self.worker_proc.is_alive():
            self.worker_proc.terminate()
        self.destroy()


# ─────────────────────────────────────────────

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = CuffnCodeApp()
    app.mainloop()