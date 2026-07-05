"""Analysis tables and diagnostic worklists for Furniture sales."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from furniture_analytics.config import Settings
from furniture_analytics.metrics import calculate_growth, safe_ratio, summarize_group
from furniture_analytics.validation import assert_no_duplicate_key


def _mode_or_first(series: pd.Series) -> object:
    mode = series.mode(dropna=True)
    return mode.iloc[0] if not mode.empty else series.iloc[0]


def _margin_from_columns(df: pd.DataFrame, profit_col: str, sales_col: str) -> pd.Series:
    return df[profit_col] / df[sales_col].replace(0, np.nan)


def build_order_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per order without duplicating line-level dollars."""

    summary = (
        df.groupby("order_id", dropna=False, observed=False)
        .agg(
            order_date=("order_date", "min"),
            ship_date=("ship_date", "max"),
            shipping_days=("shipping_days", "max"),
            customer_id=("customer_id", _mode_or_first),
            segment=("segment", _mode_or_first),
            region=("region", _mode_or_first),
            state=("state", _mode_or_first),
            city=("city", _mode_or_first),
            order_sales=("sales", "sum"),
            order_profit=("profit", "sum"),
            order_quantity=("quantity", "sum"),
            order_line_count=("row_id", "count"),
            order_avg_discount=("discount", "mean"),
            order_has_loss_line=("is_loss_line", "any"),
            order_loss_line_count=("is_loss_line", "sum"),
        )
        .reset_index()
    )
    summary["order_margin"] = _margin_from_columns(summary, "order_profit", "order_sales")
    assert_no_duplicate_key(summary, ["order_id"], "order_summary")
    return summary


def build_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per customer with within-window measures."""

    summary = (
        df.groupby("customer_id", dropna=False, observed=False)
        .agg(
            segment=("segment", _mode_or_first),
            customer_orders=("order_id", "nunique"),
            customer_sales=("sales", "sum"),
            customer_profit=("profit", "sum"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
            customer_avg_discount=("discount", "mean"),
            line_count=("row_id", "count"),
            loss_line_count=("is_loss_line", "sum"),
        )
        .reset_index()
        .sort_values(["customer_sales", "customer_id"], ascending=[False, True])
    )
    cutoff = df["order_date"].max()
    summary["customer_margin"] = _margin_from_columns(summary, "customer_profit", "customer_sales")
    summary["recency_days"] = (cutoff - summary["last_order_date"]).dt.days.astype("int64")
    summary["customer_avg_order_value"] = summary["customer_sales"] / summary[
        "customer_orders"
    ].replace(0, np.nan)
    summary["is_repeat_customer"] = summary["customer_orders"] >= 2
    summary["loss_line_rate"] = summary["loss_line_count"] / summary["line_count"].replace(0, np.nan)
    summary["customer_label"] = [f"KH-{i:03d}" for i in range(1, len(summary) + 1)]
    assert_no_duplicate_key(summary, ["customer_id"], "customer_summary")
    return summary


def _classify_product(row: pd.Series, sales_threshold: float, margin_threshold: float) -> str:
    high_sales = row["total_sales"] >= sales_threshold
    acceptable_profit = row["total_profit"] > 0 and row["profit_margin"] >= margin_threshold
    if high_sales and acceptable_profit:
        return "Grow"
    if high_sales:
        return "Repair"
    if acceptable_profit:
        return "Scale selectively"
    return "Rationalize"


def build_product_summary(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    """Create one row per product ID, product name, and sub-category."""

    summary = summarize_group(df, ["product_id", "product_name", "sub_category"])
    summary["product_label"] = summary["product_id"] + " - " + summary["product_name"]

    min_lines = settings.analysis.min_product_line_count_for_margin_ranking
    eligible = summary.loc[summary["line_count"] >= min_lines, "total_sales"]
    sales_threshold = float(eligible.median() if not eligible.empty else summary["total_sales"].median())
    margin_threshold = safe_ratio(df["profit"].sum(), df["sales"].sum()) or 0.0

    summary["classification"] = summary.apply(
        _classify_product,
        axis=1,
        sales_threshold=sales_threshold,
        margin_threshold=margin_threshold,
    )
    summary["classification_rule"] = (
        f"sales_threshold={sales_threshold:.2f}; margin_threshold={margin_threshold:.4f}; "
        f"min_lines={min_lines}"
    )
    assert_no_duplicate_key(
        summary,
        ["product_id", "product_name", "sub_category"],
        "product_summary",
    )
    return summary.sort_values(["total_profit", "total_sales"], ascending=[True, False])


def build_summaries(df: pd.DataFrame, settings: Settings) -> dict[str, pd.DataFrame]:
    """Build required semantic summary tables."""

    return {
        "order_summary": build_order_summary(df),
        "customer_summary": build_customer_summary(df),
        "product_summary": build_product_summary(df, settings),
    }


def _add_growth(summary: pd.DataFrame, sort_col: str | list[str]) -> pd.DataFrame:
    output = summary.sort_values(sort_col).reset_index(drop=True).copy()
    output["sales_growth"] = calculate_growth(output["total_sales"], denominator_mode="prior")
    output["profit_growth"] = calculate_growth(output["total_profit"], denominator_mode="prior_abs")
    return output


def build_time_analysis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = _add_growth(summarize_group(df, ["order_month", "order_month_label"]), "order_month")
    quarterly = _add_growth(summarize_group(df, ["order_quarter"]), "order_quarter")
    yearly = _add_growth(summarize_group(df, ["order_year"]), "order_year")
    return {
        "monthly_performance": monthly,
        "quarterly_performance": quarterly,
        "yearly_performance": yearly,
    }


def _rank(df: pd.DataFrame, column: str, ascending: bool, top_n: int) -> pd.DataFrame:
    return df.sort_values([column, "total_sales"], ascending=[ascending, False]).head(top_n)


def build_product_analysis(
    df: pd.DataFrame,
    product_summary: pd.DataFrame,
    settings: Settings,
) -> dict[str, pd.DataFrame]:
    top_n = settings.analysis.top_n_products
    sub_category = summarize_group(df, ["sub_category"]).sort_values("total_sales", ascending=False)
    min_lines = settings.analysis.min_product_line_count_for_margin_ranking
    eligible_profitable = product_summary[
        (product_summary["line_count"] >= min_lines) & (product_summary["total_profit"] > 0)
    ]
    underrepresented = eligible_profitable.sort_values(
        ["profit_margin", "total_profit"], ascending=[False, False]
    ).head(top_n)

    return {
        "sub_category_performance": sub_category,
        "product_performance": product_summary.sort_values("total_sales", ascending=False),
        "top_sales_products": _rank(product_summary, "total_sales", False, top_n),
        "top_profit_products": _rank(product_summary, "total_profit", False, top_n),
        "top_loss_products": _rank(product_summary, "total_profit", True, top_n),
        "underrepresented_profitable_products": underrepresented,
        "product_classification_matrix": product_summary[
            [
                "product_id",
                "product_name",
                "sub_category",
                "total_sales",
                "total_profit",
                "profit_margin",
                "line_count",
                "classification",
                "classification_rule",
            ]
        ].sort_values(["classification", "total_sales"], ascending=[True, False]),
    }


def build_discount_analysis(df: pd.DataFrame, settings: Settings) -> dict[str, pd.DataFrame]:
    threshold = settings.analysis.high_discount_review_threshold
    exact = summarize_group(df, ["discount"]).sort_values("discount")
    exact["discount_pct"] = exact["discount"] * 100
    exact["discount_label"] = exact["discount_pct"].map(lambda value: f"{value:.0f}%")

    band = summarize_group(df, ["discount_band"]).sort_values("discount_band")
    high = df[df["discount"] >= threshold]
    high_threshold = summarize_group(high, ["sub_category", "region"]).sort_values(
        "total_profit", ascending=True
    )
    high_threshold["threshold"] = threshold

    loss_without_high_discount = summarize_group(
        df[(df["is_loss_line"]) & (df["discount"] < threshold)],
        ["sub_category", "region", "state"],
    ).sort_values("total_profit")

    return {
        "discount_exact_performance": exact,
        "discount_band_performance": band,
        "discount_sub_category": summarize_group(df, ["discount_band", "sub_category"]).sort_values(
            ["discount_band", "total_profit"]
        ),
        "discount_region": summarize_group(df, ["discount_band", "region"]).sort_values(
            ["discount_band", "total_profit"]
        ),
        "discount_state": summarize_group(df, ["discount_band", "state"]).sort_values(
            ["discount_band", "total_profit"]
        ),
        "discount_threshold_worklist": high_threshold,
        "loss_without_high_discount": loss_without_high_discount,
    }


def _score_state_priority(state_summary: pd.DataFrame, high_loss_threshold: float) -> pd.DataFrame:
    output = state_summary.copy()
    sales_threshold = output["total_sales"].median()
    discount_threshold = output["average_discount"].median()
    negative_losses = output.loc[output["total_profit"] < 0, "total_profit"].abs()
    material_loss_threshold = float(negative_losses.median()) if not negative_losses.empty else 0.0

    score_parts: dict[str, Callable[[pd.DataFrame], pd.Series]] = {
        "negative_profit_points": lambda frame: frame["total_profit"] < 0,
        "material_sales_points": lambda frame: frame["total_sales"] >= sales_threshold,
        "high_discount_points": lambda frame: frame["average_discount"] >= discount_threshold,
        "high_loss_rate_points": lambda frame: frame["loss_line_rate"] >= high_loss_threshold,
        "material_loss_points": lambda frame: frame["total_profit"].lt(0)
        & frame["total_profit"].abs().ge(material_loss_threshold),
    }
    for column, scorer in score_parts.items():
        output[column] = scorer(output).astype(int)
    point_cols = list(score_parts)
    output["priority_score"] = output[point_cols].sum(axis=1)
    output["priority_rule"] = (
        f"+1 negative profit; +1 sales >= state median ${sales_threshold:,.2f}; "
        f"+1 mean discount >= state median {discount_threshold:.1%}; "
        f"+1 loss rate >= {high_loss_threshold:.1%}; "
        f"+1 absolute loss >= negative-state median ${material_loss_threshold:,.2f}"
    )
    return output.sort_values(
        ["priority_score", "total_profit", "total_sales"],
        ascending=[False, True, False],
    )


def build_geography_analysis(df: pd.DataFrame, settings: Settings) -> dict[str, pd.DataFrame]:
    region = summarize_group(df, ["region"]).sort_values("total_sales", ascending=False)
    state = summarize_group(df, ["state", "region"]).sort_values("total_profit")
    region_sub_category = summarize_group(df, ["region", "sub_category"]).sort_values("total_profit")
    state_sub_category = summarize_group(df, ["state", "sub_category"]).sort_values("total_profit")
    priority = _score_state_priority(
        state,
        high_loss_threshold=settings.analysis.high_loss_line_rate_threshold,
    )
    return {
        "region_performance": region,
        "state_performance": state,
        "region_sub_category_performance": region_sub_category,
        "state_sub_category_performance": state_sub_category,
        "state_priority_worklist": priority,
    }


def build_customer_segment_analysis(
    df: pd.DataFrame,
    customer_summary: pd.DataFrame,
    settings: Settings,
) -> dict[str, pd.DataFrame]:
    top_n = settings.analysis.top_n_products
    segment = summarize_group(df, ["segment"]).sort_values("total_sales", ascending=False)

    repeat = (
        customer_summary.groupby("is_repeat_customer", dropna=False)
        .agg(
            customers=("customer_id", "nunique"),
            orders=("customer_orders", "sum"),
            total_sales=("customer_sales", "sum"),
            total_profit=("customer_profit", "sum"),
        )
        .reset_index()
    )
    repeat["profit_margin"] = repeat["total_profit"] / repeat["total_sales"].replace(0, np.nan)
    repeat["order_share"] = repeat["orders"] / repeat["orders"].sum()

    frequency = (
        customer_summary.groupby("customer_orders", dropna=False)
        .agg(customers=("customer_id", "nunique"), total_sales=("customer_sales", "sum"))
        .reset_index()
        .sort_values("customer_orders")
    )
    high_sales_low_profit = customer_summary[
        (customer_summary["customer_sales"] >= customer_summary["customer_sales"].median())
        & (customer_summary["customer_profit"] <= 0)
    ].sort_values(["customer_profit", "customer_sales"], ascending=[True, False])

    cross_sell_candidates = customer_summary[
        (customer_summary["is_repeat_customer"]) & (customer_summary["customer_profit"] > 0)
    ].sort_values(["customer_profit", "customer_sales"], ascending=[False, False])

    return {
        "segment_performance": segment,
        "repeat_customer_summary": repeat,
        "customer_frequency_distribution": frequency,
        "top_sales_customers": customer_summary.sort_values("customer_sales", ascending=False).head(top_n),
        "top_profit_customers": customer_summary.sort_values("customer_profit", ascending=False).head(
            top_n
        ),
        "high_sales_low_profit_customers": high_sales_low_profit.head(top_n),
        "cross_sell_candidates": cross_sell_candidates.head(top_n),
    }


def build_shipping_analysis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "ship_mode_performance": summarize_group(df, ["ship_mode"]).sort_values(
            "total_sales", ascending=False
        ),
        "shipping_days_performance": summarize_group(df, ["shipping_days"]).sort_values(
            "shipping_days"
        ),
    }


def build_analysis_outputs(
    df: pd.DataFrame,
    summaries: dict[str, pd.DataFrame],
    settings: Settings,
) -> dict[str, pd.DataFrame]:
    """Build every analysis table required by the business questions."""

    outputs: dict[str, pd.DataFrame] = {}
    outputs.update(build_time_analysis(df))
    outputs.update(build_product_analysis(df, summaries["product_summary"], settings))
    outputs.update(build_discount_analysis(df, settings))
    outputs.update(build_geography_analysis(df, settings))
    outputs.update(build_customer_segment_analysis(df, summaries["customer_summary"], settings))
    outputs.update(build_shipping_analysis(df))
    return outputs
