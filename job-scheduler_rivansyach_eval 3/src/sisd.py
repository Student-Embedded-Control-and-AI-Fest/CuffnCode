import time
from typing import Callable, Dict, List, Optional

from retail_core import summarize_transactions


class SISDProcessor:
    def __init__(self, data: List[Dict], on_progress: Optional[Callable] = None):
        if not data:
            raise ValueError("Dataset tidak boleh kosong")

        self.data = data
        self.total_time = 0.0
        self.on_progress = on_progress
        self.results = {
            'total_revenue': 0.0,
            'total_quantity': 0,
            'revenue_per_country': {},
            'top_10_products': [],
            'total_rows_processed': 0,
            'total_valid_rows': 0,
            'total_invalid_rows': 0
        }

    def run(self) -> Dict:
        total_rows = len(self.data)
        started_at = time.perf_counter()

        report = summarize_transactions(
            self.data,
            on_progress=(
                lambda current: self.on_progress(current, total_rows)
                if self.on_progress else None
            ),
        )

        if self.on_progress:
            self.on_progress(total_rows, total_rows)

        self.total_time = time.perf_counter() - started_at
        self.results = report.to_dict(total_rows)

        worker_distribution = {'Worker-SISD': total_rows}

        return {
            'mode': 'SISD',
            'total_time': self.total_time,
            'results': self.results,
            'num_rows': total_rows,
            'num_workers': 1,
            'worker_distribution': worker_distribution
        }
