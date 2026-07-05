"""Validation checks that protect analytical correctness."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from furniture_analytics.config import Settings
from furniture_analytics.constants import EXPECTED_CATEGORY, RAW_COLUMNS


class ValidationError(ValueError):
    """Raised when source data violates the agreed contract."""


def _failures_or_raise(failures: list[str]) -> None:
    if failures:
        message = "Validation failed:\n- " + "\n- ".join(failures)
        raise ValidationError(message)


def _close(actual: float, expected: float, tolerance: float) -> bool:
    return abs(float(actual) - float(expected)) <= tolerance


def validate_raw_sales(
    df: pd.DataFrame,
    settings: Settings,
    *,
    source_hash: str | None = None,
) -> dict[str, Any]:
    """Validate the raw line-level file before transformation."""

    failures: list[str] = []
    validation = settings.validation

    if list(df.columns) != RAW_COLUMNS:
        failures.append("Raw columns do not match the required 21-column contract.")
    if df.shape[0] != validation.expected_rows:
        failures.append(f"Expected {validation.expected_rows} rows, found {df.shape[0]}.")
    if df.shape[1] != validation.expected_columns:
        failures.append(f"Expected {validation.expected_columns} columns, found {df.shape[1]}.")
    if int(df.isna().sum().sum()) != 0:
        failures.append("Expected zero missing values in supplied baseline file.")
    if df.duplicated().any():
        failures.append("Fully duplicated rows are present.")
    if df["Row ID"].duplicated().any():
        failures.append("Row ID must be unique.")
    if df["Category"].nunique(dropna=False) != 1 or df["Category"].iloc[0] != EXPECTED_CATEGORY:
        failures.append("Category must contain exactly one value: Furniture.")
    if (df["Sales"] < 0).any():
        failures.append("Sales must be non-negative.")
    if (df["Quantity"] <= 0).any():
        failures.append("Quantity must be positive.")
    if ((df["Discount"] < 0) | (df["Discount"] > 1)).any():
        failures.append("Discount must be between 0 and 1.")
    if (df["Ship Date"] < df["Order Date"]).any():
        failures.append("Ship Date must be greater than or equal to Order Date.")
    if not _close(df["Sales"].sum(), validation.expected_total_sales, validation.tolerance):
        failures.append("Total sales does not reconcile to the baseline.")
    if not _close(df["Profit"].sum(), validation.expected_total_profit, validation.tolerance):
        failures.append("Total profit does not reconcile to the baseline.")
    if df["Order ID"].nunique() != validation.expected_orders:
        failures.append("Unique order count does not match the baseline.")
    if df["Customer ID"].nunique() != validation.expected_customers:
        failures.append("Unique customer count does not match the baseline.")
    if int((df["Profit"] < 0).sum()) != validation.expected_loss_lines:
        failures.append("Loss-making line count does not match the baseline.")
    if source_hash and source_hash != validation.expected_sha256:
        failures.append("Source SHA-256 does not match the expected Dataset.csv checksum.")

    _failures_or_raise(failures)

    return {
        "raw_rows": int(df.shape[0]),
        "raw_columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_row_ids": int(df["Row ID"].duplicated().sum()),
        "orders": int(df["Order ID"].nunique()),
        "customers": int(df["Customer ID"].nunique()),
        "total_sales": float(df["Sales"].sum()),
        "total_profit": float(df["Profit"].sum()),
        "loss_lines": int((df["Profit"] < 0).sum()),
        "category": EXPECTED_CATEGORY,
    }


def validate_transformed_sales(df: pd.DataFrame, settings: Settings) -> dict[str, Any]:
    """Validate the canonical transformed fact table."""

    failures: list[str] = []
    validation = settings.validation

    if df.shape[0] != validation.expected_rows:
        failures.append("Transformed row count changed.")
    if df["row_id"].duplicated().any():
        failures.append("Transformed row_id must stay unique.")
    if df["discount_band"].isna().any():
        failures.append("discount_band must be populated for every row.")
    if (df["shipping_days"] < 0).any():
        failures.append("shipping_days must be non-negative.")
    if int(df["is_loss_line"].sum()) != validation.expected_loss_lines:
        failures.append("Transformed loss-line count does not match baseline.")
    if not _close(df["sales"].sum(), validation.expected_total_sales, validation.tolerance):
        failures.append("Transformed sales does not reconcile to raw total.")
    if not _close(df["profit"].sum(), validation.expected_total_profit, validation.tolerance):
        failures.append("Transformed profit does not reconcile to raw total.")

    _failures_or_raise(failures)

    return {
        "transformed_rows": int(df.shape[0]),
        "transformed_columns": int(df.shape[1]),
        "total_sales": float(df["sales"].sum()),
        "total_profit": float(df["profit"].sum()),
        "loss_lines": int(df["is_loss_line"].sum()),
    }


def validate_summaries(
    fact: pd.DataFrame,
    summaries: dict[str, pd.DataFrame],
    settings: Settings,
) -> dict[str, Any]:
    """Validate summary tables reconcile to the line-level fact table."""

    failures: list[str] = []
    tolerance = settings.validation.tolerance
    fact_sales = fact["sales"].sum()
    fact_profit = fact["profit"].sum()

    for name, frame in summaries.items():
        sales_cols = [col for col in frame.columns if col.endswith("_sales") or col == "total_sales"]
        profit_cols = [col for col in frame.columns if col.endswith("_profit") or col == "total_profit"]
        if not sales_cols or not profit_cols:
            continue
        sales_col = sales_cols[0]
        profit_col = profit_cols[0]
        if not _close(frame[sales_col].sum(), fact_sales, tolerance):
            failures.append(f"{name} sales does not reconcile to fact table.")
        if not _close(frame[profit_col].sum(), fact_profit, tolerance):
            failures.append(f"{name} profit does not reconcile to fact table.")

    _failures_or_raise(failures)
    return {"summary_tables_validated": sorted(summaries)}


def validate_analysis_reconciliations(
    fact: pd.DataFrame,
    outputs: dict[str, pd.DataFrame],
    settings: Settings,
) -> dict[str, Any]:
    """Fail if required aggregate analysis tables do not reconcile to fact totals."""

    required_tables = [
        "yearly_performance",
        "region_performance",
        "sub_category_performance",
        "discount_band_performance",
    ]
    failures: list[str] = []
    tolerance = settings.validation.tolerance
    fact_sales = fact["sales"].sum()
    fact_profit = fact["profit"].sum()

    for table_name in required_tables:
        frame = outputs.get(table_name)
        if frame is None:
            failures.append(f"{table_name} was not generated.")
            continue
        if "total_sales" not in frame.columns or "total_profit" not in frame.columns:
            failures.append(f"{table_name} is missing total_sales or total_profit.")
            continue
        if not _close(frame["total_sales"].sum(), fact_sales, tolerance):
            failures.append(f"{table_name} sales does not reconcile to fact table.")
        if not _close(frame["total_profit"].sum(), fact_profit, tolerance):
            failures.append(f"{table_name} profit does not reconcile to fact table.")

    _failures_or_raise(failures)
    return {"analysis_tables_validated": required_tables}


def assert_no_duplicate_key(df: pd.DataFrame, key_cols: list[str], table_name: str) -> None:
    if df.duplicated(key_cols).any():
        raise ValidationError(f"{table_name} has duplicate rows at grain {key_cols}.")


def assert_series_close(actual: pd.Series, expected: pd.Series, tolerance: float) -> None:
    if not np.allclose(actual.to_numpy(), expected.to_numpy(), atol=tolerance, equal_nan=True):
        raise ValidationError("Series values do not match within tolerance.")
