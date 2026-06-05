"""
parallel.py
===========
Modul untuk pencarian bilangan prima secara paralel menggunakan multiprocessing.

Modul ini mengimplementasikan pencarian bilangan prima menggunakan
multiprocessing.Pool untuk memanfaatkan beberapa core CPU secara paralel.
"""

import time
import multiprocessing
from typing import List, Tuple, Optional
from tqdm import tqdm

from .prime_utils import (
    is_prime,
    find_primes_in_range,
    find_primes_in_range_optimized,
    count_primes_in_range,
    count_primes_in_range_optimized,
    split_range
)


class ParallelPrimeFinder:
    """
    Kelas untuk pencarian bilangan prima secara paralel.
    
    Attributes:
        start (int): Batas bawah rentang pencarian
        end (int): Batas atas rentang pencarian
        num_workers (int): Jumlah worker processes
        primes (List[int]): List bilangan prima yang ditemukan
        execution_time (float): Waktu eksekusi dalam detik
        speedup (float): Perbandingan kecepatan vs serial
        efficiency (float): Efisiensi penggunaan core (%)
    """
    
    def __init__(self, start: int, end: int, num_workers: Optional[int] = None):
        """
        Inisialisasi ParallelPrimeFinder.
        
        Args:
            start (int): Batas bawah rentang pencarian
            end (int): Batas atas rentang pencarian
            num_workers (Optional[int]): Jumlah worker. Jika None, gunakan semua core
        """
        self.start = start
        self.end = end
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.primes: List[int] = []
        self.execution_time: float = 0.0
        self.speedup: float = 0.0
        self.efficiency: float = 0.0
    
    @staticmethod
    def get_cpu_count() -> int:
        """
        Mendapatkan jumlah core CPU yang tersedia.
        
        Returns:
            int: Jumlah core CPU
        """
        return multiprocessing.cpu_count()
    
    def find_primes(self, show_progress: bool = False) -> List[int]:
        """
        Mencari semua bilangan prima dalam rentang secara paralel.
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            List[int]: List bilangan prima yang ditemukan
        """
        self.primes = []
        start_time = time.time()
        
        # Bagi rentang untuk setiap worker
        ranges = split_range(self.start, self.end, self.num_workers)
        
        # Gunakan multiprocessing.Pool
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            if show_progress:
                # Dengan progress bar
                results = list(tqdm(
                    pool.imap(find_primes_in_range, ranges),
                    total=len(ranges),
                    desc=f"Parallel Search ({self.num_workers} workers)",
                    unit="chunk",
                    colour="blue"
                ))
            else:
                # Tanpa progress bar
                results = pool.map(find_primes_in_range, ranges)
        
        # Gabungkan hasil dari semua worker
        for worker_primes in results:
            self.primes.extend(worker_primes)
        
        # Urutkan hasil
        self.primes.sort()
        
        self.execution_time = time.time() - start_time
        return self.primes
    
    def find_primes_optimized(self, show_progress: bool = False) -> List[int]:
        """
        Versi optimasi pencarian bilangan prima secara paralel.
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            List[int]: List bilangan prima yang ditemukan
        """
        self.primes = []
        start_time = time.time()
        
        # Bagi rentang untuk setiap worker
        ranges = split_range(self.start, self.end, self.num_workers)
        
        # Gunakan multiprocessing.Pool dengan fungsi optimasi
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            if show_progress:
                results = list(tqdm(
                    pool.imap(find_primes_in_range_optimized, ranges),
                    total=len(ranges),
                    desc=f"Parallel Search ({self.num_workers} workers)",
                    unit="chunk",
                    colour="blue"
                ))
            else:
                results = pool.map(find_primes_in_range_optimized, ranges)
        
        # Gabungkan hasil dari semua worker
        for worker_primes in results:
            self.primes.extend(worker_primes)
        
        # Urutkan hasil
        self.primes.sort()
        
        self.execution_time = time.time() - start_time
        return self.primes
    
    def count_primes(self, show_progress: bool = False) -> int:
        """
        Menghitung jumlah bilangan prima secara paralel.
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            int: Jumlah bilangan prima yang ditemukan
        """
        start_time = time.time()
        
        # Bagi rentang untuk setiap worker
        ranges = split_range(self.start, self.end, self.num_workers)
        
        # Gunakan multiprocessing.Pool
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            if show_progress:
                counts = list(tqdm(
                    pool.imap(count_primes_in_range, ranges),
                    total=len(ranges),
                    desc=f"Parallel Count ({self.num_workers} workers)",
                    unit="chunk",
                    colour="blue"
                ))
            else:
                counts = pool.map(count_primes_in_range, ranges)
        
        self.execution_time = time.time() - start_time
        return sum(counts)
    
    def calculate_metrics(self, serial_time: float):
        """
        Menghitung speedup dan efficiency berdasarkan waktu serial.
        
        Args:
            serial_time (float): Waktu eksekusi serial dalam detik
        """
        if serial_time > 0 and self.execution_time > 0:
            self.speedup = serial_time / self.execution_time
            self.efficiency = (self.speedup / self.num_workers) * 100
    
    def set_execution_time(self, time_val: float):
        """
        Mengatur waktu eksekusi (untuk keperluan benchmark).
        
        Args:
            time_val (float): Waktu eksekusi dalam detik
        """
        self.execution_time = time_val
    
    def get_execution_time(self) -> float:
        """
        Mendapatkan waktu eksekusi dari pencarian terakhir.
        
        Returns:
            float: Waktu eksekusi dalam detik
        """
        return self.execution_time
    
    def get_results(self) -> Tuple[List[int], float]:
        """
        Mendapatkan hasil pencarian lengkap.
        
        Returns:
            Tuple[List[int], float]: Tuple berisi (list prima, waktu eksekusi)
        """
        return self.primes, self.execution_time
    
    def print_results(self, serial_time: Optional[float] = None, show_primes: bool = False):
        """
        Menampilkan hasil pencarian ke console.
        
        Args:
            serial_time (Optional[float]): Waktu serial untuk perbandingan
            show_primes (bool): Menampilkan semua bilangan prima jika True
        """
        if serial_time is not None:
            self.calculate_metrics(serial_time)
        
        print("\n" + "=" * 50)
        print(" HASIL PENCARIAN PARALEL")
        print("=" * 50)
        print(f"Rentang          : {self.start} - {self.end}")
        print(f"Jumlah Worker    : {self.num_workers}")
        print(f"Jumlah Prima     : {len(self.primes)}")
        print(f"Waktu Eksekusi   : {self.execution_time:.6f} detik")
        
        if serial_time is not None:
            print(f"Speedup          : {self.speedup:.2f}x")
            print(f"Efficiency       : {self.efficiency:.2f}%")
        
        if show_primes and len(self.primes) <= 100:
            print(f"\nBilangan Prima   : {self.primes}")
        elif show_primes:
            print(f"\n10 Prima Pertama : {self.primes[:10]}")
            print(f"10 Prima Terakhir: {self.primes[-10:]}")
        
        print("=" * 50)


def run_parallel(
    start: int, 
    end: int, 
    num_workers: Optional[int] = None,
    show_progress: bool = False
) -> Tuple[List[int], float]:
    """
    Fungsi helper untuk menjalankan pencarian paralel.
    
    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        num_workers (Optional[int]): Jumlah worker. Jika None, gunakan semua core
        show_progress (bool): Menampilkan progress bar jika True
        
    Returns:
        Tuple[List[int], float]: Tuple berisi (list prima, waktu eksekusi)
    """
    finder = ParallelPrimeFinder(start, end, num_workers)
    finder.find_primes_optimized(show_progress)
    return finder.get_results()


def run_parallel_count(
    start: int, 
    end: int, 
    num_workers: Optional[int] = None,
    show_progress: bool = False
) -> Tuple[int, float]:
    """
    Fungsi helper untuk menghitung bilangan prima secara paralel.
    
    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        num_workers (Optional[int]): Jumlah worker. Jika None, gunakan semua core
        show_progress (bool): Menampilkan progress bar jika True
        
    Returns:
        Tuple[int, float]: Tuple berisi (jumlah prima, waktu eksekusi)
    """
    finder = ParallelPrimeFinder(start, end, num_workers)
    count = finder.count_primes(show_progress)
    return count, finder.get_execution_time()


def run_parallel_benchmark(
    start: int,
    end: int,
    num_workers: int,
    serial_time: float
) -> Tuple[int, float, float, float]:
    """
    Fungsi khusus untuk benchmark paralel.
    
    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        num_workers (int): Jumlah worker
        serial_time (float): Waktu serial untuk perhitungan speedup
        
    Returns:
        Tuple[int, float, float, float]: (count, time, speedup, efficiency)
    """
    finder = ParallelPrimeFinder(start, end, num_workers)
    count = finder.count_primes()
    finder.calculate_metrics(serial_time)
    
    return count, finder.execution_time, finder.speedup, finder.efficiency