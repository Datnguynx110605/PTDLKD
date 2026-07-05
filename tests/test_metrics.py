from __future__ import annotations

import pandas as pd

from furniture_analytics.metrics import average_order_value, summarize_group, weighted_profit_margin


def test_weighted_margin_uses_sum_not_row_average():
    df = pd.DataFrame(
        {
            "sales": [100.0, 1.0],
            "profit": [10.0, -1.0],
            "order_id": ["A", "B"],
            "customer_id": ["C1", "C2"],
            "quantity": [1, 1],
            "discount": [0.0, 0.0],
            "is_loss_line": [False, True],
            "shipping_days": [1, 1],
        }
    )
    assert weighted_profit_margin(df) == 9.0 / 101.0


def test_aov_uses_distinct_orders_not_lines():
    df = pd.DataFrame(
        {
            "sales": [100.0, 50.0, 25.0],
            "profit": [10.0, 5.0, 2.5],
            "order_id": ["A", "A", "B"],
            "customer_id": ["C1", "C1", "C2"],
            "quantity": [1, 1, 1],
            "discount": [0.0, 0.0, 0.0],
            "is_loss_line": [False, False, False],
            "shipping_days": [1, 1, 1],
        }
    )
    assert average_order_value(df) == 175.0 / 2
    assert summarize_group(df, []).iloc[0]["orders"] == 2
