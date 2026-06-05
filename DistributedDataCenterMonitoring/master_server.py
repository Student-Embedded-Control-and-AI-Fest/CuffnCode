"""
master_server.py
================
Module untuk Master Server yang mengkoordinasikan seluruh sistem.

Master Server adalah pusat koordinasi yang:
1. Menerima data dari seluruh node Data Center (Sistem Terdistribusi)
2. Mendistribusikan data ke worker-worker (Komputasi Paralel)
3. Mengumpulkan dan menampilkan hasil monitoring secara real-time

 Master Server
 ┌──────────────────────────────────────────────────┐
 │                                                  │
 │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
 │  │CPU Worker│  │RAM Worker│  │Net Worker│       │
 │  │ (Proc 1) │  │ (Proc 2) │  │ (Proc 3) │       │
 │  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
 │       │              │              │            │
 │  ┌────┴──────────────┴──────────────┴────┐       │
 │  │          Master Server (Proc 0)       │       │
 │  └────┬──────────────┬──────────────┬────┘       │
 │       │              │              │            │
 │  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐       │
 │  │Jakarta   │  │Bandung   │  │Surabaya  │  Bali │
 │  │DC (Proc) │  │DC (Proc) │  │DC (Proc) │ (Proc)│
 │  └──────────┘  └──────────┘  └──────────┘       │
 │                                                  │
 └──────────────────────────────────────────────────┘
"""

import os
import sys
import time
import queue
import multiprocessing
from datacenter_node import DataCenterNode, DATA_CENTERS
from workers import CPUWorker, RAMWorker, NetworkWorker


class MasterServer:
    """
    Master Server - Pusat koordinasi sistem monitoring terdistribusi.

    Master Server memiliki beberapa tanggung jawab utama:

    1. SISTEM TERDISTRIBUSI:
       - Menerima data dari 4 node Data Center yang berjalan independen
       - Setiap node berjalan sebagai process terpisah
       - Komunikasi menggunakan multiprocessing.Queue (message passing)

    2. KOMPUTASI PARALEL:
       - Mendistribusikan data ke 3 worker yang berjalan paralel
       - CPUWorker, RAMWorker, NetworkWorker berjalan simultan
       - Mempercepat proses analisis data

    3. MONITORING REAL-TIME:
       - Menampilkan hasil monitoring secara periodik
       - Setiap node menampilkan status CPU, RAM, Network
       - Menampilkan overall status (HEALTHY / WARNING / CRITICAL)

    Attributes:
        data_queue (multiprocessing.Queue): Queue dari nodes -> master
        cpu_queue (multiprocessing.Queue): Queue master -> CPU worker
        ram_queue (multiprocessing.Queue): Queue master -> RAM worker
        network_queue (multiprocessing.Queue): Queue master -> Network worker
        result_queue (multiprocessing.Queue): Queue workers -> master
        node_status (dict): Status terkini setiap node
        processes (list): Daftar process untuk cleanup
    """

    def __init__(self):
        """
        Inisialisasi Master Server.

        Membuat semua Queue yang digunakan untuk komunikasi antar process
        dan menginisialisasi struktur data untuk menyimpan status node.
        """
        # ---------------------------------------------------------------
        # Queue untuk komunikasi antar process (Inter-Process Communication)
        # ---------------------------------------------------------------
        # Queue dari node Data Center ke Master Server
        # Berisi data mentah dari setiap node
        self.data_queue = multiprocessing.Queue()

        # Queue dari Master Server ke worker-worker
        # Masing-masing worker memiliki queue sendiri
        self.cpu_queue = multiprocessing.Queue()       # Data untuk CPU Worker
        self.ram_queue = multiprocessing.Queue()       # Data untuk RAM Worker
        self.network_queue = multiprocessing.Queue()   # Data untuk Network Worker

        # Queue dari worker-worker ke Master Server (hasil analisis)
        self.result_queue = multiprocessing.Queue()

        # ---------------------------------------------------------------
        # Status terkini setiap node
        # ---------------------------------------------------------------
        # Dictionary untuk menyimpan data monitoring terakhir setiap node
        self.node_status = {}
        for name in DATA_CENTERS:
            self.node_status[name] = {
                'cpu_value': '---',
                'ram_value': '---',
                'network_value': '---',
                'cpu_status': '---',
                'ram_status': '---',
                'network_status': '---',
                'overall': '---'
            }

        # Timer untuk display interval (supaya tidak refresh tiap kali data masuk)
        self.last_display_time = 0
        self.display_interval = 3  # Refresh tampilan setiap 3 detik

        # Daftar semua process untuk keperluan cleanup saat shutdown
        self.processes = []

    def start_workers(self):
        """
        Membuat dan menjalankan worker processes secara PARALEL.

        Tiga worker akan dibuat dan dijalankan sebagai process terpisah:
        - CPUWorker: Menganalisis CPU Usage
        - RAMWorker: Menganalisis RAM Usage
        - NetworkWorker: Menganalisis Network Traffic

        Ketiga worker berjalan BERSAMAAN (paralel) karena masing-masing
        adalah process independen yang dijalankan dengan .start().
        Inilah inti dari implementasi Komputasi Paralel.
        """
        print("Starting workers...")
        time.sleep(0.3)

        # Buat instance masing-masing worker
        cpu_worker = CPUWorker(self.cpu_queue, self.result_queue)
        ram_worker = RAMWorker(self.ram_queue, self.result_queue)
        network_worker = NetworkWorker(self.network_queue, self.result_queue)

        # Buat Process untuk setiap worker
        # target=method run dari worker
        cpu_process = multiprocessing.Process(target=cpu_worker.run)
        ram_process = multiprocessing.Process(target=ram_worker.run)
        network_process = multiprocessing.Process(target=network_worker.run)

        # Simpan process untuk cleanup nanti
        self.processes.extend([cpu_process, ram_process, network_process])

        # ---------------------------------------------------------------
        # JALANKAN SEMUA WORKER SECARA PARALEL
        # ---------------------------------------------------------------
        # method .start() akan menjalankan process secara asynchronous
        # Ketiga worker mulai berjalan BERSAMAAN di sini
        cpu_process.start()
        ram_process.start()
        network_process.start()

    def start_nodes(self):
        """
        Membuat dan menjalankan node Data Center processes.

        Setiap Data Center (Jakarta, Bandung, Surabaya, Bali) berjalan
        sebagai process multiprocessing terpisah. Masing-masing node
        secara independen menghasilkan data dan mengirimkannya ke
        Master Server melalui Queue.

        Inilah implementasi dari konsep SISTEM TERDISTRIBUSI:
        - Banyak node berjalan secara independen
        - Setiap node memiliki tugas spesifik (menghasilkan data)
        - Node-node berkomunikasi dengan pusat (Master Server)
        - Jika satu node mati, node lain tetap berjalan
        """
        print("Starting Data Center nodes...")
        time.sleep(0.3)

        for dc_name in DATA_CENTERS:
            # Buat instance node Data Center
            node = DataCenterNode(dc_name, self.data_queue)

            # Buat Process untuk node ini
            process = multiprocessing.Process(target=node.run)

            # Simpan ke daftar process
            self.processes.append(process)

            # Jalankan node (setiap node berjalan sebagai process terpisah)
            process.start()

    def distribute_data(self, data):
        """
        Mendistribusikan data dari node ke worker yang sesuai.

        Setiap data dari node berisi 3 metrik (CPU, RAM, Network).
        Master Server memisahkan data tersebut dan mengirimkan
        masing-masing metrik ke worker yang berkompeten.

        Contoh:
        Data masuk: {'node': 'Jakarta', 'cpu': 92, 'ram': 75, 'network': 350}
        Distribusi:
          -> CPU Queue     : {'node': 'Jakarta', 'value': 92}
          -> RAM Queue     : {'node': 'Jakarta', 'value': 75}
          -> Network Queue : {'node': 'Jakarta', 'value': 350}

        Args:
            data (dict): Data dari node (berisi node, cpu, ram, network)
        """
        node_name = data['node']

        # Kirim data CPU ke CPU Worker
        self.cpu_queue.put({'node': node_name, 'value': data['cpu']})

        # Kirim data RAM ke RAM Worker
        self.ram_queue.put({'node': node_name, 'value': data['ram']})

        # Kirim data Network ke Network Worker
        self.network_queue.put({'node': node_name, 'value': data['network']})

    def collect_results(self):
        """
        Mengumpulkan hasil analisis dari worker-worker.

        Method ini membaca semua hasil yang tersedia di result_queue
        secara non-blocking (menggunakan timeout). Hasil dari worker
        digunakan untuk memperbarui status node yang bersangkutan.

        Worker mengirimkan hasil dalam format:
        {'node': 'Jakarta', 'metric': 'CPU', 'value': 92, 'status': 'CRITICAL'}
        """
        while True:
            try:
                # Coba ambil hasil dari queue (timeout 0.1 detik)
                # Jika tidak ada data dalam 0.1 detik, raise queue.Empty
                result = self.result_queue.get(timeout=0.1)

                node = result['node']
                metric = result['metric']
                value = result['value']
                status = result['status']

                # Update status node berdasarkan metrik
                if node in self.node_status:
                    if metric == 'CPU':
                        self.node_status[node]['cpu_value'] = value
                        self.node_status[node]['cpu_status'] = status
                    elif metric == 'RAM':
                        self.node_status[node]['ram_value'] = value
                        self.node_status[node]['ram_status'] = status
                    elif metric == 'NETWORK':
                        self.node_status[node]['network_value'] = value
                        self.node_status[node]['network_status'] = status

                    # Hitung overall status node
                    self.update_overall_status(node)

            except:
                # Tidak ada data di queue, keluar dari loop
                break

    def update_overall_status(self, node_name):
        """
        Menghitung status keseluruhan (overall) sebuah node.

        Logika penentuan overall status:
        - CRITICAL : Jika minimal satu metrik berstatus CRITICAL
        - WARNING  : Jika minimal satu metrik berstatus WARNING (dan tidak ada CRITICAL)
        - HEALTHY  : Jika semua metrik berstatus NORMAL
        - '---'    : Jika masih ada metrik yang belum terisi

        Args:
            node_name (str): Nama node yang akan dihitung overall status-nya
        """
        status = self.node_status[node_name]

        # Ambil status masing-masing metrik
        cpu_s = status['cpu_status']
        ram_s = status['ram_status']
        net_s = status['network_status']

        # Jika masih ada metrik yang belum terdata, skip
        if '---' in [cpu_s, ram_s, net_s]:
            return

        # Kumpulkan semua status
        statuses = [cpu_s, ram_s, net_s]

        # Tentukan overall status berdasarkan prioritas
        if 'CRITICAL' in statuses:
            status['overall'] = 'CRITICAL'
        elif 'WARNING' in statuses:
            status['overall'] = 'WARNING'
        elif all(s == 'NORMAL' for s in statuses):
            status['overall'] = 'HEALTHY'
        else:
            status['overall'] = '---'

    def display_startup_screen(self):
        print()
        print("=== Distributed Data Center Monitoring ===")
        print()
        print(f"[Master Server] Online (PID: {os.getpid()})")
        print()
        print("-- TERDISTRIBUSI --------------------------------")
        print("4 Data Center node jalan sebagai process terpisah,")
        print("masing-masing kirim data ke server tiap 2-4 detik:")
        print("  - Jakarta DC")
        print("  - Bandung DC")
        print("  - Surabaya DC")
        print("  - Bali DC")
        print()
        print("-- PARALEL --------------------------------------")
        print("3 worker jalan bersamaan (parallel processing),")
        print("menganalisis data dari semua node:")
        print("  - CPU Worker")
        print("  - RAM Worker")
        print("  - Network Worker")
        print()
        print("Sistem siap -- mindahin data dari node ke worker, lalu di-display!")
        print()

    def display_results(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=== Distributed Data Center Monitoring ===")
        print()
        print(f"[Master Server] Running -- nerima data dari {len(DATA_CENTERS)} node, distribusi ke 3 worker")
        print()

        print("-- DISTRIBUTED -----------------------------------")
        print(f"{len(DATA_CENTERS)} node jalan sendiri-sendiri, kirim data real-time:")
        print()

        for node_name in DATA_CENTERS:
            status = self.node_status[node_name]
            has_data = status['cpu_value'] != '---'

            short_name = node_name.replace(" Data Center", "")
            print(f"-- {short_name} --")

            if has_data:
                print(f"  CPU     : {status['cpu_value']}%       -> {status['cpu_status']}")
                print(f"  RAM     : {status['ram_value']}%       -> {status['ram_status']}")
                print(f"  Network : {status['network_value']} Mbps -> {status['network_status']}")
                print("  " + "-" * 30)
                print(f"  Overall : {status['overall']}")
            else:
                print("  [Menunggu data dari node...]")

            print()

        print("-- PARALLEL -------------------------------------")
        print("3 worker jalan barengan menganalisis semua node:")
        print("  - CPU     : liat beban processor")
        print("  - RAM     : liat pemakaian memory")
        print("  - Network : liat traffic jaringan")
        print()
        print("[Ctrl+C buat berhenti]")

    def run(self):
        """
        Method utama untuk menjalankan Master Server.

        Alur lengkap sistem:
        =====================

        TAHAP 1: Inisialisasi
        ├── Tampilkan banner startup
        └── Tampilkan status Master Server

        TAHAP 2: Memulai Worker (KOMPUTASI PARALEL)
        ├── Buat CPUWorker, RAMWorker, NetworkWorker
        ├── Jalankan sebagai process terpisah
        └── Worker siap menerima data

        TAHAP 3: Memulai Node (SISTEM TERDISTRIBUSI)
        ├── Buat 4 node Data Center
        ├── Jalankan sebagai process terpisah
        └── Node mulai menghasilkan data

        TAHAP 4: Loop Monitoring (REAL-TIME)
        ├── Terima data dari node (via data_queue)
        ├── Distribusikan ke worker (via worker queues)
        ├── Kumpulkan hasil analisis (via result_queue)
        └── Tampilkan hasil monitoring
        """
        try:
            # ---------------------------------------------------------------
            # TAHAP 1: Tampilkan layar startup
            # ---------------------------------------------------------------
            self.display_startup_screen()

            # ---------------------------------------------------------------
            # TAHAP 2: Jalankan worker secara PARALEL
            # ---------------------------------------------------------------
            self.start_workers()
            time.sleep(0.5)
            print()

            # ---------------------------------------------------------------
            # TAHAP 3: Jalankan node secara TERDISTRIBUSI
            # ---------------------------------------------------------------
            self.start_nodes()
            time.sleep(0.5)

            # Tampilkan hasil pertama setelah semua siap
            self.display_results()

            # ---------------------------------------------------------------
            # TAHAP 4: Loop monitoring utama
            # ---------------------------------------------------------------
            while True:
                # Terima data dari node dengan timeout
                # Jika tidak ada data dalam 0.5 detik, lanjutkan (supaya timer display bisa dicek)
                try:
                    data = self.data_queue.get(timeout=0.5)
                    self.distribute_data(data)
                except queue.Empty:
                    pass

                # Kumpulkan hasil analisis dari worker (available)
                self.collect_results()

                # Tampilkan hasil hanya setiap interval tertentu (3 detik)
                now = time.time()
                if now - self.last_display_time >= self.display_interval:
                    self.display_results()
                    self.last_display_time = now

        except KeyboardInterrupt:
            # Tangani Ctrl+C untuk shutdown yang graceful
            print("\n[MASTER SERVER] SHUTTING DOWN...")
            self.cleanup()

    def cleanup(self):
        """
        Membersihkan dan menghentikan semua process dengan aman.

        Method ini akan:
        1. Menampilkan jumlah process yang akan dihentikan
        2. Menghentikan setiap process dengan .terminate()
        3. Menunggu process benar-benar berhenti dengan .join()
        4. Menampilkan pesan selesai

        Ini penting untuk memastikan tidak ada process zombie
        yang tertinggal setelah program selesai.
        """
        print(f"[MASTER SERVER] Terminating {len(self.processes)} processes...")

        for p in self.processes:
            if p.is_alive():
                # Terminate: menghentikan process secara paksa
                p.terminate()
                # Join: menunggu process benar-benar berhenti
                p.join(timeout=1)

        print("[MASTER SERVER] All processes terminated. Goodbye!")
        sys.exit(0)
