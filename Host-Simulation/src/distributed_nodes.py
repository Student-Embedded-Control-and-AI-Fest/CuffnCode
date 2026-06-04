"""
CuffnCode — Distributed system simulation (3 logical nodes).

Node A: Acquisition  — generates / streams samples
Node B: Processing   — filter + feature extraction
Node C: Storage/UI   — aggregates BP estimate

Komunikasi antar-node via multiprocessing.Queue (message passing).
"""

import time
from multiprocessing import Process, Queue

import numpy as np

from signal_generator import generate_cuff_waveform
from filters import moving_average, notch_50hz


def node_acquisition(out_q: Queue, fs: float) -> None:
    signal, _ = generate_cuff_waveform()
    chunk_size = len(signal) // 4
    for i in range(0, len(signal), chunk_size):
        batch = signal[i : i + chunk_size]
        out_q.put({"type": "samples", "batch_id": i // chunk_size, "data": batch})
        time.sleep(0.05)
    out_q.put({"type": "eof"})
    print("[Node A | Acquisition] Streaming selesai.")


def node_processing(in_q: Queue, out_q: Queue, fs: float) -> None:
    peaks = []
    while True:
        msg = in_q.get()
        if msg["type"] == "eof":
            out_q.put({"type": "features", "peaks": peaks})
            out_q.put({"type": "eof"})
            print("[Node B | Processing] Selesai.")
            break
        batch = msg["data"]
        filtered = notch_50hz(moving_average(batch), fs)
        peaks.append(float(np.max(filtered)))
        print(f"[Node B | Processing] Batch {msg['batch_id']} diproses.")


def node_storage(in_q: Queue) -> None:
    while True:
        msg = in_q.get()
        if msg["type"] == "eof":
            break
        peaks = msg["peaks"]
        env_peak = max(peaks)
        sys = int(70 + env_peak * 0.55)
        dia = int(sys * 0.62)
        print("[Node C | Storage/UI] Hasil terkumpul.")
        print(f"  -> Distributed BP estimate: {sys}/{dia} mmHg (demo)")


def run_distributed_demo() -> None:
    print("=" * 55)
    print("  CuffnCode — Distributed Node Simulation")
    print("=" * 55)

    fs = 200.0
    q_ab: Queue = Queue()
    q_bc: Queue = Queue()

    p_a = Process(target=node_acquisition, args=(q_ab, fs))
    p_b = Process(target=node_processing, args=(q_ab, q_bc, fs))
    p_c = Process(target=node_storage, args=(q_bc,))

    t0 = time.perf_counter()
    for p in (p_a, p_b, p_c):
        p.start()
    for p in (p_a, p_b, p_c):
        p.join()
    print(f"\nTotal pipeline time: {time.perf_counter() - t0:.2f} s")


if __name__ == "__main__":
    run_distributed_demo()
