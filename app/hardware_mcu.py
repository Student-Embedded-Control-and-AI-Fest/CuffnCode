# hardware_mcu.py
import random


class STM32F411Simulator:
    def __init__(self):
        # Resolusi ADC 12-bit (2^12 - 1 = 4095)
        self.adc_resolution = 4095
        self.v_ref = 3.3  # Tegangan referensi internal

    def read_adc(self, analog_volt):
        """Mengubah tegangan menjadi nilai digital dan menambahkan sedikit noise sirkuit digital"""
        # Konversi ke nilai digital 12-bit
        adc_value = int((analog_volt / self.v_ref) * self.adc_resolution)

        # Menambahkan sedikit noise internal ADC (+/- 2 angka random)
        noise = random.randint(-2, 2)
        adc_value_with_noise = adc_value + noise

        # Batasi agar tetap di koridor resolusi ADC 12-bit
        return min(max(adc_value_with_noise, 0), self.adc_resolution)
