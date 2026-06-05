import io
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from src.benchmark import BenchmarkRunner
from src.parallel import ParallelPrimeFinder
from src.serial import SerialPrimeFinder


class PrimeFinderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Parallel Prime Finder")
        self.root.geometry("850x650")
        self.root.resizable(False, False)

        self.cpu_count = ParallelPrimeFinder.get_cpu_count()

        self.mode_var = tk.StringVar(value="serial")
        self.range_var = tk.IntVar(value=1)
        self.worker_var = tk.StringVar(value="2")
        self.custom_worker_var = tk.StringVar(value="")
        self.custom_start_var = tk.StringVar(value="1")
        self.custom_end_var = tk.StringVar(value="100000")

        self.running = False

        self._build_ui()

    def _build_ui(self):
        title_label = ttk.Label(
            self.root,
            text="Parallel Prime Finder",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(pady=10)

        self._build_options_frame()
        self._build_output_frame()
        self._build_buttons_frame()
        self._update_widgets_state()

    def _build_options_frame(self):
        outer_frame = ttk.Frame(self.root)
        outer_frame.pack(fill="x", padx=16)

        mode_frame = ttk.LabelFrame(outer_frame, text="Mode")
        mode_frame.grid(row=0, column=0, padx=8, pady=4, sticky="nsew")
        ttk.Radiobutton(
            mode_frame,
            text="Serial",
            variable=self.mode_var,
            value="serial",
            command=self._on_mode_changed
        ).pack(anchor="w", padx=12, pady=4)
        ttk.Radiobutton(
            mode_frame,
            text="Paralel",
            variable=self.mode_var,
            value="parallel",
            command=self._on_mode_changed
        ).pack(anchor="w", padx=12, pady=4)
        ttk.Radiobutton(
            mode_frame,
            text="Benchmark",
            variable=self.mode_var,
            value="benchmark",
            command=self._on_mode_changed
        ).pack(anchor="w", padx=12, pady=4)

        range_frame = ttk.LabelFrame(outer_frame, text="Rentang Pencarian")
        range_frame.grid(row=0, column=1, padx=8, pady=4, sticky="nsew")
        ttk.Radiobutton(
            range_frame,
            text="1 - 100.000",
            variable=self.range_var,
            value=1,
            command=self._on_range_changed
        ).pack(anchor="w", padx=12, pady=2)
        ttk.Radiobutton(
            range_frame,
            text="1 - 500.000",
            variable=self.range_var,
            value=2,
            command=self._on_range_changed
        ).pack(anchor="w", padx=12, pady=2)
        ttk.Radiobutton(
            range_frame,
            text="1 - 1.000.000",
            variable=self.range_var,
            value=3,
            command=self._on_range_changed
        ).pack(anchor="w", padx=12, pady=2)
        ttk.Radiobutton(
            range_frame,
            text="Custom",
            variable=self.range_var,
            value=4,
            command=self._on_range_changed
        ).pack(anchor="w", padx=12, pady=2)
        custom_range_frame = ttk.Frame(range_frame)
        custom_range_frame.pack(fill="x", padx=12, pady=6)
        ttk.Label(custom_range_frame, text="Batas bawah:").grid(row=0, column=0, sticky="w")
        self.start_entry = ttk.Entry(custom_range_frame, width=12, textvariable=self.custom_start_var)
        self.start_entry.grid(row=0, column=1, padx=6, pady=2)
        ttk.Label(custom_range_frame, text="Batas atas:").grid(row=0, column=2, sticky="w")
        self.end_entry = ttk.Entry(custom_range_frame, width=12, textvariable=self.custom_end_var)
        self.end_entry.grid(row=0, column=3, padx=6, pady=2)

        worker_frame = ttk.LabelFrame(outer_frame, text="Pengaturan Worker")
        worker_frame.grid(row=0, column=2, padx=8, pady=4, sticky="nsew")
        self.worker_buttons = []
        for label, value in [
            ("2 Worker", "2"),
            ("4 Worker", "4"),
            ("8 Worker", "8"),
            (f"Semua cores ({self.cpu_count})", "all"),
            ("Custom", "custom")
        ]:
            rb = ttk.Radiobutton(
                worker_frame,
                text=label,
                variable=self.worker_var,
                value=value,
                command=self._on_worker_changed
            )
            rb.pack(anchor="w", padx=12, pady=2)
            self.worker_buttons.append(rb)

        custom_worker_frame = ttk.Frame(worker_frame)
        custom_worker_frame.pack(fill="x", padx=12, pady=6)
        ttk.Label(custom_worker_frame, text="Jumlah worker:").grid(row=0, column=0, sticky="w")
        self.worker_entry = ttk.Entry(custom_worker_frame, width=10, textvariable=self.custom_worker_var)
        self.worker_entry.grid(row=0, column=1, padx=6, pady=2)

    def _build_output_frame(self):
        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.pack(fill="both", expand=True, padx=16, pady=8)
        self.output_area = scrolledtext.ScrolledText(
            output_frame,
            wrap="word",
            state="disabled",
            height=18,
            font=("Consolas", 10)
        )
        self.output_area.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_buttons_frame(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=16, pady=8)

        self.run_button = ttk.Button(button_frame, text="Jalankan", command=self._on_run)
        self.run_button.pack(side="left", padx=4)
        self.clear_button = ttk.Button(button_frame, text="Bersihkan", command=self._clear_output)
        self.clear_button.pack(side="left", padx=4)
        self.exit_button = ttk.Button(button_frame, text="Keluar", command=self.root.quit)
        self.exit_button.pack(side="right", padx=4)

    def _on_mode_changed(self):
        self._update_widgets_state()

    def _on_range_changed(self):
        if self.range_var.get() == 1:
            self.custom_start_var.set("1")
            self.custom_end_var.set("100000")
        elif self.range_var.get() == 2:
            self.custom_start_var.set("1")
            self.custom_end_var.set("500000")
        elif self.range_var.get() == 3:
            self.custom_start_var.set("1")
            self.custom_end_var.set("1000000")
        self._update_widgets_state()

    def _on_worker_changed(self):
        self._update_widgets_state()

    def _update_widgets_state(self):
        mode = self.mode_var.get()
        is_parallel = mode == "parallel"
        is_benchmark = mode == "benchmark"

        state = "normal" if is_parallel else "disabled"
        for rb in self.worker_buttons:
            rb.configure(state=state)
        self.worker_entry.configure(state="normal" if self.worker_var.get() == "custom" and is_parallel else "disabled")

        self.start_entry.configure(state="normal" if self.range_var.get() == 4 else "disabled")
        self.end_entry.configure(state="normal" if self.range_var.get() == 4 else "disabled")

        self.run_button.configure(text="Jalankan Benchmark" if is_benchmark else "Jalankan")

    def _clear_output(self):
        self.output_area.configure(state="normal")
        self.output_area.delete("1.0", tk.END)
        self.output_area.configure(state="disabled")

    def _log(self, message: str):
        self.root.after(0, self._append_text, message)

    def _append_text(self, text: str):
        self.output_area.configure(state="normal")
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state="disabled")

    def _set_active(self, active: bool):
        state = "normal" if active else "disabled"
        self.run_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.exit_button.configure(state=state)

    def _on_run(self):
        if self.running:
            return
        self.running = True
        self._set_active(False)
        self._log("Memulai proses...")
        thread = threading.Thread(target=self._execute_task, daemon=True)
        thread.start()

    def _execute_task(self):
        try:
            mode = self.mode_var.get()
            if mode == "serial":
                self._run_serial()
            elif mode == "parallel":
                self._run_parallel()
            else:
                self._run_benchmark()
        except Exception as exc:
            self._log(f"Terjadi kesalahan: {exc}")
        finally:
            self.running = False
            self.root.after(0, self._set_active, True)

    def _get_range(self):
        if self.range_var.get() == 1:
            return 1, 100000
        if self.range_var.get() == 2:
            return 1, 500000
        if self.range_var.get() == 3:
            return 1, 1000000

        try:
            start = int(self.custom_start_var.get())
            end = int(self.custom_end_var.get())
        except ValueError:
            raise ValueError("Rentang custom harus berupa angka bulat.")

        if start < 1:
            raise ValueError("Batas bawah harus >= 1.")
        if end <= start:
            raise ValueError("Batas atas harus lebih besar dari batas bawah.")
        return start, end

    def _get_workers(self):
        selection = self.worker_var.get()
        if selection == "all":
            return self.cpu_count
        if selection == "custom":
            try:
                workers = int(self.custom_worker_var.get())
            except ValueError:
                raise ValueError("Jumlah worker custom harus berupa angka.")
            if workers < 1:
                raise ValueError("Jumlah worker harus minimal 1.")
            return workers
        return int(selection)

    def _run_serial(self):
        start, end = self._get_range()
        self._log(f"Mode: Serial | Rentang: {start} - {end}")
        serial = SerialPrimeFinder(start, end)
        primes = serial.find_primes_optimized(show_progress=False)
        self._display_search_result(serial, primes)

    def _run_parallel(self):
        start, end = self._get_range()
        workers = self._get_workers()
        self._log(f"Mode: Paralel | Rentang: {start} - {end} | Worker: {workers}")
        parallel = ParallelPrimeFinder(start, end, workers)
        primes = parallel.find_primes_optimized(show_progress=False)
        self._display_search_result(parallel, primes)

    def _run_benchmark(self):
        self._log("Mode: Benchmark Lengkap")
        runner = BenchmarkRunner()

        buffer = io.StringIO()
        saved_stdout = sys.stdout
        sys.stdout = buffer
        try:
            runner.run_preset_tests(show_progress=False)
            csv_path = runner.save_to_csv("hasil_pengujian.csv")
            chart_path = runner.create_comparison_chart(
                "grafik_perbandingan.png",
                show_chart=False
            )
        finally:
            sys.stdout = saved_stdout

        self._log("Benchmark selesai.")
        self._log(f"Hasil benchmark disimpan ke: {csv_path}")
        self._log(f"Grafik perbandingan disimpan ke: {chart_path}")
        self._log("Ringkasan hasil benchmark:")
        self._display_benchmark_summary(runner)

    def _display_search_result(self, finder, primes):
        duration = finder.get_execution_time()
        self._log(f"Jumlah prima ditemukan: {len(primes)}")
        self._log(f"Waktu eksekusi: {duration:.6f} detik")

        if len(primes) == 0:
            self._log("Tidak ada bilangan prima dalam rentang ini.")
            return

        if len(primes) <= 100:
            self._log(f"Bilangan prima: {primes}")
        else:
            self._log(f"10 prima pertama: {primes[:10]}")
            self._log(f"10 prima terakhir: {primes[-10:]}")

    def _display_benchmark_summary(self, runner: BenchmarkRunner):
        if not runner.results:
            self._log("Tidak ada data benchmark untuk ditampilkan.")
            return

        avg_speedup = sum(r.speedup for r in runner.results) / len(runner.results)
        avg_efficiency = sum(r.efficiency for r in runner.results) / len(runner.results)
        self._log(f"Total pengujian: {len(runner.results)}")
        self._log(f"Rata-rata speedup: {avg_speedup:.2f}x")
        self._log(f"Rata-rata efficiency: {avg_efficiency:.2f}%")

        self._log("Hasil per pengujian:")
        for result in runner.results:
            self._log(
                f"Range {result.start}-{result.end} | "
                f"Workers: {result.num_workers} | "
                f"Serial: {result.serial_time:.6f}s | "
                f"Paralel: {result.parallel_time:.6f}s | "
                f"Speedup: {result.speedup:.2f}x | "
                f"Efficiency: {result.efficiency:.2f}%"
            )


def run_gui():
    root = tk.Tk()
    PrimeFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
