from __future__ import annotations

from furniture_analytics.io import file_sha256
from furniture_analytics.validation import validate_raw_sales, validate_transformed_sales


def test_raw_validation_reproduces_baseline(raw_df, settings):
    source_hash = file_sha256(settings.paths.raw_csv)
    summary = validate_raw_sales(raw_df, settings, source_hash=source_hash)
    assert summary["raw_rows"] == 2121
    assert summary["orders"] == 1764
    assert summary["customers"] == 707
    assert round(summary["total_sales"], 4) == 741999.7953
    assert round(summary["total_profit"], 4) == 18451.2728
    assert summary["loss_lines"] == 714


def test_transformed_validation_reconciles(fact_df, settings):
    summary = validate_transformed_sales(fact_df, settings)
    assert summary["transformed_rows"] == 2121
    assert round(summary["total_sales"], 4) == 741999.7953
    assert round(summary["total_profit"], 4) == 18451.2728
