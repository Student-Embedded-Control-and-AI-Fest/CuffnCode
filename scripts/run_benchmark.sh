#!/usr/bin/env bash
set -euo pipefail

SIMULATIONS="${1:-100000}"
DAYS="${2:-60}"
CSV_PATH="${3:-data/sample_prices.csv}"

python3 src/stock_monte_carlo.py simulate \
  --mode serial \
  --csv "$CSV_PATH" \
  --simulations "$SIMULATIONS" \
  --days "$DAYS" \
  --no-plots \
  --out output/benchmark_serial

for workers in 2 4 8; do
  python3 src/stock_monte_carlo.py simulate \
    --mode parallel \
    --workers "$workers" \
    --csv "$CSV_PATH" \
    --simulations "$SIMULATIONS" \
    --days "$DAYS" \
    --no-plots \
    --out "output/benchmark_parallel_${workers}"
done

python3 - <<'PY_REPORT'
import csv
import json
from pathlib import Path

rows = []
serial_time = None
for path in sorted(Path('output').glob('benchmark_*_summary.json')):
    data = json.loads(path.read_text())
    if data['mode'] == 'serial':
        serial_time = data['elapsed_seconds']
    rows.append(data)

if serial_time is None:
    raise SystemExit('serial benchmark summary not found')

out = Path('output/benchmark_comparison.csv')
with out.open('w', newline='', encoding='utf-8') as handle:
    writer = csv.writer(handle)
    writer.writerow(['mode', 'simulations', 'workers', 'elapsed_seconds', 'speedup', 'efficiency'])
    for data in rows:
        speedup = serial_time / data['elapsed_seconds'] if data['elapsed_seconds'] else 0
        efficiency = speedup / data['workers'] if data['workers'] else 0
        writer.writerow([
            data['mode'],
            data['simulations'],
            data['workers'],
            f"{data['elapsed_seconds']:.6f}",
            f"{speedup:.4f}",
            f"{efficiency:.4f}",
        ])
print(f'Benchmark comparison saved to {out}')
PY_REPORT
