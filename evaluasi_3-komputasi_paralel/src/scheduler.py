import csv
import time
import json
import os
import sys
from datetime import datetime
from typing import List, Dict

from sisd import SISDProcessor
from mimd import MIMDProcessor
from load_balancer import LoadBalancer


class DatasetLoader:
    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset tidak ditemukan: {filepath}")

        self.filepath = filepath
        self.data = []
        self.columns = []
        self.total_rows = 0

    def load(self) -> List[Dict]:
        self.data = []

        with open(self.filepath, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            self.columns = reader.fieldnames or []

            for row in reader:
                self.data.append(row)

        self.total_rows = len(self.data)
        return self.data

    def get_info(self) -> Dict:
        return {
            'filepath': self.filepath,
            'filename': os.path.basename(self.filepath),
            'total_rows': self.total_rows,
            'columns': self.columns,
            'num_columns': len(self.columns),
            'file_size_mb': round(
                os.path.getsize(self.filepath) / (1024 * 1024), 2
            )
        }


class PerformanceMetrics:
    @staticmethod
    def calculate_speedup(sisd_time: float, mimd_time: float) -> float:
        if mimd_time <= 0:
            return float('inf')
        return sisd_time / mimd_time

    @staticmethod
    def calculate_efficiency(speedup: float, num_workers: int) -> float:
        if num_workers <= 0:
            return 0.0
        return (speedup / num_workers) * 100


class Scheduler:
    def __init__(self, dataset_path: str, num_workers: int = 4,
                 lb_strategy: str = 'equal', output_fn=print,
                 progress_fn=None):
        self.dataset_path = dataset_path
        self.num_workers = num_workers
        self.lb_strategy = lb_strategy
        self.output_fn = output_fn
        self.progress_fn = progress_fn

        self.data = []
        self.dataset_info = {}
        self.sisd_result = None
        self.mimd_result = None
        self.distribution = None
        self.balance_percentage = 0.0

    def _report(self, *args, **kwargs):
        if not args and not kwargs:
            self.output_fn('')
        else:
            self.output_fn(*args, **kwargs)

    def _print_header(self):
        self._report()
        self._report("Parallel Retail Data Analyzer")
        self._report("=" * 50)
        self._report()

    def _print_progress(self, current: int, total: int, prefix: str = '', width: int = 40):
        if total <= 0:
            return

        percentage = min((current / total) * 100, 100.0)
        filled = int(width * min(current, total) // total)
        bar = "#" * filled + "-" * (width - filled)

        sys.stdout.write(
            f"\r  {prefix} [{bar}] {percentage:>5.1f}%"
        )
        sys.stdout.flush()

        if current >= total:
            self._report()

    def _report_progress(self, current: int, total: int, prefix: str = ''):
        if self.progress_fn:
            self.progress_fn(current, total, prefix)
        else:
            self._print_progress(current, total, prefix)

    def load_dataset(self):
        self._report("[1/5] Membaca dataset...")

        loader = DatasetLoader(self.dataset_path)
        load_start = time.time()
        self.data = loader.load()
        load_time = time.time() - load_start

        self.dataset_info = loader.get_info()

        self._report()
        self._report("Dataset Information")
        self._report(f"  File: {self.dataset_info['filename']}")
        self._report(f"  Total Rows: {self.dataset_info['total_rows']:,}")
        self._report(f"  Columns: {self.dataset_info['num_columns']}")
        self._report()

    def run_sisd(self):
        self._report("[2/5] Menjalankan SISD (Sequential)...")

        processor = SISDProcessor(
            self.data,
            on_progress=lambda cur, tot: self._report_progress(
                cur, tot, prefix="SISD"
            )
        )
        self.sisd_result = processor.run()

        res = self.sisd_result['results']
        self._report()
        self._report("SISD Result")
        self._report(f"  Execution Time: {self.sisd_result['total_time']:.4f} detik")
        self._report(f"  Total Revenue: {res['total_revenue']:,.2f}")
        self._report(f"  Total Quantity: {res['total_quantity']:,}")
        self._report()

    def run_mimd(self):
        self._report("[3/5] Menjalankan MIMD (Parallel)...")
        self._report(f"  Workers: {self.num_workers}")

        lb = LoadBalancer(len(self.data), self.num_workers)
        self.distribution = lb.get_distribution(self.lb_strategy)
        self.balance_percentage = lb.calculate_balance_percentage(
            self.distribution
        )

        dist_summary = lb.get_distribution_summary(self.distribution)
        for worker, info in dist_summary.items():
            count = info['num_rows']
            self._report(f"  {worker}: {count:,} baris ({info['percentage']:.2f}%)")

        self._report()

        processor = MIMDProcessor(
            self.data,
            num_workers=self.num_workers,
            data_distribution=self.distribution,
            on_progress=lambda cur, tot: self._report_progress(
                cur, tot, prefix="MIMD"
            )
        )
        self.mimd_result = processor.run()

        res = self.mimd_result['results']
        self._report()
        self._report("MIMD Result")
        self._report(f"  Execution Time: {self.mimd_result['total_time']:.4f} detik")
        self._report(f"  Total Revenue: {res['total_revenue']:,.2f}")
        self._report(f"  Total Quantity: {res['total_quantity']:,}")
        self._report()

    def _verify_results(self):
        self._report("[4/5] Verifikasi konsistensi...")

        sisd_rev = self.sisd_result['results']['total_revenue']
        mimd_rev = self.mimd_result['results']['total_revenue']
        sisd_qty = self.sisd_result['results']['total_quantity']
        mimd_qty = self.mimd_result['results']['total_quantity']

        rev_match = abs(sisd_rev - mimd_rev) < 0.01
        qty_match = sisd_qty == mimd_qty

        if rev_match and qty_match:
            self._report("  Revenue SISD = MIMD (Match)")
            self._report("  Quantity SISD = MIMD (Match)")
        else:
            self._report("  Revenue mismatch detected")

        self._report()

    def show_results(self):
        speedup = PerformanceMetrics.calculate_speedup(
            self.sisd_result['total_time'],
            self.mimd_result['total_time']
        )
        efficiency = PerformanceMetrics.calculate_efficiency(
            speedup, self.num_workers
        )

        self._report("[5/5] Performance Comparison")
        self._report()
        self._report("=" * 50)
        self._report("Performance Comparison")
        self._report("=" * 50)
        self._report()
        self._report(f"  Waktu SISD: {self.sisd_result['total_time']:.4f} detik")
        self._report(f"  Waktu MIMD: {self.mimd_result['total_time']:.4f} detik")
        self._report()
        self._report(f"  Speedup: {speedup:.2f}x")
        self._report(f"  Efficiency: {efficiency:.2f}%")
        self._report(f"  Load Balance: {self.balance_percentage:.1f}%")
        self._report()
        self._report("=" * 50)
        self._report()

        return speedup, efficiency

    def save_results(self, filepath: str = None):
        if filepath is None:
            project_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            filepath = os.path.join(project_dir, 'results.json')

        speedup = PerformanceMetrics.calculate_speedup(
            self.sisd_result['total_time'],
            self.mimd_result['total_time']
        )
        efficiency = PerformanceMetrics.calculate_efficiency(
            speedup, self.num_workers
        )

        results_data = {
            'timestamp': datetime.now().isoformat(),
            'dataset': {
                'name': self.dataset_info.get('filename', 'OnlineRetail.csv'),
                'total_rows': self.dataset_info.get('total_rows', 0),
                'columns': self.dataset_info.get('columns', []),
                'file_size_mb': self.dataset_info.get('file_size_mb', 0)
            },
            'config': {
                'num_workers': self.num_workers,
                'lb_strategy': self.lb_strategy
            },
            'sisd': {
                'total_time': round(self.sisd_result['total_time'], 4),
                'num_workers': 1,
                'total_revenue': self.sisd_result['results']['total_revenue'],
                'total_quantity': self.sisd_result['results']['total_quantity'],
                'valid_rows': self.sisd_result['results']['total_valid_rows'],
                'invalid_rows': self.sisd_result['results']['total_invalid_rows']
            },
            'mimd': {
                'total_time': round(self.mimd_result['total_time'], 4),
                'num_workers': self.num_workers,
                'total_revenue': self.mimd_result['results']['total_revenue'],
                'total_quantity': self.mimd_result['results']['total_quantity'],
                'valid_rows': self.mimd_result['results']['total_valid_rows']
            },
            'metrics': {
                'speedup': round(speedup, 4),
                'efficiency': round(efficiency, 2),
                'load_balance_percentage': round(self.balance_percentage, 2)
            },
            'worker_distribution': {},
            'revenue_result': {
                'total_revenue': self.sisd_result['results']['total_revenue'],
                'total_quantity': self.sisd_result['results']['total_quantity'],
                'top_10_products': self.sisd_result['results']['top_10_products']
            }
        }

        if self.mimd_result and 'worker_distribution' in self.mimd_result:
            results_data['worker_distribution'] = \
                self.mimd_result['worker_distribution']

        if self.mimd_result and 'worker_stats' in self.mimd_result:
            results_data['worker_stats'] = {
                k: {
                    'rows_processed': v['rows_processed'],
                    'valid_rows': v['valid_rows'],
                    'total_time': round(v['total_time'], 4)
                }
                for k, v in self.mimd_result['worker_stats'].items()
            }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)

            self._report(f"  Results saved: {filepath}")

            project_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            results_dir = os.path.join(project_dir, 'results')
            os.makedirs(results_dir, exist_ok=True)

            timestamp_name = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamped_path = os.path.join(
                results_dir, f'result_{timestamp_name}.json')

            with open(timestamped_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)

        except IOError as e:
            self._report(f"  Error saving results: {e}")

        return results_data

    def run(self) -> Dict:
        self._print_header()
        self.load_dataset()
        self.run_sisd()
        self.run_mimd()
        self._verify_results()
        self.show_results()
        self.save_results()

        self._report("Simulasi selesai")
        self._report()

        return {}
