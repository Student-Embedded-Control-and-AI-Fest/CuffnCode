import argparse
import sys
from scheduler import run_benchmark

def main():
    parser = argparse.ArgumentParser(
        description="Parallel Job Scheduler - Retail Workload Benchmark (SISD vs MIMD)"
    )
    
    parser.add_argument(
        "-f", "--file",
        default="OnlineRetail.csv",
        help="Path to the OnlineRetail.csv dataset file (default: OnlineRetail.csv)"
    )
    
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of worker threads for MIMD parallel execution (default: 4)"
    )
    
    parser.add_argument(
        "-s", "--strategy",
        choices=["equal", "round_robin", "weighted"],
        default="equal",
        help="Load balancing strategy to distribute transactions (default: equal)"
    )
    
    parser.add_argument(
        "--weights",
        help="Comma-separated list of worker weights (e.g. 3,2,1,1). Required for 'weighted' strategy."
    )
    
    args = parser.parse_args()
    
    # Process weights
    weights = None
    if args.strategy == "weighted":
        if not args.weights:
            parser.error("The --weights argument is required when using the 'weighted' strategy.")
        try:
            weights = [int(w.strip()) for w in args.weights.split(",")]
            if len(weights) != args.workers:
                parser.error(f"Number of weights ({len(weights)}) must match the number of workers ({args.workers}).")
        except ValueError:
            parser.error("Weights must be a comma-separated list of integers.")
            
    print("=" * 70)
    print("    PARALLEL JOB SCHEDULER — RETAIL WORKLOAD BENCHMARK (SISD vs MIMD)")
    print("=" * 70)
    print(f"Dataset File : {args.file}")
    print(f"Workers      : {args.workers}")
    print(f"Strategy     : {args.strategy}")
    if weights:
        print(f"Weights      : {weights}")
    print("-" * 70)
    
    try:
        report = run_benchmark(args.file, args.workers, args.strategy, weights)
        
        # Print results table
        print("\n" + "=" * 70)
        print("    BENCHMARK PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"SISD Execution Time (s) : {report['performance']['sequential_time_sec']:.4f}")
        print(f"MIMD Execution Time (s) : {report['performance']['parallel_time_sec']:.4f}")
        print(f"Calculated Speedup      : {report['performance']['speedup']}x")
        print(f"Calculated Efficiency   : {report['performance']['efficiency'] * 100:.1f}%")
        print(f"Result Verification     : {'[PASSED] ' + report['verification']['message'] if report['verification']['is_valid'] else '[FAILED] ' + report['verification']['message']}")
        print("-" * 70)
        
        print("\n" + "=" * 70)
        print("    LOAD BALANCING ANALYSIS")
        print("=" * 70)
        print("Worker ID | Assigned Records | Execution Time (s)")
        print("-" * 70)
        for w_id in range(args.workers):
            count = report['load_balancing']['distribution_counts'][w_id]
            dur = report['load_balancing']['worker_durations_sec'][str(w_id)]
            print(f"Worker {w_id:2d} | {count:16d} | {dur:.4f}")
        print(f"Max Load Deviation      : {report['load_balancing']['max_deviation_percent']}%")
        print("-" * 70)
        
        print("\n" + "=" * 70)
        print("    TOP 10 RETAIL PRODUCTS BY REVENUE")
        print("=" * 70)
        print(f"{'StockCode':10} | {'Description':40} | {'Revenue':12}")
        print("-" * 70)
        for code, info in report['results']['top_10_products'].items():
            desc = info['description'][:40]
            rev = f"${info['revenue']:,.2f}"
            print(f"{code:10} | {desc:40} | {rev:>12}")
        print("=" * 70)
        print(f"Total Aggregated Revenue: ${report['results']['total_revenue']:,.2f}")
        print(f"Total Aggregated Units  : {report['results']['total_quantity']:,}")
        print(f"Valid Lines Processed   : {report['results']['processed_count']:,}")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {str(e)}", file=sys.stderr)
        print("Please ensure OnlineRetail.csv exists or generate a sample dataset first.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
