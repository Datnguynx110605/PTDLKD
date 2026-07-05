from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from furniture_analytics.pipeline import validate_only


def main() -> None:
    summary = validate_only()
    print("Raw data validation passed.")
    print(f"Rows: {summary['raw_rows']:,}")
    print(f"Orders: {summary['orders']:,}")
    print(f"Customers: {summary['customers']:,}")
    print(f"Sales: ${summary['total_sales']:,.2f}")
    print(f"Profit: ${summary['total_profit']:,.2f}")


if __name__ == "__main__":
    main()
