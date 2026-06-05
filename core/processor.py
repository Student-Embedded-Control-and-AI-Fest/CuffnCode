import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

class VideoProcessorThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage, float)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0) # Embedded I/O
        while self._run_flag:
            start_time = time.time()
            ret, frame = cap.read()
            
            if ret:
                # Komputasi Paralel (Pengolahan matriks piksel)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                
                fps = 1.0 / (time.time() - start_time)
                
                h, w, ch = edges_bgr.shape
                bytes_per_line = ch * w
                qt_img = QImage(edges_bgr.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_img = qt_img.scaled(640, 480, Qt.KeepAspectRatio)
                
                self.change_pixmap_signal.emit(scaled_img, fps)
            time.sleep(0.01)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()