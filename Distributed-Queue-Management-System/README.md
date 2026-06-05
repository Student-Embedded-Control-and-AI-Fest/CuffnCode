# Distributed Queue Management System

Simulasi Komputasi Paralel Menggunakan Python Flask dan Multiprocessing

## Deskripsi

Aplikasi ini mensimulasikan sistem manajemen antrian terdistribusi dengan menggunakan Python Flask sebagai backend dan multiprocessing untuk parallelisasi tugas.

## Fitur

- Simulasi distribusi tugas ke multiple workers
- Perhitungan Speed Up dan Efficiency
- Real-time monitoring status worker
- Dashboard interaktif dengan Bootstrap 5

## Requirements

- Python 3.7+
- Flask 3.1.1

## Instalasi

1. Clone repository ini:
```bash
git clone <repository-url>
cd Distributed-Queue-Management-System
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Penggunaan

Jalankan aplikasi Flask:
```bash
python app.py
```

Buka browser dan akses `http://127.0.0.1:5000`

## Struktur Direktori

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── script.js       # Frontend JavaScript
│   └── style.css       # Frontend CSS
├── templates/
│   └── index.html      # HTML template
└── README.md          # This file
```

## Cara Kerja

1. Pengguna menginputkan jumlah tugas dan jumlah worker
2. Sistem mendistribusikan tugas ke workers secara paralel
3. Setiap worker memproses tugasnya secara concurrent
4. Hasil ditampilkan dengan metrik performa (Speed Up, Efficiency)

## Metrik Performa

- **Speed Up**: Perbandingan waktu eksekusi serial vs paralel
- **Efficiency**: Efisiensi penggunaan worker terhadap speed up
- **Execution Time**: Waktu total eksekusi paralel

## Lisensi

MIT
