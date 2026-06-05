# CuffnCode — Evaluasi 3: Komputasi Paralel

> **IFB 206 Komputasi Paralel** | Semester Genap 2025/2026  
> Institut Teknologi Nasional (Itenas) Bandung

---

**CuffnCode** is a retrofitted blood pressure measurement system for teaching and research. In the long term, it aims to become an overinstrumented platform for developing and testing signal processing and control algorithms.

This **Evaluasi 3** submission adds a **Python-based parallel computing simulation** that models the pump and solenoid valve control system with a real-time GUI dashboard.

---

## Retrofitted Pump System

The system uses a DC micro-pump with 2 solenoid valves controlled via a switching circuit. The digital controller reads pressure data from an **MPS20N0040D** bridge sensor, amplified through an **AD620** instrumentation amplifier and offset with a **TLC2272** op-amp.

---

## Parallel Computing Implementation

This submission simulates the pump and valve control logic using Python's **multiprocessing** and **threading** modules.

### Architecture

```
┌─────────────────────────────────┐
│           GUI Thread            │  ← tkinter main loop
│   (plots, controls, logging)    │
└────────────┬────────────────────┘
             │  multiprocessing.Queue
             ▼
┌─────────────────────────────────┐
│     Pressure Worker Process     │  ← multiprocessing.Process
│  (physics simulation: pressure  │
│   & flow rate calculation)      │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     Signal Simulation Thread    │  ← threading.Thread
│  (real-time sensor signal with  │
│   noise, shared via Lock)       │
└─────────────────────────────────┘
```

| Mechanism | Role |
|---|---|
| `multiprocessing.Process` | Separate process for pressure & flow rate computation — non-blocking |
| `multiprocessing.Queue` | Bidirectional IPC: GUI → worker (commands), worker → GUI (data) |
| `threading.Thread` | Continuous sensor signal generation in background |
| `threading.Lock` | Synchronize access to shared signal buffer |

---

## GUI Features

- **Live pressure chart** (bar) with overpressure threshold line
- **Live flow rate chart** (L/min)
- **Real-time sensor signal** waveform (threading demo)
- **Pump ON/OFF** control → sends command to worker process
- **Solenoid Valve 1 & 2** open/close → affects simulated pressure
- **Manual pressure input** with status analysis (normal / high / overpressure)
- **System log** with timestamps

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

**Requirements:** Python 3.8+, `matplotlib`

---

## File Structure

```
evaluasi_3-komputasi_paralel/
├── main.py           ← Main program: GUI + parallel computing
├── requirements.txt  ← Dependencies (matplotlib)
└── README.md         ← This file
```

---

## Safety & Notes

- This is a **software simulation** — no real hardware is connected.
- The pressure worker process is terminated cleanly on window close.
- The signal thread uses a `threading.Lock` to prevent race conditions on the shared buffer.

---

## Credits & References

- Main CuffnCode repository: https://github.com/Student-Embedded-Control-and-AI-Fest/CuffnCode
- Project documentation: https://publish.obsidian.md/auralius/Published/CuffnCode
- Instrumentation amplifier intro: https://www.youtube.com/watch?v=O0-iczIq1aU

---

**Nama  :** senja  
**NIM   :** 152024191  
**Dosen :** Lisa Kristiana Ph.D  
**Kelas :** AA / BB / CC