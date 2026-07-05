"""Shared constants for the Furniture sales analytics project."""

from __future__ import annotations

RAW_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]

COLUMN_MAP = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

REGION_ORDER = ["Central", "East", "South", "West"]
SEGMENT_ORDER = ["Consumer", "Corporate", "Home Office"]
SHIP_MODE_ORDER = ["Standard Class", "Second Class", "First Class", "Same Day"]
SUB_CATEGORY_ORDER = ["Bookcases", "Chairs", "Furnishings", "Tables"]
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DISCOUNT_BAND_ORDER = ["0%", "1-10%", "11-20%", "21-30%", ">30%"]

EXPECTED_CATEGORY = "Furniture"
EXPECTED_COUNTRY = "United States"

MONEY_COLUMNS = [
    "total_sales",
    "total_profit",
    "average_order_value",
    "profit_per_order",
]
