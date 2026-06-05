import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Optional

from retail_core import RevenueReport, summarize_transactions


class MIMDProcessor:
    def __init__(self, data: List[Dict], num_workers: int = 4,
                 data_distribution: Optional[Dict] = None,
                 on_progress: Optional[Callable] = None):

        if not data:
            raise ValueError("Dataset tidak boleh kosong")
        if num_workers < 2:
            raise ValueError("MIMD membutuhkan minimal 2 worker")

        self.data = data
        self.num_workers = num_workers
        self.data_distribution = data_distribution
        self.on_progress = on_progress

        self.partial_results = {}
        self.worker_stats = {}
        self.total_time = 0.0
        self.merged_results = {}

        self._lock = threading.Lock()
        self._progress_counter = 0

    def _worker_function(self, worker_id: int, chunk: List[Dict]) -> Dict:
        worker_name = f"Worker-{worker_id}"
        started_at = time.perf_counter()
        report = summarize_transactions(chunk)
        elapsed = time.perf_counter() - started_at

        return {
            "name": worker_name,
            "report": report,
            "stats": {
                "rows_processed": len(chunk),
                "valid_rows": report.valid_rows,
                "total_time": elapsed,
            },
        }

    def _distribute_data(self) -> Dict[int, List[Dict]]:
        chunks = {}

        if self.data_distribution:
            for worker_id, indexes in self.data_distribution.items():
                chunks[worker_id] = [self.data[index] for index in indexes]
        else:
            total = len(self.data)
            chunk_size = total // self.num_workers
            remainder = total % self.num_workers

            current = 0
            for w in range(1, self.num_workers + 1):
                size = chunk_size + (1 if w <= remainder else 0)
                chunks[w] = self.data[current:current + size]
                current += size

        return chunks

    def run(self) -> Dict:
        self.partial_results = {}
        self.worker_stats = {}
        self._progress_counter = 0

        data_chunks = self._distribute_data()
        combined_report = RevenueReport()
        started_at = time.perf_counter()

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(
                    self._worker_function,
                    worker_id,
                    data_chunks.get(worker_id, []),
                ): worker_id
                for worker_id in range(1, self.num_workers + 1)
            }

            for future in as_completed(futures):
                worker_id = futures[future]
                worker_result = future.result()
                worker_name = worker_result["name"]
                worker_report = worker_result["report"]

                combined_report.absorb(worker_report)
                self.partial_results[worker_name] = worker_report
                self.worker_stats[worker_name] = worker_result["stats"]

                if self.on_progress:
                    with self._lock:
                        self._progress_counter += len(data_chunks.get(worker_id, []))
                        self.on_progress(self._progress_counter, len(self.data))

        self.total_time = time.perf_counter() - started_at
        self.merged_results = combined_report.to_dict(len(self.data))

        if self.on_progress:
            self.on_progress(len(self.data), len(self.data))

        worker_distribution = {}
        for worker_id in range(1, self.num_workers + 1):
            worker_name = f"Worker-{worker_id}"
            worker_distribution[worker_name] = len(
                data_chunks.get(worker_id, [])
            )

        return {
            'mode': 'MIMD',
            'total_time': self.total_time,
            'results': self.merged_results,
            'num_rows': len(self.data),
            'num_workers': self.num_workers,
            'worker_distribution': worker_distribution,
            'worker_stats': self.worker_stats
        }
