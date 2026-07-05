"""Reusable business metrics with explicit aggregation rules."""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_ratio(numerator: float, denominator: float) -> float | None:
    """Return numerator / denominator, or None when the denominator is zero."""

    if denominator is None or pd.isna(denominator) or denominator == 0:
        return None
    return float(numerator) / float(denominator)


def weighted_profit_margin(df: pd.DataFrame) -> float | None:
    return safe_ratio(df["profit"].sum(), df["sales"].sum())


def loss_line_rate(df: pd.DataFrame) -> float:
    return float(df["is_loss_line"].mean()) if len(df) else 0.0


def average_order_value(df: pd.DataFrame) -> float | None:
    return safe_ratio(df["sales"].sum(), df["order_id"].nunique())


def profit_per_order(df: pd.DataFrame) -> float | None:
    return safe_ratio(df["profit"].sum(), df["order_id"].nunique())


def discounted_sales_share(df: pd.DataFrame) -> float | None:
    return safe_ratio(df.loc[df["discount"] > 0, "sales"].sum(), df["sales"].sum())


def summarize_group(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Summarize line-level sales at a requested business grain."""

    if not group_cols:
        grouped = [((), df)]
        rows = []
        for _, group in grouped:
            rows.append(_summary_row(group))
        return pd.DataFrame(rows)

    rows = []
    for keys, group in df.groupby(group_cols, dropna=False, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys, strict=True))
        row.update(_summary_row(group))
        rows.append(row)
    return pd.DataFrame(rows)


def _summary_row(group: pd.DataFrame) -> dict[str, float | int | None]:
    sales = float(group["sales"].sum())
    profit = float(group["profit"].sum())
    orders = int(group["order_id"].nunique())
    customers = int(group["customer_id"].nunique())
    lines = int(len(group))
    loss_lines = int(group["is_loss_line"].sum())
    return {
        "line_count": lines,
        "orders": orders,
        "customers": customers,
        "total_sales": sales,
        "total_profit": profit,
        "profit_margin": safe_ratio(profit, sales),
        "quantity": int(group["quantity"].sum()),
        "average_discount": float(group["discount"].mean()) if lines else np.nan,
        "discounted_sales_share": discounted_sales_share(group),
        "loss_line_count": loss_lines,
        "loss_line_rate": safe_ratio(loss_lines, lines),
        "average_order_value": safe_ratio(sales, orders),
        "profit_per_order": safe_ratio(profit, orders),
        "shipping_days_avg": float(group["shipping_days"].mean()) if lines else np.nan,
    }


def calculate_growth(series: pd.Series, denominator_mode: str = "prior_abs") -> pd.Series:
    """Calculate period growth with explicit denominator handling."""

    prior = series.shift(1)
    if denominator_mode == "prior_abs":
        denominator = prior.abs()
    elif denominator_mode == "prior":
        denominator = prior
    else:
        raise ValueError("denominator_mode must be 'prior_abs' or 'prior'.")
    growth = (series - prior) / denominator.replace(0, np.nan)
    return growth.replace([np.inf, -np.inf], np.nan)


def high_discount_metrics(df: pd.DataFrame, threshold: float = 0.30) -> dict[str, float | int | None]:
    high = df[df["discount"] >= threshold]
    return {
        "threshold": threshold,
        "line_count": int(len(high)),
        "sales": float(high["sales"].sum()),
        "profit": float(high["profit"].sum()),
        "profit_margin": weighted_profit_margin(high),
        "loss_line_count": int(high["is_loss_line"].sum()),
        "loss_line_rate": loss_line_rate(high),
        "sales_share": safe_ratio(high["sales"].sum(), df["sales"].sum()),
    }
