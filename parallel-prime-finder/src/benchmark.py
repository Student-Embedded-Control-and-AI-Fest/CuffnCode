"""
benchmark.py
============
Modul untuk melakukan benchmark dan analisis performa.

Modul ini menyediakan fungsi-fungsi untuk:
- Menjalankan benchmark serial vs paralel
- Menghitung speedup dan efficiency
- Menyimpan hasil ke CSV
- Membuat visualisasi grafik
"""

import os
import csv
import time
import multiprocessing
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend untuk menyimpan file

from .serial import SerialPrimeFinder
from .parallel import ParallelPrimeFinder


class BenchmarkResult:
    """
    Kelas untuk menyimpan hasil satu kali benchmark.
    
    Attributes:
        date (str): Tanggal dan waktu benchmark
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        prime_count (int): Jumlah bilangan prima ditemukan
        serial_time (float): Waktu eksekusi serial
        parallel_time (float): Waktu eksekusi paralel
        num_workers (int): Jumlah worker paralel
        speedup (float): Nilai speedup
        efficiency (float): Nilai efficiency (%)
    """
    
    def __init__(
        self,
        start: int,
        end: int,
        prime_count: int,
        serial_time: float,
        parallel_time: float,
        num_workers: int,
        speedup: float,
        efficiency: float
    ):
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.start = start
        self.end = end
        self.prime_count = prime_count
        self.serial_time = serial_time
        self.parallel_time = parallel_time
        self.num_workers = num_workers
        self.speedup = speedup
        self.efficiency = efficiency
    
    def to_dict(self) -> Dict[str, any]:
        """Mengembalikan hasil sebagai dictionary."""
        return {
            'Tanggal': self.date,
            'Range_Start': self.start,
            'Range_End': self.end,
            'Jumlah_Prima': self.prime_count,
            'Waktu_Serial': f"{self.serial_time:.6f}",
            'Waktu_Paralel': f"{self.parallel_time:.6f}",
            'Jumlah_Worker': self.num_workers,
            'Speedup': f"{self.speedup:.2f}",
            'Efficiency': f"{self.efficiency:.2f}"
        }
    
    def __str__(self) -> str:
        return (
            f"Range: {self.start}-{self.end} | "
            f"Workers: {self.num_workers} | "
            f"Serial: {self.serial_time:.6f}s | "
            f"Parallel: {self.parallel_time:.6f}s | "
            f"Speedup: {self.speedup:.2f}x | "
            f"Efficiency: {self.efficiency:.2f}%"
        )


class BenchmarkRunner:
    """
    Kelas untuk menjalankan serangkaian benchmark.
    
    Attributes:
        results (List[BenchmarkResult]): List hasil benchmark
        results_dir (str): Direktori untuk menyimpan hasil
    """
    
    def __init__(self, results_dir: str = "results"):
        """
        Inisialisasi BenchmarkRunner.
        
        Args:
            results_dir (str): Direktori untuk menyimpan hasil
        """
        self.results: List[BenchmarkResult] = []
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def run_single_benchmark(
        self,
        start: int,
        end: int,
        num_workers: int,
        show_progress: bool = False
    ) -> BenchmarkResult:
        """
        Menjalankan satu kali benchmark (serial vs paralel).
        
        Args:
            start (int): Batas bawah rentang
            end (int): Batas atas rentang
            num_workers (int): Jumlah worker paralel
            show_progress (bool): Menampilkan progress bar
            
        Returns:
            BenchmarkResult: Hasil benchmark
        """
        # Jalankan serial
        serial_finder = SerialPrimeFinder(start, end)
        serial_finder.count_primes(show_progress)
        serial_time = serial_finder.get_execution_time()
        prime_count = len(serial_finder.primes) if serial_finder.primes else 0
        
        # Jika prime_count = 0, hitung ulang untuk mendapatkan count
        if prime_count == 0:
            serial_finder.find_primes_optimized()
            prime_count = len(serial_finder.primes)
        
        # Jalankan paralel
        parallel_finder = ParallelPrimeFinder(start, end, num_workers)
        parallel_finder.count_primes(show_progress)
        parallel_time = parallel_finder.get_execution_time()
        
        # Hitung speedup dan efficiency
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        efficiency = (speedup / num_workers) * 100
        
        result = BenchmarkResult(
            start=start,
            end=end,
            prime_count=prime_count,
            serial_time=serial_time,
            parallel_time=parallel_time,
            num_workers=num_workers,
            speedup=speedup,
            efficiency=efficiency
        )
        
        self.results.append(result)
        return result
    
    def run_multiple_workers(
        self,
        start: int,
        end: int,
        worker_list: List[int],
        show_progress: bool = False
    ) -> List[BenchmarkResult]:
        """
        Menjalankan benchmark dengan berbagai jumlah worker.
        
        Args:
            start (int): Batas bawah rentang
            end (int): Batas atas rentang
            worker_list (List[int]): List jumlah worker yang akan diuji
            show_progress (bool): Menampilkan progress bar
            
        Returns:
            List[BenchmarkResult]: List hasil benchmark
        """
        results = []
        for num_workers in worker_list:
            print(f"\n{'='*60}")
            print(f" Menguji dengan {num_workers} Worker(s)")
            print(f"{'='*60}")
            result = self.run_single_benchmark(start, end, num_workers, show_progress)
            results.append(result)
            print(f"\n{result}")
        
        return results
    
    def run_preset_tests(
        self,
        show_progress: bool = False
    ) -> List[BenchmarkResult]:
        """
        Menjalankan semua preset tests sesuai spesifikasi.
        
        Preset:
        - Range 1-100000 dengan 2, 4, 8 workers
        - Range 1-500000 dengan 2, 4, 8 workers
        - Range 1-1000000 dengan 2, 4, 8 workers
        
        Args:
            show_progress (bool): Menampilkan progress bar
            
        Returns:
            List[BenchmarkResult]: List hasil benchmark
        """
        presets = [
            (1, 100000, [2, 4, 8]),
            (1, 500000, [2, 4, 8]),
            (1, 1000000, [2, 4, 8])
        ]
        
        all_results = []
        
        for start, end, workers in presets:
            print(f"\n{'#'*60}")
            print(f"# Pengujiian Range: {start} - {end}")
            print(f"{'#'*60}")
            
            results = self.run_multiple_workers(start, end, workers, show_progress)
            all_results.extend(results)
        
        return all_results
    
    def save_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Menyimpan hasil benchmark ke file CSV.
        
        Args:
            filename (Optional[str]): Nama file. Jika None, gunakan timestamp
            
        Returns:
            str: Path file yang disimpan
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hasil_pengujian_{timestamp}.csv"
        
        filepath = os.path.join(self.results_dir, filename)
        
        if not self.results:
            print("Tidak ada hasil benchmark untuk disimpan!")
            return filepath
        
        fieldnames = [
            'Tanggal', 'Range_Start', 'Range_End', 'Jumlah_Prima',
            'Waktu_Serial', 'Waktu_Paralel', 'Jumlah_Worker',
            'Speedup', 'Efficiency'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())
        
        print(f"\nHasil benchmark disimpan ke: {filepath}")
        return filepath
    
    def create_comparison_chart(
        self,
        filename: Optional[str] = None,
        show_chart: bool = True
    ) -> str:
        """
        Membuat grafik perbandingan waktu serial vs paralel.
        
        Args:
            filename (Optional[str]): Nama file. Jika None, gunakan default
            show_chart (bool): Menampilkan grafik setelah dibuat
            
        Returns:
            str: Path file grafik
        """
        if not filename:
            filename = "grafik_perbandingan.png"
        
        filepath = os.path.join(self.results_dir, filename)
        
        if not self.results:
            print("Tidak ada hasil benchmark untuk divisualisasikan!")
            return filepath
        
        # Kelompokkan hasil berdasarkan range
        range_groups: Dict[str, List[BenchmarkResult]] = {}
        for result in self.results:
            range_key = f"{result.start}-{result.end}"
            if range_key not in range_groups:
                range_groups[range_key] = []
            range_groups[range_key].append(result)
        
        # Buat figure dengan subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Analisis Performa Parallel Prime Finder', fontsize=16, fontweight='bold')
        
        # 1. Grafik Waktu Eksekusi
        ax1 = axes[0, 0]
        for range_key, results in range_groups.items():
            workers = [r.num_workers for r in results]
            serial_times = [r.serial_time for r in results]
            parallel_times = [r.parallel_time for r in results]
            
            ax1.plot(workers, serial_times, 'r--', marker='o', label=f'Serial ({range_key})', linewidth=2)
            ax1.plot(workers, parallel_times, 'b-', marker='s', label=f'Paralel ({range_key})', linewidth=2)
        
        ax1.set_xlabel('Jumlah Worker')
        ax1.set_ylabel('Waktu Eksekusi (detik)')
        ax1.set_title('Waktu Eksekusi: Serial vs Paralel')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Grafik Speedup
        ax2 = axes[0, 1]
        for range_key, results in range_groups.items():
            workers = [r.num_workers for r in results]
            speedups = [r.speedup for r in results]
            
            # Garis ideal speedup
            ax2.plot(workers, workers, 'k--', alpha=0.3, label='Ideal (hanya untuk range terkecil)')
            ax2.plot(workers, speedups, 'g-', marker='^', label=f'Actual ({range_key})', linewidth=2)
        
        ax2.set_xlabel('Jumlah Worker')
        ax2.set_ylabel('Speedup (x)')
        ax2.set_title('Speedup')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Grafik Efficiency
        ax3 = axes[1, 0]
        for range_key, results in range_groups.items():
            workers = [r.num_workers for r in results]
            efficiencies = [r.efficiency for r in results]
            
            ax3.plot(workers, efficiencies, 'm-', marker='d', label=f'{range_key}', linewidth=2)
        
        ax3.axhline(y=100, color='r', linestyle='--', alpha=0.3, label='Efisiensi Ideal (100%)')
        ax3.set_xlabel('Jumlah Worker')
        ax3.set_ylabel('Efficiency (%)')
        ax3.set_title('Efficiency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Grafik Prime Count vs Time
        ax4 = axes[1, 1]
        for range_key, results in range_groups.items():
            prime_counts = [r.prime_count for r in results]
            serial_times = [r.serial_time for r in results]
            parallel_times = [r.parallel_time for r in results]
            
            ax4.scatter(prime_counts, serial_times, marker='o', s=100, label=f'Serial ({range_key})', alpha=0.7)
            ax4.scatter(prime_counts, parallel_times, marker='s', s=100, label=f'Paralel ({range_key})', alpha=0.7)
        
        ax4.set_xlabel('Jumlah Bilangan Prima')
        ax4.set_ylabel('Waktu Eksekusi (detik)')
        ax4.set_title('Jumlah Prima vs Waktu Eksekusi')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        
        if show_chart:
            plt.show()
        else:
            plt.close()
        
        print(f"Grafik disimpan ke: {filepath}")
        return filepath
    
    def print_summary(self):
        """Menampilkan ringkasan semua hasil benchmark dalam bentuk tabel."""
        if not self.results:
            print("Tidak ada hasil benchmark untuk ditampilkan!")
            return
        
        print("\n" + "=" * 100)
        print(" RINGKASAN HASIL BENCHMARK")
        print("=" * 100)
        print(f"{'Range':<20} {'Workers':<10} {'Prima':<10} {'Serial (s)':<15} {'Paralel (s)':<15} {'Speedup':<10} {'Efficiency':<12}")
        print("-" * 100)
        
        for result in self.results:
            print(
                f"{result.start:>6} - {result.end:<10} "
                f"{result.num_workers:<10} "
                f"{result.prime_count:<10} "
                f"{result.serial_time:<15.6f} "
                f"{result.parallel_time:<15.6f} "
                f"{result.speedup:<10.2f} "
                f"{result.efficiency:<12.2f}%"
            )
        
        print("=" * 100)
        
        # Statistik tambahan
        cpu_count = multiprocessing.cpu_count()
        print(f"\nJumlah Core CPU: {cpu_count}")
        print(f"Total Pengujian: {len(self.results)}")
        
        # Rata-rata speedup dan efficiency
        avg_speedup = sum(r.speedup for r in self.results) / len(self.results)
        avg_efficiency = sum(r.efficiency for r in self.results) / len(self.results)
        print(f"Rata-rata Speedup: {avg_speedup:.2f}x")
        print(f"Rata-rata Efficiency: {avg_efficiency:.2f}%")


def run_full_benchmark(
    show_progress: bool = False,
    save_results: bool = True,
    show_chart: bool = True
) -> BenchmarkRunner:
    """
    Fungsi helper untuk menjalankan full benchmark sesuai spesifikasi.
    
    Args:
        show_progress (bool): Menampilkan progress bar
        save_results (bool): Menyimpan hasil ke CSV
        show_chart (bool): Menampilkan grafik
        
    Returns:
        BenchmarkRunner: Instance BenchmarkRunner dengan hasil
    """
    runner = BenchmarkRunner()
    
    print("=" * 60)
    print(" PARALLEL PRIME FINDER - FULL BENCHMARK")
    print("=" * 60)
    print(f"CPU Cores: {multiprocessing.cpu_count()}")
    print(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Jalankan preset tests
    runner.run_preset_tests(show_progress)
    
    # Simpan hasil
    if save_results:
        runner.save_to_csv("hasil_pengujian.csv")
    
    # Buat grafik
    if show_chart:
        runner.create_comparison_chart("grafik_perbandingan.png", show_chart=True)
    
    # Tampilkan ringkasan
    runner.print_summary()
    
    return runner