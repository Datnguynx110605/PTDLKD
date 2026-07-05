"""End-to-end pipeline orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from furniture_analytics.analysis import build_analysis_outputs, build_summaries
from furniture_analytics.charts import create_all_figures
from furniture_analytics.config import Settings, load_settings
from furniture_analytics.io import (
    file_sha256,
    load_raw_sales,
    source_metadata,
    write_csv,
    write_json,
    write_parquet,
)
from furniture_analytics.metrics import (
    average_order_value,
    high_discount_metrics,
    loss_line_rate,
    profit_per_order,
    weighted_profit_margin,
)
from furniture_analytics.reporting import write_reports
from furniture_analytics.transform import transform_sales
from furniture_analytics.validation import (
    validate_analysis_reconciliations,
    validate_raw_sales,
    validate_summaries,
    validate_transformed_sales,
)


def build_kpis(df: pd.DataFrame) -> dict[str, float | int | None]:
    """Build project-wide baseline KPIs from the transformed fact table."""

    orders = int(df["order_id"].nunique())
    customers = int(df["customer_id"].nunique())
    repeat_orders = int(df.loc[df["is_repeat_customer"], "order_id"].nunique())
    return {
        "total_sales": float(df["sales"].sum()),
        "total_profit": float(df["profit"].sum()),
        "profit_margin": weighted_profit_margin(df),
        "quantity": int(df["quantity"].sum()),
        "orders": orders,
        "customers": customers,
        "average_order_value": average_order_value(df),
        "profit_per_order": profit_per_order(df),
        "loss_line_count": int(df["is_loss_line"].sum()),
        "loss_line_rate": loss_line_rate(df),
        "repeat_customers": int(
            df.drop_duplicates("customer_id").loc[
                lambda frame: frame["is_repeat_customer"], "customer_id"
            ].nunique()
        ),
        "repeat_order_share": repeat_orders / orders if orders else None,
    }


def build_metric_baseline(
    df: pd.DataFrame,
    source: dict[str, Any],
    raw_validation: dict[str, Any],
    transformed_validation: dict[str, Any],
    summary_validation: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    """Create the machine-readable manifest and baseline metrics file."""

    return {
        "source": source,
        "config": {
            "encoding": settings.input.encoding,
            "date_format": settings.input.date_format,
            "high_discount_review_threshold": settings.analysis.high_discount_review_threshold,
            "top_n_products": settings.analysis.top_n_products,
        },
        "validation": {
            "raw": raw_validation,
            "transformed": transformed_validation,
            "summaries": summary_validation,
        },
        "kpis": build_kpis(df),
        "high_discount_30_plus": high_discount_metrics(
            df,
            threshold=settings.analysis.high_discount_review_threshold,
        ),
    }


def write_analysis_tables(
    outputs: dict[str, pd.DataFrame],
    summaries: dict[str, pd.DataFrame],
    settings: Settings,
) -> dict[str, str]:
    """Write all principal drill-down tables to CSV."""

    table_paths: dict[str, str] = {}
    for name, frame in {**summaries, **outputs}.items():
        path = settings.paths.tables_dir / f"{name}.csv"
        write_csv(frame, path)
        table_paths[name] = str(path)
    return table_paths


def write_processed_data(
    fact: pd.DataFrame,
    summaries: dict[str, pd.DataFrame],
    settings: Settings,
) -> dict[str, str]:
    """Write required processed parquet artifacts."""

    processed_paths = {
        "furniture_sales_clean": settings.paths.processed_dir / "furniture_sales_clean.parquet",
        "order_summary": settings.paths.processed_dir / "order_summary.parquet",
        "customer_summary": settings.paths.processed_dir / "customer_summary.parquet",
        "product_summary": settings.paths.processed_dir / "product_summary.parquet",
    }
    write_parquet(fact, processed_paths["furniture_sales_clean"])
    write_parquet(summaries["order_summary"], processed_paths["order_summary"])
    write_parquet(summaries["customer_summary"], processed_paths["customer_summary"])
    write_parquet(summaries["product_summary"], processed_paths["product_summary"])
    return {name: str(path) for name, path in processed_paths.items()}


def run_pipeline(
    settings: Settings | None = None,
    *,
    settings_path: str | Path = "config/settings.yaml",
    generate_figures: bool = True,
) -> dict[str, Any]:
    """Run the full reproducible analysis pipeline."""

    resolved_settings = settings or load_settings(settings_path)
    resolved_settings.ensure_output_dirs()

    source_hash = file_sha256(resolved_settings.paths.raw_csv)
    source = source_metadata(resolved_settings.paths.raw_csv, source_hash)
    raw = load_raw_sales(
        resolved_settings.paths.raw_csv,
        encoding=resolved_settings.input.encoding,
        date_format=resolved_settings.input.date_format,
    )
    raw_validation = validate_raw_sales(raw, resolved_settings, source_hash=source_hash)

    fact = transform_sales(raw)
    transformed_validation = validate_transformed_sales(fact, resolved_settings)

    summaries = build_summaries(fact, resolved_settings)
    summary_validation = validate_summaries(fact, summaries, resolved_settings)
    outputs = build_analysis_outputs(fact, summaries, resolved_settings)
    analysis_validation = validate_analysis_reconciliations(fact, outputs, resolved_settings)

    processed_paths = write_processed_data(fact, summaries, resolved_settings)
    table_paths = write_analysis_tables(outputs, summaries, resolved_settings)

    metric_baseline = build_metric_baseline(
        fact,
        source,
        raw_validation,
        transformed_validation,
        {**summary_validation, **analysis_validation},
        resolved_settings,
    )
    metric_baseline["artifacts"] = {
        "processed": processed_paths,
        "tables": table_paths,
        "figures": {},
        "reports": {},
    }
    if generate_figures:
        metric_baseline["artifacts"]["figures"] = create_all_figures(outputs, resolved_settings)
    metric_baseline["artifacts"]["reports"] = write_reports(
        outputs,
        metric_baseline,
        resolved_settings,
    )
    baseline_path = resolved_settings.paths.processed_dir / "metric_baseline.json"
    metric_baseline["artifacts"]["metric_baseline"] = str(baseline_path)
    write_json(metric_baseline, baseline_path)
    return {
        "settings": resolved_settings,
        "raw": raw,
        "fact": fact,
        "summaries": summaries,
        "outputs": outputs,
        "metric_baseline": metric_baseline,
    }


def validate_only(
    settings: Settings | None = None,
    *,
    settings_path: str | Path = "config/settings.yaml",
) -> dict[str, Any]:
    """Load and validate the raw source without generating all artifacts."""

    resolved_settings = settings or load_settings(settings_path)
    source_hash = file_sha256(resolved_settings.paths.raw_csv)
    raw = load_raw_sales(
        resolved_settings.paths.raw_csv,
        encoding=resolved_settings.input.encoding,
        date_format=resolved_settings.input.date_format,
    )
    return validate_raw_sales(raw, resolved_settings, source_hash=source_hash)
