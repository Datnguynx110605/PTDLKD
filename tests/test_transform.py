from __future__ import annotations

from furniture_analytics.transform import assign_discount_band


def test_discount_band_boundaries():
    cases = {
        0.00: "0%",
        0.01: "1-10%",
        0.10: "1-10%",
        0.11: "11-20%",
        0.20: "11-20%",
        0.21: "21-30%",
        0.30: "21-30%",
        0.31: ">30%",
    }
    for discount, expected in cases.items():
        assert assign_discount_band(discount) == expected


def test_transform_preserves_rows_and_adds_required_fields(fact_df):
    assert len(fact_df) == 2121
    required = {
        "order_year",
        "order_quarter",
        "order_month",
        "order_month_label",
        "order_weekday",
        "shipping_days",
        "profit_margin",
        "is_loss_line",
        "is_zero_profit_line",
        "discount_pct",
        "discount_band",
        "sales_per_unit",
        "profit_per_unit",
        "product_label",
        "is_repeat_customer",
        "customer_order_count",
        "customer_sales",
        "customer_profit",
        "customer_last_order_date",
        "customer_recency_days",
    }
    assert required.issubset(fact_df.columns)
    assert fact_df["discount_band"].isna().sum() == 0
    assert fact_df["shipping_days"].min() >= 0
    assert int(fact_df["is_loss_line"].sum()) == 714
