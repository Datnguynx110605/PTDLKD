from __future__ import annotations

import pandas as pd
import pytest

from furniture_analytics.constants import RAW_COLUMNS
from furniture_analytics.io import load_raw_sales


def test_load_raw_sales_uses_expected_shape(raw_df):
    assert raw_df.shape == (2121, 21)
    assert list(raw_df.columns) == RAW_COLUMNS
    assert pd.api.types.is_datetime64_any_dtype(raw_df["Order Date"])
    assert pd.api.types.is_datetime64_any_dtype(raw_df["Ship Date"])


def test_load_raw_sales_fails_on_invalid_date(tmp_path, settings):
    row = {
        "Row ID": 1,
        "Order ID": "O-1",
        "Order Date": "31/12/2017",
        "Ship Date": "1/2/2018",
        "Ship Mode": "Standard Class",
        "Customer ID": "C-1",
        "Customer Name": "Customer",
        "Segment": "Consumer",
        "Country": "United States",
        "City": "City",
        "State": "State",
        "Postal Code": "00000",
        "Region": "West",
        "Product ID": "P-1",
        "Category": "Furniture",
        "Sub-Category": "Chairs",
        "Product Name": "Chair",
        "Sales": 10.0,
        "Quantity": 1,
        "Discount": 0.0,
        "Profit": 1.0,
    }
    path = tmp_path / "bad_dates.csv"
    pd.DataFrame([row]).to_csv(path, index=False)
    with pytest.raises(ValueError):
        load_raw_sales(path, encoding=settings.input.encoding, date_format=settings.input.date_format)
