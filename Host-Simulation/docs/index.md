---
title: CuffnCode Host-Simulation — Dokumentasi Teknis
layout: default
---

# Host-Simulation — Dokumentasi Teknis

Modul ini adalah inti kontribusi **Komputasi Paralel** pada [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode).

Dokumentasi ringkas untuk dosen dan Pages utama: [`../../docs/index.md`](../../docs/index.md)

---

## Instalasi cepat

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py
python main.py
```

---

## Modul sumber

| Modul | Topik matkul | Deskripsi |
|-------|--------------|-----------|
| `parallel_pipeline.py` | Data parallelism | `Pool.map`, sequential vs parallel vs dynamic chunksize |
| `distributed_nodes.py` | Distributed systems | 3 proses, `Queue`, pipeline A→B→C |
| `filters.py` | — | CPU-bound task per chunk (notch + MA) |
| `signal_generator.py` | — | Waveform cuff + noise/hum sintetis |
| `gui_app.py` | — | Visualisasi hardware + grafik filter |
| `hardware_sim.py` | — | State machine pump/valve |
| `cuffncode_specs.py` | — | Konstanta AD620, TLC2272, STM32 |

---

## Parameter benchmark default

| Parameter | Nilai | File |
|-----------|-------|------|
| Jumlah sampel | 4800 | `signal_generator` |
| Jumlah chunk | 16 | `run_benchmark(n_chunks=16)` |
| Filter passes | 12 | meningkatkan beban CPU per chunk |
| Sample rate (distributed) | 200 Hz | `distributed_nodes.run_distributed_demo` |

Ubah `n_chunks` dan `filter_passes` di `parallel_pipeline.py` untuk eksperimen speedup di laporan.

---

## Alur eksekusi `main.py`

1. Menjalankan `src/parallel_pipeline.py` — benchmark timing + estimasi BP demo  
2. Menjalankan `src/distributed_nodes.py` — log node A/B/C  

Exit code menggabungkan status kedua skrip (berguna untuk CI lokal).

---

## Filter (kaitan roadmap CuffnCode)

Repo utama mencantumkan **50/60 Hz notch** sebagai next-to-do hardware. Di simulasi Host, `notch_50hz()` mengimplementasikan IIR notch pada 50 Hz — membuktikan algoritma yang nantinya bisa di-port ke STM32 atau Host production.

---

## Pelaksana

| Nama | NRP | Kelas |
|------|-----|-------|
| Farhan Kamil Hermansyah | 152024150 | CC |

Mata kuliah: **IFB 206** · EVALUASI 3 · ITENAS 2025/2026
