#!/usr/bin/env python3
"""Monte Carlo stock price simulation with serial, parallel, and sharded modes."""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import multiprocessing as mp
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_input_path(path_value: str) -> str:
    path = Path(path_value)
    if path.is_absolute() or path.exists():
        return str(path)
    project_path = PROJECT_ROOT / path
    return str(project_path)


def resolve_output_prefix(path_value: str) -> str:
    path = Path(path_value)
    if path.is_absolute():
        return str(path)
    return str(PROJECT_ROOT / path)


def resolve_input_patterns(patterns: list[str]) -> list[str]:
    resolved = []
    for pattern in patterns:
        path = Path(pattern)
        if path.is_absolute() or glob.glob(pattern):
            resolved.append(pattern)
        else:
            resolved.append(str(PROJECT_ROOT / path))
    return resolved


@dataclass
class MarketParams:
    initial_price: float
    daily_mu: float
    daily_sigma: float
    observations: int
    price_column: str


@dataclass
class Summary:
    mode: str
    simulations: int
    days: int
    workers: int
    elapsed_seconds: float
    initial_price: float
    mean_final_price: float
    median_final_price: float
    min_final_price: float
    max_final_price: float
    probability_profit: float
    probability_loss: float
    var_95_percent: float
    expected_shortfall_95_percent: float
    percentile_5: float
    percentile_95: float
    daily_mu: float
    daily_sigma: float


def read_prices(csv_path: str, price_column: str) -> list[float]:
    prices: list[float] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or price_column not in reader.fieldnames:
            fields = ", ".join(reader.fieldnames or [])
            raise ValueError(
                f"Kolom harga '{price_column}' tidak ditemukan. Kolom tersedia: {fields}"
            )

        for row_number, row in enumerate(reader, start=2):
            value = row.get(price_column, "").strip()
            if not value:
                continue
            try:
                price = float(value)
            except ValueError as exc:
                raise ValueError(
                    f"Nilai harga tidak valid di baris {row_number}: {value!r}"
                ) from exc
            if price <= 0:
                raise ValueError(f"Harga harus positif di baris {row_number}: {price}")
            prices.append(price)

    if len(prices) < 3:
        raise ValueError("Butuh minimal 3 data harga untuk menghitung return historis.")
    return prices


def estimate_market_params(csv_path: str, price_column: str) -> MarketParams:
    prices = np.asarray(read_prices(resolve_input_path(csv_path), price_column), dtype=np.float64)
    log_returns = np.diff(np.log(prices))
    return MarketParams(
        initial_price=float(prices[-1]),
        daily_mu=float(np.mean(log_returns)),
        daily_sigma=float(np.std(log_returns, ddof=1)),
        observations=int(prices.size),
        price_column=price_column,
    )


def split_counts(total: int, parts: int) -> list[int]:
    if total < 1:
        raise ValueError("Jumlah simulasi harus lebih dari 0.")
    if parts < 1:
        raise ValueError("Jumlah partisi/worker harus lebih dari 0.")
    base = total // parts
    remainder = total % parts
    return [base + (1 if i < remainder else 0) for i in range(parts)]


def simulate_chunk(
    simulations: int,
    days: int,
    params: MarketParams,
    seed: int,
    sample_paths: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    terminal_prices = np.empty(simulations, dtype=np.float64)
    paths_to_store = min(sample_paths, simulations)
    stored_paths = np.empty((paths_to_store, days + 1), dtype=np.float64)

    drift = params.daily_mu - 0.5 * params.daily_sigma**2
    initial_price = params.initial_price

    for index in range(simulations):
        shocks = rng.normal(0.0, 1.0, size=days)
        increments = drift + params.daily_sigma * shocks
        path = initial_price * np.exp(np.cumsum(increments))
        terminal_prices[index] = path[-1]
        if index < paths_to_store:
            stored_paths[index, 0] = initial_price
            stored_paths[index, 1:] = path

    return terminal_prices, stored_paths


def simulate_serial(
    simulations: int,
    days: int,
    params: MarketParams,
    seed: int,
    sample_paths: int,
) -> tuple[np.ndarray, np.ndarray]:
    return simulate_chunk(simulations, days, params, seed, sample_paths)


def _parallel_worker(payload: tuple[int, int, MarketParams, int, int]) -> tuple[np.ndarray, np.ndarray]:
    return simulate_chunk(*payload)


def simulate_parallel(
    simulations: int,
    days: int,
    params: MarketParams,
    seed: int,
    workers: int,
    sample_paths: int,
) -> tuple[np.ndarray, np.ndarray]:
    counts = [count for count in split_counts(simulations, workers) if count > 0]
    path_quotas = split_counts(sample_paths, len(counts)) if sample_paths > 0 else [0] * len(counts)
    payloads = [
        (count, days, params, seed + worker_index * 100_003, path_quotas[worker_index])
        for worker_index, count in enumerate(counts)
    ]

    with mp.Pool(processes=len(payloads)) as pool:
        results = pool.map(_parallel_worker, payloads)

    terminal_prices = np.concatenate([result[0] for result in results])
    stored_paths = stack_paths((result[1] for result in results), sample_paths)
    return terminal_prices, stored_paths


def stack_paths(path_arrays: Iterable[np.ndarray], limit: int) -> np.ndarray:
    arrays = [array for array in path_arrays if array.size > 0]
    if not arrays or limit <= 0:
        return np.empty((0, 0), dtype=np.float64)
    return np.concatenate(arrays, axis=0)[:limit]


def summarize(
    terminal_prices: np.ndarray,
    params: MarketParams,
    days: int,
    mode: str,
    workers: int,
    elapsed_seconds: float,
) -> Summary:
    returns = (terminal_prices - params.initial_price) / params.initial_price
    loss_returns = -returns
    var_95 = float(np.percentile(loss_returns, 95))
    tail_losses = loss_returns[loss_returns >= var_95]
    expected_shortfall = float(np.mean(tail_losses)) if tail_losses.size else var_95

    return Summary(
        mode=mode,
        simulations=int(terminal_prices.size),
        days=days,
        workers=workers,
        elapsed_seconds=elapsed_seconds,
        initial_price=params.initial_price,
        mean_final_price=float(np.mean(terminal_prices)),
        median_final_price=float(np.median(terminal_prices)),
        min_final_price=float(np.min(terminal_prices)),
        max_final_price=float(np.max(terminal_prices)),
        probability_profit=float(np.mean(terminal_prices > params.initial_price)),
        probability_loss=float(np.mean(terminal_prices < params.initial_price)),
        var_95_percent=var_95 * 100.0,
        expected_shortfall_95_percent=expected_shortfall * 100.0,
        percentile_5=float(np.percentile(terminal_prices, 5)),
        percentile_95=float(np.percentile(terminal_prices, 95)),
        daily_mu=params.daily_mu,
        daily_sigma=params.daily_sigma,
    )


def ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def write_summary(summary: Summary, out_prefix: str) -> None:
    json_path = f"{out_prefix}_summary.json"
    csv_path = f"{out_prefix}_summary.csv"
    ensure_parent(json_path)

    payload = asdict(summary)
    payload["created_at"] = datetime.now().isoformat(timespec="seconds")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(payload.keys()))
        writer.writeheader()
        writer.writerow(payload)


def write_terminal_prices(terminal_prices: np.ndarray, out_prefix: str) -> None:
    path = f"{out_prefix}_terminal_prices.csv"
    ensure_parent(path)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["simulation", "final_price"])
        for index, price in enumerate(terminal_prices, start=1):
            writer.writerow([index, f"{price:.6f}"])


def create_plots(
    terminal_prices: np.ndarray,
    paths: np.ndarray,
    params: MarketParams,
    out_prefix: str,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        create_svg_plots(terminal_prices, paths, params, out_prefix)
        return

    hist_path = f"{out_prefix}_histogram.png"
    paths_path = f"{out_prefix}_paths.png"
    ensure_parent(hist_path)

    plt.figure(figsize=(10, 6))
    plt.hist(terminal_prices, bins=50, color="#2563eb", edgecolor="white", alpha=0.9)
    plt.axvline(params.initial_price, color="#dc2626", linestyle="--", label="Harga awal")
    plt.title("Distribusi Harga Akhir Simulasi Monte Carlo")
    plt.xlabel("Harga akhir")
    plt.ylabel("Frekuensi")
    plt.legend()
    plt.tight_layout()
    plt.savefig(hist_path, dpi=150)
    plt.close()

    if paths.size > 0:
        plt.figure(figsize=(10, 6))
        for path in paths:
            plt.plot(path, linewidth=1.1, alpha=0.75)
        plt.title("Contoh Jalur Simulasi Harga Saham")
        plt.xlabel("Hari")
        plt.ylabel("Harga")
        plt.tight_layout()
        plt.savefig(paths_path, dpi=150)
        plt.close()


def svg_text(x: float, y: float, text: str, size: int = 14, anchor: str = "middle") -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="#111827">{escaped}</text>'
    )


def create_svg_plots(
    terminal_prices: np.ndarray,
    paths: np.ndarray,
    params: MarketParams,
    out_prefix: str,
) -> None:
    hist_path = f"{out_prefix}_histogram.svg"
    paths_path = f"{out_prefix}_paths.svg"
    ensure_parent(hist_path)
    write_histogram_svg(terminal_prices, params, hist_path)
    if paths.size > 0:
        write_paths_svg(paths, paths_path)
    print("matplotlib tidak ditemukan; grafik disimpan sebagai SVG.")


def write_histogram_svg(terminal_prices: np.ndarray, params: MarketParams, path: str) -> None:
    width, height = 1000, 620
    left, right, top, bottom = 80, 40, 60, 80
    chart_w = width - left - right
    chart_h = height - top - bottom
    counts, bins = np.histogram(terminal_prices, bins=40)
    max_count = max(int(counts.max()), 1)
    min_x, max_x = float(bins[0]), float(bins[-1])
    span = max(max_x - min_x, 1e-9)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(width / 2, 32, "Distribusi Harga Akhir Simulasi Monte Carlo", 22),
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#111827"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111827"/>',
    ]

    for count, start, end in zip(counts, bins[:-1], bins[1:]):
        x = left + ((float(start) - min_x) / span) * chart_w
        bar_w = max(((float(end) - float(start)) / span) * chart_w - 1, 1)
        bar_h = (int(count) / max_count) * chart_h
        y = top + chart_h - bar_h
        elements.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" '
            'fill="#2563eb" opacity="0.9"/>'
        )

    initial_x = left + ((params.initial_price - min_x) / span) * chart_w
    elements.extend(
        [
            f'<line x1="{initial_x:.2f}" y1="{top}" x2="{initial_x:.2f}" y2="{top + chart_h}" '
            'stroke="#dc2626" stroke-dasharray="7 6" stroke-width="2"/>',
            svg_text(initial_x + 8, top + 20, "Harga awal", 13, "start"),
            svg_text(width / 2, height - 25, "Harga akhir", 15),
            svg_text(20, height / 2, "Frekuensi", 15),
            svg_text(left, height - 50, f"{min_x:.0f}", 12),
            svg_text(left + chart_w, height - 50, f"{max_x:.0f}", 12),
            svg_text(left - 12, top + chart_h, "0", 12, "end"),
            svg_text(left - 12, top + 6, str(max_count), 12, "end"),
            "</svg>",
        ]
    )

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(elements))


def write_paths_svg(paths: np.ndarray, path: str) -> None:
    width, height = 1000, 620
    left, right, top, bottom = 80, 40, 60, 80
    chart_w = width - left - right
    chart_h = height - top - bottom
    min_y = float(np.min(paths))
    max_y = float(np.max(paths))
    span_y = max(max_y - min_y, 1e-9)
    days = max(paths.shape[1] - 1, 1)
    palette = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0891b2"]

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(width / 2, 32, "Contoh Jalur Simulasi Harga Saham", 22),
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#111827"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111827"/>',
    ]

    for index, series in enumerate(paths):
        points = []
        for day, value in enumerate(series):
            x = left + (day / days) * chart_w
            y = top + chart_h - ((float(value) - min_y) / span_y) * chart_h
            points.append(f"{x:.2f},{y:.2f}")
        color = palette[index % len(palette)]
        point_string = " ".join(points)
        elements.append(
            f'<polyline points="{point_string}" fill="none" stroke="{color}" '
            'stroke-width="1.4" opacity="0.72"/>'
        )

    elements.extend(
        [
            svg_text(width / 2, height - 25, "Hari", 15),
            svg_text(20, height / 2, "Harga", 15),
            svg_text(left, height - 50, "0", 12),
            svg_text(left + chart_w, height - 50, str(days), 12),
            svg_text(left - 12, top + chart_h, f"{min_y:.0f}", 12, "end"),
            svg_text(left - 12, top + 6, f"{max_y:.0f}", 12, "end"),
            "</svg>",
        ]
    )

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(elements))


def print_summary(summary: Summary, out_prefix: str) -> None:
    print("\n=== Ringkasan Simulasi ===")
    print(f"Mode                  : {summary.mode}")
    print(f"Simulasi              : {summary.simulations:,}")
    print(f"Horizon               : {summary.days} hari")
    print(f"Worker                : {summary.workers}")
    print(f"Waktu eksekusi        : {summary.elapsed_seconds:.4f} detik")
    print(f"Harga awal            : {summary.initial_price:.2f}")
    print(f"Rata-rata harga akhir : {summary.mean_final_price:.2f}")
    print(f"Median harga akhir    : {summary.median_final_price:.2f}")
    print(f"Persentil 5%-95%      : {summary.percentile_5:.2f} - {summary.percentile_95:.2f}")
    print(f"Peluang profit        : {summary.probability_profit * 100:.2f}%")
    print(f"Peluang rugi          : {summary.probability_loss * 100:.2f}%")
    print(f"VaR 95%               : {summary.var_95_percent:.2f}%")
    print(f"Expected Shortfall 95%: {summary.expected_shortfall_95_percent:.2f}%")
    print(f"Output prefix         : {out_prefix}")


def run_simulate(args: argparse.Namespace) -> None:
    args.out = resolve_output_prefix(args.out)
    params = estimate_market_params(args.csv, args.price_column)
    workers = max(1, args.workers)

    started = time.perf_counter()
    if args.mode == "serial":
        terminal_prices, paths = simulate_serial(
            args.simulations, args.days, params, args.seed, args.plot_paths
        )
        effective_workers = 1
    else:
        terminal_prices, paths = simulate_parallel(
            args.simulations, args.days, params, args.seed, workers, args.plot_paths
        )
        effective_workers = min(workers, args.simulations)
    elapsed = time.perf_counter() - started

    summary = summarize(
        terminal_prices,
        params,
        args.days,
        args.mode,
        effective_workers,
        elapsed,
    )

    write_summary(summary, args.out)
    if args.save_terminal_prices:
        write_terminal_prices(terminal_prices, args.out)
    if not args.no_plots:
        create_plots(terminal_prices, paths, params, args.out)
    print_summary(summary, args.out)


def run_shard(args: argparse.Namespace) -> None:
    args.out = resolve_output_prefix(args.out)
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index harus berada di rentang 0 sampai num-shards - 1.")

    params = estimate_market_params(args.csv, args.price_column)
    shard_counts = split_counts(args.simulations, args.num_shards)
    shard_simulations = shard_counts[args.shard_index]
    shard_seed = args.seed + args.shard_index * 1_000_003

    started = time.perf_counter()
    terminal_prices, paths = simulate_serial(
        shard_simulations, args.days, params, shard_seed, args.plot_paths
    )
    elapsed = time.perf_counter() - started

    metadata = {
        "mode": "shard",
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        "total_requested_simulations": args.simulations,
        "shard_simulations": shard_simulations,
        "days": args.days,
        "elapsed_seconds": elapsed,
        "params": asdict(params),
    }

    ensure_parent(args.out)
    np.savez_compressed(
        args.out,
        terminal_prices=terminal_prices,
        paths=paths,
        metadata=json.dumps(metadata),
    )
    print(
        f"Shard {args.shard_index}/{args.num_shards - 1} selesai: "
        f"{shard_simulations:,} simulasi -> {args.out}"
    )


def load_shards(patterns: list[str]) -> tuple[np.ndarray, np.ndarray, MarketParams, dict]:
    files: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        files.extend(matches if matches else [pattern])
    files = sorted(dict.fromkeys(files))
    if not files:
        raise ValueError("Tidak ada file shard yang ditemukan.")

    terminal_arrays: list[np.ndarray] = []
    path_arrays: list[np.ndarray] = []
    first_metadata: dict | None = None

    for file_path in files:
        with np.load(file_path, allow_pickle=False) as data:
            terminal_arrays.append(data["terminal_prices"])
            path_arrays.append(data["paths"])
            metadata = json.loads(str(data["metadata"]))
            if first_metadata is None:
                first_metadata = metadata

    if first_metadata is None:
        raise ValueError("Metadata shard tidak valid.")

    params = MarketParams(**first_metadata["params"])
    terminal_prices = np.concatenate(terminal_arrays)
    paths = stack_paths(path_arrays, limit=sum(array.shape[0] for array in path_arrays))
    return terminal_prices, paths, params, first_metadata


def run_merge(args: argparse.Namespace) -> None:
    args.out = resolve_output_prefix(args.out)
    terminal_prices, paths, params, metadata = load_shards(resolve_input_patterns(args.inputs))
    summary = summarize(
        terminal_prices,
        params,
        int(metadata["days"]),
        "distributed-merge",
        int(metadata["num_shards"]),
        0.0,
    )
    write_summary(summary, args.out)
    if args.save_terminal_prices:
        write_terminal_prices(terminal_prices, args.out)
    if not args.no_plots:
        create_plots(terminal_prices, paths[: args.plot_paths], params, args.out)
    print_summary(summary, args.out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulasi Monte Carlo harga saham untuk komputasi paralel dan terdistribusi."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--csv", default="data/sample_prices.csv", help="Path CSV harga historis.")
    common.add_argument("--price-column", default="close", help="Nama kolom harga penutupan.")
    common.add_argument("--days", type=int, default=60, help="Horizon prediksi dalam hari.")
    common.add_argument("--simulations", type=int, default=10000, help="Jumlah jalur simulasi.")
    common.add_argument("--seed", type=int, default=42, help="Seed random agar eksperimen reproducible.")
    common.add_argument("--plot-paths", type=int, default=30, help="Jumlah jalur yang diplot.")

    simulate = subparsers.add_parser("simulate", parents=[common], help="Jalankan simulasi serial/paralel.")
    simulate.add_argument("--mode", choices=["serial", "parallel"], default="parallel")
    simulate.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    simulate.add_argument("--out", default="output/run", help="Prefix path output.")
    simulate.add_argument("--save-terminal-prices", action="store_true")
    simulate.add_argument("--no-plots", action="store_true")
    simulate.set_defaults(func=run_simulate)

    shard = subparsers.add_parser("shard", parents=[common], help="Jalankan satu shard simulasi.")
    shard.add_argument("--shard-index", type=int, required=True)
    shard.add_argument("--num-shards", type=int, required=True)
    shard.add_argument("--out", required=True, help="Path output .npz untuk shard.")
    shard.set_defaults(func=run_shard)

    merge = subparsers.add_parser("merge", help="Gabungkan file shard menjadi ringkasan akhir.")
    merge.add_argument("--inputs", nargs="+", required=True, help="File/pola glob shard .npz.")
    merge.add_argument("--out", default="output/distributed")
    merge.add_argument("--plot-paths", type=int, default=30)
    merge.add_argument("--save-terminal-prices", action="store_true")
    merge.add_argument("--no-plots", action="store_true")
    merge.set_defaults(func=run_merge)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "days") and args.days < 1:
        raise ValueError("--days harus lebih dari 0.")
    if hasattr(args, "simulations") and args.simulations < 1:
        raise ValueError("--simulations harus lebih dari 0.")
    if hasattr(args, "plot_paths") and args.plot_paths < 0:
        raise ValueError("--plot-paths tidak boleh negatif.")
    args.func(args)


if __name__ == "__main__":
    main()
