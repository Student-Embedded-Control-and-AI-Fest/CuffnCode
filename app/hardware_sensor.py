# hardware_sensor.py
import numpy as np
import time


class MPS20N0040DSimulator:
    def __init__(self):
        # Rentang output sensor murni: ~0 hingga 50 mV untuk tekanan penuh
        self.max_mv = 50.0
        self.start_time = time.time()

    def get_bridge_output_mv(self):
        """
        Mensimulasikan output mV jembatan sensor dengan bentuk gelombang detak jantung asli.
        Memiliki komponen Puncak Sistolik, Dicrotic Notch, dan Fase Diastolik.
        """
        t = time.time() - self.start_time

        # 1. SIMULASI DEFLASI MANSET (Sinyal Base DC)
        # Menurun dari 150 mmHg ke 50 mmHg dalam siklus 30 detik
        cycle_t = t % 30
        base_pressure_mmHg = 150.0 - (3.5 * cycle_t)
        if base_pressure_mmHg < 50:
            base_pressure_mmHg = 50

        # 2. SIMULASI PULSA DETAK JANTUNG BIOLOGIS (Sinyal AC)
        # Menggunakan frekuensi 1.25 Hz (Setara dengan 75 Kali Detak per Menit / BPM)
        heart_rate_hz = 1.25
        # Siklus per satu detakan (0.0 sampai 1.0)
        phase = (t * heart_rate_hz) % 1.0

        # Membuat bentuk pulsa arteri menggunakan kombinasi beberapa harmonik (Fourier Series dasar)
        # Ini membentuk tanjakan tajam (Sistolik), lekukan katup (Dicrotic Notch), dan landasan (Diastolik)
        if phase < 0.6:  # Fase Kontraksi & Ejeksi Jantung
            # Puncak Utama (Systolic Peak) + Puncak Kedua (Dicrotic Wave)
            pulse_shape = (np.sin(np.pi * phase / 0.6) ** 2) * 0.7 + \
                          (np.sin(2.5 * np.pi * phase / 0.6) ** 2) * 0.3
        else:  # Fase Relaksasi Jantung (Diastolic Tail)
            # Menurun perlahan menuju baseline
            decay_phase = (phase - 0.6) / 0.4
            pulse_shape = 0.1 * np.exp(-3 * decay_phase)

        # 3. KARAKTERISTIK METODE OSIROMETRIK
        # Sinyal detak jantung paling besar terekam saat tekanan manset berada di sekitar
        # Mean Arterial Pressure / MAP (Aritmatika Tekanan Darah, misal di antara 80 s.d 120 mmHg)
        if 80 <= base_pressure_mmHg <= 120:
            # Amplitudo detak membesar secara melengkung (envelope) di area MAP
            envelope_factor = 4.5 - 0.1 * abs(base_pressure_mmHg - 100)
        else:
            # Amplitudo detak mengecil saat manset terlalu ketat atau terlalu longgar
            envelope_factor = 0.8

        # Gabungkan penurunan tekanan sirkuit (DC) dan denyut jantung biologis (AC)
        total_pressure_mmHg = base_pressure_mmHg + \
            (pulse_shape * envelope_factor)

        # 4. KONVERSI FISIK SIRKUIT KE MILIVOLT
        # Kalibrasi: Tegangan jembatan berbanding lurus dengan tekanan sirkuit (300 mmHg = 50 mV)
        mv_output = (total_pressure_mmHg / 300.0) * self.max_mv
        return mv_output
