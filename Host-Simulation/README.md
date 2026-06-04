# Host-Simulation — Komputasi Paralel & Sistem Terdistribusi

**Institut Teknologi Nasional — IFB 206 Komputasi Paralel dan Sistem Terdistribusi**  
**EVALUASI 3** · Semester Genap 2025/2026

Kontribusi pada fork: [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)  
Proyek referensi hardware: [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)

Simulasi **software-only** rantai Host CuffnCode: pemrosesan sinyal cuff setelah ADC STM32, dengan pola yang dibahas di kuliah paralel dan terdistribusi.

Dokumentasi lengkap:

- **Solusi** (masalah GitHub → kode saya): [`../docs/index.html#solusi`](../docs/index.html#solusi)
- **Cara tunjukkan sambil menjelaskan**: [`../docs/index.html#demo`](../docs/index.html#demo)
- README root: [`../README.md`](../README.md) — panduan presentasi di bagian *Cara menunjukkan*

---

## Solusi saya (ringkas)

Repo [CuffnCode upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) tidak menyediakan kode Host. Saya menambahkan:

1. **Filter paralel** — menjawab roadmap notch 50 Hz + beban CPU batch (`parallel_pipeline.py`, `filters.py`)
2. **Pipeline terdistribusi** — memetakan STM32 stream → DSP Host → UI (`distributed_nodes.py`)
3. **Simulator + GUI** — demo oscillometric tanpa hardware (`gui_app.py`, `hardware_sim.py`, `signal_generator.py`)

---

## Cara demo cepat (sambil jelaskan)

| Urutan | Perintah / layar | Kalimat penjelasan singkat |
|--------|------------------|----------------------------|
| 1 | Bandingkan [upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) vs [Host-Simulation di fork](https://github.com/Farmil23/CuffnCode/tree/main/Host-Simulation) | “Folder ini saya tambahkan; upstream tidak punya.” |
| 2 | `python main.py` | “Paralel: Pool + timing; Distributed: log Node A/B/C.” |
| 3 | `python gui.py` → Mulai Simulasi | “Simulator hardware + grafik filter + hum ↓% dari FFT.” |

---

## Apa yang diselesaikan (konteks matkul)

### Masalah

1. Sinyal tekanan dari sensor bridge **MPS20N0040D** sangat lemah (orde mV) dan rentan **hum 50 Hz** dari jaringan listrik.
2. Setelah **STM32F411CE** melakukan ADC, Host PC menerima batch sampel yang harus difilter sebelum fitur oscillometric (envelope, peak) diekstrak.
3. Untuk EVALUASI 3, tim harus menunjukkan **komputasi paralel** dan **sistem terdistribusi** pada studi kasus nyata — tanpa wajib membawa hardware ke ruang demo.

### Solusi perangkat lunak

| Komponen | Pola paralel / terdistribusi | File |
|----------|------------------------------|------|
| Pipeline filter | **Data parallelism** — task identik (`process_chunk`) pada tiap chunk data | `src/parallel_pipeline.py` |
| Benchmark | Sequential vs `Pool` vs dynamic `chunksize` | `run_benchmark()` |
| Pipeline logis | **Distributed** — 3 proses, komunikasi `Queue` (message passing) | `src/distributed_nodes.py` |
| Presentasi | GUI diagram hardware + grafik SEBELUM/SESUDAH | `gui.py`, `src/gui_app.py` |

### Kaitan Flynn / terminologi kuliah

| Istilah | Di proyek ini |
|---------|----------------|
| **SIMD / data parallel** | Satu fungsi filter → banyak chunk waveform |
| **SPMD** | Semua worker menjalankan `process_chunk` dengan argumen berbeda |
| **Message passing** | `multiprocessing.Queue` antar Node A, B, C (analog konsep MPI send/recv pada skala proses lokal) |
| **Pipeline parallelism** | Alur A→B→C: acquisition → processing → storage |

---

## Pelaksana

| Nama | NRP | Kelas |
|------|-----|-------|
| **Farhan Kamil Hermansyah** | 152024150 | CC |

Proyek Host-Simulation (kode, GUI, benchmark, dokumentasi) dikerjakan **sendiri**.

---

## Cara menjalankan

### GUI (demo visual — disarankan untuk video / presentasi)

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py
```

Klik **Mulai Simulasi** → diagram blok (sensor, AFE, STM32, Host) dan grafik perbandingan sinyal.

### Terminal (bukti numerik speedup & distributed log)

```bash
python main.py
```

Keluaran contoh:

- **Parallel pipeline:** waktu sequential vs parallel vs dynamic; estimasi BP demo; verifikasi peak seq vs par.
- **Distributed:** log `[Node A]`, `[Node B]`, `[Node C]` dan estimasi BP teragregasi.

### Dependensi

- Python 3.10+
- `numpy`, `matplotlib` (lihat `requirements.txt`)
- Tkinter (biasanya sudah ada di instalasi Python Windows)

---

## Arsitektur perangkat lunak

```
signal_generator.py  →  waveform cuff sintetis
        ↓
   split_signal()  →  N chunk
        ↓
 parallel_pipeline  →  Pool.map(process_chunk)  [atau sequential]
        ↓
 filters.py         →  moving_average + notch_50hz (per chunk)
        ↓
 merge_chunks()     →  sinyal terfilter + envelope peak → estimasi BP demo
```

**Distributed (proses terpisah):**

```
Node A (Acquisition)  --Queue-->  Node B (Processing)  --Queue-->  Node C (Storage/UI)
   stream batch                           filter batch                      agregasi peaks
```

---

## Struktur berkas

| File | Fungsi |
|------|--------|
| `gui.py` | Entry point GUI |
| `main.py` | Runner benchmark paralel + distributed |
| `src/parallel_pipeline.py` | Data parallelism, speedup, merge |
| `src/distributed_nodes.py` | 3 node + Queue |
| `src/filters.py` | Notch 50 Hz + moving average |
| `src/signal_generator.py` | Sinyal cuff simulasi |
| `src/signal_analysis.py` | Analisis untuk log GUI |
| `src/hardware_sim.py` | State mesin inflate/deflate simulasi |
| `src/cuffncode_specs.py` | Konstanta & teks spesifikasi hardware |
| `src/gui_app.py` | Tkinter application |
| `docs/index.md` | Dokumentasi Pages (salinan teknis) |

---

## Kaitan dengan hardware CuffnCode

| Hardware (repo utama) | Simulasi di folder ini |
|-----------------------|-------------------------|
| MPS20N0040D | `signal_generator.py` |
| AD620 + TLC2272 (~105 gain, ~1.5 V offset) | `cuffncode_specs.py` + telemetri GUI |
| STM32F411CE (ADC, PWM pump/valve) | Fase ADC + Node A acquisition |
| Roadmap notch 50/60 Hz | `filters.notch_50hz()` |
| Pump + 2 solenoid valve | `hardware_sim.py` (state inflate/deflate) |

Nilai BP di GUI dan terminal **bukan** diagnosis medis.

---

## Dokumentasi & penilaian

| Deliverable EVALUASI 3 | Lokasi |
|------------------------|--------|
| Kode + README | Folder ini + README root repo |
| GitHub Pages | `/docs` pada repo root → [`docs/index.html`](../docs/index.html) |
| Video demo (Instagram) | [Reel](https://www.instagram.com/reel/DZK6f8TyS4B/?igsh=cGtibXh3azR0bGNv) |
| Laporan + video (Google Drive) | [Folder EVALUASI_3](https://drive.google.com/drive/folders/1at-MlfVUXRxzlCIGZBBKLNQvKkVhnb4K?usp=sharing) |

Detail arsitektur, diagram, dan checklist matkul: [`docs/index.md`](docs/index.md) dan [`../docs/index.md`](../docs/index.md).

Referensi desain: [Obsidian — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## Catatan performa

Pada mesin Windows dengan ~4800 sampel dan 16 chunk, **parallel bisa lebih lambat** dari sequential karena biaya membuat proses anak. Untuk laporan, jelaskan:

1. Pola **data parallel** tetap benar secara konseptual.
2. Speedup nyata muncul jika data lebih besar (stream ADC panjang) atau di Linux dengan `fork`.
3. **Distributed demo** menekankan **dekompisi subsistem** dan **message passing**, bukan throughput cluster HPC.
