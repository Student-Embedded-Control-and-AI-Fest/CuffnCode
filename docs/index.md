---
title: CuffnCode — Host Simulation (IFB 206)
layout: default
---

# CuffnCode — Host Simulation

**Retrofitted Blood Pressure System** · dokumentasi mini project  
**Mata kuliah:** IFB 206 — *Komputasi Paralel dan Sistem Terdistribusi*  
**Institusi:** Institut Teknologi Nasional (ITENAS)  
**Penilaian:** EVALUASI 3 · Semester Genap 2025/2026

**Repositori:** [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)  
**Program tim:** [`Host-Simulation/`](../tree/main/Host-Simulation)  
**Hardware referensi:** [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)  
**Catatan desain:** [Obsidian Publish — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## Penting: GUI vs halaman web ini

| Media | Apa yang ditampilkan |
|-------|----------------------|
| **GitHub Pages** (situs ini) | Dokumentasi, arsitektur, tim, cara install |
| **`python gui.py`** di laptop | Simulator interaktif Tkinter + grafik SEBELUM/SESUDAH |
| **Video Instagram Lab** | Demo 20–30 detik untuk dosen (disarankan) |

GUI **tidak** berjalan di browser Pages — itu program desktop Python.

---

## Menjalankan program

```bash
git clone https://github.com/Farmil23/CuffnCode.git
cd CuffnCode/Host-Simulation
pip install -r requirements.txt
python gui.py
```

Benchmark terminal (paralel + distributed):

```bash
python main.py
```

---

## 1. Latar belakang

**CuffnCode** ([IFAC Activity Fund](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)) adalah sistem pengukuran tekanan darah retrofit untuk pengajaran dan riset. Rantai sinyal: sensor bridge → analog front end → ADC mikrokontroler → (opsional) Host PC untuk filter dan analisis.

Pada **EVALUASI 3 Komputasi Paralel**, tim fokus pada **lapisan Host**:

- Bagaimana batch sampel cuff diproses dengan **data parallelism** agar latency filter menurun pada data besar.
- Bagaimana subsistem nyata (sensor/MCU/PC) dimodelkan sebagai **node terdistribusi** dengan **message passing**.

Semua ini diimplementasikan **tanpa hardware fisik** menggunakan generator sinyal dan simulator GUI yang mengikuti spesifikasi CuffnCode.

---

## 2. Arsitektur sistem

### 2.1 Hardware (referensi CuffnCode)

| Subsistem | Komponen | Fungsi |
|-----------|----------|--------|
| Sensor | MPS20N0040D | Bridge tekanan millivolt (~50–100 mV full-scale) |
| Analog Front End | AD620 + TLC2272 | Gain ≈ 105, offset ≈ 1,5 V |
| Aktuator | DC micro-pump + 2 solenoid valve | Inflate / deflate cuff |
| Digital Controller | STM32F411CE (Black Pill) | ADC, PWM, GPIO |
| Host (tim kami) | PC Python | Pipeline paralel + 3 node + GUI |

### 2.2 Diagram blok

```
[Cuff + MPS20N0040D] --> [AFE: AD620 / TLC2272] --> [STM32 ADC]
         |                                              |
   [Pump + Valves] <-------- [STM32 PWM/GPIO] <---- [Kontrol cuff]
         |                                              |
         +---------------- [Host PC] <----- UART/USB (rencana)
                    |
         +----------+----------+
         |                     |
  [Data-parallel filter]  [Distributed A→B→C]
  Pool + chunk waveform    Queue + 3 proses
```

### 2.3 Pemetaan simulasi → hardware

| Tahap nyata | Modul simulasi |
|-------------|----------------|
| Tekanan cuff → mV bridge | `signal_generator.py` |
| Gain/offset AFE | `cuffncode_specs.py`, telemetri GUI |
| Sampling ADC | Parameter `fs`, fase STM32 di GUI |
| Filter hum 50 Hz (roadmap repo) | `filters.notch_50hz()` |
| Estimasi BP oscillometric | Envelope peak → mapping demo (bukan klinis) |

---

## 3. Komputasi paralel

### 3.1 Pola: data parallelism

**Definisi:** satu *task* komputasi (filter) diterapkan ke banyak *partition* data (chunk waveform).

Alur di `parallel_pipeline.py`:

1. `generate_cuff_waveform()` — 4800 sampel (default)
2. `split_signal(signal, n_chunks)` — mis. 16 chunk
3. `process_chunk` di tiap worker: moving average → notch 50 Hz (beberapa pass)
4. `merge_chunks` — urutkan indeks, `concatenate`

Implementasi: `multiprocessing.Pool.map` — pola **SPMD** (Single Program, Multiple Data).

### 3.2 Perbandingan scheduling

| Mode | Implementasi | Kegunaan edukasi |
|------|--------------|------------------|
| **Sequential** | Loop for chunk | Baseline waktu |
| **Parallel** | `Pool.map`, `chunksize=2` | Paralelisme statis |
| **Dynamic** | `chunksize=1` | Load balancing — worker mengambil chunk berikutnya saat idle |

### 3.3 Interpretasi speedup (untuk laporan)

Contoh di Windows (8 core): parallel bisa **lebih lambat** dari sequential pada data kecil karena overhead **spawn** proses. Dalam laporan, cantumkan:

- Pola data parallel sudah benar (peak seq vs par cocok).
- Speedup > 1 diharapkan jika ukuran stream ↑ (ADC real-time panjang) atau platform `fork` (Linux).
- Referensi **Amdahl**: bagian serial (merge, I/O) membatasi speedup.

### 3.4 Cuplikan konsep kode

Worker entry (`filters.py`):

```python
def process_chunk(args):
    idx, chunk, fs, passes = args
    filtered = chunk.astype(np.float64)
    for _ in range(passes):
        filtered = notch_50hz(moving_average(filtered, 11), fs)
    return idx, filtered, float(np.max(filtered))
```

---

## 4. Sistem terdistribusi

### 4.1 Tiga node logis

| Node | Peran | Analog hardware |
|------|-------|-----------------|
| **A — Acquisition** | Streaming batch sampel | STM32 + sensor |
| **B — Processing** | Filter + ekstraksi peak per batch | DSP di MCU atau Host |
| **C — Storage/UI** | Agregasi peaks → estimasi BP demo | PC / rekam data |

### 4.2 Komunikasi

- **Mechanism:** `multiprocessing.Queue` (FIFO message passing)
- **Pesan A→B:** `{"type": "samples", "batch_id", "data"}`, lalu `{"type": "eof"}`
- **Pesan B→C:** `{"type": "features", "peaks"}`, lalu `{"type": "eof"}`
- **Proses:** `multiprocessing.Process` — tiap node proses OS terpisah (simulasi mesin berbeda pada satu PC)

### 4.3 Diagram alur

```
Node A --{samples, batch_id}--> Node B --{features, peaks}--> Node C
         --{eof}---------------->         --{eof}------------>
```

Implementasi: `distributed_nodes.py` — jalankan via `python main.py` (bagian 2/2).

---

## 5. GUI simulator

Fitur utama (`gui_app.py`):

- Diagram alur: sensor → AFE → STM32 → Host
- Simulasi state pump / valve (inflate, hold, deflate)
- Grafik **SEBELUM** (mentah + noise/hum) vs **SESUDAH** (filter Host)
- Log telemetri dan penjelasan spesifikasi AD620/TLC2272

Tombol **Mulai Simulasi** menjalankan animasi dan update grafik — cocok untuk rekaman video demo.

---

## 6. Analog Front End (ringkas)

Gain instrumen AD620:

$$G = 1 + \frac{49.4\,\text{k}\Omega}{R_g} \approx 1 + \frac{49.4\,\text{k}\Omega}{470\,\Omega} \approx 105$$

Offset TLC2272:

$$\frac{56\,\text{k}}{47\,\text{k} + 56\,\text{k}} \times 3.3\,\text{V} \approx 1.5\,\text{V}$$

Simulasi TINA-TI dan skema KiCad ada di folder root repo (`TINA-TI/`, `KiCad/`).

---

## 7. Checklist kesesuaian EVALUASI 3

| Kriteria | Status | Bukti |
|----------|--------|-------|
| Studi kasus terkait domain (sinyal / embedded) | ✅ | CuffnCode BP cuff |
| Data parallelism | ✅ | `parallel_pipeline.py` |
| Sistem terdistribusi / message passing | ✅ | `distributed_nodes.py` |
| Dokumentasi GitHub + Pages | ✅ | Folder `docs/` |
| Demo runnable | ✅ | `gui.py`, `main.py` |
| Video demo (opsional kuliah) | ⬜ | Instagram Lab — tim unggah |

---

## 8. Tim

| Nama | NRP | Kelas |
|------|-----|-------|
| **Farhan Kamil Hermansyah** | 152024150 | CC |
| Ratu Qolbu Maziah | 152024151 | CC |
| Syafa Meisya Fitria | 152024182 | AA |

Implementasi kode Host-Simulation: **Farhan Kamil Hermansyah**.

---

## 9. Keamanan & batasan

- Jangan over-pressure pada sensor MPS20N0040D (hardware nyata).
- Hindari ground noise USB PC saat pengukuran nyata.
- Estimasi BP pada simulasi **bukan** diagnosis medis.

---

## 10. Roadmap

- [ ] Integrasi data ADC nyata dari STM32 (serial/USB)
- [ ] Notch 60 Hz (region US)
- [ ] Deploy node B/C ke Raspberry Pi (distributed fisik)
- [ ] PCB & evaluasi performa (mengikuti repo utama CuffnCode)

---

## 11. Kredit

- [CuffnCode — IFAC Activity Fund](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)
- [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode) — fork tim IFB 206
- Instrumentation Amps Guide — Analog Devices
- Materi kuliah: OpenMP/MPI, load balancing, Flynn taxonomy
