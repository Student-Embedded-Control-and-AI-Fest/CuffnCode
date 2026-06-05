import time
from concurrent.futures import ThreadPoolExecutor
from retail_core import aggregate_transactions, merge_results

def worker_task(worker_id, lines):
    """
    Sub-task run by each worker thread to aggregate its share of data.
    """
    # Track worker start and end time
    start = time.time()
    result = aggregate_transactions(lines)
    duration = time.time() - start
    return result, duration

def run_parallel(distributed_lines, num_workers):
    """
    Orchestrates parallel execution (MIMD model) using ThreadPoolExecutor.
    distributed_lines is a list of lists of lines (one list per worker).
    """
    start_time = time.time()
    
    worker_results = []
    worker_durations = {}
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit tasks for all workers
        futures = {
            executor.submit(worker_task, i, distributed_lines[i]): i
            for i in range(num_workers)
        }
        
        # Collect results as they complete
        for future in futures:
            worker_id = futures[future]
            res, duration = future.result()
            worker_results.append(res)
            worker_durations[worker_id] = duration
            
    # Merge the results from all workers
    final_results = merge_results(worker_results)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return final_results, execution_time, worker_durations
