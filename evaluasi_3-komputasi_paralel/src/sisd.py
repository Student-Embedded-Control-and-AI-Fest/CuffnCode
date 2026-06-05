import time
import sys
import hashlib
from typing import List, Dict, Optional, Callable

HASH_ITERATIONS = 5
BATCH_SLEEP_INTERVAL = 1000
BATCH_SLEEP_DURATION = 0.01


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

    def run(self) -> Dict:
        total_revenue = 0.0
        total_quantity = 0
        revenue_per_country = {}
        product_revenue = {}
        valid_rows = 0
        invalid_rows = 0

        total_rows = len(self.data)
        overall_start = time.time()

        for i, row in enumerate(self.data):
            parsed = self._parse_row(row)

            if parsed is None:
                invalid_rows += 1
                continue

            valid_rows += 1
            total_revenue += parsed['revenue']
            total_quantity += parsed['quantity']

            country = parsed['country']
            if country in revenue_per_country:
                revenue_per_country[country] += parsed['revenue']
            else:
                revenue_per_country[country] = parsed['revenue']

            desc = parsed['description']
            if desc:
                if desc in product_revenue:
                    product_revenue[desc] += parsed['revenue']
                else:
                    product_revenue[desc] = parsed['revenue']

            if (i + 1) % BATCH_SLEEP_INTERVAL == 0:
                time.sleep(BATCH_SLEEP_DURATION)

            if self.on_progress and (i + 1) % 50000 == 0:
                self.on_progress(i + 1, total_rows)

        if self.on_progress:
            self.on_progress(total_rows, total_rows)

        overall_end = time.time()
        self.total_time = overall_end - overall_start

        sorted_products = sorted(
            product_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        top_10 = [
            {'product': name, 'revenue': round(rev, 2)}
            for name, rev in sorted_products
        ]

        self.results = {
            'total_revenue': round(total_revenue, 2),
            'total_quantity': total_quantity,
            'revenue_per_country': {
                k: round(v, 2)
                for k, v in sorted(
                    revenue_per_country.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'top_10_products': top_10,
            'total_rows_processed': total_rows,
            'total_valid_rows': valid_rows,
            'total_invalid_rows': invalid_rows
        }

        worker_distribution = {'Worker-SISD': total_rows}

        return {
            'mode': 'SISD',
            'total_time': self.total_time,
            'results': self.results,
            'num_rows': total_rows,
            'num_workers': 1,
            'worker_distribution': worker_distribution
        }
