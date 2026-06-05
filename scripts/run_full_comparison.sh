#!/usr/bin/env bash
set -euo pipefail

SIMULATIONS="${1:-30000}"
DAYS="${2:-60}"
WORKERS="${3:-4}"
CSV_PATH="${4:-data/sample_prices.csv}"
if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  PYTHON_BIN="python"
fi

mkdir -p output/full_comparison_shards

echo "=== Full Comparison: Serial vs Parallel vs Distributed/Shard ==="
echo "Simulations: ${SIMULATIONS}"
echo "Days       : ${DAYS}"
echo "Workers    : ${WORKERS}"
echo

echo "[1/4] Running serial..."
"$PYTHON_BIN" src/stock_monte_carlo.py simulate \
  --mode serial \
  --csv "$CSV_PATH" \
  --simulations "$SIMULATIONS" \
  --days "$DAYS" \
  --out output/full_serial

echo
echo "[2/4] Running parallel with ${WORKERS} workers..."
"$PYTHON_BIN" src/stock_monte_carlo.py simulate \
  --mode parallel \
  --workers "$WORKERS" \
  --csv "$CSV_PATH" \
  --simulations "$SIMULATIONS" \
  --days "$DAYS" \
  --out output/full_parallel

echo
echo "[3/4] Running distributed shards..."
for shard_index in $(seq 0 $((WORKERS - 1))); do
  "$PYTHON_BIN" src/stock_monte_carlo.py shard \
    --shard-index "$shard_index" \
    --num-shards "$WORKERS" \
    --csv "$CSV_PATH" \
    --simulations "$SIMULATIONS" \
    --days "$DAYS" \
    --out "output/full_comparison_shards/shard_${shard_index}.npz"
done

echo
echo "[4/4] Merging distributed shards..."
"$PYTHON_BIN" src/stock_monte_carlo.py merge \
  --inputs "output/full_comparison_shards/shard_*.npz" \
  --out output/full_distributed

"$PYTHON_BIN" - <<'PY_REPORT'
import csv
import json
from pathlib import Path

import numpy as np

output = Path('output')
serial = json.loads((output / 'full_serial_summary.json').read_text())
parallel = json.loads((output / 'full_parallel_summary.json').read_text())
distributed = json.loads((output / 'full_distributed_summary.json').read_text())

shard_times = []
for shard_path in sorted((output / 'full_comparison_shards').glob('shard_*.npz')):
    with np.load(shard_path, allow_pickle=False) as data:
        metadata = json.loads(str(data['metadata']))
    shard_times.append(float(metadata['elapsed_seconds']))

serial_time = float(serial['elapsed_seconds'])
parallel_time = float(parallel['elapsed_seconds'])
# Jika shard dijalankan di beberapa node secara bersamaan, waktu idealnya mendekati shard paling lama + waktu merge.
distributed_estimated_time = max(shard_times) if shard_times else 0.0
distributed_sequential_time = sum(shard_times)

rows = [
    {
        'method': 'serial',
        'simulations': serial['simulations'],
        'workers_or_shards': 1,
        'elapsed_seconds': serial_time,
        'speedup_vs_serial': 1.0,
        'efficiency': 1.0,
        'profit_percent': serial['probability_profit'] * 100,
        'loss_percent': serial['probability_loss'] * 100,
        'var_95_percent': serial['var_95_percent'],
        'note': 'baseline',
    },
    {
        'method': 'parallel',
        'simulations': parallel['simulations'],
        'workers_or_shards': parallel['workers'],
        'elapsed_seconds': parallel_time,
        'speedup_vs_serial': serial_time / parallel_time if parallel_time else 0.0,
        'efficiency': (serial_time / parallel_time / parallel['workers']) if parallel_time and parallel['workers'] else 0.0,
        'profit_percent': parallel['probability_profit'] * 100,
        'loss_percent': parallel['probability_loss'] * 100,
        'var_95_percent': parallel['var_95_percent'],
        'note': 'actual local multiprocessing',
    },
    {
        'method': 'distributed_shard_estimate',
        'simulations': distributed['simulations'],
        'workers_or_shards': distributed['workers'],
        'elapsed_seconds': distributed_estimated_time,
        'speedup_vs_serial': serial_time / distributed_estimated_time if distributed_estimated_time else 0.0,
        'efficiency': (serial_time / distributed_estimated_time / distributed['workers']) if distributed_estimated_time and distributed['workers'] else 0.0,
        'profit_percent': distributed['probability_profit'] * 100,
        'loss_percent': distributed['probability_loss'] * 100,
        'var_95_percent': distributed['var_95_percent'],
        'note': 'estimated if shards run concurrently on nodes',
    },
    {
        'method': 'distributed_shard_sequential',
        'simulations': distributed['simulations'],
        'workers_or_shards': distributed['workers'],
        'elapsed_seconds': distributed_sequential_time,
        'speedup_vs_serial': serial_time / distributed_sequential_time if distributed_sequential_time else 0.0,
        'efficiency': (serial_time / distributed_sequential_time / distributed['workers']) if distributed_sequential_time and distributed['workers'] else 0.0,
        'profit_percent': distributed['probability_profit'] * 100,
        'loss_percent': distributed['probability_loss'] * 100,
        'var_95_percent': distributed['var_95_percent'],
        'note': 'actual if shards are run one-by-one on this laptop',
    },
]

csv_path = output / 'full_comparison.csv'
with csv_path.open('w', newline='', encoding='utf-8') as handle:
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            key: f'{value:.6f}' if isinstance(value, float) else value
            for key, value in row.items()
        })

lines = []
lines.append('=== HASIL PERBANDINGAN ===')
lines.append(f"{'method':30} {'sim':>8} {'w/s':>5} {'time(s)':>10} {'speedup':>9} {'eff':>8} {'profit%':>9} {'loss%':>8} {'VaR95%':>8}")
lines.append('-' * 105)
for row in rows:
    lines.append(
        f"{row['method']:30} "
        f"{row['simulations']:8} "
        f"{row['workers_or_shards']:5} "
        f"{row['elapsed_seconds']:10.6f} "
        f"{row['speedup_vs_serial']:9.4f} "
        f"{row['efficiency']:8.4f} "
        f"{row['profit_percent']:9.2f} "
        f"{row['loss_percent']:8.2f} "
        f"{row['var_95_percent']:8.2f}"
    )

lines.append('')
lines.append('File output:')
lines.append('- output/full_comparison.csv')
lines.append('- output/full_serial_summary.csv')
lines.append('- output/full_parallel_summary.csv')
lines.append('- output/full_distributed_summary.csv')
lines.append('')
lines.append('Catatan: distributed_shard_estimate memakai waktu shard paling lama, asumsi shard jalan bersamaan di beberapa node.')
lines.append('distributed_shard_sequential memakai total waktu shard jika semua shard dijalankan satu per satu di laptop ini.')

report = '\n'.join(lines)
print('\n' + report)
(output / 'full_comparison_report.txt').write_text(report + '\n', encoding='utf-8')
PY_REPORT
