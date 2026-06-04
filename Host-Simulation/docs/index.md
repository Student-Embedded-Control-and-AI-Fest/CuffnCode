---
title: CuffnCode — Dokumentasi Proyek
layout: default
---

# CuffnCode Mini Project

**Retrofitted Blood Pressure System** — dokumentasi untuk mata kuliah *Komputasi Paralel dan Sistem Terdistribusi*.

Proyek referensi hardware: [Student-Embedded-Control-and-AI-Fest/CuffnCode](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)  
Catatan desain: [Obsidian Publish — CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

---

## 1. Latar Belakang

**CuffnCode** adalah sistem pengukuran tekanan darah hasil retrofit untuk pengajaran dan riset. Platform ini dirancang agar dapat di-*overinstrument* untuk menguji algoritma pemrosesan sinyal dan kontrol.

Pada tugas ini, fokus kami adalah **lapisan komputasi**: bagaimana sinyal tekanan dari sensor bridge (MPS20N0040D) diproses secara **paralel** dan bagaimana subsistem dibagi menjadi **node terdistribusi**.

---

## 2. Arsitektur Sistem

### 2.1 Hardware (referensi CuffnCode)

| Subsistem | Komponen | Fungsi |
|-----------|----------|--------|
| Sensor | MPS20N0040D | Bridge tekanan millivolt (~50–100 mV FS) |
| Analog Front End | AD620 + TLC2272 | Gain ~105, offset ~1.5 V |
| Aktuator | DC micro-pump + 2 solenoid valve | Inflate / deflate cuff |
| Digital Controller | STM32F411CE (Black Pill) | ADC, PWM, komunikasi |

### 2.2 Diagram blok (konsep)

```
[Cuff + Sensor] --> [AFE: AD620/TLC2272] --> [STM32 ADC]
        |                                        |
   [Pump + Valves] <-- [STM32 GPIO/PWM] <-- [Algoritma Kontrol]
        |                                        |
        +------------ [Host / PC] <----- UART/USB (opsional)
                         |
              [Parallel Filter Pipeline]
              [Distributed: Acquire | Process | Store]
```

### 2.3 Switching pump & valve

Mengikuti desain pada [dokumentasi Obsidian](https://publish.obsidian.md/auralius/Published/CuffnCode): satu DC micro-pump menggerakkan dua solenoid valve untuk inflate dan deflate.

---

## 3. Komputasi Paralel

### 3.1 Pola: Data Parallelism (SIMD-like)

Task **sama** diterapkan ke **data berbeda** (tiap *chunk* waveform):

1. Moving average (noise reduction)
2. Notch 50 Hz (*hum killer* — sesuai roadmap CuffnCode)
3. Ekstraksi peak envelope

Implementasi: `multiprocessing.Pool.map` di `src/parallel_pipeline.py`.

### 3.2 Perbandingan scheduling

| Mode | Keterangan |
|------|------------|
| Sequential | Satu proses, chunk demi chunk |
| Parallel | `Pool` dengan beberapa worker |
| Dynamic | `chunksize=1` — load balancing untuk chunk heterogen |

### 3.3 Menjalankan benchmark

```bash
cd LECTURE_10
pip install -r requirements.txt
python main.py
```

---

## 4. Sistem Terdistribusi

### 4.1 Tiga node logis

| Node | Peran | Analog hardware |
|------|-------|-----------------|
| **A — Acquisition** | Streaming sample ADC | STM32 + sensor |
| **B — Processing** | Filter & fitur | STM32 atau host |
| **C — Storage/UI** | Agregasi hasil BP | PC / cloud |

Komunikasi: `multiprocessing.Queue` (message passing).  
Implementasi: `src/distributed_nodes.py`.

### 4.2 Alur pesan

```
Node A --{samples, batch_id}--> Node B --{features, peaks}--> Node C
         --{eof}---------------->         --{eof}------------>
```

---

## 5. Analog Front End (ringkas)

Gain instrumen AD620:

$$G = 1 + \frac{49.4\,\text{k}\Omega}{R_g} \approx 1 + \frac{49.4\,\text{k}\Omega}{470\,\Omega} \approx 105$$

Offset TLC2272:

$$\frac{56\,\text{k}}{47\,\text{k} + 56\,\text{k}} \times 3.3\,\text{V} \approx 1.5\,\text{V}$$

---

## 6. Keamanan

- Jangan over-pressure pada MPS20N0040D.
- Hindari ground noise saat power dari USB PC (ferrite pada kabel USB membantu).
- Estimasi BP pada simulasi ini **bukan** diagnosis medis.

---

## 7. Tim & Mata Kuliah

| Item | Nilai |
|------|-------|
| Mata kuliah | Komputasi Paralel dan Sistem Terdistribusi |
| Folder | `LECTURE_10` |
| Referensi | [CuffnCode GitHub](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode) |

---

## 8. Roadmap

- [ ] Integrasi data ADC nyata dari STM32
- [ ] Notch 60 Hz (region US)
- [ ] Deploy pipeline ke Raspberry Pi / edge node
- [ ] PCB layout (mengikuti repo utama)

---

## 9. Kredit

- [CuffnCode — IFAC Activity Fund project](https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode)
- Instrumentation Amps Guide — Analog Devices
- Kuliah: OpenMP/MPI, load balancing (`LECTURE_6`, `LECTURE_9`)
