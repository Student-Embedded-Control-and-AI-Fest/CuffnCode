## Host simulation — Komputasi Paralel (ITENAS IFB 206)

**EVALUASI 3** · Semester Genap 2025/2026 · Fork: [Farmil23/CuffnCode](https://github.com/Farmil23/CuffnCode)

Simulasi pemrosesan sinyal cuff di **PC Host** setelah ADC STM32:

| Pola | Teknologi |
|------|-----------|
| Data parallelism | `multiprocessing.Pool` pada chunk waveform |
| Sistem terdistribusi | Node A (acquire) → B (process) → C (store) via `Queue` |
| Demo | GUI Tkinter + `python main.py` |

```bash
cd Host-Simulation
pip install -r requirements.txt
python gui.py
```

- Folder: [`Host-Simulation/`](Host-Simulation/)
- Dokumentasi Pages: [`docs/`](docs/)
- Detail teknis: [`Host-Simulation/docs/`](Host-Simulation/docs/)
- Desain hardware: [Obsidian CuffnCode](https://publish.obsidian.md/auralius/Published/CuffnCode)

Tim: Farhan Kamil Hermansyah (152024150), Ratu Qolbu Maziah (152024151), Syafa Meisya Fitria (152024182).
