import hashlib
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional


HASH_ROUNDS = 5
PAUSE_EVERY = 1000
PAUSE_SECONDS = 0.01
PROGRESS_STEP = 50000


@dataclass
class Transaction:
    quantity: int
    price: float
    revenue: float
    product: str
    country: str
    stock_code: str


@dataclass
class RevenueReport:
    revenue: float = 0.0
    quantity: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    revenue_by_country: Dict[str, float] = field(default_factory=dict)
    revenue_by_product: Dict[str, float] = field(default_factory=dict)

    def record_invalid(self) -> None:
        self.invalid_rows += 1

    def record_sale(self, transaction: Transaction) -> None:
        self.valid_rows += 1
        self.quantity += transaction.quantity
        self.revenue += transaction.revenue
        self.revenue_by_country[transaction.country] = (
            self.revenue_by_country.get(transaction.country, 0.0)
            + transaction.revenue
        )

        if transaction.product:
            self.revenue_by_product[transaction.product] = (
                self.revenue_by_product.get(transaction.product, 0.0)
                + transaction.revenue
            )

    def absorb(self, other: "RevenueReport") -> None:
        self.revenue += other.revenue
        self.quantity += other.quantity
        self.valid_rows += other.valid_rows
        self.invalid_rows += other.invalid_rows

        for country, value in other.revenue_by_country.items():
            self.revenue_by_country[country] = (
                self.revenue_by_country.get(country, 0.0) + value
            )

        for product, value in other.revenue_by_product.items():
            self.revenue_by_product[product] = (
                self.revenue_by_product.get(product, 0.0) + value
            )

    def to_dict(self, total_rows: int) -> Dict:
        top_products = sorted(
            self.revenue_by_product.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]

        return {
            "total_revenue": round(self.revenue, 2),
            "total_quantity": self.quantity,
            "revenue_per_country": {
                country: round(value, 2)
                for country, value in sorted(
                    self.revenue_by_country.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            },
            "top_10_products": [
                {"product": product, "revenue": round(value, 2)}
                for product, value in top_products
            ],
            "total_rows_processed": total_rows,
            "total_valid_rows": self.valid_rows,
            "total_invalid_rows": self.invalid_rows,
        }


def parse_transaction(row: Dict) -> Optional[Transaction]:
    try:
        quantity = int(row.get("Quantity", 0))
        price = float(row.get("UnitPrice", 0.0))
    except (TypeError, ValueError):
        return None

    if quantity <= 0 or price <= 0:
        return None

    product = str(row.get("Description") or "").strip()
    country = str(row.get("Country") or "Unknown").strip() or "Unknown"
    stock_code = str(row.get("StockCode") or "").strip()

    payload = f"{stock_code}|{product}|{quantity}|{price}".encode("utf-8")
    for _ in range(HASH_ROUNDS):
        payload = hashlib.sha256(payload).digest()

    return Transaction(
        quantity=quantity,
        price=price,
        revenue=quantity * price,
        product=product,
        country=country,
        stock_code=stock_code,
    )


def summarize_transactions(
    rows: Iterable[Dict],
    on_progress: Optional[Callable[[int], None]] = None,
) -> RevenueReport:
    report = RevenueReport()

    for position, row in enumerate(rows, start=1):
        transaction = parse_transaction(row)
        if transaction is None:
            report.record_invalid()
        else:
            report.record_sale(transaction)

        if position % PAUSE_EVERY == 0:
            time.sleep(PAUSE_SECONDS)

        if on_progress and position % PROGRESS_STEP == 0:
            on_progress(position)

    return report
