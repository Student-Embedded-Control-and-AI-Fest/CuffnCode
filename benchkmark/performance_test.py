import time
from multiprocessing import Pool

from simulator.traffic_generator import generate_traffic
from nodes.controller_node import detect_vehicle


def sequential_benchmark():

    traffic_data = generate_traffic()

    lane_input = list(traffic_data.items())

    start = time.perf_counter()

    results = []

    for lane in lane_input:
        results.append(
            detect_vehicle(lane)
        )

    end = time.perf_counter()

    return end - start


def parallel_benchmark():

    traffic_data = generate_traffic()

    lane_input = list(traffic_data.items())

    start = time.perf_counter()

    with Pool(processes=4) as pool:

        results = pool.map(
            detect_vehicle,
            lane_input
        )

    end = time.perf_counter()

    return end - start


def run_benchmark():

    sequential_time = sequential_benchmark()

    parallel_time = parallel_benchmark()

    speedup = sequential_time / parallel_time

    efficiency = (speedup / 4) * 100

    print("\n" + "=" * 60)
    print("PARALLEL COMPUTING BENCHMARK")
    print("=" * 60)

    print(
        f"Sequential Time : {sequential_time:.4f} sec"
    )

    print(
        f"Parallel Time   : {parallel_time:.4f} sec"
    )

    print(
        f"Speedup         : {speedup:.2f}x"
    )

    print(
        f"Efficiency      : {efficiency:.2f}%"
    )

    print("=" * 60)