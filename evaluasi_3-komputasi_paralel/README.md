# Parallel Retail Data Analyzer

Perbandingan SISD dan MIMD pada Pemrosesan Dataset Online Retail Menggunakan Load Balancing

## Latar Belakang

Dalam pemrosesan data berskala besar, pemrosesan sequential (SISD) menjadi bottleneck. Komputasi paralel (MIMD) dapat mempercepat pemrosesan dengan memanfaatkan multiple cores. Proyek ini membandingkan performa kedua pendekatan pada dataset Online Retail yang berisi 541,909 transaksi e-commerce.

## Tujuan

1. Membandingkan performa SISD dan MIMD dalam pemrosesan dataset skala besar
2. Mengukur execution time untuk kedua arsitektur
3. Menghitung speedup dan efficiency
4. Mengevaluasi efektivitas load balancing

## Dataset

Dataset: OnlineRetail.csv
- Jumlah baris: 541,909 transaksi
- Kolom: 8 (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
- Ukuran file: 43.47 MB
- Format: CSV (comma-separated values)
- Sumber: UCI Machine Learning Repository

Statistik setelah pemrosesan:
- Transaksi valid: 530,104 (97.8%)
- Transaksi invalid: 11,805 (2.2%)
- Total revenue: 10,666,684.54
- Total unit terjual: 5,588,376

## Teori Singkat

### SISD (Single Instruction Single Data)
SISD adalah arsitektur Von Neumann klasik dimana satu prosesor mengeksekusi satu instruksi pada satu data pada satu waktu. Pada proyek ini, SISD memproses seluruh dataset 541,909 baris secara berurutan dengan 1 worker.

### MIMD (Multiple Instruction Multiple Data)
MIMD adalah arsitektur dimana multiple prosesor dapat mengeksekusi instruksi berbeda pada data berbeda secara bersamaan. Pada proyek ini, MIMD menggunakan 4 threads untuk memproses dataset secara parallel dengan pola MapReduce.

### Load Balancing
Load balancing adalah teknik mendistribusikan beban kerja secara merata ke semua resource. Proyek ini menggunakan strategi equal division yang membagi 541,909 baris menjadi 4 chunk dengan ukuran kurang lebih sama.

### Speedup dan Efficiency
Speedup mengukur seberapa banyak lebih cepat program parallel dibanding sequential:
- Speedup (S) = T_SISD / T_MIMD
- Efficiency (E) = (S / P) x 100%, dimana P adalah jumlah worker

## Struktur Program

Program terdiri dari 5 file Python:
- main.py: Entry point program
- scheduler.py: Koordinator simulasi
- sisd.py: SISD processor
- mimd.py: MIMD processor
- load_balancer.py: Load balancing algorithm

Alur pemrosesan:
1. Load dataset dari CSV
2. Jalankan SISD processing
3. Jalankan load balancing
4. Jalankan MIMD processing
5. Verifikasi konsistensi hasil
6. Hitung metrik performa
7. Output hasil

## Cara Menjalankan

### Prasyarat
- Python 3.10 atau lebih baru
- Dataset: data/OnlineRetail.csv
- Tidak ada library eksternal

### Menjalankan Program

Default (4 workers, equal load balancing):
```bash
cd src
python main.py
```

Dengan parameter:
```bash
python main.py --workers 8              # 8 workers
python main.py --strategy weighted      # Weighted load balancing
python main.py --data /path/to/file.csv # Custom dataset
python main.py --help                   # Bantuan
```

Output:
- Terminal: Progress bar dan hasil perbandingan
- File: results.json (hasil dalam format JSON)
- File: results/result_TIMESTAMP.json (timestamped copy)

## Hasil Eksperimen

Konfigurasi:
- Dataset: OnlineRetail.csv
- Total rows: 541,909
- Workers: 4
- Load balancing strategy: Equal Division

Hasil (rata-rata dari 3 run):

| Metrik | Nilai |
|--------|-------|
| SISD Time | 12.1 detik |
| MIMD Time | 4.15 detik |
| Speedup | 2.82x |
| Efficiency | 70.5% |
| Load Balance | 100.0% |

Data analitik:
- Total Revenue: 10,666,684.54
- Total Quantity: 5,588,376
- Top Country: United Kingdom (84.7%)
- Top Product: DOTCOM POSTAGE

## Analisis

### Mengapa MIMD Lebih Cepat

1. Paralelisme: 4 worker memproses 4 chunk data secara bersamaan
2. I/O Overlap: Saat satu worker melakukan I/O wait, worker lain dapat melanjutkan komputasi
3. Load Balancing: Data terdistribusi merata (100% balance)
4. Total waktu: Sama dengan waktu worker terlama, bukan penjumlahan semua worker

### Mengapa Speedup Tidak Mencapai 4x

1. Overhead threading: Waktu untuk membuat thread, context switching, sinkronisasi
2. GIL (Global Interpreter Lock): Python membatasi CPU-bound operations ke 1 thread
3. REDUCE phase: Penggabungan hasil berjalan sequential
4. Lock contention: Thread-safety memerlukan synchronization
5. Hukum Amdahl: Bagian program yang sequential tidak dapat di-parallelize

### Pengaruh Jumlah Worker

- 1 worker: Speedup = 1x (sama dengan SISD)
- 2 workers: Speedup ~1.8-2.0x
- 4 workers: Speedup ~2.6-3.2x (eksperimen ini)
- 8 workers: Speedup tidak meningkat signifikan (~3.1-3.3x)

Optimal worker count untuk dataset ini adalah 4 (sesuai jumlah CPU cores).

### Pengaruh Load Balancing

Dengan equal division load balancing:
- Balance percentage: 100% (sempurna)
- Semua worker selesai pada waktu hampir bersamaan
- Tidak ada worker yang idle atau bottleneck

Tanpa load balancing yang baik:
- Beberapa worker overload, beberapa underload
- Total waktu ditentukan oleh worker terlambat (bottleneck)
- Efficiency turun drastis

## Kesimpulan

Pemrosesan paralel (MIMD) dengan 4 threads menghasilkan speedup rata-rata 2.82x dan efficiency 70.5% dibanding pemrosesan sequential (SISD). Speedup ini signifikan meskipun tidak mencapai nilai ideal 4x karena overhead threading, GIL Python, dan fase merge yang sequential.

Load balancing dengan strategi equal division menghasilkan distribusi beban kerja sempurna (100% balance). Untuk dataset berukuran besar seperti OnlineRetail dengan 541,909 transaksi, komputasi paralel dengan load balancing yang tepat memberikan peningkatan performa yang signifikan dan praktis untuk diterapkan pada sistem analitik data real-world.

## Struktur Folder

```
parallel-job-scheduler/
├── src/
│   ├── main.py
│   ├── scheduler.py
│   ├── sisd.py
│   ├── mimd.py
│   ├── load_balancer.py
│   └── __init__.py
│
├── data/
│   └── OnlineRetail.csv
│
├── docs/
│   └── (docs folder untuk referensi lanjutan)
│
├── results/
│   └── result_*.json
│
├── README.md
├── results.json
└── requirements.txt
```

## Referensi

1. Flynn, M. J. (1972). Some Computer Organizations and Their Effectiveness. IEEE Transactions on Computers.
2. Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities.
3. Chen, D., & Chen, M. (2015). Online Retail Dataset. UCI Machine Learning Repository.
4. Python Documentation - threading module. https://docs.python.org/3/library/threading.html
