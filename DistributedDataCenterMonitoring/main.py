"""
Distributed Data Center Monitoring System
==========================================
Entry point program.

Program ini mensimulasikan sistem monitoring Data Center
terdistribusi dengan pemrosesan paralel menggunakan
multiprocessing Python.

Konsep yang diimplementasikan:
1. SISTEM TERDISTRIBUSI
   - 4 node Data Center berjalan sebagai process terpisah
   - Setiap node mengirim data ke Master Server via Queue
   - Node-node independen dan tidak saling mempengaruhi

2. KOMPUTASI PARALEL
   - 3 worker (CPU, RAM, Network) berjalan sebagai process terpisah
   - Worker menganalisis data secara simultan
   - Hasil analisis ditampilkan secara real-time

Cara menjalankan:
    python main.py
"""

from master_server import MasterServer


def main():
    """
    Fungsi utama program.

    Membuat instance MasterServer dan menjalankannya.
    Master Server akan mengkoordinasikan seluruh node
    dan worker dalam sistem monitoring.

    Alur:
    1. Master Server online
    2. Worker-worker mulai berjalan (paralel)
    3. Node-node Data Center mulai berjalan (terdistribusi)
    4. Monitoring berjalan terus menerus
    5. Tekan Ctrl+C untuk berhenti
    """
    master = MasterServer()
    master.run()


if __name__ == "__main__":
    main()
