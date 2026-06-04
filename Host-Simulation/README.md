# Host-Simulation — Komputasi Paralel & Sistem Terdistribusi

**Institut Teknologi Nasional — IFB 206 Komputasi Paralel**  
Kontribusi untuk [CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) (EVALUASI 3, Semester Genap 2025/2026).

Simulasi **software-only** rantai Host: pemrosesan sinyal cuff setelah ADC STM32, dengan:

- **Data parallelism** — `multiprocessing.Pool` pada chunk waveform  
- **Distributed pipeline** — Node A (acquire) → B (process) → C (store)  
- **GUI** — diagram hardware CuffnCode + grafik SEBELUM/SESUDAH filter  

Referensi desain hardware: [Obsidian — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## Tim

| Nama | NRP | Peran |
|------|-----|-------|
| *(isi)* | *(isi)* | GUI & dokumentasi |
| *(isi)* | *(isi)* | Parallel pipeline |
| *(isi)* | *(isi)* | Distributed nodes |

---

## Cara menjalankan

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py
```

Terminal (benchmark):

```bash
python main.py
```

---

## Struktur

| File | Fungsi |
|------|--------|
| `gui.py` | Simulator + grafik perbandingan sinyal |
| `main.py` | Demo terminal paralel & distributed |
| `src/parallel_pipeline.py` | Data parallelism |
| `src/distributed_nodes.py` | 3 node + Queue |
| `src/filters.py` | Notch 50 Hz + moving average |
| `docs/` | Dokumentasi GitHub Pages |

---

## Kaitan dengan hardware CuffnCode

| Hardware (repo utama) | Simulasi di folder ini |
|-----------------------|-------------------------|
| MPS20N0040D | `signal_generator.py` |
| AD620 + TLC2272 | Spesifikasi + telemetri di GUI |
| STM32F411CE | Fase ADC + Node A |
| Notch hum 50/60 Hz (roadmap) | `filters.notch_50hz()` |

Nilai BP di GUI **bukan** diagnosis medis.
