| NRP       | Nama                  |
|-----------|-----------------------|
| 152024007 | Harpan                |
| 152024057 | Shouqi Haz Yanuar     |
| 152024058 | Yuddha Wastu Pramukha |

**Mata Kuliah**: Komputasi Paralel dan Sistem Terdistribusi

**Informatika** - Itenas

---

# Distributed Data Center Monitoring System

## Deskripsi Project

**Distributed Data Center Monitoring System** adalah program simulasi berbasis Python yang memonitoring 4 Data Center (Jakarta, Bandung, Surabaya, Bali) secara real-time melalui terminal. Program ini didesain untuk memperlihatkan konsep **Komputasi Paralel** dan **Sistem Terdistribusi** dengan cara yang sederhana dan mudah dipahami.

Setiap node Data Center menghasilkan data server acak (CPU Usage, RAM Usage, Network Traffic) dan mengirimkannya ke Master Server. Master Server kemudian mendistribusikan data tersebut ke worker-worker yang berjalan secara paralel untuk dianalisis. Hasil monitoring ditampilkan secara real-time di terminal.

## Tujuan Project

1. Memahami konsep **Komputasi Paralel** dengan multiprocessing Python
2. Memahami konsep **Sistem Terdistribusi** dengan komunikasi antar process
3. Mengimplementasikan message passing menggunakan multiprocessing.Queue
4. Menampilkan proses monitoring secara real-time dengan visualisasi terminal
5. Menunjukkan perbedaan process ID (PID) setiap process yang berjalan

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER SERVER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ CPU Worker  │  │ RAM Worker  │  │ Net Worker  │         │
│  │  (Paralel)  │  │  (Paralel)  │  │  (Paralel)  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                 │                 │               │
│  ┌──────┴─────────────────┴─────────────────┴──────┐        │
│  │              Master Server (Coordinator)         │        │
│  └──────┬─────────────────┬─────────────────┬──────┘        │
│         │                 │                 │               │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐        │
│  │  Jakarta DC │  │  Bandung DC │  │ Surabaya DC │ Bali DC │
│  │ (Distribusi)│  │ (Distribusi)│  │ (Distribusi)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Komponen Sistem

| Komponen | Jumlah | Fungsi |
|----------|--------|--------|
| Master Server | 1 | Koordinator utama sistem |
| Data Center Node | 4 | Menghasilkan data server |
| CPU Worker | 1 | Menganalisis CPU Usage |
| RAM Worker | 1 | Menganalisis RAM Usage |
| Network Worker | 1 | Menganalisis Network Traffic |

## Implementasi Komputasi Paralel

Komputasi Paralel diimplementasikan menggunakan **multiprocessing** dari Python standard library.

### Cara Kerja

1. **CPUWorker**, **RAMWorker**, dan **NetworkWorker** dibuat sebagai instance dari kelas turunan `BaseWorker`
2. Setiap worker dijalankan sebagai **Process** terpisah menggunakan `multiprocessing.Process`
3. Ketiga worker berjalan BERSAMAAN (simultan) setelah method `.start()` dipanggil
4. Setiap worker memiliki **input queue** dan **output queue** sendiri untuk komunikasi dengan Master Server
5. Master Server mendistribusikan data ke worker yang sesuai melalui queue masing-masing

### Kode Utama

```python
# Membuat process untuk setiap worker
cpu_process = multiprocessing.Process(target=cpu_worker.run)
ram_process = multiprocessing.Process(target=ram_worker.run)
network_process = multiprocessing.Process(target=network_worker.run)

# Menjalankan semua worker secara paralel
cpu_process.start()
ram_process.start()
network_process.start()
```

### Analisis Paralel

Setiap worker menganalisis data secara independen dengan threshold masing-masing:

| Metrik | NORMAL | WARNING | CRITICAL |
|--------|--------|---------|----------|
| CPU | < 50% | 50% - 80% | > 80% |
| RAM | < 70% | 70% - 90% | > 90% |
| Network | < 500 Mbps | 500 - 800 Mbps | > 800 Mbps |

## Implementasi Sistem Terdistribusi

Sistem Terdistribusi diimplementasikan dengan setiap node Data Center berjalan sebagai **Process** terpisah dan berkomunikasi menggunakan **multiprocessing.Queue**.

### Cara Kerja

1. Terdapat **4 node** Data Center: Jakarta, Bandung, Surabaya, Bali
2. Setiap node berjalan sebagai **Process** independen
3. Node menghasilkan data monitoring secara acak dan periodik
4. Data dikirim ke Master Server melalui **Queue** (message passing)
5. Master Server menerima data dan mendistribusikannya ke worker

### Kode Utama

```python
# Membuat process untuk setiap node
node = DataCenterNode(dc_name, data_queue)
process = multiprocessing.Process(target=node.run)

# Menjalankan node (setiap node independen)
process.start()
```

### Komunikasi Antar Process

```
Node Jakarta ──Queue──> Master Server ──Queue──> CPU Worker
                    │                       └──> RAM Worker
                    │                       └──> Network Worker
                    │
Node Bandung ──Queue──> Master Server <──Queue── Workers (results)
Node Surabaya ──Queue─┘
Node Bali ──────Queue─┘
```

### Keunggulan Sistem Terdistribusi

- **Independence**: Setiap node berjalan tanpa bergantung pada node lain
- **Scalability**: Node baru dapat ditambahkan dengan mudah
- **Fault Tolerance**: Kegagalan satu node tidak mempengaruhi node lain
- **Communication**: Menggunakan Queue untuk komunikasi yang aman antar process

## Cara Menjalankan Program

### Persyaratan

- Python 3.x
- Tidak memerlukan library eksternal (hanya menggunakan standard library)

### Langkah-langkah

```bash
# Masuk ke direktori project
cd DistributedDataCenterMonitoring

# Jalankan program
python main.py
```

### Menghentikan Program

Tekan **Ctrl+C** pada keyboard untuk menghentikan program.

## Contoh Output

```
==================================================
DISTRIBUTED DATA CENTER MONITORING SYSTEM
==================================================

[MASTER SERVER] ONLINE (PID: 12345)
Starting workers...
[CPU WORKER] PID: 12346
[RAM WORKER] PID: 12347
[NETWORK WORKER] PID: 12348

Starting Data Center nodes...
[NODE Jakarta Data Center] PID: 12349 - ONLINE
[NODE Bandung Data Center] PID: 12350 - ONLINE
[NODE Surabaya Data Center] PID: 12351 - ONLINE
[NODE Bali Data Center] PID: 12352 - ONLINE

---
## NODE : Jakarta Data Center

CPU Usage     : 92%
RAM Usage     : 75%
Network Load  : 350 Mbps

CPU Status    : CRITICAL
RAM Status    : WARNING
Network Status: NORMAL

OVERALL STATUS: CRITICAL

---
## NODE : Bandung Data Center

CPU Usage     : 35%
RAM Usage     : 48%
Network Load  : 120 Mbps

CPU Status    : NORMAL
RAM Status    : NORMAL
Network Status: NORMAL

OVERALL STATUS: HEALTHY

---
## NODE : Surabaya Data Center

CPU Usage     : 67%
RAM Usage     : 85%
Network Load  : 650 Mbps

CPU Status    : WARNING
RAM Status    : WARNING
Network Status: WARNING

OVERALL STATUS: WARNING

---
## NODE : Bali Data Center

CPU Usage     : 45%
RAM Usage     : 55%
Network Load  : 200 Mbps

CPU Status    : NORMAL
RAM Status    : NORMAL
Network Status: NORMAL

OVERALL STATUS: HEALTHY

==================================================
Press Ctrl+C to stop monitoring
==================================================
```

---
