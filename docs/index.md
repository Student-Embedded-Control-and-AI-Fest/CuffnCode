---
title: CuffnCode Host-Simulation — Dokumentasi
layout: default
---

# CuffnCode — Host Simulation

**Farhan Kamil Hermansyah** · 152024150 · IFB 206 · EVALUASI 3

> **Navigasi klik + penjelasan lengkap:** buka **[`index.html`](index.html)** (titik mengambang di kanan).  
> Bagian penting: **Solusi** (masalah GitHub vs karya saya) · **Demo** (cara tunjukkan sambil menjelaskan).

---

## Solusi saya berdasarkan CuffnCode GitHub

| Di repo [upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) | Yang saya tambahkan di [fork](https://github.com/Farmil23/CuffnCode) |
|----------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Hardware, KiCad, TINA-TI | Folder **`Host-Simulation/`** (Python) |
| Roadmap notch 50 Hz (belum kode) | `filters.notch_50hz` + FFT verifikasi GUI |
| Roadmap evaluasi performa | `parallel_pipeline.py` benchmark |
| Rantai sensor → STM32 → Host (konsep) | `distributed_nodes.py` Node A→B→C |
| Tidak ada demo software | `gui.py` + grafik SEBELUM/SESUDAH |

---

## Cara menunjukkan sambil menjelaskan

### Langkah 1 — Dua repo

1. Buka **upstream** → tunjukkan **tidak ada** `Host-Simulation/`.  
   *Jelaskan:* “Proyek asli hardware saja.”
2. Buka **fork** → `Host-Simulation/`.  
   *Jelaskan:* “Ini kontribusi paralel & distributed saya.”

### Langkah 2 — Terminal

```bash
cd Host-Simulation && pip install -r requirements.txt && python main.py
```

- `Peak match: OK` → filter paralel benar.  
- Log `[Node A/B/C]` → sistem terdistribusi jalan.  
- Speedup &lt; 1 (opsional) → saya jujur, bukan copy template.

### Langkah 3 — GUI

```bash
python gui.py
```

**Mulai Simulasi** → tunjukkan hum di grafik merah, penurunan % di panel hijau, fase pump/valve.

### Langkah 4 — Bukan copy-paste

Folder baru · kode jalan · angka dari FFT/benchmark · README/Pages jelaskan masalah→solusi→file.

Detail naskah presentasi: **[`index.html#demo`](index.html#demo)**.

---

## Menjalankan

```bash
git clone https://github.com/Farmil23/CuffnCode.git
cd CuffnCode/Host-Simulation
pip install -r requirements.txt
python gui.py
python main.py
```

---

## Pelaksana

| Nama | NRP | Kelas |
|------|-----|-------|
| Farhan Kamil Hermansyah | 152024150 | CC |

Dikerjakan **sendiri**.

---

## Referensi

- [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)
- [CuffnCode upstream](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)
- [Obsidian CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)
