"""
prime_utils.py
==============
Modul utilitas untuk operasi bilangan prima.

Modul ini menyediakan fungsi-fungsi untuk:
- Mengecek apakah suatu bilangan adalah prima
- Mencari bilangan prima dalam rentang tertentu
"""

import math
from typing import List, Tuple


def is_prime(n: int) -> bool:
    """
    Mengecek apakah suatu bilangan adalah bilangan prima.

    Algoritma yang digunakan:
    1. Jika n < 2, bukan bilangan prima
    2. Jika n == 2, adalah bilangan prima
    3. Jika n genap (selain 2), bukan bilangan prima
    4. Cek pembagi ganjil dari 3 sampai sqrt(n)

    Args:
        n (int): Bilangan yang akan dicek

    Returns:
        bool: True jika n adalah bilangan prima, False jika tidak
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Cek pembagi ganjil sampai sqrt(n)
    sqrt_n = int(math.sqrt(n)) + 1
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            return False
    return True


def find_primes_in_range(args: Tuple[int, int]) -> List[int]:
    """
    Mencari semua bilangan prima dalam rentang tertentu.

    Fungsi ini dirancang untuk digunakan dengan multiprocessing.Pool,
    sehingga menerima tuple sebagai argumen.

    Args:
        args (Tuple[int, int]): Tuple berisi (start, end) rentang pencarian

    Returns:
        List[int]: List berisi semua bilangan prima dalam rentang tersebut
    """
    start, end = args
    primes = []
    for num in range(start, end):
        if is_prime(num):
            primes.append(num)
    return primes


def find_primes_in_range_optimized(args: Tuple[int, int]) -> List[int]:
    """
    Versi optimasi untuk mencari bilangan prima dalam rentang tertentu.

    Menggunakan teknik:
    - Lewati bilangan genap (kecuali 2)
    - Gunakan slicing untuk iterasi lebih cepat

    Args:
        args (Tuple[int, int]): Tuple berisi (start, end) rentang pencarian

    Returns:
        List[int]: List berisi semua bilangan prima dalam rentang tersebut
    """
    start, end = args
    primes = []
    
    # Handle kasus khusus untuk angka 2
    if start <= 2 < end:
        primes.append(2)
    
    # Mulai dari angka ganjil pertama
    if start < 3:
        start = 3
    elif start % 2 == 0:
        start += 1
    
    # Cek hanya bilangan ganjil
    for num in range(start, end, 2):
        if is_prime(num):
            primes.append(num)
    
    return primes


def count_primes_in_range(args: Tuple[int, int]) -> int:
    """
    Menghitung jumlah bilangan prima dalam rentang tertentu.

    Fungsi ini lebih efisien untuk benchmark karena hanya mengembalikan
    jumlah, bukan list bilangan prima.

    Args:
        args (Tuple[int, int]): Tuple berisi (start, end) rentang pencarian

    Returns:
        int: Jumlah bilangan prima dalam rentang tersebut
    """
    start, end = args
    count = 0
    
    for num in range(start, end):
        if is_prime(num):
            count += 1
    
    return count


def count_primes_in_range_optimized(args: Tuple[int, int]) -> int:
    """
    Versi optimasi untuk menghitung jumlah bilangan prima.

    Args:
        args (Tuple[int, int]): Tuple berisi (start, end) rentang pencarian

    Returns:
        int: Jumlah bilangan prima dalam rentang tersebut
    """
    start, end = args
    count = 0
    
    # Handle kasus khusus untuk angka 2
    if start <= 2 < end:
        count += 1
    
    # Mulai dari angka ganjil pertama
    if start < 3:
        start = 3
    elif start % 2 == 0:
        start += 1
    
    # Cek hanya bilangan ganjil
    for num in range(start, end, 2):
        if is_prime(num):
            count += 1
    
    return count


def split_range(start: int, end: int, num_workers: int) -> List[Tuple[int, int]]:
    """
    Membagi rentang bilangan menjadi beberapa bagian untuk diproses paralel.

    Args:
        start (int): Batas bawah rentang
        end (int): Batas atas rentang
        num_workers (int): Jumlah worker/proses yang akan digunakan

    Returns:
        List[Tuple[int, int]]: List tuple berisi (start, end) untuk setiap worker
    """
    total_range = end - start
    chunk_size = total_range // num_workers
    ranges = []
    
    for i in range(num_workers):
        chunk_start = start + i * chunk_size
        # Worker terakhir mendapatkan sisa elemen
        if i == num_workers - 1:
            chunk_end = end
        else:
            chunk_end = chunk_start + chunk_size
        ranges.append((chunk_start, chunk_end))
    
    return ranges