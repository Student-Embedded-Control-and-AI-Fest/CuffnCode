---
title: CuffnCode — Dokumentasi Proyek
layout: default
---

# CuffnCode Mini Project

**Retrofitted Blood Pressure System** — dokumentasi untuk mata kuliah *Komputasi Paralel dan Sistem Terdistribusi* (ITENAS IFB 206).

Program: [`Host-Simulation/`](../tree/main/Host-Simulation) · Fork: [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)

Proyek referensi hardware: [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)  
Catatan desain: [Obsidian Publish — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## Menjalankan program

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py
```

---

## 1. Latar Belakang

**CuffnCode** adalah sistem pengukuran tekanan darah hasil retrofit untuk pengajaran dan riset. Fokus tim kami: **lapisan Host** — pemrosesan sinyal **paralel** dan **terdistribusi**.

---

## 2. Arsitektur

| Subsistem | Komponen |
|-----------|----------|
| Sensor | MPS20N0040D |
| AFE | AD620 + TLC2272 |
| MCU | STM32F411CE |
| Host | Parallel + distributed pipeline + GUI |

---

## 3. Komputasi Paralel

Data parallelism — `multiprocessing.Pool.map` pada chunk waveform (notch 50 Hz + moving average).

---

## 4. Sistem Terdistribusi

Node A (acquire) → Node B (process) → Node C (store) via `Queue`.

---

## 5. Tim

| Nama | NRP | Kelas |
|------|-----|-------|
| Farhan Kamil Hermansyah | 152024150 | CC |
| Ratu Qolbu Maziah | 152024151 | CC |
| Syafa Meisya Fitria | 152024182 | AA |

---

## 6. Kredit

- [CuffnCode — IFAC Activity Fund](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)
- [Obsidian — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)
