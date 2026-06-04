---
title: CuffnCode Host-Simulation — Dokumentasi Implementasi
layout: default
---

# CuffnCode — Host Simulation

**IFB 206 Komputasi Paralel & Sistem Terdistribusi** · EVALUASI 3 · ITENAS 2025/2026  
**Pelaksana implementasi:** Farhan Kamil Hermansyah (152024150)

Dokumentasi ini menjelaskan **apa yang saya implementasikan** di fork [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode) — bukan ringkasan README hardware upstream.

> Versi HTML lengkap (disarankan untuk GitHub Pages): lihat [`index.html`](index.html) di folder yang sama.  
> **GUI** (`python gui.py`) tidak berjalan di browser; rekam layar untuk video Instagram Lab.

---

## 1. Kontribusi asli (bukan copy-paste upstream)

Repo [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) berisi KiCad, TINA-TI, dan foto prototipe. **Folder `Host-Simulation/` saya tambahkan** untuk kuliah.

| Modul | Yang saya tulis |
|-------|-----------------|
| `parallel_pipeline.py` | Benchmark sequential / `Pool.map` / dynamic `chunksize`, merge terindeks |
| `distributed_nodes.py` | 3 `Process` + `Queue`, pesan `samples` / `features` / `eof` |
| `filters.py` | MA + **IIR notch 50 Hz manual** (state biquad per sampel) |
| `signal_generator.py` | Envelope oscillometric + carrier + **hum 50 Hz** + noise |
| `signal_analysis.py` | FFT band-power hum, noise residu, panel PENGARUH GUI |
| `cuffncode_specs.py` | Hitung gain AD620 & offset TLC dari nilai repo |
| `hardware_sim.py` | State machine 11 fase + telemetri ADC |
| `gui_app.py` | ~750 baris Tkinter + Matplotlib + threading |
| `main.py` | Orkestrator dua benchmark terminal |

**Referensi** (komponen, rumus): README/Obsidian CuffnCode. **Implementasi** (paralel, distributed, GUI): kode di atas.

---

## 2. Keputusan desain

### Studi kasus = notch hum di Host

Roadmap CuffnCode: *50/60 Hz hum killer*. Saya letakkan di PC Host karena batch ADC panjang cocok untuk **data parallelism** dan pipeline **A→B→C**.

### `multiprocessing` di Windows

- Benchmark: `Pool.map` + catatan jujur jika speedup &lt; 1 (overhead spawn).
- GUI: **tidak** memanggil `Pool` dari thread animasi — loop 8 chunk + `process_chunk` agar progress bar terlihat.

### Notch tanpa scipy

`notch_50hz` implementasi koefisien sendiri → CPU-bound per chunk, bisa di-port ke STM32.

---

## 3. Model sinyal (`signal_generator.py`)

```text
envelope = 80·exp(-0.35t)·(1-exp(-2.5t))   # deflate oscillometric
carrier  = 0.15·sin(2π·1.2t)
hum      = 3.0·sin(2π·50t)                 # PLN
noise    = N(0, 0.8)
fs = 200 Hz, seed=42 (reproduksibel)
```

---

## 4. Komputasi paralel (`parallel_pipeline.py`)

1. `split_signal` → 16 chunk (benchmark)  
2. `process_chunk`: 12× (MA → notch) per chunk  
3. Sequential vs `Pool(cpu_count()-1)` vs `chunksize=1`  
4. `merge_chunks` sort by index  
5. Verifikasi `peak_seq ≈ peak_par` → cetak `Peak match: OK`

Worker mengembalikan `(idx, filtered, peak)` agar merge tidak salah urutan.

---

## 5. Sistem terdistribusi (`distributed_nodes.py`)

| Node | Fungsi | Pesan |
|------|--------|-------|
| A | Stream 4 batch + delay 50 ms | `samples`, `eof` |
| B | `in_q.get()` → MA + notch → list peak | `features`, `eof` |
| C | `max(peaks)` → BP demo | print |

Tiga **proses OS** terpisah — bukan thread — agar sesuai konsep message passing.

---

## 6. GUI (`gui_app.py`)

- Diagram: cuff, pump, 2 solenoid, MPS20N0040D, AD620, TLC2272, STM32, Host, Node A/B/C  
- `HardwareSimulator.active_blocks()` menyalakan blok per fase  
- Animasi deflate + plot slice  
- `compare_before_after()` → % penurunan hum/noise di panel hijau  
- Thread ` _run_simulation` + `root.after` untuk thread-safety Tkinter  

---

## 7. Menjalankan

```bash
git clone https://github.com/Farmil23/CuffnCode.git
cd CuffnCode/Host-Simulation
pip install -r requirements.txt
python gui.py
python main.py
```

**Saat demo:** fase GUI berubah berurutan; terminal menampilkan timing + log `[Node A/B/C]`.

---

## 8. Pemetaan IFB 206

| Topik | Bukti di repo |
|-------|----------------|
| Data parallelism | `Pool.map` + `process_chunk` |
| Load balancing | `chunksize` 2 vs 1 |
| Message passing | `Queue` di `distributed_nodes.py` |
| Pipeline tersegmentasi | Node A→B→C + diagram GUI |
| Studi kasus | Notch 50 Hz cuff (roadmap CuffnCode) |

---

## 9. Tim & deliverable

| Nama | NRP | Peran |
|------|-----|-------|
| **Farhan Kamil Hermansyah** | 152024150 | Implementasi Host-Simulation |
| Ratu Qolbu Maziah | 152024151 | Tim kelas |
| Syafa Meisya Fitria | 152024182 | Tim kelas |

| Deliverable | Status |
|-------------|--------|
| Kode | ✓ |
| Dokumentasi implementasi | ✓ |
| GitHub Pages | ✓ `/docs` |
| Video GUI | Instagram Lab |

---

## Referensi

- [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)
- [CuffnCode upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)
- [Obsidian CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

*Estimasi BP demo — bukan diagnosis medis.*
