# Smart Parking System with Multithreading

## Deskripsi Proyek
Smart Parking System adalah simulasi sistem parkir sederhana yang dibuat menggunakan bahasa pemrograman Python. Program ini menerapkan konsep komputasi paralel menggunakan multithreading untuk mensimulasikan beberapa gerbang parkir yang bekerja secara bersamaan.

Pada simulasi ini terdapat:
- 2 Gerbang Masuk
- 1 Gerbang Keluar
- Kapasitas parkir maksimal 10 kendaraan
- Perhitungan slot parkir secara otomatis menggunakan mekanisme *thread locking* (`threading.Lock`) untuk mencegah *race condition*.

## Tujuan
Tujuan proyek ini adalah untuk memahami penerapan komputasi paralel menggunakan multithreading pada Python dalam simulasi sistem parkir real-time.

## Teknologi yang Digunakan
- Python 3
- Standard Library: `threading`, `time`, `random`

## Konsep Komputasi Paralel
Program menggunakan tiga thread yang berjalan secara bersamaan:
1. Thread Gerbang Masuk 1 (`Gerbang 1`)
2. Thread Gerbang Masuk 2 (`Gerbang 2`)
3. Thread Gerbang Keluar (`GERBANG KELUAR`)

Ketiga thread dijalankan secara paralel sehingga proses kendaraan masuk dan keluar dapat terjadi pada waktu yang bersamaan secara asinkron.

## Struktur Program
```text
mohammadzaky9-eng/CuffnCode/
│
├── smart_parking.py
└── README.md
