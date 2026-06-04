"""
CuffnCode Mini Project — Komputasi Paralel & Sistem Terdistribusi
Jalankan: python main.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"


def run_script(name: str, label: str) -> int:
    print(f"\n{label}\n", flush=True)
    result = subprocess.run(
        [sys.executable, str(SRC / name)],
        cwd=ROOT,
        check=False,
    )
    return result.returncode


def main() -> int:
    code = 0
    code |= run_script("parallel_pipeline.py", "[1/2] Data Parallelism — Parallel Pipeline")
    print("\n" + "=" * 55)
    code |= run_script("distributed_nodes.py", "[2/2] Distributed Systems — Multi-Node Pipeline")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
