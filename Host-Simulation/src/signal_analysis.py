"""Analisis perbandingan sinyal sebelum vs sesudah filter (host processing)."""

from dataclasses import dataclass

import numpy as np

from cuffncode_specs import NOTCH_TARGET_HZ


@dataclass
class FilterComparison:
    """Metrik untuk panel GUI: sebelum / sesudah / pengaruh."""

    # Noise & hum
    hum_power_before: float
    hum_power_after: float
    hum_reduction_pct: float
    noise_std_before: float
    noise_std_after: float
    noise_reduction_pct: float

    # Envelope / peak (untuk estimasi BP demo)
    peak_before: float
    peak_after: float
    peak_change_pct: float

    bp_sys_before: int
    bp_dia_before: int
    bp_sys_after: int
    bp_dia_after: int

    rms_before: float
    rms_after: float

    summary_lines: tuple[str, ...]
    impact_lines: tuple[str, ...]


def _band_power(signal: np.ndarray, fs: float, f0: float, bandwidth: float = 3.0) -> float:
    n = len(signal)
    if n < 8:
        return 0.0
    spec = np.fft.rfft(signal - np.mean(signal))
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mask = (freqs >= f0 - bandwidth) & (freqs <= f0 + bandwidth)
    power = np.sum(np.abs(spec[mask]) ** 2) / n
    return float(power)


def _estimate_bp(peak: float) -> tuple[int, int]:
    sys = int(70 + peak * 0.55)
    dia = int(sys * 0.62)
    return sys, dia


def compare_before_after(
    raw: np.ndarray,
    filtered: np.ndarray,
    fs: float,
    hum_hz: float = NOTCH_TARGET_HZ,
) -> FilterComparison:
    raw = np.asarray(raw, dtype=np.float64)
    filtered = np.asarray(filtered, dtype=np.float64)

    hum_b = _band_power(raw, fs, hum_hz)
    hum_a = _band_power(filtered, fs, hum_hz)
    hum_red = (1.0 - hum_a / hum_b) * 100.0 if hum_b > 1e-12 else 0.0

    # Noise: komponen cepat (difference from smooth)
    smooth_b = np.convolve(raw, np.ones(21) / 21, mode="same")
    smooth_a = np.convolve(filtered, np.ones(21) / 21, mode="same")
    std_b = float(np.std(raw - smooth_b))
    std_a = float(np.std(filtered - smooth_a))
    noise_red = (1.0 - std_a / std_b) * 100.0 if std_b > 1e-12 else 0.0

    peak_b = float(np.max(raw))
    peak_a = float(np.max(filtered))
    peak_chg = ((peak_a - peak_b) / peak_b) * 100.0 if abs(peak_b) > 1e-12 else 0.0

    sys_b, dia_b = _estimate_bp(peak_b)
    sys_a, dia_a = _estimate_bp(peak_a)

    rms_b = float(np.sqrt(np.mean(raw**2)))
    rms_a = float(np.sqrt(np.mean(filtered**2)))

    summary = (
        "── SEBELUM (raw / pre-filter) ──",
        f"  • RMS amplitudo     : {rms_b:.2f}",
        f"  • Peak envelope     : {peak_b:.2f}",
        f"  • Daya hum {hum_hz:.0f} Hz  : {hum_b:.4f} (relatif)",
        f"  • Std noise residu  : {std_b:.3f}",
        f"  • Estimasi BP demo  : {sys_b}/{dia_b} mmHg",
        "",
        "── SESUDAH (filtered) ──",
        f"  • RMS amplitudo     : {rms_a:.2f}",
        f"  • Peak envelope     : {peak_a:.2f}",
        f"  • Daya hum {hum_hz:.0f} Hz  : {hum_a:.4f} (relatif)",
        f"  • Std noise residu  : {std_a:.3f}",
        f"  • Estimasi BP demo  : {sys_a}/{dia_a} mmHg",
    )

    impact = (
        "── PENGARUH pemrosesan (Host) ──",
        f"  1. Notch {hum_hz:.0f} Hz: hum PLN ↓ ~{hum_red:.1f}%",
        "     → osilasi cuff lebih terbaca; deteksi peak lebih stabil",
        f"  2. Moving average  : noise residu ↓ ~{noise_red:.1f}%",
        "     → kurva envelope lebih halus untuk algoritma BP",
        f"  3. Peak envelope   : perubahan {peak_chg:+.1f}%",
        f"     → BP demo: {sys_b}/{dia_b} → {sys_a}/{dia_a} mmHg",
        "",
        "  Kesimpulan: filter host (paralel/distributed) menekan",
        "  gangguan listrik & noise tanpa mengganti hardware AFE.",
        "  Nilai BP tetap demo — bukan kalibrasi klinis.",
    )

    return FilterComparison(
        hum_power_before=hum_b,
        hum_power_after=hum_a,
        hum_reduction_pct=hum_red,
        noise_std_before=std_b,
        noise_std_after=std_a,
        noise_reduction_pct=noise_red,
        peak_before=peak_b,
        peak_after=peak_a,
        peak_change_pct=peak_chg,
        bp_sys_before=sys_b,
        bp_dia_before=dia_b,
        bp_sys_after=sys_a,
        bp_dia_after=dia_a,
        rms_before=rms_b,
        rms_after=rms_a,
        summary_lines=summary,
        impact_lines=impact,
    )
