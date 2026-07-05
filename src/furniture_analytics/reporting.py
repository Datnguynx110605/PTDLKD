"""Markdown report generation with Vietnamese stakeholder-facing language."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from furniture_analytics.config import Settings


def format_currency(value: Any) -> str:
    if pd.isna(value):
        return "N/A"
    return f"${float(value):,.2f}"


def format_int(value: Any) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{int(value):,}"


def format_pct(value: Any, decimals: int = 2) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.{decimals}f}%"


def _format_cell(column: str, value: Any) -> str:
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if pd.isna(value):
        return "N/A"
    if isinstance(value, str):
        return value
    lower = column.lower()
    if any(token in lower for token in ["rank", "score", "days"]):
        return format_int(value)
    if any(
        token in lower
        for token in ["margin", "rate", "share", "discount", "growth", "pct"]
    ):
        return format_pct(value)
    if any(token in lower for token in ["sales", "profit", "value", "aov"]):
        return format_currency(value)
    if any(token in lower for token in ["orders", "customers", "count", "quantity", "lines"]):
        return format_int(value)
    return str(value)


def dataframe_to_markdown(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    *,
    max_rows: int = 10,
) -> str:
    """Render a compact markdown table without requiring optional tabulate."""

    if df.empty:
        return "_Khong co dong du lieu phu hop._"
    table = df.loc[:, columns] if columns else df.copy()
    table = table.head(max_rows).copy()
    headers = list(table.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in table.iterrows():
        values = [_format_cell(column, row[column]) for column in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_data_quality_report(metric_baseline: dict[str, Any]) -> str:
    raw = metric_baseline["validation"]["raw"]
    transformed = metric_baseline["validation"]["transformed"]
    source = metric_baseline["source"]

    return f"""
# Báo cáo chất lượng dữ liệu

## Nguồn dữ liệu

- Tệp nguồn: `{source["source_file"]}`
- SHA-256: `{source["sha256"]}`
- Encoding: `cp1252`
- Định dạng ngày: `%m/%d/%Y`
- Thời điểm xử lý UTC: `{source["processed_at_utc"]}`

## Kiểm tra raw file

| Chỉ số | Giá trị |
|---|---:|
| Dòng | {format_int(raw["raw_rows"])} |
| Cột | {format_int(raw["raw_columns"])} |
| Giá trị thiếu | {format_int(raw["missing_values"])} |
| Dòng trùng lặp | {format_int(raw["duplicate_rows"])} |
| Row ID trùng lặp | {format_int(raw["duplicate_row_ids"])} |
| Đơn hàng duy nhất | {format_int(raw["orders"])} |
| Khách hàng duy nhất | {format_int(raw["customers"])} |
| Tổng doanh thu | {format_currency(raw["total_sales"])} |
| Tổng lợi nhuận | {format_currency(raw["total_profit"])} |
| Dòng lỗ | {format_int(raw["loss_lines"])} |

## Kết luận

Dữ liệu đầu vào đạt các ràng buộc bắt buộc: Furniture-only, không có giá trị thiếu, không có `Row ID` trùng lặp, ngày giao hàng không sớm hơn ngày đặt hàng, và các tổng doanh thu/lợi nhuận khớp baseline trong `CONTEXT.md`.

Bảng fact sau biến đổi có {format_int(transformed["transformed_rows"])} dòng và giữ nguyên tổng doanh thu {format_currency(transformed["total_sales"])} cùng tổng lợi nhuận {format_currency(transformed["total_profit"])}.
"""


def build_executive_summary(
    outputs: dict[str, pd.DataFrame],
    metric_baseline: dict[str, Any],
) -> str:
    kpi = metric_baseline["kpis"]
    yearly = outputs["yearly_performance"]
    subcat = outputs["sub_category_performance"]
    region = outputs["region_performance"]
    state_priority = outputs["state_priority_worklist"]
    discount = outputs["discount_exact_performance"]
    high_discount = metric_baseline["high_discount_30_plus"]

    year_2017 = yearly.loc[yearly["order_year"] == 2017].iloc[0]
    tables = subcat.loc[subcat["sub_category"].astype(str) == "Tables"].iloc[0]
    bookcases = subcat.loc[subcat["sub_category"].astype(str) == "Bookcases"].iloc[0]
    central = region.loc[region["region"].astype(str) == "Central"].iloc[0]
    discount_30 = discount.loc[discount["discount"].round(2) == 0.30].iloc[0]

    return f"""
# Tóm tắt điều hành

## Phạm vi và câu hỏi quyết định

Phân tích này chỉ bao phủ danh mục `Furniture` trong `Dataset.csv`. Mục tiêu là tìm cách tăng doanh thu mà không hy sinh lợi nhuận, dựa trên dữ liệu quan sát được. Các kết luận về giảm giá là mối quan hệ mô tả, không phải bằng chứng nhân quả vì dữ liệu không có COGS, phí vận chuyển, marketing spend hoặc returns.

## KPI tổng quan

| KPI | Giá trị |
|---|---:|
| Doanh thu | {format_currency(kpi["total_sales"])} |
| Lợi nhuận | {format_currency(kpi["total_profit"])} |
| Biên lợi nhuận có trọng số | {format_pct(kpi["profit_margin"])} |
| Đơn hàng | {format_int(kpi["orders"])} |
| Khách hàng | {format_int(kpi["customers"])} |
| AOV | {format_currency(kpi["average_order_value"])} |
| Dòng lỗ | {format_int(kpi["loss_line_count"])} |
| Tỷ lệ dòng lỗ | {format_pct(kpi["loss_line_rate"])} |

## Phát hiện chính

- **Sự thật quan sát:** Năm 2017 đạt doanh thu {format_currency(year_2017["total_sales"])} nhưng lợi nhuận chỉ {format_currency(year_2017["total_profit"])} và biên lợi nhuận {format_pct(year_2017["profit_margin"])}.
- **Sự thật quan sát:** `Tables` lỗ {format_currency(tables["total_profit"])} và `Bookcases` lỗ {format_currency(bookcases["total_profit"])}; đây là hai nhóm cần sửa chữa lợi nhuận.
- **Sự thật quan sát:** `Central` là vùng lỗ tổng thể với lợi nhuận {format_currency(central["total_profit"])} và mean discount {format_pct(central["average_discount"])}.
- **Sự thật quan sát:** Discount 30% tạo lợi nhuận {format_currency(discount_30["total_profit"])}; nhóm discount >=30% tạo lợi nhuận {format_currency(high_discount["profit"])} với tỷ lệ dòng lỗ {format_pct(high_discount["loss_line_rate"])}.
- **Giả thuyết có bằng chứng:** Giảm giá cao có liên quan mạnh với lợi nhuận âm, nhưng cơ chế đầy đủ cần dữ liệu chi phí và vận chuyển để xác nhận.

## Bảng ưu tiên tiểu bang

{dataframe_to_markdown(state_priority, ["state", "region", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate", "priority_score"], max_rows=10)}

Xem `reports/business_questions.md` để có câu trả lời chi tiết cho toàn bộ nhóm câu hỏi A-F trong `CONTEXT.md`.
"""


def build_recommendations_report(
    outputs: dict[str, pd.DataFrame],
    metric_baseline: dict[str, Any],
) -> str:
    subcat = outputs["sub_category_performance"]
    region = outputs["region_performance"]
    states = outputs["state_priority_worklist"]
    high_discount = metric_baseline["high_discount_30_plus"]

    tables = subcat.loc[subcat["sub_category"].astype(str) == "Tables"].iloc[0]
    bookcases = subcat.loc[subcat["sub_category"].astype(str) == "Bookcases"].iloc[0]
    chairs = subcat.loc[subcat["sub_category"].astype(str) == "Chairs"].iloc[0]
    furnishings = subcat.loc[subcat["sub_category"].astype(str) == "Furnishings"].iloc[0]
    central = region.loc[region["region"].astype(str) == "Central"].iloc[0]
    state_names = ", ".join(states.head(4)["state"].astype(str).tolist())

    rows = [
        {
            "Priority": "1",
            "Scope": "Discount >=30%",
            "Evidence": (
                f"Profit {format_currency(high_discount['profit'])}; "
                f"loss-line rate {format_pct(high_discount['loss_line_rate'])}"
            ),
            "Action": "Yeu cau review margin truoc khi ap dung giam gia >=30%.",
            "KPI": "Giam loss-line rate va cai thien total profit.",
            "Limitation": "Khong co COGS/freight nen khong chung minh nhan qua.",
        },
        {
            "Priority": "2",
            "Scope": "Tables va Bookcases",
            "Evidence": (
                f"Tables {format_currency(tables['total_profit'])}; "
                f"Bookcases {format_currency(bookcases['total_profit'])}"
            ),
            "Action": "Review pricing, promotion va state exposure truoc khi scale doanh thu.",
            "KPI": "Profit margin theo sub-category va top loss products.",
            "Limitation": "Can them cost detail de tach gia von va phi fulfillment.",
        },
        {
            "Priority": "3",
            "Scope": f"Central va cac bang uu tien: {state_names}",
            "Evidence": (
                f"Central profit {format_currency(central['total_profit'])}; "
                f"mean discount {format_pct(central['average_discount'])}"
            ),
            "Action": "Dung blanket promotion tai diem lo; drill down theo product x discount.",
            "KPI": "State profit, discount exposure va loss-line rate.",
            "Limitation": "State priority score la worklist minh bach, khong phai statistical model.",
        },
        {
            "Priority": "4",
            "Scope": "Chairs va Furnishings",
            "Evidence": (
                f"Chairs profit {format_currency(chairs['total_profit'])}; "
                f"Furnishings margin {format_pct(furnishings['profit_margin'])}"
            ),
            "Action": "Bao ve availability va test cross-sell co muc tieu thay vi discount rong.",
            "KPI": "Sales growth, profit growth va weighted margin.",
            "Limitation": "Khong co ton kho nen khong ket luan duoc stockout.",
        },
        {
            "Priority": "5",
            "Scope": "Repeat customers va segments",
            "Evidence": (
                f"Repeat-order share {format_pct(metric_baseline['kpis']['repeat_order_share'])}"
            ),
            "Action": "Uu tien offer co muc tieu cho khach lap lai/co loi nhuan thay vi giam gia dai tra.",
            "KPI": "Profit per order, AOV va customer margin.",
            "Limitation": "Chi la within-window behavior trong giai doan 2014-2017.",
        },
    ]
    recs = pd.DataFrame(rows)
    return f"""
# Khuyến nghị hành động

Mỗi khuyến nghị dưới đây gắn với evidence trong dữ liệu và được trình bày như hành động quản trị, không phải kết luận nhân quả tuyệt đối.

{dataframe_to_markdown(recs, max_rows=len(recs))}
"""


def _divergence_periods(monthly: pd.DataFrame) -> pd.DataFrame:
    data = monthly.copy()
    data["sales_rank"] = data["total_sales"].rank(ascending=False, method="dense")
    data["profit_rank"] = data["total_profit"].rank(ascending=False, method="dense")
    data["divergence_score"] = data["profit_rank"] - data["sales_rank"]
    return data.sort_values(["divergence_score", "total_sales"], ascending=[False, False])


def _first_negative_discount_threshold(discount_exact: pd.DataFrame) -> pd.Series:
    negative = discount_exact.sort_values("discount").loc[
        lambda frame: frame["total_profit"] < 0
    ]
    return negative.iloc[0]


def build_business_questions_report(
    outputs: dict[str, pd.DataFrame],
    metric_baseline: dict[str, Any],
) -> str:
    """Answer all required business questions from CONTEXT.md with evidence and implications."""

    kpi = metric_baseline["kpis"]
    high_discount = metric_baseline["high_discount_30_plus"]
    yearly = outputs["yearly_performance"]
    quarterly = outputs["quarterly_performance"]
    monthly = outputs["monthly_performance"]
    divergence = _divergence_periods(monthly)
    first_negative_discount = _first_negative_discount_threshold(
        outputs["discount_exact_performance"]
    )
    material_negative_states = outputs["state_priority_worklist"].loc[
        lambda frame: frame["total_profit"] < 0
    ]

    return f"""
# Trả lời câu hỏi kinh doanh

## A. Hiệu quả điều hành

**A1. Doanh thu, lợi nhuận và weighted margin biến động thế nào theo tháng, quý, năm?**  
Bảng tháng, quý và năm đã được xuất tại `reports/tables/monthly_performance.csv`, `quarterly_performance.csv`, và `yearly_performance.csv`. Năm 2017 đạt doanh thu {format_currency(yearly.loc[yearly["order_year"] == 2017, "total_sales"].iloc[0])}, nhưng margin chỉ {format_pct(yearly.loc[yearly["order_year"] == 2017, "profit_margin"].iloc[0])}.  
**Hàm ý:** tăng trưởng doanh thu cần được quản trị cùng chất lượng lợi nhuận, không chỉ theo doanh số.

{dataframe_to_markdown(yearly, ["order_year", "total_sales", "total_profit", "profit_margin", "sales_growth", "profit_growth"], max_rows=10)}

{dataframe_to_markdown(quarterly, ["order_quarter", "total_sales", "total_profit", "profit_margin", "sales_growth", "profit_growth"], max_rows=8)}

**A2-A3. Tăng trưởng doanh thu có chuyển thành tăng trưởng lợi nhuận không, và kỳ nào lệch nhất?**  
Các kỳ dưới đây có doanh thu xếp hạng cao hơn nhiều so với lợi nhuận.  
**Hàm ý:** cần review khuyến mại, nhóm sản phẩm và bang trong các kỳ doanh thu cao nhưng profit yếu.

{dataframe_to_markdown(divergence, ["order_month_label", "total_sales", "total_profit", "profit_margin", "sales_rank", "profit_rank", "divergence_score"], max_rows=8)}

**A4. Tỷ lệ dòng giao dịch bị lỗ là bao nhiêu?**  
Có {format_int(kpi["loss_line_count"])} dòng lỗ, tương đương {format_pct(kpi["loss_line_rate"])} tổng số dòng.  
**Hàm ý:** lỗ không phải ngoại lệ nhỏ; cần worklist kiểm soát giá/discount ở cấp dòng.

## B. Sản phẩm và danh mục

**B1. Sub-category nào tạo doanh thu, lợi nhuận và margin?**  
**Hàm ý:** Chairs tạo profit lớn nhất, Furnishings có margin tốt nhất; Tables và Bookcases cần sửa lợi nhuận trước khi mở rộng.

{dataframe_to_markdown(outputs["sub_category_performance"], ["sub_category", "total_sales", "total_profit", "profit_margin", "loss_line_rate"], max_rows=10)}

**B2. Sản phẩm nào doanh thu cao nhưng lợi nhuận thấp hoặc âm?**  
**Hàm ý:** các sản phẩm này thuộc nhóm `Repair`: cần xem lại giá, mức giảm giá và vùng bán.

{dataframe_to_markdown(outputs["product_classification_matrix"].loc[lambda frame: frame["classification"] == "Repair"], ["product_id", "product_name", "sub_category", "total_sales", "total_profit", "profit_margin", "classification"], max_rows=10)}

**B3. Sản phẩm nào có lợi nhuận tốt nhưng chưa đại diện lớn trong doanh thu?**  
**Hàm ý:** đây là nhóm có thể scale/cross-sell chọn lọc thay vì giảm giá đại trà.

{dataframe_to_markdown(outputs["underrepresented_profitable_products"], ["product_id", "product_name", "sub_category", "total_sales", "total_profit", "profit_margin"], max_rows=10)}

**B4-B5. Sản phẩm/sub-category và tổ hợp region x sub-category nào lỗ lớn nhất?**  
**Hàm ý:** ưu tiên review top loss products và ô region x sub-category âm sâu trước.

{dataframe_to_markdown(outputs["top_loss_products"], ["product_id", "product_name", "sub_category", "total_sales", "total_profit", "profit_margin"], max_rows=10)}

{dataframe_to_markdown(outputs["region_sub_category_performance"], ["region", "sub_category", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate"], max_rows=10)}

## C. Rủi ro discount và pricing

**C1. Profit và loss rate khác nhau thế nào theo discount level/band?**  
**Hàm ý:** discount càng cao càng cần kiểm soát margin; band `>30%` là vùng rủi ro rõ rệt.

{dataframe_to_markdown(outputs["discount_band_performance"], ["discount_band", "total_sales", "total_profit", "profit_margin", "loss_line_rate"], max_rows=10)}

**C2. Ngưỡng discount đầu tiên có aggregate profit âm là gì?**  
Discount {format_pct(first_negative_discount["discount"])} là mức đầu tiên có tổng profit âm trong bảng exact discount, với profit {format_currency(first_negative_discount["total_profit"])}. Nhóm discount >=30% có profit {format_currency(high_discount["profit"])} và loss-line rate {format_pct(high_discount["loss_line_rate"])}.  
**Hàm ý:** discount >=30% nên là exception cần phê duyệt margin.

**C3. Nhóm nào phơi nhiễm discount cao nhất?**  
**Hàm ý:** ưu tiên review các tổ hợp sub-category x region và state có profit âm dưới ngưỡng >=30%.

{dataframe_to_markdown(outputs["discount_threshold_worklist"], ["sub_category", "region", "total_sales", "total_profit", "average_discount", "loss_line_rate"], max_rows=10)}

**C4. Có pattern lỗ nào xảy ra dù không discount cao không?**  
**Hàm ý:** những dòng lỗ dưới 30% discount gợi ý vấn đề khác ngoài discount, nhưng cần thêm cost/freight để kết luận nguyên nhân.

{dataframe_to_markdown(outputs["loss_without_high_discount"], ["sub_category", "region", "state", "total_sales", "total_profit", "average_discount", "loss_line_rate"], max_rows=10)}

## D. Địa lý

**D1-D2. Region/state nào có lợi nhuận sau khi xét margin, và state nào doanh thu đáng kể nhưng âm profit?**  
**Hàm ý:** Central và các state điểm cao cần worklist quản trị riêng thay vì scale doanh thu tự động.

{dataframe_to_markdown(outputs["region_performance"], ["region", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate"], max_rows=10)}

{dataframe_to_markdown(material_negative_states, ["state", "region", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate", "priority_score"], max_rows=10)}

**D3-D4. State lỗ nặng có discount cao, sub-category cụ thể, hay cả hai? Tổ hợp region-product nào nên mở rộng/bảo vệ/review/giảm?**  
**Hàm ý:** dùng heatmap region x sub-category và state x sub-category để phân nhóm hành động: mở rộng ô xanh, bảo vệ ô profit cao, review/giảm ô âm sâu.

{dataframe_to_markdown(outputs["state_sub_category_performance"], ["state", "sub_category", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate"], max_rows=10)}

## E. Khách hàng và segment

**E1. Consumer, Corporate, Home Office khác nhau thế nào?**  
**Hàm ý:** segment có margin/loss-rate tốt hơn nên là nền cho cross-sell có mục tiêu.

{dataframe_to_markdown(outputs["segment_performance"], ["segment", "total_sales", "total_profit", "profit_margin", "average_discount", "loss_line_rate"], max_rows=10)}

**E2. Repeat customers đóng góp bao nhiêu hoạt động?**  
Repeat customers chiếm {format_pct(kpi["repeat_order_share"])} tổng số đơn trong cửa sổ dữ liệu.  
**Hàm ý:** có cơ sở để ưu tiên retention/cross-sell thay vì blanket discount.

{dataframe_to_markdown(outputs["repeat_customer_summary"], ["is_repeat_customer", "customers", "orders", "total_sales", "total_profit", "profit_margin", "order_share"], max_rows=10)}

**E3-E4. Khách hàng nào sales cao nhưng profit thấp/âm, và nhóm nào phù hợp cross-sell?**  
**Hàm ý:** dùng nhãn ẩn danh để review thương mại mà không phơi bày tên khách hàng không cần thiết.

{dataframe_to_markdown(outputs["high_sales_low_profit_customers"], ["customer_label", "segment", "customer_orders", "customer_sales", "customer_profit", "customer_margin"], max_rows=10)}

{dataframe_to_markdown(outputs["cross_sell_candidates"], ["customer_label", "segment", "customer_orders", "customer_sales", "customer_profit", "customer_margin"], max_rows=10)}

## F. Fulfillment context

**F1-F2. Shipping mode hoặc shipping days có khác biệt đáng kể về sales, profit, loss rate không?**  
Các bảng dưới đây là mô tả quan sát, không phải kết luận chi phí vận chuyển vì dữ liệu không có freight-cost field.  
**Hàm ý:** nếu mode hoặc số ngày giao hàng có loss-rate cao, nên xem như tín hiệu drill-down chứ không quy kết nguyên nhân.

{dataframe_to_markdown(outputs["ship_mode_performance"], ["ship_mode", "total_sales", "total_profit", "profit_margin", "shipping_days_avg", "loss_line_rate"], max_rows=10)}

{dataframe_to_markdown(outputs["shipping_days_performance"], ["shipping_days", "total_sales", "total_profit", "profit_margin", "loss_line_rate"], max_rows=10)}
"""


def write_reports(
    outputs: dict[str, pd.DataFrame],
    metric_baseline: dict[str, Any],
    settings: Settings,
) -> dict[str, str]:
    """Write required Markdown reports and return their paths."""

    report_paths = {
        "data_quality_report": settings.paths.reports_dir / "data_quality_report.md",
        "executive_summary": settings.paths.reports_dir / "executive_summary.md",
        "recommendations": settings.paths.reports_dir / "recommendations.md",
        "business_questions": settings.paths.reports_dir / "business_questions.md",
    }
    _write_text(report_paths["data_quality_report"], build_data_quality_report(metric_baseline))
    _write_text(
        report_paths["executive_summary"],
        build_executive_summary(outputs, metric_baseline),
    )
    _write_text(
        report_paths["recommendations"],
        build_recommendations_report(outputs, metric_baseline),
    )
    _write_text(
        report_paths["business_questions"],
        build_business_questions_report(outputs, metric_baseline),
    )
    return {name: str(path) for name, path in report_paths.items()}
