"""
datacenter_node.py
==================
Module untuk Data Center Node dalam sistem monitoring terdistribusi.

Setiap node merepresentasikan sebuah Data Center yang menghasilkan
data server secara acak (CPU, RAM, Network) dan mengirimkannya
ke Master Server melalui Queue.

Ini adalah implementasi dari konsep SISTEM TERDISTRIBUSI dimana
setiap node berjalan sebagai process independen dan berkomunikasi
melalui message passing (multiprocessing.Queue).
"""

import random
import time
import os


# ============================================================
# Daftar Data Center yang akan dimonitoring
# ============================================================
# Setiap entry adalah nama node dalam sistem terdistribusi
DATA_CENTERS = [
    "Jakarta Data Center",
    "Bandung Data Center",
    "Surabaya Data Center",
    "Bali Data Center"
]


class DataCenterNode:
    """
    Kelas yang merepresentasikan sebuah node Data Center.

    Sebuah node Data Center bertugas untuk:
    1. Menghasilkan data monitoring server secara acak (simulasi)
    2. Mengirimkan data tersebut ke Master Server secara periodik

    Setiap node berjalan sebagai process multiprocessing terpisah,
    sehingga seluruh node berjalan secara independen dan simultan
    layaknya sistem terdistribusi sesungguhnya.

    Attributes:
        name (str): Nama Data Center (contoh: "Jakarta Data Center")
        data_queue (multiprocessing.Queue): Queue untuk komunikasi dengan Master Server
    """

    def __init__(self, name, data_queue):
        """
        Inisialisasi node Data Center.

        Args:
            name (str): Nama Data Center
            data_queue (multiprocessing.Queue): Queue untuk mengirim data ke Master Server
        """
        self.name = name
        self.data_queue = data_queue

    def generate_data(self):
        """
        Menghasilkan data monitoring server secara acak.

        Data yang dihasilkan mensimulasikan kondisi server riil:
        - CPU Usage: Persentase penggunaan CPU (10% - 100%)
        - RAM Usage: Persentase penggunaan RAM (20% - 100%)
        - Network Traffic: Throughput jaringan dalam Mbps (50 - 1000)

        Returns:
            dict: Dictionary berisi data monitoring dengan format:
                  {'node': str, 'cpu': int, 'ram': int, 'network': int}
        """
        data = {
            'node': self.name,
            'cpu': random.randint(10, 100),      # CPU Usage dalam persen
            'ram': random.randint(20, 100),       # RAM Usage dalam persen
            'network': random.randint(50, 1000),  # Network Traffic dalam Mbps
        }
        return data

    def run(self):
        """
        Method utama yang dijalankan sebagai process terpisah.

        Method ini akan berjalan dalam loop forever:
        1. Menampilkan informasi node beserta PID-nya
        2. Generate data server secara acak
        3. Mengirim data ke Master Server via Queue
        4. Menunggu beberapa detik sebelum iterasi berikutnya

        Queue digunakan sebagai mekanisme komunikasi antar process (IPC)
        untuk mengirim data dari node ke Master Server.
        """
        pid = os.getpid()
        print(f"[NODE {self.name}] PID: {pid} - ONLINE")

        while True:
            # Generate data server acak
            data = self.generate_data()

            # Kirim data ke Master Server melalui multiprocessing.Queue
            # Ini adalah bentuk komunikasi antar process (Inter-Process Communication)
            self.data_queue.put(data)

            # Interval pengiriman data: 2-4 detik (bervariasi per node)
            # Ini membuat setiap node mengirim data pada waktu yang berbeda
            time.sleep(random.uniform(2, 4))
