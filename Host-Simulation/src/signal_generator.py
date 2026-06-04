"""Synthetic cuff-pressure waveform for simulation (no hardware required)."""

import numpy as np


def generate_cuff_waveform(
    sample_rate_hz: int = 200,
    duration_s: float = 24.0,
    seed: int = 42,
) -> tuple[np.ndarray, float]:
    """
    Approximate oscillometric envelope during deflate.
    Returns (samples in mV-equivalent units, sample_period_s).
    """
    rng = np.random.default_rng(seed)
    n = int(sample_rate_hz * duration_s)
    t = np.linspace(0, duration_s, n)

    envelope = 80 * np.exp(-0.35 * t) * (1 - np.exp(-2.5 * t))
    carrier = 0.15 * np.sin(2 * np.pi * 1.2 * t)
    hum = 3.0 * np.sin(2 * np.pi * 50 * t)
    noise = rng.normal(0, 0.8, n)

    signal = envelope + carrier + hum + noise + 15.0
    return signal.astype(np.float64), 1.0 / sample_rate_hz
