"""Signal-processing tasks executed per chunk (CPU-bound, data-parallel friendly)."""

import numpy as np


def moving_average(chunk: np.ndarray, window: int = 11) -> np.ndarray:
    if len(chunk) < window:
        return chunk.copy()
    kernel = np.ones(window) / window
    return np.convolve(chunk, kernel, mode="same")


def notch_50hz(chunk: np.ndarray, fs: float, f0: float = 50.0, q: float = 8.0) -> np.ndarray:
    """Simple IIR notch — same task applied to every chunk (data parallelism)."""
    w0 = 2 * np.pi * f0 / fs
    alpha = np.sin(w0) / (2 * q)
    b0, b1, b2 = 1.0, -2 * np.cos(w0), 1.0
    a0 = 1 + alpha
    a1, a2 = -2 * np.cos(w0) / a0, (1 - alpha) / a0
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1, a2])

    out = np.zeros_like(chunk)
    x1 = x2 = y1 = y2 = 0.0
    for i, x0 in enumerate(chunk):
        y0 = b[0] * x0 + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        out[i] = y0
        x2, x1, y2, y1 = x1, x0, y1, y0
    return out


def process_chunk(args: tuple[int, np.ndarray, float, int]) -> tuple[int, np.ndarray, float]:
    """Worker entry: index, samples, sample rate, filter_passes."""
    idx, chunk, fs, passes = args
    filtered = chunk.astype(np.float64)
    for _ in range(passes):
        filtered = notch_50hz(moving_average(filtered, 11), fs)
    peak = float(np.max(filtered))
    return idx, filtered, peak
