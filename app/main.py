# main.py
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# Mengimpor modul simulasi masing-masing hardware
from hardware_sensor import MPS20N0040DSimulator
from hardware_afe import AnalogFrontEndSimulator
from hardware_mcu import STM32F411Simulator


class CuffnCodeDashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Instansiasi objek masing-masing simulasi hardware
        self.sensor = MPS20N0040DSimulator()
        self.afe = AnalogFrontEndSimulator()
        self.mcu = STM32F411Simulator()

        # Pengaturan Tampilan GUI Window
        self.setWindowTitle(
            "CuffnCode - Multi-Hardware Real-time Selector Simulation")
        self.resize(900, 600)

        # Layouting komponen GUI Utama
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # --- PANEL PEMILIH GRAFIK (DROP-DOWN SELECTION) ---
        self.selector_layout = QtWidgets.QHBoxLayout()
        self.label_select = QtWidgets.QLabel(
            "Pilih Data Komponen Hardware yang Ingin Ditampilkan:")
        self.label_select.setStyleSheet(
            "font-weight: bold; font-size: 13px; color: #ffffff;")

        self.combo_hardware = QtWidgets.QComboBox()
        self.combo_hardware.addItems([
            "1. Hasil Akhir Medis (Konversi ke mmHg)",
            "2. Sinyal Asli Sensor MPS20N0040D (miliVolt)",
            "3. Sinyal Setelah Analog Front End (Voltase)",
            "4. Sinyal Digital dari STM32F411 (Nilai ADC 12-bit)"
        ])
        self.combo_hardware.setStyleSheet(
            "font-size: 13px; padding: 5px; background-color: #333333; color: white;")
        # Menghubungkan perubahan pilihan drop-down dengan fungsi penyesuaian label grafik
        self.combo_hardware.currentIndexChanged.connect(
            self.on_hardware_selection_changed)

        self.selector_layout.addWidget(self.label_select)
        self.selector_layout.addWidget(self.combo_hardware)
        self.layout.addLayout(self.selector_layout)

        # --- GRAFIK REAL-TIME ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True)
        self.layout.addWidget(self.plot_widget)

        # Buffer penampung data untuk grafik berjalan (Windowing effect)
        self.max_samples = 400
        self.display_buffer = np.zeros(self.max_samples)
        self.curve = self.plot_widget.plot(
            self.display_buffer, pen=pg.mkPen('g', width=2))

        # Set tema label awal grafik
        self.on_hardware_selection_changed()

        # Label Info Status Parameter Teknis seluruh komponen di bagian paling bawah
        self.info_label = QtWidgets.QLabel(
            "Status Hardware: Menghubungkan sirkuit simulasi...")
        self.info_label.setStyleSheet(
            "font-family: monospace; font-size: 12px; color: #ffffff; background-color: #222222; padding: 10px;")
        self.layout.addWidget(self.info_label)

        # Timer untuk memicu loop update data real-time (~50 Hz sampling rate)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.run_hardware_pipeline)
        self.timer.start()

    def on_hardware_selection_changed(self):
        """Mengubah label nama grafik dan satuan di sumbu Y sesuai pilihan user"""
        selected_index = self.combo_hardware.currentIndex()

        if selected_index == 0:
            self.plot_widget.setTitle(
                "Grafik Estimasi Tekanan Darah Terkalibrasi")
            self.plot_widget.setLabel('left', 'Tekanan', units='mmHg')
            self.curve.setPen(pg.mkPen('#00FF00', width=2))  # Hijau
        elif selected_index == 1:
            self.plot_widget.setTitle(
                "Grafik Output Tegangan Jembatan Sensor MPS20N0040D")
            self.plot_widget.setLabel('left', 'Tegangan Sensor', units='mV')
            self.curve.setPen(pg.mkPen('#00FFFF', width=2))  # Cyan
        elif selected_index == 2:
            self.plot_widget.setTitle(
                "Grafik Tegangan Hasil Penguatan & Offset Sirkuit AFE (AD620 + TLC2272)")
            self.plot_widget.setLabel('left', 'Tegangan Masuk ADC', units='V')
            self.curve.setPen(pg.mkPen('#FFCC00', width=2))  # Kuning/Emas
        elif selected_index == 3:
            self.plot_widget.setTitle(
                "Grafik Nilai Kuantisasi Digital MCU STM32F411")
            self.plot_widget.setLabel(
                'left', 'Nilai ADC Mentah (12-bit)', units='raw')
            self.curve.setPen(pg.mkPen('#FF3333', width=2))  # Merah

    def run_hardware_pipeline(self):
        """Menjalankan aliran data sirkuit berantai dan memilah data mana yang mau diplot"""

        # 1. Aliran Sirkuit: Sensor menghasilkan miliVolt
        sensor_output_mv = self.sensor.get_bridge_output_mv()

        # 2. Aliran Sirkuit: AFE memperkuat & memberi offset
        afe_output_v = self.afe.process_signal(sensor_output_mv)

        # 3. Aliran Sirkuit: STM32 mengubah menjadi data ADC digital
        mcu_adc_value = self.mcu.read_adc(afe_output_v)

        # 4. Aliran Aplikasi: Menghitung ulang nilai konversi medis ke mmHg
        v_from_adc = (mcu_adc_value / self.mcu.adc_resolution) * self.mcu.v_ref
        v_recovered_from_offset = v_from_adc - self.afe.offset_v
        mv_recovered_from_gain = (
            v_recovered_from_offset / self.afe.gain_ad620) * 1000
        calculated_pressure_mmHg = max(
            0.0, (mv_recovered_from_gain / 50.0) * 300.0)

        # --- SELEKSI DATA YANG AKAN DIALIRKAN KE GRAFIK ---
        selected_index = self.combo_hardware.currentIndex()
        if selected_index == 0:
            current_value = calculated_pressure_mmHg
        elif selected_index == 1:
            current_value = sensor_output_mv
        elif selected_index == 2:
            current_value = afe_output_v
        elif selected_index == 3:
            current_value = mcu_adc_value

        # Perbarui data buffer grafik berjalan
        self.display_buffer[:-1] = self.display_buffer[1:]
        self.display_buffer[-1] = current_value
        self.curve.setData(self.display_buffer)

        # Selalu tampilkan status teknis lengkap di bagian bawah sebagai alat pantau perbandingan hardware
        self.info_label.setText(
            f"[HW-1 SENSOR] Output Bridge      : {sensor_output_mv:6.2f} mV\n"
            f"[HW-2 AFE   ] Output Amp+Offset  : {afe_output_v:4.2f} V\n"
            f"[HW-3 STM32 ] Pembacaan ADC      : {mcu_adc_value:4d} (12-bit)\n"
            f"[APLIKASI   ] Hasil Akhir Sistem : {calculated_pressure_mmHg:5.1f} mmHg"
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = CuffnCodeDashboard()
    main_window.show()
    sys.exit(app.exec_())
