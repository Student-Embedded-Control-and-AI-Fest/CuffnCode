"""
CuffnCode — Parallel signal-processing pipeline (MapReduce-style).

Studi kasus: pemrosesan waveform tekanan cuff secara data-parallel
menggunakan multiprocessing.Pool (pola SIMD / data parallelism).
"""

import time
from multiprocessing import Pool, cpu_count

import numpy as np

from signal_generator import generate_cuff_waveform
from filters import process_chunk


def split_signal(signal: np.ndarray, n_chunks: int) -> list[np.ndarray]:
    return np.array_split(signal, n_chunks)


def sequential_process(
    chunks: list[np.ndarray], fs: float, filter_passes: int
) -> tuple[np.ndarray, float, float]:
    t0 = time.perf_counter()
    results = []
    global_peak = 0.0
    for i, ch in enumerate(chunks):
        _, filtered, peak = process_chunk((i, ch, fs, filter_passes))
        results.append((i, filtered))
        global_peak = max(global_peak, peak)
    merged = merge_chunks(results)
    elapsed = time.perf_counter() - t0
    return merged, global_peak, elapsed


def parallel_process(
    chunks: list[np.ndarray],
    fs: float,
    filter_passes: int,
    workers: int | None = None,
    chunksize: int = 1,
) -> tuple[np.ndarray, float, float]:
    workers = workers or max(2, cpu_count() - 1)
    tasks = [(i, ch, fs, filter_passes) for i, ch in enumerate(chunks)]

    t0 = time.perf_counter()
    with Pool(workers) as pool:
        out = pool.map(process_chunk, tasks, chunksize=chunksize)

    global_peak = max(r[2] for r in out)
    merged = merge_chunks([(r[0], r[1]) for r in out])
    elapsed = time.perf_counter() - t0
    return merged, global_peak, elapsed


def merge_chunks(indexed: list[tuple[int, np.ndarray]]) -> np.ndarray:
    indexed.sort(key=lambda x: x[0])
    return np.concatenate([x[1] for x in indexed])


def estimate_bp_from_envelope(envelope_peak: float) -> tuple[int, int]:
    """Toy mapping for demo output (not clinical)."""
    sys = int(70 + envelope_peak * 0.55)
    dia = int(sys * 0.62)
    return sys, dia


def run_benchmark(n_chunks: int = 16, filter_passes: int = 12) -> None:
    print("=" * 55)
    print("  CuffnCode — Parallel Pipeline Benchmark")
    print("  Mata kuliah: Komputasi Paralel & Sistem Terdistribusi")
    print("=" * 55)

    signal, dt = generate_cuff_waveform()
    fs = 1.0 / dt
    chunks = split_signal(signal, n_chunks)

    print(f"\nSamples: {len(signal)} | Chunks: {n_chunks} | CPU cores: {cpu_count()}")

    _, peak_seq, t_seq = sequential_process(chunks, fs, filter_passes)
    _, peak_par, t_par = parallel_process(chunks, fs, filter_passes, chunksize=2)
    _, peak_dyn, t_dyn = parallel_process(chunks, fs, filter_passes, chunksize=1)

    sys, dia = estimate_bp_from_envelope(max(peak_seq, peak_par))

    speedup = t_seq / t_par if t_par > 0 else 0.0
    print("\n--- Timing ---")
    print(f"Sequential : {t_seq:.4f} s")
    print(f"Parallel   : {t_par:.4f} s  (speedup ~ {speedup:.2f}x)")
    print(f"Dynamic    : {t_dyn:.4f} s  (chunksize=1, load balancing)")
    if speedup < 1.0:
        print(
            "\nCatatan: di Windows, overhead spawn process bisa > gain untuk data kecil."
            "\n         Untuk tugas, yang dinilai adalah pemahaman pola paralel & distributed."
        )

    print("\n--- Result (simulation) ---")
    print(f"Envelope peak : {max(peak_seq, peak_par):.2f}")
    print(f"Estimated BP    : {sys}/{dia} mmHg (demo only, not medical)")

    diff = np.max(np.abs(peak_seq - peak_par))
    print(f"\nPeak match (seq vs par): {'OK' if diff < 1e-6 else 'CHECK'}")


if __name__ == "__main__":
    run_benchmark()
