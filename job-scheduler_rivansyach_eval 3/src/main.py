import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding='utf-8', errors='replace'
    )

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler import Scheduler


def get_default_dataset_path():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_dir, 'data', 'OnlineRetail.csv')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parallel Retail Data Analyzer"
    )

    parser.add_argument(
        '--data', '-d',
        type=str,
        default=None,
        help='Path dataset CSV'
    )

    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Jumlah worker (default: 4)'
    )

    parser.add_argument(
        '--strategy', '-s',
        type=str,
        default='equal',
        choices=['round_robin', 'equal', 'weighted'],
        help='Strategi load balancing'
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    dataset_path = args.data or get_default_dataset_path()

    if args.workers < 2:
        print("Error: Jumlah worker minimal 2")
        sys.exit(1)

    if not os.path.exists(dataset_path):
        print(f"Error: Dataset tidak ditemukan: {dataset_path}")
        sys.exit(1)

    try:
        scheduler = Scheduler(
            dataset_path=dataset_path,
            num_workers=args.workers,
            lb_strategy=args.strategy
        )
        scheduler.run()

    except KeyboardInterrupt:
        print("\nSimulasi dibatalkan")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
