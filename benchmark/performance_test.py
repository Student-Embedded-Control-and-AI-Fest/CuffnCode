import random
import time

from multiprocessing import Pool


def analyze_energy(data):

    total = sum(data.values())

    average = total / len(data)

    return total, average


def generate_dataset(size):

    dataset = []

    for _ in range(size):

        dataset.append({
            "hvac": random.randint(300,700),
            "lighting": random.randint(100,350),
            "elevator": random.randint(200,600),
            "server": random.randint(400,900),
            "solar": random.randint(100,500)
        })

    return dataset


def sequential_test(dataset):

    start = time.time()

    results = []

    for item in dataset:
        results.append(
            analyze_energy(item)
        )

    end = time.time()

    return end - start


def parallel_test(dataset):

    start = time.time()

    with Pool() as pool:

        pool.map(
            analyze_energy,
            dataset
        )

    end = time.time()

    return end - start


def main():

    dataset = generate_dataset(100000)

    sequential_time = sequential_test(dataset)

    parallel_time = parallel_test(dataset)

    print("\nBENCHMARK RESULT")
    print("-" * 40)

    print(
        f"Sequential Time : {sequential_time:.4f} sec"
    )

    print(
        f"Parallel Time   : {parallel_time:.4f} sec"
    )

    print(
        f"Speedup         : "
        f"{sequential_time/parallel_time:.2f}x"
    )


if __name__ == "__main__":
    main()