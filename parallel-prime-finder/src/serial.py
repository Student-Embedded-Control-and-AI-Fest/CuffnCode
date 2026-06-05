"""
serial.py
=========
Modul untuk pencarian bilangan prima secara serial (sekuensial).

Modul ini mengimplementasikan pencarian bilangan prima menggunakan
pendekatan serial/single-threaded untuk tujuan perbandingan dengan
versi paralel.
"""

import time
from typing import List, Tuple
from tqdm import tqdm

from .prime_utils import is_prime, count_primes_in_range


class SerialPrimeFinder:
    """
    Kelas untuk pencarian bilangan prima secara serial.
    
    Attributes:
        start (int): Batas bawah rentang pencarian
        end (int): Batas atas rentang pencarian
        primes (List[int]): List bilangan prima yang ditemukan
        execution_time (float): Waktu eksekusi dalam detik
    """
    
    def __init__(self, start: int, end: int):
        """
        Inisialisasi SerialPrimeFinder.
        
        Args:
            start (int): Batas bawah rentang pencarian
            end (int): Batas atas rentang pencarian
        """
        self.start = start
        self.end = end
        self.primes: List[int] = []
        self.execution_time: float = 0.0
    
    def find_primes(self, show_progress: bool = False) -> List[int]:
        """
        Mencari semua bilangan prima dalam rentang secara serial.
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            List[int]: List bilangan prima yang ditemukan
        """
        self.primes = []
        start_time = time.time()
        
        if show_progress:
            iterator = tqdm(
                range(self.start, self.end),
                desc="Serial Search",
                unit="num",
                colour="green"
            )
        else:
            iterator = range(self.start, self.end)
        
        for num in iterator:
            if is_prime(num):
                self.primes.append(num)
        
        self.execution_time = time.time() - start_time
        return self.primes
    
    def find_primes_optimized(self, show_progress: bool = False) -> List[int]:
        """
        Versi optimasi pencarian bilangan prima.
        
        Optimasi:
        - Lewati bilangan genap (kecuali 2)
        - Iterasi lebih efisien
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            List[int]: List bilangan prima yang ditemukan
        """
        self.primes = []
        start_time = time.time()
        
        # Handle kasus khusus untuk angka 2
        if self.start <= 2 < self.end:
            self.primes.append(2)
        
        # Tentukan mulai dari angka ganjil pertama
        if self.start < 3:
            start = 3
        elif self.start % 2 == 0:
            start = self.start + 1
        else:
            start = self.start
        
        # Hitung jumlah iterasi untuk progress bar
        num_iterations = (self.end - start) // 2 + 1
        
        if show_progress:
            iterator = tqdm(
                range(start, self.end, 2),
                desc="Serial Search (Optimized)",
                unit="num",
                colour="green",
                total=num_iterations
            )
        else:
            iterator = range(start, self.end, 2)
        
        for num in iterator:
            if is_prime(num):
                self.primes.append(num)
        
        self.execution_time = time.time() - start_time
        return self.primes
    
    def count_primes(self, show_progress: bool = False) -> int:
        """
        Menghitung jumlah bilangan prima tanpa menyimpan hasilnya.
        
        Lebih efisien untuk benchmark karena tidak memerlukan memori
        untuk menyimpan list bilangan prima.
        
        Args:
            show_progress (bool): Menampilkan progress bar jika True
            
        Returns:
            int: Jumlah bilangan prima yang ditemukan
        """
        count = 0
        start_time = time.time()
        
        if show_progress:
            iterator = tqdm(
                range(self.start, self.end),
                desc="Serial Count",
                unit="num",
                colour="green"
            )
        else:
            iterator = range(self.start, self.end)
        
        for num in iterator:
            if is_prime(num):
                count += 1
        
        self.execution_time = time.time() - start_time
        return count
    
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
    
    def print_results(self, show_primes: bool = False):
        """
        Menampilkan hasil pencarian ke console.
        
        Args:
            show_primes (bool): Menampilkan semua bilangan prima jika True
        """
        print("\n" + "=" * 50)
        print(" HASIL PENCARIAN SERIAL")
        print("=" * 50)
        print(f"Rentang          : {self.start} - {self.end}")
        print(f"Jumlah Prima     : {len(self.primes)}")
        print(f"Waktu Eksekusi   : {self.execution_time:.6f} detik")
        
        if show_primes and len(self.primes) <= 100:
            print(f"\nBilangan Prima   : {self.primes}")
        elif show_primes:
            print(f"\n10 Prima Pertama : {self.primes[:10]}")
            print(f"10 Prima Terakhir: {self.primes[-10:]}")
        
        print("=" * 50)


def run_serial(start: int, end: int, show_progress: bool = False) -> Tuple[List[int], float]:
    """
    Fungsi helper untuk menjalankan pencarian serial.
    
    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        show_progress (bool): Menampilkan progress bar jika True
        
    Returns:
        Tuple[List[int], float]: Tuple berisi (list prima, waktu eksekusi)
    """
    finder = SerialPrimeFinder(start, end)
    finder.find_primes_optimized(show_progress)
    return finder.get_results()


def run_serial_count(start: int, end: int, show_progress: bool = False) -> Tuple[int, float]:
    """
    Fungsi helper untuk menghitung bilangan prima secara serial.
    
    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        show_progress (bool): Menampilkan progress bar jika True
        
    Returns:
        Tuple[int, float]: Tuple berisi (jumlah prima, waktu eksekusi)
    """
    finder = SerialPrimeFinder(start, end)
    count = finder.count_primes(show_progress)
    return count, finder.get_execution_time()