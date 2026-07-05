from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from furniture_analytics.pipeline import run_pipeline


def main() -> None:
    result = run_pipeline()
    baseline_path = result["metric_baseline"]["artifacts"]["metric_baseline"]
    print(f"Pipeline complete. Baseline manifest: {baseline_path}")


if __name__ == "__main__":
    main()
