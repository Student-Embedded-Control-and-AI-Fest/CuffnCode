"""
Spesifikasi & teks referensi proyek CuffnCode.
Sumber: https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode
        https://publish.obsidian.md/auralius/Published/CuffnCode
"""

from dataclasses import dataclass

# --- Konstanta desain (repo resmi) ---
AD620_RG_OHM = 470.0
AD620_GAIN = 1.0 + 49_400.0 / AD620_RG_OHM  # ≈ 106.17, dokumentasi ≈105

TLC_R1_K = 47.0
TLC_R2_K = 56.0
VCC_V = 3.3
TLC_OFFSET_V = (TLC_R2_K / (TLC_R1_K + TLC_R2_K)) * VCC_V  # ≈ 1.79 V (repo ≈1.5 V dengan toleransi)

SENSOR_MODEL = "MPS20N0040D"
SENSOR_FS_MV = (50.0, 100.0)  # full-scale tipikal
SENSOR_IMPEDANCE_KOHM = (4.0, 6.0)

MCU_MODEL = "STM32F411CEU6"
MCU_ALIAS = "Black Pill"
ADC_RATE_HZ = 200
ADC_BITS = 12
ADC_VREF = 3.3

NOTCH_TARGET_HZ = 50.0  # roadmap: 50/60 Hz hum killer

PROJECT_TITLE = "CuffnCode"
PROJECT_TAGLINE = (
    "Retrofitted blood pressure measurement system for teaching and research. "
    "Overinstrumented platform for signal processing & control algorithms."
)
PROJECT_FUNDING = "IFAC Activity Fund (July 2025 – June 2026)"


@dataclass(frozen=True)
class PhaseInfo:
    title: str
    short: str
    detail: str
    specs: str
    log_lines: tuple[str, ...]


# Kunci fase mengikuti hardware_sim.Phase (string untuk hindari circular import)
PHASE_SPECS: dict[str, PhaseInfo] = {
    "IDLE": PhaseInfo(
        title="CuffnCode — Siap",
        short="Tekan Mulai Simulasi untuk menjalankan alur lengkap",
        detail=(
            "Proyek ini mensimulasikan sistem pengukuran tekanan darah hasil retrofit. "
            "Hardware fisik tidak terhubung; nilai sinyal dan tekanan adalah model matematis "
            "untuk demonstrasi kuliah Komputasi Paralel & Sistem Terdistribusi."
        ),
        specs=(
            f"Referensi: {PROJECT_TITLE}\n"
            f"{PROJECT_TAGLINE}\n"
            f"Funding: {PROJECT_FUNDING}\n\n"
            "Komponen utama:\n"
            f"  • Sensor: {SENSOR_MODEL} (bridge ~{SENSOR_FS_MV[0]}–{SENSOR_FS_MV[1]} mV FS)\n"
            f"  • AFE: AD620 (G≈{AD620_GAIN:.0f}) + TLC2272 (rail-to-rail offset)\n"
            f"  • MCU: {MCU_MODEL} ({MCU_ALIAS})\n"
            "  • Aktuator: 1× DC micro-pump + 2× solenoid valve\n"
            "  • Host: PC — pipeline paralel & 3 node terdistribusi"
        ),
        log_lines=(),
    ),
    "PUMP_INFLATE": PhaseInfo(
        title="Retrofitted Pump — Inflate",
        short="DC micro-pump ON — mengisi manset (cuff)",
        detail=(
            "Pada desain CuffnCode, satu pompa DC menggerakkan aliran udara ke cuff "
            "melalui rangkaian switching dua solenoid valve (inflate / deflate). "
            "Tahap ini mensimulasikan fase pengembangan cuff sebelum pengukuran oscillometric."
        ),
        specs=(
            "Switching (Obsidian / system design):\n"
            "  • 1 DC micro-pump\n"
            "  • 2 solenoid valve pada satu jalur pompa\n"
            "  • Valve inflate: mengarahkan aliran ke cuff\n\n"
            "Safety (repo):\n"
            "  • MPS20N0040D rapuh — hindari over-pressure\n"
            "  • Jangan melebihi tekanan aman hobbyist sphygmomanometer"
        ),
        log_lines=(
            "[Pump] DC micro-pump ON — jalur inflate aktif",
            "[Valve] Solenoid inflate: OPEN | deflate: CLOSED",
            "[Cuff] Tekanan naik (simulasi oscillometric pre-measure)",
        ),
    ),
    "VALVE_HOLD": PhaseInfo(
        title="Hold Pressure",
        short="Kedua valve TUTUP — tekanan cuff dipertahankan",
        detail=(
            "Setelah inflate, tekanan dipertahankan singkat agar cuff stabil. "
            "Pada implementasi nyata, STM32 mengatur GPIO/PWM ke driver valve & pump."
        ),
        specs=(
            f"MCU: {MCU_MODEL}\n"
            "  • GPIO: driver solenoid / MOSFET switching\n"
            "  • Kontrol tertutup (roadmap): algoritma control di platform overinstrumented"
        ),
        log_lines=(
            "[Valve] inflate: CLOSED | deflate: CLOSED",
            "[Cuff] Hold — menunggu fase pengukuran",
        ),
    ),
    "VALVE_DEFLATE": PhaseInfo(
        title="Deflate — Oscillometric Acquisition",
        short="Valve deflate OPEN — cuff mengempis, sensor aktif",
        detail=(
            "Metode oscillometric: saat cuff mengempis terkontrol, tekanan arteri "
            "menghasilkan osilasi pada sensor bridge. Envelope osilasi dipakai "
            "untuk estimasi systolic/diastolic (di perangkat nyata; di sini: demo)."
        ),
        specs=(
            "Fase kritis pengukuran:\n"
            "  • Deflate terkontrol (rate stabil)\n"
            "  • Acquisition sinkron dengan penurunan tekanan\n"
            f"  • Sampling target: {ADC_RATE_HZ} Hz (simulasi GUI)"
        ),
        log_lines=(
            "[Valve] deflate: OPEN — udara keluar",
            "[Sensor] Bridge mulai merespons osilasi tekanan",
            "[Catatan] Sinyal sintetis: envelope + carrier + noise + hum 50 Hz",
        ),
    ),
    "SENSOR_BRIDGE": PhaseInfo(
        title=f"Sensor — {SENSOR_MODEL}",
        short="Bridge piezo-resistive millivolt",
        detail=(
            "MPS20N0040D adalah sensor tekanan level millivolt untuk "
            "sphygmomanometer hobi / retrofit. Output berupa jembatan Wheatstone "
            "dengan impedansi beberapa kΩ dan full-scale tipikal puluhan mV."
        ),
        specs=(
            f"Model: {SENSOR_MODEL}\n"
            f"  • Full-scale: ≈{SENSOR_FS_MV[0]}–{SENSOR_FS_MV[1]} mV\n"
            f"  • Impedansi bridge: ≈{SENSOR_IMPEDANCE_KOHM[0]}–{SENSOR_IMPEDANCE_KOHM[1]} kΩ\n"
            "  • Aplikasi: hobbyist BP cuff / reproducible teaching platform\n"
            "  • Peringatan: hindari over-pressure (kerusakan permanen)"
        ),
        log_lines=("[Sensor] Bridge output (sim): lihat panel metrik mV",),
    ),
    "AFE_AD620": PhaseInfo(
        title="Analog Front End — AD620",
        short="Instrumentation amplifier — gain tinggi",
        detail=(
            "AD620 memperkuat sinyal differential dari bridge dengan CMRR tinggi. "
            "Pada desain CuffnCode, resistor gain Rg = 470 Ω (TINA-TI & KiCad repo)."
        ),
        specs=(
            "Gain (Designer’s Guide / repo TINA-TI):\n"
            f"  G = 1 + 49.4 kΩ / Rg\n"
            f"  Rg = {AD620_RG_OHM:.0f} Ω\n"
            f"  G ≈ {AD620_GAIN:.2f} (dokumentasi ≈105)\n\n"
            "Alasan pemilihan:\n"
            "  • Relatif murah & tersedia di pasar Indonesia\n"
            "  • Cocok untuk sensor millivolt generik"
        ),
        log_lines=(
            f"[AFE] AD620: G = 1 + 49.4k/{AD620_RG_OHM:.0f} ≈ {AD620_GAIN:.1f}",
            "[AFE] Input diff. dari bridge → output amplified",
        ),
    ),
    "AFE_TLC2272": PhaseInfo(
        title="Analog Front End — TLC2272",
        short="Dual op-amp — level shift & headroom",
        detail=(
            "TLC2272 (low-noise, rail-to-rail) menggeser level sinyal setelah AD620 "
            "agar berada di tengah rentang ADC 3.3 V, memberi headroom untuk undershoot "
            "dan sinyal bipolar acuan."
        ),
        specs=(
            "Offset (divider repo):\n"
            f"  Voffset = R2/(R1+R2) × {VCC_V} V\n"
            f"  R1={TLC_R1_K:.0f} kΩ, R2={TLC_R2_K:.0f} kΩ\n"
            f"  Voffset ≈ {TLC_OFFSET_V:.2f} V (README ≈1.5 V)\n\n"
            "TINA-TI: AC simulation tersedia di folder /TINA-TI repo"
        ),
        log_lines=(
            f"[AFE] TLC2272: level shift ≈ {TLC_OFFSET_V:.2f} V",
            "[AFE] Headroom untuk sinyal bipolar pasca-instrumen",
        ),
    ),
    "STM32_ADC": PhaseInfo(
        title=f"Digital Controller — {MCU_MODEL}",
        short=f"{MCU_ALIAS} — ADC + PWM/GPIO",
        detail=(
            "STM32F411CE mengambil sampel analog hasil AFE, mengendalikan pump/valve, "
            "dan dapat mengirim data ke host (UART/USB) untuk algoritma lanjutan."
        ),
        specs=(
            f"MCU: {MCU_MODEL} ({MCU_ALIAS})\n"
            f"  • ADC: {ADC_BITS}-bit, Vref={ADC_VREF} V\n"
            f"  • Rate simulasi: {ADC_RATE_HZ} Hz\n"
            "  • Prototype: lihat images/prototype1.png di repo GitHub\n\n"
            "Catatan daya:\n"
            "  • Power USB: waspada ground noise dari PC\n"
            "  • Ferrite pada kabel USB dapat membantu"
        ),
        log_lines=(
            f"[STM32] ADC @ {ADC_RATE_HZ} Hz — DMA/stream ke buffer",
            "[STM32] PWM/GPIO: pump & solenoid (hardware nyata)",
        ),
    ),
    "HOST_PARALLEL": PhaseInfo(
        title="Host — Data Parallelism",
        short="Pemrosesan chunk — multiprocessing.Pool",
        detail=(
            "Di mini project kuliah, pipeline host memecah waveform menjadi chunk "
            "dan menerapkan task identik (moving average + notch 50 Hz) — pola "
            "data parallelism (SIMD-like). Roadmap CuffnCode: 50/60 Hz hum killer."
        ),
        specs=(
            "Filter (roadmap repo + simulasi):\n"
            f"  • Notch {NOTCH_TARGET_HZ} Hz (hum PLN)\n"
            "  • Moving average — reduksi noise\n"
            "  • 8 chunk — Pool.map / chunksize tuning\n\n"
            "Mata kuliah: bandingkan sequential vs parallel vs dynamic scheduling"
        ),
        log_lines=("[Host] Data parallelism — task sama, data berbeda (chunk)",),
    ),
    "HOST_DISTRIBUTED": PhaseInfo(
        title="Host — Distributed Pipeline",
        short="Node A → B → C (message passing)",
        detail=(
            "Simulasi sistem terdistribusi: Acquisition (stream sample), "
            "Processing (filter + fitur), Storage/UI (agregasi BP). "
            "Komunikasi via Queue — analogi cluster / microservices edge."
        ),
        specs=(
            "Node A (Acquisition):\n"
            "  • Setara STM32 streaming / batch ADC\n"
            "Node B (Processing):\n"
            "  • Filter + envelope peak\n"
            "Node C (Storage/UI):\n"
            "  • Rekaman & tampilan hasil\n\n"
            "Referensi arsitektur: publish.obsidian.md — switching & AFE"
        ),
        log_lines=(),
    ),
    "DONE": PhaseInfo(
        title="Selesai",
        short="Estimasi BP demo + ringkasan",
        detail=(
            "Nilai BP yang ditampilkan berasal dari peak envelope simulasi — "
            "bukan kalibrasi klinis. Proyek asli CuffnCode bertujuan teaching/research "
            "dan evaluasi performa (roadmap: PCB layout, performance evaluation)."
        ),
        specs=(
            "Next-to-do (repo CuffnCode):\n"
            "  • 50/60 Hz notch filter (hum killer) — sebagian di simulasi ini\n"
            "  • PCB layouting (KiCad/)\n"
            "  • Performance evaluations\n\n"
            "Kredit desain: Analog Devices Instrumentation Amp Guide, TINA-TI"
        ),
        log_lines=("=== Simulasi selesai — bukan diagnosis medis ===",),
    ),
}


def get_phase_info(phase_key: str) -> PhaseInfo:
    return PHASE_SPECS.get(phase_key, PHASE_SPECS["IDLE"])
