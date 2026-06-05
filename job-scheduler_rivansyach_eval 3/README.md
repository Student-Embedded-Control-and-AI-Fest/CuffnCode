# Retail Workload Benchmark

Project ini membandingkan pemrosesan transaksi retail secara berurutan (SISD)
dan paralel (MIMD). Dataset dibaca dari CSV, transaksi tidak valid disaring,
lalu program menghitung revenue, quantity, revenue per negara, dan 10 produk
dengan revenue tertinggi.

## Fitur

- Baseline SISD untuk memproses seluruh dataset dengan satu alur kerja.
- MIMD berbasis `ThreadPoolExecutor` untuk membagi pekerjaan ke beberapa worker.
- Strategi distribusi data: `equal`, `round_robin`, dan `weighted`.
- Verifikasi hasil SISD dan MIMD.
- Output ringkasan performa ke terminal dan JSON.

## Struktur

```text
src/
  main.py           Entry point CLI
  scheduler.py      Orkestrasi benchmark
  sisd.py           Processor sequential
  mimd.py           Processor paralel
  load_balancer.py  Pembagian indeks data ke worker
  retail_core.py    Parsing transaksi dan agregasi revenue
data/
  OnlineRetail.csv
results/
  result_*.json
results.json
```

## Cara Menjalankan

```bash
python src/main.py
```

Opsi CLI:

```bash
python src/main.py --workers 8
python src/main.py --strategy weighted
python src/main.py --data data/OnlineRetail.csv
```

## Output

Program menampilkan:

- Informasi dataset.
- Waktu eksekusi SISD dan MIMD.
- Speedup dan efficiency.
- Load balance antar worker.
- Status konsistensi revenue dan quantity.

Hasil juga disimpan ke:

- `results.json`
- `results/result_YYYYMMDD_HHMMSS.json`

## Catatan Implementasi

File `retail_core.py` menjadi pusat logika domain: satu fungsi untuk parsing
baris transaksi dan satu struktur `RevenueReport` untuk menggabungkan hasil.
Dengan begitu, SISD dan MIMD memakai aturan bisnis yang sama, sementara cara
eksekusinya tetap berbeda.
