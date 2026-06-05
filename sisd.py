import time
from retail_core import aggregate_transactions, merge_results

def run_sequential(lines):
    """
    Processes all lines in a single thread (SISD model).
    Returns the aggregated results and execution time.
    """
    start_time = time.time()
    
    # Process all lines sequentially
    raw_results = aggregate_transactions(lines)
    
    # Merge/Format results to get the top 10 products and final format
    # We pass it as a list to merge_results to ensure matching output format with MIMD
    final_results = merge_results([raw_results])
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return final_results, execution_time
