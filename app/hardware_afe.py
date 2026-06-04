# hardware_afe.py
class AnalogFrontEndSimulator:
    def __init__(self):
        # Rumus Gain AD620 dari README: G = 1 + (49.4kOhm / Rg)
        # Dengan Rg = 470 Ohm, Gain sekitar 106.1 kali
        self.rg = 470
        self.gain_ad620 = 1 + (49400 / self.rg)

        # Rumus Offset TLC2272 dari README: (56k / (47k + 56k)) * 3.3V ≈ 1.79V
        # Digunakan untuk menggeser level sinyal agar aman dari undershoot
        self.offset_v = (56 / (47 + 56)) * 3.3

    def process_signal(self, sensor_mv):
        """Menguatkan sinyal sensor dan menambahkan offset tegangan"""
        # Ubah mV ke Volt terlebih dahulu
        sensor_volt = sensor_mv / 1000.0

        # 1. Penguatan oleh AD620
        amplified_volt = sensor_volt * self.gain_ad620

        # 2. Penambahan tingkat offset dari TLC2272
        afe_output_volt = amplified_volt + self.offset_v

        # Batasi output sesuai tegangan saturasi rel mikro (0V - 3.3V)
        return min(max(afe_output_volt, 0.0), 3.3)
