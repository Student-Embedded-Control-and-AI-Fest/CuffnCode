import time
import json
import os
from datetime import datetime
from load_balancer import distribute_workload
from sisd import run_sequential
from mimd import run_parallel

def verify_equality(seq_res, par_res):
    """
    Verifies that the results of the sequential (SISD) and parallel (MIMD) execution are identical.
    Checks total revenue, total quantity, country breakdowns, and top 10 products.
    """
    try:
        # Check basic metrics
        revenue_diff = abs(seq_res['total_revenue'] - par_res['total_revenue'])
        if revenue_diff > 0.05:  # Tolerance for small floating point diffs
            return False, f"Revenue mismatch: SISD={seq_res['total_revenue']}, MIMD={par_res['total_revenue']}"
            
        if seq_res['total_quantity'] != par_res['total_quantity']:
            return False, f"Quantity mismatch: SISD={seq_res['total_quantity']}, MIMD={par_res['total_quantity']}"
            
        if seq_res['processed_count'] != par_res['processed_count']:
            return False, f"Processed count mismatch: SISD={seq_res['processed_count']}, MIMD={par_res['processed_count']}"
            
        # Check country results
        for country, seq_rev in seq_res['revenue_by_country'].items():
            par_rev = par_res['revenue_by_country'].get(country, 0.0)
            if abs(seq_rev - par_rev) > 0.05:
                return False, f"Country revenue mismatch for '{country}': SISD={seq_rev}, MIMD={par_rev}"
                
        # Check top 10 products (only keys because order might have slight ties, but let's check keys and values)
        seq_top = seq_res['top_10_products']
        par_top = par_res['top_10_products']
        if len(seq_top) != len(par_top):
            return False, "Top 10 products list length mismatch"
            
        for code in seq_top:
            if code not in par_top:
                return False, f"Product '{code}' missing in MIMD top products"
            if abs(seq_top[code]['revenue'] - par_top[code]['revenue']) > 0.05:
                return False, f"Product '{code}' revenue mismatch: SISD={seq_top[code]['revenue']}, MIMD={par_top[code]['revenue']}"
                
        return True, "Outputs match perfectly."
    except Exception as e:
        return False, f"Verification failed with exception: {str(e)}"

def run_benchmark(file_path, num_workers, strategy="equal", weights=None):
    """
    Runs the full benchmarking pipeline.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
        
    print(f"Loading dataset: {file_path}...")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Read all lines and skip the header
        lines = f.readlines()
        if len(lines) > 0:
            header = lines[0]
            data_lines = lines[1:]
        else:
            data_lines = []
            
    print(f"Total records loaded: {len(data_lines)}")
    
    # 1. SISD Run
    print("\nRunning SISD (Sequential Processing) Benchmark...")
    seq_results, seq_time = run_sequential(data_lines)
    print(f"SISD completed in {seq_time:.4f} seconds.")
    
    # 2. Workload Distribution
    print(f"\nDistributing workload using '{strategy}' strategy...")
    distributed_lines, distribution_counts = distribute_workload(
        data_lines, num_workers, strategy, weights
    )
    
    # 3. MIMD Run
    print(f"Running MIMD (Parallel Processing) Benchmark with {num_workers} workers...")
    par_results, par_time, worker_durations = run_parallel(distributed_lines, num_workers)
    print(f"MIMD completed in {par_time:.4f} seconds.")
    
    # 4. Verification
    is_valid, verification_msg = verify_equality(seq_results, par_results)
    print(f"Verification: {verification_msg}")
    
    # 5. Performance Metrics
    speedup = seq_time / par_time if par_time > 0 else 0.0
    efficiency = speedup / num_workers if num_workers > 0 else 0.0
    
    # 6. Load Balance Analysis
    # Ideal load balance is when each worker gets exactly the average lines count
    avg_lines = len(data_lines) / num_workers
    load_deviations = [abs(count - avg_lines) / avg_lines * 100 if avg_lines > 0 else 0.0 for count in distribution_counts]
    max_deviation = max(load_deviations) if load_deviations else 0.0
    
    benchmark_report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'configuration': {
            'dataset': file_path,
            'records_count': len(data_lines),
            'num_workers': num_workers,
            'strategy': strategy,
            'weights': weights
        },
        'performance': {
            'sequential_time_sec': round(seq_time, 4),
            'parallel_time_sec': round(par_time, 4),
            'speedup': round(speedup, 2),
            'efficiency': round(efficiency, 2)
        },
        'verification': {
            'is_valid': is_valid,
            'message': verification_msg
        },
        'load_balancing': {
            'distribution_counts': distribution_counts,
            'worker_durations_sec': {str(k): round(v, 4) for k, v in worker_durations.items()},
            'max_deviation_percent': round(max_deviation, 2)
        },
        'results': {
            'total_revenue': par_results['total_revenue'],
            'total_quantity': par_results['total_quantity'],
            'processed_count': par_results['processed_count'],
            'top_10_products': par_results['top_10_products']
        }
    }
    
    # Save output to file
    output_filename = f"benchmark_result_{int(time.time())}.json"
    with open(output_filename, 'w') as out_f:
        json.dump(benchmark_report, out_f, indent=4)
    print(f"\nBenchmark results saved to: {output_filename}")
    
    return benchmark_report
