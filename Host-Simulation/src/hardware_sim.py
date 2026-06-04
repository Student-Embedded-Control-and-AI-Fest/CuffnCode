"""
Simulasi alur hardware CuffnCode (software-only).
Tidak membutuhkan board STM32 / sensor fisik.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np

from cuffncode_specs import (
    AD620_GAIN,
    ADC_BITS,
    ADC_RATE_HZ,
    ADC_VREF,
    TLC_OFFSET_V,
    get_phase_info,
)
from signal_generator import generate_cuff_waveform
from filters import moving_average, notch_50hz


class Phase(Enum):
    IDLE = auto()
    PUMP_INFLATE = auto()
    VALVE_HOLD = auto()
    VALVE_DEFLATE = auto()
    SENSOR_BRIDGE = auto()
    AFE_AD620 = auto()
    AFE_TLC2272 = auto()
    STM32_ADC = auto()
    HOST_PARALLEL = auto()
    HOST_DISTRIBUTED = auto()
    DONE = auto()


def _phase_key(phase: Phase) -> str:
    return phase.name


PHASE_LABELS: dict[Phase, str] = {
    p: get_phase_info(_phase_key(p)).short for p in Phase
}


@dataclass
class SignalTelemetry:
    """Nilai simulasi yang ditampilkan di GUI (setara rantai AFE)."""
    bridge_peak_mv: float = 0.0
    ad620_peak_mv: float = 0.0
    after_offset_v: float = 0.0
    adc_code_peak: int = 0
    hum_component_mv: float = 3.0
    sample_count: int = 0
    fs_hz: float = ADC_RATE_HZ


@dataclass
class SimulationResult:
    raw: np.ndarray
    filtered: np.ndarray
    fs: float
    systolic: int
    diastolic: int
    envelope_peak: float
    telemetry: SignalTelemetry
    parallel_chunks: int = 8


@dataclass
class HardwareSimulator:
    """State machine + sinyal untuk GUI."""

    phase: Phase = Phase.IDLE
    cuff_pressure_mmhg: float = 0.0
    pump_on: bool = False
    valve_inflate_open: bool = False
    valve_deflate_open: bool = False
    adc_progress: float = 0.0
    parallel_progress: float = 0.0
    distributed_node: str = ""
    log: list[str] = field(default_factory=list)
    telemetry: SignalTelemetry = field(default_factory=SignalTelemetry)
    _result: SimulationResult | None = None

    def reset(self) -> None:
        self.phase = Phase.IDLE
        self.cuff_pressure_mmhg = 0.0
        self.pump_on = False
        self.valve_inflate_open = False
        self.valve_deflate_open = False
        self.adc_progress = 0.0
        self.parallel_progress = 0.0
        self.distributed_node = ""
        self.log.clear()
        self.telemetry = SignalTelemetry()
        self._result = None

    def _compute_telemetry(self, bridge: np.ndarray, fs: float) -> SignalTelemetry:
        peak_bridge = float(np.max(np.abs(bridge - np.mean(bridge))))
        peak_bridge = min(max(peak_bridge, 45.0), 95.0)
        ad620_out = peak_bridge * AD620_GAIN / 1000.0
        after_v = ad620_out + TLC_OFFSET_V
        code = int(min((after_v / ADC_VREF) * ((1 << ADC_BITS) - 1), (1 << ADC_BITS) - 1))
        return SignalTelemetry(
            bridge_peak_mv=peak_bridge,
            ad620_peak_mv=peak_bridge * AD620_GAIN,
            after_offset_v=after_v,
            adc_code_peak=code,
            sample_count=len(bridge),
            fs_hz=fs,
        )

    def prepare_signal(self, duration_s: float = 10.0) -> SimulationResult:
        raw, dt = generate_cuff_waveform(duration_s=duration_s, sample_rate_hz=ADC_RATE_HZ)
        fs = 1.0 / dt
        bridge = raw - np.mean(raw)
        scale = 70.0 / max(float(np.max(np.abs(bridge))), 1e-6)
        bridge = bridge * scale
        filtered = notch_50hz(moving_average(raw, 11), fs)
        peak = float(np.max(filtered))
        sys = int(70 + peak * 0.55)
        dia = int(sys * 0.62)
        telem = self._compute_telemetry(bridge, fs)
        self.telemetry = telem
        self._result = SimulationResult(
            raw=raw,
            filtered=filtered,
            fs=fs,
            systolic=sys,
            diastolic=dia,
            envelope_peak=peak,
            telemetry=telem,
        )
        return self._result

    @property
    def result(self) -> SimulationResult | None:
        return self._result

    def phase_info(self, phase: Phase | None = None):
        return get_phase_info(_phase_key(phase or self.phase))

    def active_blocks(self) -> set[str]:
        m: dict[Phase, set[str]] = {
            Phase.IDLE: set(),
            Phase.PUMP_INFLATE: {"cuff", "pump"},
            Phase.VALVE_HOLD: {"cuff", "valve_a", "valve_b"},
            Phase.VALVE_DEFLATE: {"cuff", "valve_b", "sensor"},
            Phase.SENSOR_BRIDGE: {"cuff", "sensor"},
            Phase.AFE_AD620: {"sensor", "ad620"},
            Phase.AFE_TLC2272: {"ad620", "tlc"},
            Phase.STM32_ADC: {"tlc", "stm32"},
            Phase.HOST_PARALLEL: {"stm32", "host"},
            Phase.HOST_DISTRIBUTED: {"host", "node_a", "node_b", "node_c"},
            Phase.DONE: {"host", "stm32", "sensor"},
        }
        return m.get(self.phase, set())
