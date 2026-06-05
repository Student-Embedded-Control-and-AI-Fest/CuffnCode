def distribute_workload(lines, num_workers, strategy="equal", weights=None):
    """
    Distributes raw CSV transaction lines among workers.
    Returns a list of lists of lines, where the index represents the worker's assigned lines,
    and a list of counts of lines distributed to each worker for load balancing analysis.
    """
    total_lines = len(lines)
    if total_lines == 0:
        return [[] for _ in range(num_workers)], [0 for _ in range(num_workers)]
        
    distributed_data = [[] for _ in range(num_workers)]
    
    if strategy == "equal":
        # Divide the dataset into equal-sized chunks
        chunk_size = total_lines // num_workers
        for i in range(num_workers):
            start = i * chunk_size
            # The last worker takes the remaining lines
            end = total_lines if i == num_workers - 1 else (i + 1) * chunk_size
            distributed_data[i] = lines[start:end]
            
    elif strategy == "round_robin":
        # Distribute lines one by one in a round-robin fashion
        for idx, line in enumerate(lines):
            worker_id = idx % num_workers
            distributed_data[worker_id].append(line)
            
    elif strategy == "weighted":
        # Distribute based on worker weights
        if not weights or len(weights) != num_workers:
            # Fallback to equal if weights are missing or misconfigured
            weights = [1] * num_workers
            
        total_weight = sum(weights)
        
        # Calculate line limits per worker
        limits = []
        accumulated = 0
        for i in range(num_workers):
            allocated = int((weights[i] / total_weight) * total_lines)
            accumulated += allocated
            limits.append(accumulated)
            
        # Adjust last worker to capture rounding differences
        limits[-1] = total_lines
        
        start = 0
        for i in range(num_workers):
            end = limits[i]
            distributed_data[i] = lines[start:end]
            start = end
            
    else:
        raise ValueError(f"Unknown load balancing strategy: {strategy}")
        
    distribution_counts = [len(chunk) for chunk in distributed_data]
    return distributed_data, distribution_counts
