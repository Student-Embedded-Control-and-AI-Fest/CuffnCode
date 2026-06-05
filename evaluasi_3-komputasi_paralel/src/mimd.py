import time
import threading
import hashlib
from typing import List, Dict, Optional, Callable

from sisd import HASH_ITERATIONS, BATCH_SLEEP_INTERVAL, BATCH_SLEEP_DURATION


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

    def _parse_row(self, row: Dict) -> Optional[Dict]:
        try:
            quantity = int(row.get('Quantity', 0))
            unit_price = float(row.get('UnitPrice', 0.0))
            description = row.get('Description', '').strip()
            country = row.get('Country', 'Unknown').strip()
            stock_code = row.get('StockCode', '').strip()

            if quantity <= 0 or unit_price <= 0:
                return None

            revenue = quantity * unit_price

            data_str = f"{stock_code}:{description}:{quantity}:{unit_price}"
            data_bytes = data_str.encode()
            for _ in range(HASH_ITERATIONS):
                data_bytes = hashlib.sha256(data_bytes).digest()

            return {
                'quantity': quantity,
                'unit_price': unit_price,
                'revenue': revenue,
                'description': description,
                'country': country,
                'stock_code': stock_code
            }

        except (ValueError, TypeError):
            return None

    def _worker_function(self, worker_id: int, chunk: List[Dict]):
        worker_name = f"Worker-{worker_id}"
        worker_start = time.time()

        partial_revenue = 0.0
        partial_quantity = 0
        partial_country_revenue = {}
        partial_product_revenue = {}
        valid_rows = 0
        invalid_rows = 0

        for i, row in enumerate(chunk):
            parsed = self._parse_row(row)

            if parsed is None:
                invalid_rows += 1
                continue

            valid_rows += 1
            partial_revenue += parsed['revenue']
            partial_quantity += parsed['quantity']

            country = parsed['country']
            if country in partial_country_revenue:
                partial_country_revenue[country] += parsed['revenue']
            else:
                partial_country_revenue[country] = parsed['revenue']

            desc = parsed['description']
            if desc:
                if desc in partial_product_revenue:
                    partial_product_revenue[desc] += parsed['revenue']
                else:
                    partial_product_revenue[desc] = parsed['revenue']

            if (i + 1) % BATCH_SLEEP_INTERVAL == 0:
                time.sleep(BATCH_SLEEP_DURATION)

            if self.on_progress and (i + 1) % 50000 == 0:
                with self._lock:
                    self._progress_counter += 50000
                    self.on_progress(self._progress_counter, len(self.data))

        worker_end = time.time()

        with self._lock:
            self.partial_results[worker_name] = {
                'total_revenue': partial_revenue,
                'total_quantity': partial_quantity,
                'revenue_per_country': partial_country_revenue,
                'product_revenue': partial_product_revenue,
                'valid_rows': valid_rows,
                'invalid_rows': invalid_rows
            }

            self.worker_stats[worker_name] = {
                'rows_processed': len(chunk),
                'valid_rows': valid_rows,
                'total_time': worker_end - worker_start
            }

    def _merge_results(self):
        total_revenue = 0.0
        total_quantity = 0
        merged_country_revenue = {}
        merged_product_revenue = {}
        total_valid = 0
        total_invalid = 0

        for worker_name, partial in self.partial_results.items():
            total_revenue += partial['total_revenue']
            total_quantity += partial['total_quantity']
            total_valid += partial['valid_rows']
            total_invalid += partial['invalid_rows']

            for country, rev in partial['revenue_per_country'].items():
                if country in merged_country_revenue:
                    merged_country_revenue[country] += rev
                else:
                    merged_country_revenue[country] = rev

            for product, rev in partial['product_revenue'].items():
                if product in merged_product_revenue:
                    merged_product_revenue[product] += rev
                else:
                    merged_product_revenue[product] = rev

        sorted_countries = {
            k: round(v, 2)
            for k, v in sorted(
                merged_country_revenue.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }

        sorted_products = sorted(
            merged_product_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        top_10 = [
            {'product': name, 'revenue': round(rev, 2)}
            for name, rev in sorted_products
        ]

        self.merged_results = {
            'total_revenue': round(total_revenue, 2),
            'total_quantity': total_quantity,
            'revenue_per_country': sorted_countries,
            'top_10_products': top_10,
            'total_rows_processed': len(self.data),
            'total_valid_rows': total_valid,
            'total_invalid_rows': total_invalid
        }

    def _distribute_data(self) -> Dict[int, List[Dict]]:
        chunks = {}

        if self.data_distribution:
            for worker_id, (start, end) in self.data_distribution.items():
                chunks[worker_id] = self.data[start:end]
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

        threads = []
        for worker_id in range(1, self.num_workers + 1):
            chunk = data_chunks.get(worker_id, [])

            thread = threading.Thread(
                target=self._worker_function,
                args=(worker_id, chunk),
                name=f"Worker-{worker_id}",
                daemon=True
            )
            threads.append(thread)

        overall_start = time.time()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self._merge_results()

        overall_end = time.time()
        self.total_time = overall_end - overall_start

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
