NRP	Nama
152024041	Rivaldi

Mata Kuliah: Komputasi Paralel dan Sistem Terdistribusi
Informatika - Itenas

# Parallel Image Processing

## Deskripsi Project
**Parallel Image Processing** adalah program yang mendemonstrasikan perbandingan kecepatan antara **Komputasi Sekuensial** (berurutan) dan **Komputasi Paralel** (bersamaan) dalam konteks pengolahan citra digital. Program ini memproses puluhan gambar (grayscale + blur) menggunakan Python, lalu membandingkan waktu eksekusi kedua metode.

Tugas pengolahan gambar dipilih karena termasuk **Embarrassingly Parallel** — setiap gambar dapat diproses secara independen tanpa perlu sinkronisasi, sehingga ideal untuk menunjukkan konsep parallel computing.

## Tujuan Project
- Memahami konsep **Komputasi Paralel** menggunakan `ProcessPoolExecutor` Python
- Membandingkan performa **sekuensial vs paralel** secara kuantitatif (speedup)
- Memahami **GIL (Global Interpreter Lock)** dan mengapa `ProcessPoolExecutor` lebih cocok untuk CPU-bound task
- Mengimplementasikan **image processing pipeline** (grayscale + blur) secara paralel
- Menampilkan analisis **speedup** dan efisiensi paralel

## Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────┐
│                      INPUT                                   │
│               ┌──────────────────────┐                       │
│               │    Folder images/     │                       │
│               │  (81 file .jpg/.png)  │                       │
│               └──────────┬───────────┘                       │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    PROGRAM UTAMA                         │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │          proses_satu_gambar()                      │  │ │
│  │  │  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────┐  │  │ │
│  │  │  │ Open    │→│ Grayscale │→│ Blur   │→│ Save │  │  │ │
│  │  │  │ Image   │  │ (mode L) │  │ Filter │  │ File │  │  │ │
│  │  │  └─────────┘  └──────────┘  └────────┘  └──────┘  │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│         ┌────────────────┴────────────────┐                   │
│         ▼                                 ▼                    │
│  ┌──────────────┐                ┌──────────────┐             │
│  │   SEKUENSIAL  │                │    PARALEL    │             │
│  │  (1 proses)   │                │ (12 workers)  │             │
│  │  for loop     │                │ ProcessPool-  │             │
│  │  satu per satu│                │ Executor.map()│             │
│  └──────┬───────┘                └──────┬────────┘             │
│         │                               │                      │
│         ▼                               ▼                      │
│  ┌──────────────┐                ┌──────────────┐             │
│  │ hasil_       │                │ hasil_        │             │
│  │ sekuensial/  │                │ paralel/      │             │
│  └──────────────┘                └──────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

## Komponen Sistem

| Komponen | Detail |
|----------|--------|
| **Input** | 81 gambar (79 JPG + 2 PNG) |
| **Core Function** | `proses_satu_gambar()` — open → grayscale → blur → save |
| **Metode Sekuensial** | Loop `for` biasa (1 proses) |
| **Metode Paralel** | `ProcessPoolExecutor` (12 workers — Ryzen 6C/12T) |
| **Output Sekuensial** | Folder `hasil_sekuensial/` |
| **Output Paralel** | Folder `hasil_paralel/` |

## Implementasi Komputasi Paralel

Komputasi Paralel diimplementasikan menggunakan `concurrent.futures.ProcessPoolExecutor` dari Python standard library.

### Cara Kerja
1. `ProcessPoolExecutor` membuat **worker processes** sebanyak jumlah CPU core (12 threads)
2. Method `.map()` mendistribusikan daftar gambar ke worker-worker tersebut
3. Setiap worker memproses gambar secara **independen dan simultan** (paralel nyata)
4. Hasil dikumpulkan secara otomatis dalam urutan yang sama dengan input

### Kode Utama (Paralel)
```python
with ProcessPoolExecutor() as executor:
    hasil = executor.map(proses_satu_gambar, daftar_gambar)
```

### Kode Utama (Sekuensial — sebagai pembanding)
```python
for gambar in daftar_gambar:
    proses_satu_gambar(gambar)
```

### Alur Perbandingan

```
SEKUENSIAL:
Gambar 1 → [Proses] → Selesai → Gambar 2 → [Proses] → Selesai → ...

PARALEL (12 workers):
        ┌→ [Proses] Gambar 1
Core 1 ─┼→ [Proses] Gambar 13
        └→ ...
        
        ┌→ [Proses] Gambar 2
Core 2 ─┼→ [Proses] Gambar 14
        └→ ...

... (12 core bekerja bersamaan)
```

### Kenapa ProcessPoolExecutor?
Image processing adalah **CPU-bound task** — Python memiliki **GIL (Global Interpreter Lock)** yang membatasi satu thread dalam satu waktu. `ProcessPoolExecutor` membuat proses terpisah (masing-masing dengan interpreter sendiri), sehingga **benar-benar memanfaatkan multi-core CPU**.

## Analisis

| Metode | Waktu Rata-rata | Kecepatan |
|--------|:---:|:---:|
| **Sekuensial** | 1.29 detik | 1x (baseline) |
| **Paralel** (12 threads) | 1.03 detik | **1.25x lebih cepat** |

### Detail 5 Percobaan

| Percobaan | Sekuensial | Paralel | Speedup |
|:---:|:---:|:---:|:---:|
| 1 (cold cache) | 2.64s | 1.18s | 2.24x |
| 2 | 1.33s | 1.02s | 1.30x |
| 3 | 1.29s | 1.12s | 1.15x |
| 4 | 1.28s | 0.98s | 1.31x |
| 5 | 1.26s | 1.01s | 1.25x |
| **Rata-rata** (2-5) | **1.29s** | **1.03s** | **1.25x** |

## Cara Menjalankan Program

### Persyaratan
- Python 3.x
- Library: Pillow (`pip install Pillow`)

### Langkah-langkah
```bash
# 1. Clone repositori
git clone https://github.com/Valdiirivaldi/eval3_kompar.git
cd eval3_kompar

# 2. Install dependensi
pip install Pillow

# 3. Masukkan gambar ke folder images/
#    (format .jpg atau .png)

# 4. Jalankan program
python parallel_image_processing.py
```

### Menghentikan Program
Program akan berhenti otomatis setelah selesai memproses semua gambar.

## Contoh Output

```
============================================================
  PERBANDINGAN SEKUENSIAL vs PARALEL (IMAGE PROCESSING)
============================================================

Ditemukan 81 gambar: ['06b17490...jpg', '...', 'fc106215...jpg']

--------------------------------------------------
[SEKUENSIAL] Waktu sekuensial: 1.29 detik
--------------------------------------------------
[PARALEL] Waktu paralel: 1.03 detik
--------------------------------------------------

==================================================
================ KESIMPULAN ========================
Waktu Sekuensial : 1.29 detik
Waktu Paralel    : 1.03 detik
Komputasi Paralel lebih cepat 1.25x lipat!
==================================================
```

## Dokumentasi Lengkap

👉 [**GitHub Pages**](https://valdiirivaldi.github.io/eval3_kompar/)

Berisi dokumentasi detail meliputi:
- 🔬 [Cara Kerja Parallel Computing](https://valdiirivaldi.github.io/eval3_kompar/how-it-works)
- 💻 [Penjelasan Kode Lengkap](https://valdiirivaldi.github.io/eval3_kompar/code-walkthrough)
- 📊 [Hasil dan Analisis](https://valdiirivaldi.github.io/eval3_kompar/results)
