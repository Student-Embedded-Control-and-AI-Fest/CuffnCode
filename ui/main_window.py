from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class AppWindow(QMainWindow):
    def __init__(self, processor_thread):
        super().__init__()
        self.thread = processor_thread # Menghubungkan thread yang dikirim dari main.py
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Embedded Parallel Computing GUI")
        self.setGeometry(100, 100, 700, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setText("Kamera Bersiap...")
        self.layout.addWidget(self.label_video)

        self.label_fps = QLabel("FPS: 0.0", self)
        self.label_fps.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.layout.addWidget(self.label_fps)

        self.btn_close = QPushButton("Keluar Aplikasi", self)
        self.btn_close.clicked.connect(self.close_application)
        self.layout.addWidget(self.btn_close)

        # Menghubungkan signal dari thread ke fungsi update gambar di UI
        self.thread.change_pixmap_signal.connect(self.update_image)

    def update_image(self, q_img, fps):
        self.label_video.setPixmap(QPixmap.fromImage(q_img))
        self.label_fps.setText(f"Performa Sistem: {fps:.2f} FPS")

    def close_application(self):
        self.thread.stop()
        self.close()