"""
src/
====
Package untuk Parallel Prime Finder.

Modul-modul yang tersedia:
- prime_utils: Fungsi utilitas untuk operasi bilangan prima
- serial: Implementasi pencarian serial
- parallel: Implementasi pencarian paralel
- benchmark: Fungsi benchmark dan visualisasi
"""

from .prime_utils import (
    is_prime,
    find_primes_in_range,
    find_primes_in_range_optimized,
    count_primes_in_range,
    count_primes_in_range_optimized,
    split_range
)

from .serial import (
    SerialPrimeFinder,
    run_serial,
    run_serial_count
)

from .parallel import (
    ParallelPrimeFinder,
    run_parallel,
    run_parallel_count,
    run_parallel_benchmark
)

from .benchmark import (
    BenchmarkResult,
    BenchmarkRunner,
    run_full_benchmark
)

__version__ = "1.0.0"
__author__ = "Tugas Besar Komputasi Paralel"

__all__ = [
    # prime_utils
    'is_prime',
    'find_primes_in_range',
    'find_primes_in_range_optimized',
    'count_primes_in_range',
    'count_primes_in_range_optimized',
    'split_range',
    
    # serial
    'SerialPrimeFinder',
    'run_serial',
    'run_serial_count',
    
    # parallel
    'ParallelPrimeFinder',
    'run_parallel',
    'run_parallel_count',
    'run_parallel_benchmark',
    
    # benchmark
    'BenchmarkResult',
    'BenchmarkRunner',
    'run_full_benchmark'
]