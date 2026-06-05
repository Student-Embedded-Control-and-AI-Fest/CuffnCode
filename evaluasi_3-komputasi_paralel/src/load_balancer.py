from typing import Dict, Tuple
import statistics


class LoadBalancer:
    def __init__(self, total_rows: int, num_workers: int = 4):
        if total_rows < 1:
            raise ValueError("Total baris harus minimal 1")
        if num_workers < 1:
            raise ValueError("Jumlah worker harus minimal 1")

        self.total_rows = total_rows
        self.num_workers = num_workers

    def equal_division(self) -> Dict[int, Tuple[int, int]]:
        distribution = {}
        chunk_size = self.total_rows // self.num_workers
        remainder = self.total_rows % self.num_workers

        current = 0
        for worker_id in range(1, self.num_workers + 1):
            size = chunk_size + (1 if worker_id <= remainder else 0)
            distribution[worker_id] = (current, current + size)
            current += size

        return distribution

    def round_robin(self) -> Dict[int, Tuple[int, int]]:
        return self.equal_division()

    def weighted_by_chunk(self) -> Dict[int, Tuple[int, int]]:
        return self.equal_division()

    def get_distribution(self, strategy: str = 'equal') -> Dict[int, Tuple[int, int]]:
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
                                     distribution: Dict[int, Tuple[int, int]]
                                     ) -> float:
        counts = [end - start for start, end in distribution.values()]

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
                                  distribution: Dict[int, Tuple[int, int]]
                                  ) -> Dict:
        summary = {}
        for worker_id, (start, end) in distribution.items():
            worker_name = f"Worker-{worker_id}"
            num_rows = end - start
            summary[worker_name] = {
                'num_rows': num_rows,
                'start_index': start,
                'end_index': end,
                'percentage': round(num_rows / self.total_rows * 100, 2)
            }

        return summary
