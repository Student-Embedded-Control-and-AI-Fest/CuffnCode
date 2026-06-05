#!/usr/bin/env python3
"""
main.py
=======
Program utama Parallel Prime Finder dengan antarmuka CLI.

Program ini menyediakan menu interaktif untuk:
- Menjalankan pencarian bilangan prima secara serial
- Menjalankan pencarian bilangan prima secara paralel
- Menjalankan benchmark lengkap dengan visualisasi
"""

import sys
import os
import multiprocessing

# Tambahkan parent directory ke path untuk import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.serial import SerialPrimeFinder, run_serial
from src.parallel import ParallelPrimeFinder, run_parallel
from src.benchmark import BenchmarkRunner, run_full_benchmark


def print_header():
    """Menampilkan header program."""
    print("\n" + "=" * 55)
    print("       PARALLEL PRIME NUMBER FINDER")
    print("  Implementasi Komputasi Paralel dengan Multiprocessing")
    print("=" * 55)
    print(f"  CPU Cores tersedia : {ParallelPrimeFinder.get_cpu_count()}")
    print(f"  Python version     : {sys.version.split()[0]}")
    print("=" * 55)


def print_menu():
    """Menampilkan menu utama."""
    print("\nMENU UTAMA")
    print("-" * 30)
    print("1. Jalankan Mode Serial")
    print("2. Jalankan Mode Paralel")
    print("3. Benchmark Lengkap")
    print("4. Keluar")
    print("-" * 30)


def get_valid_input(prompt: str, min_val: int, max_val: int) -> int:
    """
    Mendapatkan input integer yang valid dari pengguna.
    
    Args:
        prompt (str): Pesan prompt
        min_val (int): Nilai minimum yang diperbolehkan
        max_val (int): Nilai maximum yang diperbolehkan
        
    Returns:
        int: Input integer yang valid
    """
    while True:
        try:
            value = int(input(prompt))
            if value < min_val or value > max_val:
                print(f"Error: Input harus antara {min_val} dan {max_val}")
                continue
            return value
        except ValueError:
            print("Error: Masukkan angka yang valid!")


def run_serial_mode():
    """Menjalankan pencarian bilangan prima mode serial."""
    print("\n" + "=" * 50)
    print(" MODE SERIAL")
    print("=" * 50)
    
    # Pilih preset atau custom
    print("\nPilih rentang:")
    print("1. 1 - 100.000")
    print("2. 1 - 500.000")
    print("3. 1 - 1.000.000")
    print("4. Custom Range")
    
    choice = get_valid_input("Pilihan (1-4): ", 1, 4)
    
    ranges = {
        1: (1, 100000),
        2: (1, 500000),
        3: (1, 1000000)
    }
    
    if choice in ranges:
        start, end = ranges[choice]
    else:
        print("\nMasukkan rentang custom:")
        start = get_valid_input("  Batas bawah (min 1): ", 1, 1000000000)
        end = get_valid_input("  Batas atas (max 1000000000): ", start, 1000000000)
    
    # Tanyakan apakah ingin menampilkan progress
    show_progress = input("\nTampilkan progress bar? (y/n): ").lower().strip() == 'y'
    
    # Jalankan pencarian serial
    print(f"\nMencari bilangan prima dari {start} sampai {end}...")
    finder = SerialPrimeFinder(start, end)
    finder.find_primes_optimized(show_progress)
    finder.print_results(show_primes=True)
    
    return finder


def run_parallel_mode():
    """Menjalankan pencarian bilangan prima mode paralel."""
    print("\n" + "=" * 50)
    print(" MODE PARALEL")
    print("=" * 50)
    
    # Pilih rentang
    print("\nPilih rentang:")
    print("1. 1 - 100.000")
    print("2. 1 - 500.000")
    print("3. 1 - 1.000.000")
    print("4. Custom Range")
    
    range_choice = get_valid_input("Pilihan (1-4): ", 1, 4)
    
    ranges = {
        1: (1, 100000),
        2: (1, 500000),
        3: (1, 1000000)
    }
    
    if range_choice in ranges:
        start, end = ranges[range_choice]
    else:
        print("\nMasukkan rentang custom:")
        start = get_valid_input("  Batas bawah (min 1): ", 1, 1000000000)
        end = get_valid_input("  Batas atas (max 1000000000): ", start, 1000000000)
    
    # Pilih jumlah worker
    cpu_count = ParallelPrimeFinder.get_cpu_count()
    print(f"\nJumlah CPU cores tersedia: {cpu_count}")
    print("\nPilih jumlah worker:")
    print("1. 2 Worker")
    print("2. 4 Worker")
    print("3. 8 Worker")
    print(f"4. Semua cores ({cpu_count} worker)")
    print("5. Custom")
    
    worker_choice = get_valid_input("Pilihan (1-5): ", 1, 5)
    
    worker_options = {
        1: 2,
        2: 4,
        3: 8,
        4: cpu_count
    }
    
    if worker_choice in worker_options:
        num_workers = worker_options[worker_choice]
    else:
        num_workers = get_valid_input(f"Masukkan jumlah worker (1-{cpu_count * 2}): ", 1, cpu_count * 2)
    
    # Tanyakan apakah ingin menampilkan progress
    show_progress = input("\nTampilkan progress bar? (y/n): ").lower().strip() == 'y'
    
    # Jalankan pencarian paralel
    print(f"\nMencari bilangan prima dari {start} sampai {end} dengan {num_workers} worker...")
    finder = ParallelPrimeFinder(start, end, num_workers)
    finder.find_primes_optimized(show_progress)
    finder.print_results(show_primes=True)
    
    return finder


def run_benchmark_mode():
    """Menjalankan benchmark lengkap."""
    print("\n" + "=" * 50)
    print(" BENCHMARK LENGKAP")
    print("=" * 50)
    
    print("\nBenchmark akan menjalankan:")
    print("  - Range 1-100.000 dengan 2, 4, 8 workers")
    print("  - Range 1-500.000 dengan 2, 4, 8 workers")
    print("  - Range 1-1.000.000 with 2, 4, 8 workers")
    print("\nTotal: 9 pengujian")
    
    confirm = input("\nLanjutkan? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Benchmark dibatalkan.")
        return None
    
    show_progress = input("\nTampilkan progress bar? (y/n): ").lower().strip() == 'y'
    
    # Jalankan full benchmark
    runner = run_full_benchmark(
        show_progress=show_progress,
        save_results=True,
        show_chart=True
    )
    
    return runner


def run_quick_comparison():
    """Menjalankan perbandingan cepat serial vs paralel."""
    print("\n" + "=" * 50)
    print(" PERBANDINGAN CEPAT")
    print("=" * 50)
    
    # Pilih rentang
    print("\nPilih rentang:")
    print("1. 1 - 100.000")
    print("2. 1 - 500.000")
    print("3. 1 - 1.000.000")
    print("4. Custom Range")
    
    range_choice = get_valid_input("Pilihan (1-4): ", 1, 4)
    
    ranges = {
        1: (1, 100000),
        2: (1, 500000),
        3: (1, 1000000)
    }
    
    if range_choice in ranges:
        start, end = ranges[range_choice]
    else:
        print("\nMasukkan rentang custom:")
        start = get_valid_input("  Batas bawah (min 1): ", 1, 1000000000)
        end = get_valid_input("  Batas atas (max 1000000000): ", start, 1000000000)
    
    # Pilih jumlah worker
    cpu_count = ParallelPrimeFinder.get_cpu_count()
    print(f"\nJumlah CPU cores: {cpu_count}")
    num_workers = get_valid_input(f"Jumlah worker (1-{cpu_count}): ", 1, cpu_count)
    
    print(f"\n{'='*60}")
    print(f" Running Serial...")
    print(f"{'='*60}")
    serial_primes, serial_time = run_serial(start, end)
    print(f"Waktu Serial: {serial_time:.6f} detik")
    
    print(f"\n{'='*60}")
    print(f" Running Paralel ({num_workers} workers)...")
    print(f"{'='*60}")
    parallel_primes, parallel_time = run_parallel(start, end, num_workers)
    print(f"Waktu Paralel: {parallel_time:.6f} detik")
    
    # Hitung speedup dan efficiency
    speedup = serial_time / parallel_time if parallel_time > 0 else 0
    efficiency = (speedup / num_workers) * 100
    
    print(f"\n{'='*60}")
    print(" HASIL PERBANDINGAN")
    print(f"{'='*60}")
    print(f"Rentang          : {start} - {end}")
    print(f"Jumlah Prima     : {len(serial_primes)}")
    print(f"Waktu Serial     : {serial_time:.6f} detik")
    print(f"Waktu Paralel    : {parallel_time:.6f} detik")
    print(f"Speedup          : {speedup:.2f}x")
    print(f"Efficiency       : {efficiency:.2f}%")
    print(f"{'='*60}")
    
    # Verifikasi hasil sama
    if serial_primes == parallel_primes:
        print("âœ“ Hasil serial dan paralel SAMA (terverifikasi)")
    else:
        print("âœ— PERINGATAN: Hasil serial dan paralel BERBEDA!")


def main():
    """Fungsi utama program."""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = get_valid_input("Pilihan Anda: ", 1, 4)
        except (EOFError, KeyboardInterrupt):
            print("\n\nProgram dihentikan.")
            break
        
        if choice == 1:
            run_serial_mode()
        elif choice == 2:
            run_parallel_mode()
        elif choice == 3:
            run_benchmark_mode()
        elif choice == 4:
            print("\nTerima kasih telah menggunakan Parallel Prime Finder!")
            print("Program selesai.")
            break
        
        # Tanyakan apakah ingin melanjutkan
        if choice != 4:
            cont = input("\nKembali ke menu utama? (y/n): ").lower().strip()
            if cont != 'y':
                print("\nTerima kasih telah menggunakan Parallel Prime Finder!")
                print("Program selesai.")
                break
    
    sys.exit(0)


if __name__ == "__main__":
    if "--cli" in sys.argv or "-c" in sys.argv:
        main()
    else:
        from gui import run_gui
        run_gui()
