"""Professional static chart generation for reports."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache") / "matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from furniture_analytics.config import Settings

POSITIVE = "#2F6F6D"
NEGATIVE = "#B04A4A"
NEUTRAL = "#4E79A7"
ACCENT = "#D99058"
GRID = "#E5E7EB"


def _money_tick(value: float, _position: int) -> str:
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.0f}K"
    return f"${value:,.0f}"


def _pct_tick(value: float, _position: int) -> str:
    return f"{value:.0f}%"


def _style_axis(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_monthly_sales_profit(monthly: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["order_month"], monthly["total_sales"], color=NEUTRAL, linewidth=2.2, label="Sales")
    ax.plot(
        monthly["order_month"],
        monthly["total_profit"],
        color=POSITIVE,
        linewidth=2.2,
        label="Profit",
    )
    ax.axhline(0, color="#374151", linewidth=0.9)
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Doanh thu và lợi nhuận theo tháng", ylabel="USD")
    ax.legend(frameon=False, ncol=2)
    _save(fig, path)


def save_year_sales_margin(yearly: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(yearly["order_year"].astype(str), yearly["total_sales"], color=NEUTRAL, label="Sales")
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Doanh thu và biên lợi nhuận theo năm", ylabel="Sales")
    ax2 = ax.twinx()
    ax2.plot(
        yearly["order_year"].astype(str),
        yearly["profit_margin"] * 100,
        color=ACCENT,
        marker="o",
        linewidth=2.2,
        label="Margin",
    )
    ax2.yaxis.set_major_formatter(FuncFormatter(_pct_tick))
    ax2.set_ylabel("Weighted margin")
    ax2.spines["top"].set_visible(False)
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, frameon=False, loc="upper left")
    _save(fig, path)


def save_subcategory_sales_profit(sub_category: pd.DataFrame, path: Path) -> None:
    data = sub_category.sort_values("total_sales")
    y = np.arange(len(data))
    height = 0.36
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(y - height / 2, data["total_sales"], height=height, color=NEUTRAL, label="Sales")
    colors = np.where(data["total_profit"] >= 0, POSITIVE, NEGATIVE)
    ax.barh(y + height / 2, data["total_profit"], height=height, color=colors, label="Profit")
    ax.set_yticks(y)
    ax.set_yticklabels(data["sub_category"].astype(str))
    ax.axvline(0, color="#374151", linewidth=0.9)
    ax.xaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Doanh thu so với lợi nhuận theo nhóm sản phẩm", xlabel="USD")
    ax.legend(frameon=False)
    _save(fig, path)


def save_discount_band_margin(discount_band: pd.DataFrame, path: Path) -> None:
    data = discount_band.sort_values("discount_band")
    colors = np.where(data["profit_margin"] >= 0, POSITIVE, NEGATIVE)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(data["discount_band"].astype(str), data["profit_margin"] * 100, color=colors)
    ax.axhline(0, color="#374151", linewidth=0.9)
    ax.yaxis.set_major_formatter(FuncFormatter(_pct_tick))
    _style_axis(ax, "Biên lợi nhuận theo dải giảm giá", ylabel="Weighted margin")
    ax.text(
        0.01,
        -0.18,
        "Profit margin = sum(Profit) / sum(Sales).",
        transform=ax.transAxes,
        fontsize=9,
        color="#4B5563",
    )
    _save(fig, path)


def save_state_sales_profit(state: pd.DataFrame, path: Path) -> None:
    data = state.copy()
    colors = np.where(data["total_profit"] >= 0, POSITIVE, NEGATIVE)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(data["total_sales"], data["total_profit"], s=75, c=colors, alpha=0.82, edgecolor="white")
    ax.axhline(0, color="#374151", linewidth=0.9)
    for _, row in data.sort_values("total_profit").head(6).iterrows():
        ax.annotate(row["state"], (row["total_sales"], row["total_profit"]), fontsize=8)
    ax.xaxis.set_major_formatter(FuncFormatter(_money_tick))
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Tiểu bang: doanh thu so với lợi nhuận", xlabel="Sales", ylabel="Profit")
    _save(fig, path)


def save_region_subcategory_heatmap(region_sub_category: pd.DataFrame, path: Path) -> None:
    pivot = region_sub_category.pivot_table(
        index="region",
        columns="sub_category",
        values="total_profit",
        aggfunc="sum",
        fill_value=0,
        observed=False,
    )
    max_abs = max(abs(float(pivot.min().min())), abs(float(pivot.max().max())), 1.0)
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(pivot.values, cmap="RdYlGn", vmin=-max_abs, vmax=max_abs, aspect="auto")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns.astype(str), rotation=25, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index.astype(str))
    for row_idx in range(pivot.shape[0]):
        for col_idx in range(pivot.shape[1]):
            value = pivot.iloc[row_idx, col_idx]
            ax.text(col_idx, row_idx, f"${value/1000:,.1f}K", ha="center", va="center", fontsize=8)
    ax.set_title(
        "Lợi nhuận theo vùng và nhóm sản phẩm",
        loc="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.colorbar(image, ax=ax, format=FuncFormatter(_money_tick), shrink=0.85)
    _save(fig, path)


def save_product_sales_profit_scatter(product: pd.DataFrame, path: Path) -> None:
    data = product.copy()
    colors = np.where(data["total_profit"] >= 0, POSITIVE, NEGATIVE)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data["total_sales"], data["total_profit"], s=55, c=colors, alpha=0.72, edgecolor="white")
    ax.axhline(0, color="#374151", linewidth=0.9)
    for _, row in data.sort_values("total_profit").head(7).iterrows():
        ax.annotate(row["product_id"], (row["total_sales"], row["total_profit"]), fontsize=8)
    ax.xaxis.set_major_formatter(FuncFormatter(_money_tick))
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Sản phẩm: doanh thu so với lợi nhuận", xlabel="Sales", ylabel="Profit")
    _save(fig, path)


def save_top_loss_products(top_loss: pd.DataFrame, path: Path) -> None:
    data = top_loss.sort_values("total_profit", ascending=False)
    labels = data["product_name"].str.slice(0, 45)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, data["total_profit"], color=NEGATIVE)
    ax.axvline(0, color="#374151", linewidth=0.9)
    ax.xaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Top sản phẩm lỗ nhiều nhất", xlabel="Profit")
    _save(fig, path)


def save_segment_performance(segment: pd.DataFrame, path: Path) -> None:
    data = segment.sort_values("total_sales", ascending=False)
    x = np.arange(len(data))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, data["total_sales"], width=width, color=NEUTRAL, label="Sales")
    colors = np.where(data["total_profit"] >= 0, POSITIVE, NEGATIVE)
    ax.bar(x + width / 2, data["total_profit"], width=width, color=colors, label="Profit")
    ax.set_xticks(x)
    ax.set_xticklabels(data["segment"].astype(str))
    ax.axhline(0, color="#374151", linewidth=0.9)
    ax.yaxis.set_major_formatter(FuncFormatter(_money_tick))
    _style_axis(ax, "Hiệu quả theo phân khúc khách hàng", ylabel="USD")
    ax.legend(frameon=False)
    _save(fig, path)


def save_discount_threshold_worklist(worklist: pd.DataFrame, path: Path) -> None:
    data = worklist.head(8).copy()
    display = pd.DataFrame(
        {
            "Sub-category": data["sub_category"].astype(str),
            "Region": data["region"].astype(str),
            "Sales": data["total_sales"].map(lambda value: f"${value:,.0f}"),
            "Profit": data["total_profit"].map(lambda value: f"${value:,.0f}"),
            "Loss rate": data["loss_line_rate"].map(lambda value: f"{value:.0%}"),
        }
    )
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    ax.set_title("Worklist rủi ro giảm giá >=30%", loc="left", fontsize=13, fontweight="bold")
    table = ax.table(
        cellText=display.values,
        colLabels=display.columns,
        cellLoc="left",
        colLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.35)
    _save(fig, path)


def create_all_figures(outputs: dict[str, pd.DataFrame], settings: Settings) -> dict[str, str]:
    """Create the required figure set and return logical names to file paths."""

    figures_dir = settings.paths.figures_dir
    figure_map = {
        "monthly_sales_profit": figures_dir / "monthly_sales_profit.png",
        "sales_margin_by_year": figures_dir / "sales_margin_by_year.png",
        "sub_category_sales_profit": figures_dir / "sub_category_sales_profit.png",
        "discount_band_margin": figures_dir / "discount_band_margin.png",
        "state_sales_profit": figures_dir / "state_sales_profit.png",
        "region_sub_category_heatmap": figures_dir / "region_sub_category_heatmap.png",
        "product_sales_profit_scatter": figures_dir / "product_sales_profit_scatter.png",
        "top_loss_products": figures_dir / "top_loss_products.png",
        "segment_performance": figures_dir / "segment_performance.png",
        "discount_threshold_worklist": figures_dir / "discount_threshold_worklist.png",
    }
    save_monthly_sales_profit(outputs["monthly_performance"], figure_map["monthly_sales_profit"])
    save_year_sales_margin(outputs["yearly_performance"], figure_map["sales_margin_by_year"])
    save_subcategory_sales_profit(
        outputs["sub_category_performance"], figure_map["sub_category_sales_profit"]
    )
    save_discount_band_margin(
        outputs["discount_band_performance"], figure_map["discount_band_margin"]
    )
    save_state_sales_profit(outputs["state_performance"], figure_map["state_sales_profit"])
    save_region_subcategory_heatmap(
        outputs["region_sub_category_performance"],
        figure_map["region_sub_category_heatmap"],
    )
    save_product_sales_profit_scatter(
        outputs["product_performance"], figure_map["product_sales_profit_scatter"]
    )
    save_top_loss_products(outputs["top_loss_products"], figure_map["top_loss_products"])
    save_segment_performance(outputs["segment_performance"], figure_map["segment_performance"])
    save_discount_threshold_worklist(
        outputs["discount_threshold_worklist"],
        figure_map["discount_threshold_worklist"],
    )
    return {name: str(path) for name, path in figure_map.items()}
