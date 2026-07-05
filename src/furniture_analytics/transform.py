"""Canonical transformation layer for the Furniture sales fact table."""

from __future__ import annotations

import numpy as np
import pandas as pd

from furniture_analytics.constants import (
    COLUMN_MAP,
    DISCOUNT_BAND_ORDER,
    REGION_ORDER,
    SEGMENT_ORDER,
    SHIP_MODE_ORDER,
    SUB_CATEGORY_ORDER,
    WEEKDAY_ORDER,
)


def assign_discount_band(discount: float) -> str:
    """Return the required discount band label for a decimal discount."""

    if discount == 0:
        return "0%"
    if 0 < discount <= 0.10:
        return "1-10%"
    if 0.10 < discount <= 0.20:
        return "11-20%"
    if 0.20 < discount <= 0.30:
        return "21-30%"
    if 0.30 < discount <= 1.00:
        return ">30%"
    raise ValueError(f"Discount outside [0, 1]: {discount}")


def transform_sales(raw: pd.DataFrame, analysis_cutoff: pd.Timestamp | None = None) -> pd.DataFrame:
    """Return a typed, feature-engineered line-level Furniture sales table."""

    df = raw.rename(columns=COLUMN_MAP).copy()

    df["postal_code"] = df["postal_code"].astype("string")
    df["row_id"] = df["row_id"].astype("int64")
    df["quantity"] = df["quantity"].astype("int64")
    for column in ["sales", "discount", "profit"]:
        df[column] = df[column].astype("float64")

    df["order_year"] = df["order_date"].dt.year.astype("int64")
    df["order_quarter"] = (
        df["order_date"].dt.year.astype(str) + "-Q" + df["order_date"].dt.quarter.astype(str)
    )
    df["order_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["order_month_label"] = df["order_month"].dt.strftime("%Y-%m")
    df["order_weekday"] = df["order_date"].dt.day_name()
    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days.astype("int64")
    df["profit_margin"] = np.where(df["sales"] > 0, df["profit"] / df["sales"], np.nan)
    df["is_loss_line"] = df["profit"] < 0
    df["is_zero_profit_line"] = np.isclose(df["profit"], 0.0)
    df["discount_pct"] = df["discount"] * 100
    df["discount_band"] = df["discount"].map(assign_discount_band)
    df["sales_per_unit"] = np.where(df["quantity"] > 0, df["sales"] / df["quantity"], np.nan)
    df["profit_per_unit"] = np.where(df["quantity"] > 0, df["profit"] / df["quantity"], np.nan)
    df["product_label"] = df["product_id"] + " - " + df["product_name"]

    cutoff = analysis_cutoff or df["order_date"].max()
    customer_orders = df.groupby("customer_id", observed=False)["order_id"].nunique()
    customer_sales = df.groupby("customer_id", observed=False)["sales"].sum()
    customer_profit = df.groupby("customer_id", observed=False)["profit"].sum()
    customer_last = df.groupby("customer_id", observed=False)["order_date"].max()

    df["customer_order_count"] = df["customer_id"].map(customer_orders).astype("int64")
    df["is_repeat_customer"] = df["customer_order_count"] >= 2
    df["customer_sales"] = df["customer_id"].map(customer_sales).astype("float64")
    df["customer_profit"] = df["customer_id"].map(customer_profit).astype("float64")
    df["customer_last_order_date"] = df["customer_id"].map(customer_last)
    df["customer_recency_days"] = (
        pd.Timestamp(cutoff) - df["customer_last_order_date"]
    ).dt.days.astype("int64")

    category_orders = {
        "region": REGION_ORDER,
        "segment": SEGMENT_ORDER,
        "ship_mode": SHIP_MODE_ORDER,
        "sub_category": SUB_CATEGORY_ORDER,
        "order_weekday": WEEKDAY_ORDER,
        "discount_band": DISCOUNT_BAND_ORDER,
    }
    for column, order in category_orders.items():
        df[column] = pd.Categorical(df[column], categories=order, ordered=True)

    return df
