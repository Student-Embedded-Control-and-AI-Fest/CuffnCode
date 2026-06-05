# Parallel Distributed Monte Carlo Stock

## Kelompok
- Muhammad Farel Firdaus 152024061
- Hamizan Ihsan 152024063
- Ade Rahma Fauzan 152024068

Project ini mensimulasikan harga saham menggunakan metode Monte Carlo, lalu membandingkan performa tiga pendekatan komputasi:

- **Serial**: semua simulasi dijalankan dalam 1 proses.
- **Parallel**: simulasi dibagi ke beberapa worker CPU dalam 1 komputer.
- **Distributed/Shard**: simulasi dibagi menjadi beberapa shard, seolah-olah bisa dijalankan pada beberapa node berbeda, lalu hasilnya digabung.

Fokus utama project ini adalah **perbandingan waktu eksekusi, speedup, dan efisiensi**. Output simulasi juga menampilkan analisis risiko seperti peluang profit, peluang rugi, VaR 95%, dan Expected Shortfall 95%.

## Struktur Project

```text
monte-carlo-saham/
├── data/
│   └── sample_prices.csv
├── scripts/
│   ├── run_benchmark.sh
│   └── run_full_comparison.sh
├── src/
│   └── stock_monte_carlo.py
├── output/                 # dibuat otomatis saat program dijalankan
├── README.md
└── requirements.txt
```

## Setup

Masuk ke folder project dan aktifkan virtual environment:

```bash
cd /home/zeth/Desktop/Komputasi/monte-carlo-saham
source .venv/bin/activate
```

Kalau `.venv` belum ada, buat dan install dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Demo Utama: Perbandingan Langsung

Untuk demo, cukup jalankan satu command ini:

```bash
scripts/run_full_comparison.sh 30000 60 4
```

Parameter command:

```text
30000 = jumlah simulasi Monte Carlo
60    = horizon prediksi dalam hari
4     = jumlah worker/shard
```

Command tersebut otomatis menjalankan:

```text
1. Serial
2. Parallel dengan 4 worker
3. Distributed/shard dengan 4 shard
4. Merge hasil shard
5. Cetak tabel perbandingan
```

Contoh output tabel:

```text
=== HASIL PERBANDINGAN ===
method                              sim   w/s    time(s)   speedup      eff   profit%    loss%   VaR95%
---------------------------------------------------------------------------------------------------------
serial                            30000     1   ...        1.0000   1.0000     ...      ...      ...
parallel                          30000     4   ...        ...      ...        ...      ...      ...
distributed_shard_estimate        30000     4   ...        ...      ...        ...      ...      ...
distributed_shard_sequential      30000     4   ...        ...      ...        ...      ...      ...
```

File hasil perbandingan:

```text
output/full_comparison.csv
output/full_comparison_report.txt
output/full_serial_summary.csv
output/full_parallel_summary.csv
output/full_distributed_summary.csv
```

File gambar dari demo utama:

```text
output/full_serial_histogram.png
output/full_serial_paths.png
output/full_parallel_histogram.png
output/full_parallel_paths.png
output/full_distributed_histogram.png
output/full_distributed_paths.png
```

## Cara Membaca Tabel Perbandingan

Kolom penting:

```text
method     = metode komputasi yang diuji
sim        = jumlah simulasi
w/s        = worker atau shard
time(s)    = waktu eksekusi dalam detik
speedup    = percepatan dibanding serial
eff        = efisiensi penggunaan worker/shard
profit%    = peluang simulasi berakhir profit
loss%      = peluang simulasi berakhir rugi
VaR95%     = Value at Risk 95%
```

Rumus:

```text
speedup = waktu_serial / waktu_metode
efficiency = speedup / jumlah_worker
```

Contoh interpretasi:

```text
Jika serial 1.20 detik dan parallel 0.40 detik:
speedup = 1.20 / 0.40 = 3.0x

Jika parallel memakai 4 worker:
efficiency = 3.0 / 4 = 0.75 = 75%
```

## Arti Metode Yang Dibandingkan

### Serial

Serial adalah baseline. Semua simulasi Monte Carlo dikerjakan oleh satu proses.

```text
30.000 simulasi -> 1 proses
```

### Parallel

Parallel membagi simulasi ke beberapa worker CPU dalam komputer yang sama.

```text
30.000 simulasi -> 4 worker
Worker 1: 7.500 simulasi
Worker 2: 7.500 simulasi
Worker 3: 7.500 simulasi
Worker 4: 7.500 simulasi
```

### Distributed / Shard

Shard adalah potongan pekerjaan. Mode ini membagi simulasi menjadi beberapa file shard.

```text
30.000 simulasi -> 4 shard
shard_0: 7.500 simulasi
shard_1: 7.500 simulasi
shard_2: 7.500 simulasi
shard_3: 7.500 simulasi
```

Dalam sistem terdistribusi nyata, setiap shard bisa dijalankan di komputer/node berbeda. Setelah semua shard selesai, hasilnya digabung memakai `merge`.

Di tabel perbandingan ada dua baris distributed:

```text
distributed_shard_estimate
```

Estimasi waktu jika shard dijalankan bersamaan di beberapa node. Waktu ini memakai shard yang paling lama sebagai patokan.

```text
distributed_shard_sequential
```

Waktu jika semua shard dijalankan satu per satu di laptop yang sama.

## Command Manual

Jika ingin menjalankan satu per satu, gunakan command berikut.

### Serial

```bash
python src/stock_monte_carlo.py simulate --mode serial --simulations 30000 --days 60 --out output/serial
```

### Parallel

```bash
python src/stock_monte_carlo.py simulate --mode parallel --workers 4 --simulations 30000 --days 60 --out output/parallel
```

### Distributed / Shard

```bash
python src/stock_monte_carlo.py shard --shard-index 0 --num-shards 4 --simulations 30000 --days 60 --out output/shards/shard_0.npz
python src/stock_monte_carlo.py shard --shard-index 1 --num-shards 4 --simulations 30000 --days 60 --out output/shards/shard_1.npz
python src/stock_monte_carlo.py shard --shard-index 2 --num-shards 4 --simulations 30000 --days 60 --out output/shards/shard_2.npz
python src/stock_monte_carlo.py shard --shard-index 3 --num-shards 4 --simulations 30000 --days 60 --out output/shards/shard_3.npz
```

Gabungkan hasil shard:

```bash
python src/stock_monte_carlo.py merge --inputs "output/shards/shard_*.npz" --out output/distributed
```

## Output Manual

Output serial:

```text
output/serial_summary.csv
output/serial_summary.json
output/serial_histogram.png
output/serial_paths.png
```

Output parallel:

```text
output/parallel_summary.csv
output/parallel_summary.json
output/parallel_histogram.png
output/parallel_paths.png
```

Output distributed setelah merge:

```text
output/distributed_summary.csv
output/distributed_summary.json
output/distributed_histogram.png
output/distributed_paths.png
```

File `.npz` di folder `output/shards/` adalah data mentah shard, bukan file yang dibuka langsung. File yang dibuka untuk laporan adalah `.csv`, `.json`, dan `.png`.

## Histogram

Histogram menunjukkan sebaran harga akhir dari semua simulasi Monte Carlo.

Cara membaca:

```text
Sumbu X = harga akhir saham
Sumbu Y = jumlah simulasi/frekuensi
```

Jika sebagian besar histogram berada di kanan harga awal, maka lebih banyak skenario profit. Jika banyak berada di kiri harga awal, maka lebih banyak skenario rugi.

## Model Simulasi

Model yang digunakan adalah Geometric Brownian Motion:

```text
S(t+1) = S(t) * exp((mu - 0.5 * sigma^2) + sigma * Z)
```

Keterangan:

```text
S(t)  = harga saham hari ke-t
mu    = rata-rata log return harian
sigma = volatilitas log return harian
Z     = angka acak dari distribusi normal standar
```

## Metrik Risiko

Project menghitung:

```text
mean_final_price             = rata-rata harga akhir
median_final_price           = median harga akhir
probability_profit           = peluang profit
probability_loss             = peluang rugi
var_95_percent               = Value at Risk 95%
expected_shortfall_95_percent = rata-rata kerugian pada skenario buruk 5%
```

## Command Tambahan: Benchmark Serial vs Parallel

Jika hanya ingin membandingkan serial dan parallel dengan beberapa jumlah worker:

```bash
scripts/run_benchmark.sh 100000 60
cat output/benchmark_comparison.csv
```

Script ini menjalankan:

```text
Serial 1 worker
Parallel 2 worker
Parallel 4 worker
Parallel 8 worker
```

## Kesimpulan Project

Project ini menunjukkan bahwa simulasi Monte Carlo cocok untuk komputasi paralel karena setiap jalur simulasi dapat dihitung secara independen. Serial digunakan sebagai baseline, parallel mempercepat proses dengan worker CPU, dan distributed/shard menunjukkan bagaimana simulasi bisa dibagi menjadi beberapa potongan pekerjaan yang dapat dijalankan pada node berbeda.

Project ini bersifat akademik dan bukan rekomendasi investasi.
