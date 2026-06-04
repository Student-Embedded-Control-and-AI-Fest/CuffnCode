<p align="center">
  <img src="./images/cuffncode.png" width="200">
</p>

<h4 align="center">This project is funded by IFAC Activity Fund (July 2025 to June 2026)</h4>

**CuffnCode** is a retrofitted blood pressure measurement system for teaching and research. In the long term, it aims to become an overinstrumented platform for developing and testing signal processing and control algorithms.

**Fork kuliah:** [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode) — **Host-Simulation** (IFB 206, EVALUASI 3) oleh **Farhan Kamil Hermansyah** (152024150).

Repo hardware asli: [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)

---

## Solusi yang saya buat (bukan isi repo GitHub asli)

Repo CuffnCode upstream berisi **KiCad, TINA-TI, dan dokumentasi hardware** — belum ada kode Host, filter, atau demo paralel. Saya menambahkan **tiga solusi perangkat lunak** di folder `Host-Simulation/`:

| Masalah dari konteks CuffnCode | Solusi saya | Bukti di repo |
|------------------------------|-------------|---------------|
| Roadmap *50/60 Hz notch* belum diimplementasi | Filter IIR notch 50 Hz + moving average per chunk; analisis FFT hum ↓% | `filters.py`, `signal_analysis.py` |
| Pemrosesan batch ADC di PC berat | Data parallelism: `Pool.map` + merge terindeks + benchmark scheduling | `parallel_pipeline.py` |
| Rantai sensor → MCU → Host tersegmentasi | 3 proses A (acquire) → B (process) → C (store) via `Queue` | `distributed_nodes.py` |
| Demo tanpa board fisik | GUI: state machine pump/valve, grafik SEBELUM/SESUDAH, telemetri AFE | `gui_app.py`, `hardware_sim.py` |

**Bukan copy-paste:** folder `Host-Simulation/` tidak ada di upstream; algoritma & GUI saya tulis; angka benchmark dari `python main.py` di mesin saya.

Dokumentasi interaktif (titik navigasi klik): **[GitHub Pages — `docs/index.html`](docs/index.html)** · bagian **Solusi** & **Demo**.

---

## Cara menunjukkan sambil menjelaskan (panduan presentasi)

Ikuti urutan ini saat demo ke dosen atau rekam video — **tunjukkan layar** dan **jelaskan** dengan naskah di kolom kanan.

### 1. Bandingkan GitHub asli vs fork saya

| Tunjukkan | Jelaskan |
|-----------|----------|
| [CuffnCode upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) — tidak ada folder `Host-Simulation/` | “Repo asli hanya hardware: KiCad, TINA-TI, gambar. Belum ada kode Host atau komputasi paralel.” |
| [Farmil23/CuffnCode → Host-Simulation](https://github.com/Farmil23/CuffnCode/tree/main/Host-Simulation) | “Ini tambahan saya untuk IFB 206: Python, GUI, pipeline paralel & distributed.” |
| README ini + [halaman Pages](docs/index.html) | “Dokumentasi memetakan masalah CuffnCode ke file solusi saya — bukan menyalin teks README hardware.” |

### 2. Terminal — bukti paralel & distributed

```bash
cd Host-Simulation
pip install -r requirements.txt
python main.py
```

| Output yang muncul | Jelaskan ke dosen |
|--------------------|-------------------|
| `Sequential` / `Parallel` / `Dynamic` + detik | “Tiga mode scheduling; saya ukur jujur — di Windows bisa speedup &lt; 1 karena overhead proses.” |
| `Peak match (seq vs par): OK` | “Hasil filter paralel sama dengan sequential — merge chunk benar.” |
| `[Node A]`, `[Node B] Batch 0..3`, `[Node C]` | “Tiga proses terpisah + Queue: acquisition → processing → storage, analog rantai STM32→Host→UI.” |

**Kaitkan ke CuffnCode:** roadmap *notch 50 Hz* → ada di `filters.py`; roadmap *evaluasi performa* → benchmark timing di atas.

### 3. GUI — bukti simulator tanpa hardware

```bash
python gui.py
```

Klik **Mulai Simulasi**, lalu tunjukkan:

| Di layar GUI | Jelaskan |
|--------------|----------|
| Diagram pump / valve / sensor / AFE / STM32 menyala per fase | “State machine saya mengikuti alur retrofit CuffnCode — demo tanpa board.” |
| Grafik **SEBELUM** (merah, hum 50 Hz terlihat) | “Sinyal sintetis: envelope + `3·sin(50 Hz)` — masalah noise di README proyek.” |
| Grafik **SESUDAH** (hijau) + `Hum 50Hz ↓ xx%` | “Filter Host saya; persen dari FFT (`signal_analysis.py`), bukan angka hardcode.” |
| Telemetri Bridge / AD620 / ADC code | “Rumus gain & offset dari spesifikasi repo, dihitung di `cuffncode_specs.py`.” |
| Log `Pool.map chunk` dan `Node A/B/C` | “Konsep sama dengan `main.py`, divisualkan untuk penilaian.” |

### 4. Jika ditanya “ini bukan copy-paste?”

1. **Folder baru** — `Host-Simulation/` nol di upstream, penuh di fork.  
2. **Kode runnable** — `main.py` / `gui.py`, bukan hanya bullet “Next-to-Do”.  
3. **Angka hidup** — hum ↓% dan timing dari program Anda, bukan screenshot orang lain.  
4. **Keputusan saya** — GUI tanpa `Pool` (animasi); benchmark dengan `Pool`; `seed=42` reproduksibel.

**Video singkat (20–30 s):** upstream vs fork (3 s) → GUI grafik SEBELUM/SESUDAH (15 s) → terminal `Peak match: OK` + Node B (5 s).

---

## Ringkasan kesesuaian dengan matkul

| Aspek kurikulum IFB 206 | Implementasi di repo ini | Lokasi kode |
|-------------------------|--------------------------|-------------|
| **Data parallelism** (task sama, data berbeda) | `multiprocessing.Pool.map` memproses chunk waveform secara paralel | `Host-Simulation/src/parallel_pipeline.py` |
| **Scheduling / load balancing** | Perbandingan `chunksize` tetap vs dinamis (`chunksize=1`) | `parallel_pipeline.run_benchmark()` |
| **Sistem terdistribusi** | Tiga proses logis A→B→C dengan **message passing** (`Queue`) | `Host-Simulation/src/distributed_nodes.py` |
| **Pemrosesan sinyal (studikasus)** | Notch 50 Hz + moving average pada sinyal cuff simulasi | `Host-Simulation/src/filters.py` |
| **Demonstrasi & dokumentasi** | GUI Tkinter + benchmark terminal + GitHub Pages | `Host-Simulation/gui.py`, `docs/` |

Program berjalan (sudah diverifikasi di Windows): `python main.py` menjalankan benchmark paralel dan pipeline terdistribusi; `python gui.py` membuka simulator interaktif.

> **Catatan speedup:** pada dataset simulasi (~4800 sampel), overhead `spawn` di Windows sering membuat waktu paralel *lebih lama* dari sequential. Itu wajar untuk tugas — yang dinilai adalah **pola**, segmentasi data, dan arsitektur node, bukan angka speedup tinggi pada data kecil.

---

## Host simulation — Komputasi Paralel (ITENAS IFB 206)

Saya mengembangkan **lapisan Host (PC)** dari rantai CuffnCode: setelah ADC STM32, sinyal tekanan cuff perlu difilter (hum 50 Hz, noise) sebelum estimasi tekanan. Tanpa hardware fisik, modul ini mensimulasikan sensor, AFE, MCU, dan Host dengan:

- **Data parallelism** — pembagian waveform menjadi chunk; filter identik di tiap worker (`Pool`)
- **Distributed pipeline** — Node **A** (acquisition) → **B** (processing) → **C** (storage/UI) via antrian pesan
- **GUI** — diagram blok hardware CuffnCode + grafik **SEBELUM / SESUDAH** filter

### Menjalankan

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py          # simulator + grafik (disarankan untuk demo)
python main.py         # benchmark terminal: paralel + distributed
```

### Dokumentasi lengkap (GitHub Pages)

- Situs: aktifkan **Pages** dari folder `/docs` pada branch `main` → URL: `https://farmil23.github.io/CuffnCode/`
- **Dokumentasi implementasi (disarankan untuk dosen):** [`docs/index.html`](docs/index.html) — penjelasan modul, keputusan desain, cuplikan algoritma, bukan template ringkas
- Markdown ringkas: [`docs/index.md`](docs/index.md) · detail modul: [`Host-Simulation/docs/index.md`](Host-Simulation/docs/index.md)

### Pelaksana

| Nama | NRP | Kelas |
|------|-----|-------|
| **Farhan Kamil Hermansyah** | 152024150 | CC |

Seluruh modul **Host-Simulation** (GUI, pipeline paralel & terdistribusi, dokumentasi) dikerjakan **sendiri**.

### Struktur folder Host-Simulation

| Path | Fungsi |
|------|--------|
| `gui.py` | Entry point GUI |
| `main.py` | Menjalankan benchmark paralel lalu demo distributed |
| `src/parallel_pipeline.py` | Data parallelism + perbandingan sequential/parallel |
| `src/distributed_nodes.py` | Simulasi 3 node + `Queue` |
| `src/filters.py` | Notch 50 Hz, moving average, `process_chunk` |
| `src/signal_generator.py` | Waveform cuff sintetis |
| `src/gui_app.py` | Antarmuka Tkinter |
| `src/cuffncode_specs.py` | Spesifikasi hardware untuk telemetri GUI |

Referensi desain hardware: [Obsidian — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## Retrofitted pump system

<img src="./images/complete_device.png" width="600">

## Analog Front End Design

A reproducible, low-noise analog front end for millivolt bridge sensors (e.g., MPS20N0040D, typically used for **hobbyist** sphygmomanometer), using AD620 instrumentation amplifier and TLC2272 level shift. This analog front end should also work for other millivolt instruments.

### TINA-TI

AC simulation with TINA-TI:

<img src="./images/AFE.png" width="600">

<img src="./images/tina-ac-diag.jpg" width="500">

Instrumentation amplifier gain:

$$ G = 1 + \frac{49.4\text{k}\Omega}{R_g} = 1 + \frac{49.4\text{k}\Omega}{470} \approx 105$$

TLC2272 offset:

$$ \frac{56 \text{k}}{47\text{k} + 56 \text{k}} \times 3.3 V \approx 1.5 V$$

### MPS20N0040D

The MPS20N0040D is a millivolt-level bridge (≈50–100 mV full-scale; 4–6 kΩ)

| <img src="./images/mps20n0040d_1.png" width="300"> | <img src="./images/mps20n0040d_2.png" width="300"> |
| --------------------------------------------------- | --------------------------------------------------- |

### TLC2272 (Dual, Low-Noise, Rail-To-Rail Operational Amplifier)

This will be used to offset the instrumentation amplifier, giving headroom for possible undershoot or for signal that goes both ways (positive and negative).

<img src="./images/tlc2272.png" width="300">

### AD620

This is the instrumentation amplifier that is relatively cheap and widely available in Indonesian market.

| <img src="./images/ad620_1.png" width="150"> | <img src="./images/ad620_2.png" width="150"> |
| -------------------------------------------- | -------------------------------------------- |

## Digital Controller

We will use STM32F411CE (the black pill) as our digital processor.

| <img src="./images/prototype1.png" width="250"> | <img src="./images/prototype2.png" width="330"> |
| ----------------------------------------------- | ----------------------------------------------- |

## Safety & Notes

- The MPS20N0040D is fragile—avoid over-pressure.
- If powering from USB, beware ground noise from the host PC. A ferrite on the USB cable can help.
- Estimasi BP di **Host-Simulation** hanya untuk demo kuliah — **bukan** diagnosis medis.

## Next-to-Do (repo hardware)

- 50/60 Hz notch filter (hum killer) — **diimplementasikan di simulasi Host** (`filters.notch_50hz`)
- PCB layouting.
- Performance evaluations.
- Integrasi stream ADC nyata dari STM32 ke pipeline Host.

## Credits

- Instrumentation amplifier intro: https://www.youtube.com/watch?v=O0-iczIq1aU
- INA333 review with AD620 suggestion: https://blog.robertelder.org/cjmcu-333-ina-333-instrumentation-amplifier/
- A Designer's Guide to Instrumentation Amplifiers (3rd Edition) https://www.analog.com/media/en/training-seminars/design-handbooks/designers-guide-instrument-amps-complete.pdf
