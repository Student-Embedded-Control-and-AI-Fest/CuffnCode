# Smart Traffic Simulator (Lite Version)
**Tugas Evaluasi 3 - Komputasi Paralel & Sistem Terdistribusi**
**Kelompok: 152024139 ADITYA LUTHFI, 152024149 BAIHAQI FATHUROHAMAN **

## Deskripsi Sistem
Proyek ini adalah simulasi manajemen lalu lintas pintar yang menggunakan arsitektur **Distributed Systems** dan **Parallel Computing**. Untuk menjaga performa tetap ringan dan cepat, sistem ini dibangun menggunakan antarmuka Command Line (CLI).

## Arsitektur (2-Node Pipeline)
Sistem ini memecah beban kerja menjadi 2 proses OS yang berjalan secara paralel (bersamaan) menggunakan modul `multiprocessing` bawaan Python.
1. **Node 1 (Sensor/Akuisisi):** Berjalan di latar belakang, mensimulasikan tangkapan kamera jalanan untuk menghitung jumlah kendaraan secara *real-time*.
2. **Node 2 (Controller/HMI):** Mengambil data secara asinkron, menghitung algoritma penentuan durasi lampu hijau, dan merender *dashboard* di terminal.

## Komunikasi Antar Proses (IPC)
Kedua node terisolasi dan bertukar data menggunakan mekanisme *Message Passing* melalui `multiprocessing.Queue`. Hal ini mencegah *race condition* dan menjamin keamanan *memory sharing*.

## Cara Menjalankan
Buka terminal dan jalankan:
`python lite_traffic.py`
(Gunakan `Ctrl+C` untuk mematikan sistem).