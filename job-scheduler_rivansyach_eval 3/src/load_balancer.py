import statistics
from typing import Dict, List


class LoadBalancer:
    def __init__(self, total_rows: int, num_workers: int = 4):
        if total_rows < 1:
            raise ValueError("Total baris harus minimal 1")
        if num_workers < 1:
            raise ValueError("Jumlah worker harus minimal 1")

        self.total_rows = total_rows
        self.num_workers = num_workers

    def equal_division(self) -> Dict[int, List[int]]:
        distribution = {worker_id: [] for worker_id in range(1, self.num_workers + 1)}

        for index in range(self.total_rows):
            worker_id = (index % self.num_workers) + 1
            distribution[worker_id].append(index)

        return distribution

    def round_robin(self) -> Dict[int, List[int]]:
        return self.equal_division()

    def weighted_by_chunk(self) -> Dict[int, List[int]]:
        weights = list(range(self.num_workers, 0, -1))
        distribution = {worker_id: [] for worker_id in range(1, self.num_workers + 1)}

        worker_ids = []
        for worker_id, weight in enumerate(weights, start=1):
            worker_ids.extend([worker_id] * weight)

        for index in range(self.total_rows):
            distribution[worker_ids[index % len(worker_ids)]].append(index)

        return distribution

    def get_distribution(self, strategy: str = 'equal') -> Dict[int, List[int]]:
        strategies = {
            'round_robin': self.round_robin,
            'equal': self.equal_division,
            'weighted': self.weighted_by_chunk
        }

        if strategy not in strategies:
            raise ValueError(
                f"Strategi '{strategy}' tidak dikenali"
            )

        return strategies[strategy]()

    def calculate_balance_percentage(self,
                                     distribution: Dict[int, List[int]]
                                     ) -> float:
        counts = [len(indexes) for indexes in distribution.values()]

        if all(c == 0 for c in counts):
            return 100.0

        mean = statistics.mean(counts)

        if mean == 0:
            return 100.0

        if len(counts) > 1:
            std_dev = statistics.stdev(counts)
        else:
            std_dev = 0.0

        balance = (1 - (std_dev / mean)) * 100
        return max(0.0, min(100.0, balance))

    def get_distribution_summary(self,
                                  distribution: Dict[int, List[int]]
                                  ) -> Dict:
        summary = {}
        for worker_id, indexes in distribution.items():
            worker_name = f"Worker-{worker_id}"
            num_rows = len(indexes)
            summary[worker_name] = {
                'num_rows': num_rows,
                'first_index': indexes[0] if indexes else None,
                'last_index': indexes[-1] if indexes else None,
                'percentage': round(num_rows / self.total_rows * 100, 2)
            }

        return summary
