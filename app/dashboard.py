from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from furniture_analytics.analysis import build_customer_summary, build_product_summary
from furniture_analytics.config import load_settings
from furniture_analytics.io import load_raw_sales
from furniture_analytics.metrics import summarize_group
from furniture_analytics.reporting import format_currency, format_int, format_pct
from furniture_analytics.transform import transform_sales


@st.cache_data(show_spinner=False)
def load_fact() -> pd.DataFrame:
    settings = load_settings(ROOT / "config" / "settings.yaml")
    processed_path = settings.paths.processed_dir / "furniture_sales_clean.parquet"
    if processed_path.exists():
        return pd.read_parquet(processed_path)
    raw = load_raw_sales(
        settings.paths.raw_csv,
        encoding=settings.input.encoding,
        date_format=settings.input.date_format,
    )
    return transform_sales(raw)


def _filter_options(df: pd.DataFrame, column: str) -> list[str]:
    return sorted(df[column].dropna().astype(str).unique().tolist())


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    settings = load_settings(ROOT / "config" / "settings.yaml")
    st.sidebar.header("Bộ lọc")
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    date_range = st.sidebar.date_input("Ngày đặt hàng", value=(min_date, max_date))
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filters = {
        "region": st.sidebar.multiselect("Vùng", _filter_options(df, "region")),
        "state": st.sidebar.multiselect("Tiểu bang", _filter_options(df, "state")),
        "segment": st.sidebar.multiselect("Phân khúc", _filter_options(df, "segment")),
        "sub_category": st.sidebar.multiselect("Nhóm sản phẩm", _filter_options(df, "sub_category")),
        "discount_band": st.sidebar.multiselect("Dải giảm giá", _filter_options(df, "discount_band")),
        "ship_mode": st.sidebar.multiselect("Hình thức giao hàng", _filter_options(df, "ship_mode")),
    }

    output = df[
        (df["order_date"].dt.date >= start_date)
        & (df["order_date"].dt.date <= end_date)
    ].copy()
    for column, values in filters.items():
        if values:
            output = output[output[column].astype(str).isin(values)]

    if output.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc hiện tại.")
        st.stop()

    threshold = settings.analysis.high_discount_review_threshold
    st.sidebar.caption(f"Ngưỡng review giảm giá cao: {threshold:.0%}")
    return output


def render_kpis(df: pd.DataFrame) -> None:
    row = summarize_group(df, []).iloc[0]
    cols = st.columns(7)
    cols[0].metric("Sales", format_currency(row["total_sales"]))
    cols[1].metric("Profit", format_currency(row["total_profit"]))
    cols[2].metric("Margin", format_pct(row["profit_margin"]))
    cols[3].metric("Orders", format_int(row["orders"]))
    cols[4].metric("Customers", format_int(row["customers"]))
    cols[5].metric("AOV", format_currency(row["average_order_value"]))
    cols[6].metric("Loss rate", format_pct(row["loss_line_rate"]))
    st.caption("Weighted profit margin = sum(Profit) / sum(Sales).")

    settings = load_settings(ROOT / "config" / "settings.yaml")
    if row["total_profit"] < 0:
        st.error("Cảnh báo: bộ lọc hiện tại có tổng lợi nhuận âm.")
    elif row["loss_line_rate"] >= settings.analysis.high_loss_line_rate_threshold:
        st.warning("Cảnh báo: tỷ lệ dòng lỗ cao trong bộ lọc hiện tại.")


def line_trend(df: pd.DataFrame) -> go.Figure:
    monthly = summarize_group(df, ["order_month", "order_month_label"]).sort_values("order_month")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["total_sales"], name="Sales"))
    fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["total_profit"], name="Profit"))
    fig.add_hline(y=0, line_color="#374151", line_width=1)
    fig.update_layout(title="Doanh thu và lợi nhuận theo tháng", yaxis_tickprefix="$")
    return fig


def bar_margin_by_period(df: pd.DataFrame) -> go.Figure:
    yearly = summarize_group(df, ["order_year"]).sort_values("order_year")
    fig = go.Figure()
    fig.add_bar(x=yearly["order_year"].astype(str), y=yearly["total_sales"], name="Sales")
    fig.add_trace(
        go.Scatter(
            x=yearly["order_year"].astype(str),
            y=yearly["profit_margin"],
            name="Margin",
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Doanh thu và biên lợi nhuận theo năm",
        yaxis=dict(title="Sales", tickprefix="$"),
        yaxis2=dict(title="Margin", overlaying="y", side="right", tickformat=".1%"),
    )
    return fig


def render_overview(df: pd.DataFrame) -> None:
    left, right = st.columns([1.3, 1])
    left.plotly_chart(line_trend(df), use_container_width=True)
    right.plotly_chart(bar_margin_by_period(df), use_container_width=True)
    st.dataframe(
        summarize_group(df, ["order_year"]).sort_values("order_year"),
        use_container_width=True,
        hide_index=True,
    )


def render_product_discount(df: pd.DataFrame) -> None:
    settings = load_settings(ROOT / "config" / "settings.yaml")
    subcat = summarize_group(df, ["sub_category"]).sort_values("total_sales", ascending=False)
    fig = px.bar(
        subcat,
        x="total_sales",
        y="sub_category",
        orientation="h",
        color="total_profit",
        color_continuous_scale="RdYlGn",
        title="Doanh thu và lợi nhuận theo nhóm sản phẩm",
    )
    st.plotly_chart(fig, use_container_width=True)

    discount = summarize_group(df, ["discount_band"]).sort_values("discount_band")
    fig2 = px.bar(
        discount,
        x="discount_band",
        y="profit_margin",
        color="total_profit",
        color_continuous_scale="RdYlGn",
        title="Biên lợi nhuận theo dải giảm giá",
    )
    fig2.add_hline(y=0, line_color="#374151")
    fig2.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig2, use_container_width=True)

    product = build_product_summary(df, settings).sort_values("total_sales", ascending=False)
    scatter = px.scatter(
        product,
        x="total_sales",
        y="total_profit",
        color="classification",
        hover_data=["product_id", "product_name", "sub_category", "profit_margin"],
        title="Sản phẩm: doanh thu so với lợi nhuận",
    )
    scatter.add_hline(y=0, line_color="#374151")
    st.plotly_chart(scatter, use_container_width=True)

    ranking_cols = [
        "product_id",
        "product_name",
        "sub_category",
        "total_sales",
        "total_profit",
        "profit_margin",
        "classification",
    ]
    sales_rank, profit_rank, loss_rank = st.columns(3)
    sales_rank.subheader("Top sales")
    sales_rank.dataframe(
        product.sort_values("total_sales", ascending=False).head(10)[ranking_cols],
        use_container_width=True,
        hide_index=True,
    )
    profit_rank.subheader("Top profit")
    profit_rank.dataframe(
        product.sort_values("total_profit", ascending=False).head(10)[ranking_cols],
        use_container_width=True,
        hide_index=True,
    )
    loss_rank.subheader("Top loss")
    loss_rank.dataframe(
        product.sort_values("total_profit").head(10)[ranking_cols],
        use_container_width=True,
        hide_index=True,
    )


def render_geography(df: pd.DataFrame) -> None:
    state = summarize_group(df, ["state", "region"]).sort_values("total_profit")
    scatter = px.scatter(
        state,
        x="total_sales",
        y="total_profit",
        color="region",
        hover_data=["state", "profit_margin", "average_discount", "loss_line_rate"],
        title="Tiểu bang: doanh thu so với lợi nhuận",
    )
    scatter.add_hline(y=0, line_color="#374151")
    st.plotly_chart(scatter, use_container_width=True)

    matrix = summarize_group(df, ["region", "sub_category"])
    pivot = matrix.pivot_table(
        index="region",
        columns="sub_category",
        values="total_profit",
        aggfunc="sum",
        fill_value=0,
        observed=False,
    )
    heatmap = px.imshow(
        pivot,
        text_auto=".0f",
        color_continuous_scale="RdYlGn",
        title="Lợi nhuận theo vùng và nhóm sản phẩm",
        aspect="auto",
    )
    st.plotly_chart(heatmap, use_container_width=True)
    st.dataframe(state.head(15), use_container_width=True, hide_index=True)


def render_customers(df: pd.DataFrame) -> None:
    segment = summarize_group(df, ["segment"]).sort_values("total_sales", ascending=False)
    fig = px.bar(
        segment,
        x="segment",
        y=["total_sales", "total_profit"],
        barmode="group",
        title="Hiệu quả theo phân khúc",
    )
    st.plotly_chart(fig, use_container_width=True)

    customer = build_customer_summary(df)
    customer_display = customer[
        [
            "customer_label",
            "segment",
            "customer_orders",
            "customer_sales",
            "customer_profit",
            "customer_margin",
            "recency_days",
        ]
    ].sort_values("customer_profit")
    st.dataframe(customer_display.head(20), use_container_width=True, hide_index=True)


def render_fulfillment(df: pd.DataFrame) -> None:
    st.caption("Các quan hệ dưới đây là mô tả; dữ liệu không có freight-cost field.")
    ship_mode = summarize_group(df, ["ship_mode"]).sort_values("total_sales", ascending=False)
    mode_fig = px.bar(
        ship_mode,
        x="ship_mode",
        y=["total_sales", "total_profit"],
        barmode="group",
        title="Hiệu quả theo hình thức giao hàng",
    )
    st.plotly_chart(mode_fig, use_container_width=True)

    shipping_days = summarize_group(df, ["shipping_days"]).sort_values("shipping_days")
    days_fig = px.bar(
        shipping_days,
        x="shipping_days",
        y="loss_line_rate",
        title="Tỷ lệ dòng lỗ theo số ngày giao hàng",
    )
    days_fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(days_fig, use_container_width=True)
    st.dataframe(ship_mode, use_container_width=True, hide_index=True)
    st.dataframe(shipping_days, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Furniture Profit Dashboard", layout="wide")
    st.title("Furniture Sales: Revenue & Profit Optimization")
    st.caption("Phạm vi: Furniture-only, 2014-2017. Không suy rộng sang toàn bộ công ty.")
    fact = load_fact()
    filtered = apply_filters(fact)
    render_kpis(filtered)

    tabs = st.tabs(["Tổng quan", "Sản phẩm & giảm giá", "Địa lý", "Khách hàng", "Giao hàng"])
    with tabs[0]:
        render_overview(filtered)
    with tabs[1]:
        render_product_discount(filtered)
    with tabs[2]:
        render_geography(filtered)
    with tabs[3]:
        render_customers(filtered)
    with tabs[4]:
        render_fulfillment(filtered)


if __name__ == "__main__":
    main()
