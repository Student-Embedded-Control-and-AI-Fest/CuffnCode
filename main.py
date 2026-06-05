import sys
from PyQt5.QtWidgets import QApplication
from core.processor import VideoProcessorThread
from ui.main_window import AppWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Jalankan mesin komputasi paralel di latar belakang
    processor_thread = VideoProcessorThread()
    processor_thread.start()
    
    # 2. Jalankan GUI dan masukkan mesin tadi ke dalamnya
    window = AppWindow(processor_thread)
    window.show()
    
    sys.exit(app.exec_())