"""
workers.py
==========
Module untuk Worker yang menganalisis data monitoring secara paralel.

Terdapat 3 jenis worker yang masing-masing berjalan sebagai process terpisah:
1. CPUWorker     - Menganalisis CPU Usage
2. RAMWorker     - Menganalisis RAM Usage
3. NetworkWorker - Menganalisis Network Traffic

Ini adalah implementasi dari konsep KOMPUTASI PARALEL dimana
beberapa worker berjalan BERSAMAAN (simultan) sebagai process
terpisah untuk mempercepat pemrosesan data.
"""

import os
import time


class BaseWorker:
    """
    Kelas dasar (base class) untuk semua Worker.

    Worker bertanggung jawab menerima data dari Master Server,
    melakukan analisis berdasarkan threshold yang ditentukan,
    dan mengirimkan hasil analisis kembali ke Master Server.

    Pola yang digunakan adalah Worker Pool pattern dalam komputasi paralel:
    - Master Server mendistribusikan tugas ke worker-worker
    - Setiap worker memproses tugas secara independen
    - Hasil dikembalikan ke Master Server untuk ditampilkan

    Attributes:
        name (str): Nama worker (CPU, RAM, atau NETWORK)
        input_queue (multiprocessing.Queue): Queue untuk menerima data dari Master
        output_queue (multiprocessing.Queue): Queue untuk mengirim hasil ke Master
        warning_threshold (int): Batas bawah status WARNING
        critical_threshold (int): Batas bawah status CRITICAL
    """

    def __init__(self, name, input_queue, output_queue, warning_threshold, critical_threshold):
        """
        Inisialisasi worker.

        Args:
            name (str): Nama worker
            input_queue: Queue untuk menerima data dari Master Server
            output_queue: Queue untuk mengirim hasil analisis ke Master Server
            warning_threshold (int): Nilai threshold untuk status WARNING
            critical_threshold (int): Nilai threshold untuk status CRITICAL
        """
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def analyze(self, value):
        """
        Menganalisis nilai berdasarkan threshold.

        Logika analisis:
        - Jika nilai < warning_threshold  -> NORMAL
        - Jika nilai < critical_threshold  -> WARNING
        - Selain itu                      -> CRITICAL

        Args:
            value (int): Nilai yang akan dianalisis

        Returns:
            str: Status hasil analisis ("NORMAL", "WARNING", atau "CRITICAL")
        """
        if value < self.warning_threshold:
            return "NORMAL"
        elif value < self.critical_threshold:
            return "WARNING"
        else:
            return "CRITICAL"

    def run(self):
        """
        Method utama worker - berjalan sebagai process terpisah.

        Alur kerja worker:
        1. Menampilkan PID worker (menunjukkan process terpisah)
        2. Loop forever:
           a. Menerima data dari Master Server via Queue (blocking)
           b. Melakukan analisis berdasarkan threshold
           c. Mengirim hasil analisis ke Master Server via Queue

        Setiap worker berjalan sebagai process multiprocessing terpisah,
        sehingga CPUWorker, RAMWorker, dan NetworkWorker berjalan
        SECARA PARALEL (bersamaan) - inilah inti dari Komputasi Paralel.
        """
        pid = os.getpid()
        print(f"[{self.name} WORKER] PID: {pid}")

        while True:
            try:
                # Menerima data dari Master Server
                # Method get() bersifat blocking - akan menunggu sampai ada data
                data = self.input_queue.get()

                node_name = data['node']
                value = data['value']

                # Melakukan analisis data
                status = self.analyze(value)

                # Mengirim hasil analisis kembali ke Master Server
                result = {
                    'node': node_name,
                    'metric': self.name,
                    'value': value,
                    'status': status,
                }
                self.output_queue.put(result)

            except Exception as e:
                # Error handling sederhana
                print(f"[{self.name} WORKER] Error: {e}")
                time.sleep(0.1)


class CPUWorker(BaseWorker):
    """
    Worker khusus untuk menganalisis CPU Usage.

    Threshold CPU Usage:
    --------------------------------------------------
    | Kondisi    | Rentang        | Status          |
    --------------------------------------------------
    | Normal     | < 50%          | NORMAL          |
    | Warning    | 50% - 80%      | WARNING         |
    | Critical   | > 80%          | CRITICAL        |
    --------------------------------------------------

    CPU yang terlalu tinggi (>80%) menandakan server kelebihan beban
    dan perlu segera ditangani.
    """

    def __init__(self, input_queue, output_queue):
        # Threshold CPU: warning di 50%, critical di 81% (>80%)
        super().__init__("CPU", input_queue, output_queue, 50, 81)


class RAMWorker(BaseWorker):
    """
    Worker khusus untuk menganalisis RAM Usage.

    Threshold RAM Usage:
    --------------------------------------------------
    | Kondisi    | Rentang        | Status          |
    --------------------------------------------------
    | Normal     | < 70%          | NORMAL          |
    | Warning    | 70% - 90%      | WARNING         |
    | Critical   | > 90%          | CRITICAL        |
    --------------------------------------------------

    RAM yang hampir penuh (>90%) dapat menyebabkan server
    kehabisan memori dan crash.
    """

    def __init__(self, input_queue, output_queue):
        # Threshold RAM: warning di 70%, critical di 91% (>90%)
        super().__init__("RAM", input_queue, output_queue, 70, 91)


class NetworkWorker(BaseWorker):
    """
    Worker khusus untuk menganalisis Network Traffic.

    Threshold Network Traffic:
    --------------------------------------------------
    | Kondisi    | Rentang (Mbps) | Status          |
    --------------------------------------------------
    | Normal     | < 500          | NORMAL          |
    | Warning    | 500 - 800      | WARNING         |
    | Critical   | > 800          | CRITICAL        |
    --------------------------------------------------

    Network traffic yang sangat tinggi (>800 Mbps) menandakan
    kemungkinan serangan DDoS atau bottleneck jaringan.
    """

    def __init__(self, input_queue, output_queue):
        # Threshold Network: warning di 500 Mbps, critical di 801 Mbps (>800)
        super().__init__("NETWORK", input_queue, output_queue, 500, 801)
