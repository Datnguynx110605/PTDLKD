# Furniture Sales Revenue & Profit Optimization Plan

## Summary

Build a Python analytics project around the verified `Dataset.csv`, which matches the `CONTEXT.md` SHA-256 and baseline facts. The implementation will produce cleaned data, summary parquet files, CSV drill-down tables, professional charts, Vietnamese stakeholder reports, and a mandatory Streamlit dashboard.

Use `CONTEXT.md`, `Dataset.csv`, and this `PLAN.md` as required inputs. `Dataset.csv` is the canonical raw file in this workspace and must remain unchanged.

## Key Decisions

- Source file: use `Dataset.csv` as the canonical raw input in this workspace.
- Encoding/date parsing: `encoding="cp1252"` and date format `"%m/%d/%Y"` only.
- Stack: Python 3.11+, pandas, numpy, pyarrow, plotly, matplotlib, streamlit, pytest, ruff.
- Business artifact language: Vietnamese for reports/dashboard labels; English for code identifiers.
- Dashboard: mandatory, built on the same metric functions as reports.
- Margin rule: always weighted margin, `sum(profit) / sum(sales)`.
- Claims discipline: distinguish observed facts, evidence-backed hypotheses, and recommendations.

## Implementation Changes

- Create a clean project structure with `src/furniture_analytics/`, `tests/`, `reports/`, `reports/tables/`, `reports/figures/`, `data/processed/`, `app/`, `scripts/`, and `config/`.
- Add configuration for paths, expected baseline values, tolerances, top-N thresholds, product classification thresholds, high-discount threshold `0.30`, and chart/report settings.
- Implement canonical modules:
  - `io.py`: load raw CSV, hash source file, write parquet/json/csv outputs.
  - `validation.py`: schema checks, row-count checks, business-rule assertions, reconciliation checks.
  - `transform.py`: standardize names, type fields, add all required derived columns once.
  - `metrics.py`: weighted margin, AOV, distinct orders/customers, loss rate, growth, grouped summaries.
  - `analysis.py`: time, product, discount, geography, customer, segment, and shipping diagnostics.
  - `charts.py`: reusable professional figure builders.
  - `reporting.py`: Markdown report generation with Vietnamese labels and evidence tables.
  - `pipeline.py`: end-to-end orchestrator.
- Generate required data artifacts:
  - `data/processed/furniture_sales_clean.parquet`
  - `data/processed/customer_summary.parquet`
  - `data/processed/product_summary.parquet`
  - `data/processed/order_summary.parquet`
  - `data/processed/metric_baseline.json`
- Generate required reports:
  - `reports/data_quality_report.md`
  - `reports/executive_summary.md`
  - `reports/recommendations.md`
  - `reports/tables/*.csv`
  - `reports/figures/*.png`
- Implement Streamlit dashboard with date, region, state, segment, sub-category, discount-band, and ship-mode filters; KPI cards; weighted-margin tooltip; negative-profit and high-loss warnings.

## Required Analysis Coverage

- Executive performance: monthly, quarterly, yearly sales/profit/margin, growth divergence, loss-line share.
- Product: sub-category performance, high-sales negative-profit products, underrepresented profitable products, largest losses, product classification matrix.
- Discount: exact discount levels, required discount bands, independent `Discount >= 0.30` threshold, exposure by product, region, state, and sub-category.
- Geography: region/state profitability, high-sales negative-profit states, region x sub-category heatmap, state priority score.
- Customer/segment: segment performance, repeat activity, high-sales low-profit customers, privacy-safe customer labeling.
- Fulfillment: ship mode and shipping-days summaries, clearly descriptive only.

## Visualization Requirements

- Build at least these ten visuals: monthly sales/profit trend, sales plus margin by period, sub-category sales/profit, margin by discount band, state sales/profit view, region x sub-category heatmap, product sales/profit scatter, top loss products, segment comparison, and discount-risk worklist.
- Use clean professional styling: clear titles, readable labels, USD formatting, percent formatting, zero reference lines for profit/margin, diverging colors for losses/gains, horizontal bars for long product names, no 3D charts.
- Avoid overcrowding: top/bottom 10 defaults, materiality filters for states/products, no unnecessary customer names.

## Validation And Tests

- Fail loudly if baseline checks do not match: 2,121 rows, 21 columns, 1,764 orders, 707 customers, total sales `741999.7953`, total profit `18451.2728`, 714 loss lines, Furniture-only category, no missing values, unique `Row ID`, valid discounts, positive quantities, valid shipping dates.
- Add reconciliation tests for annual, regional, sub-category, discount-band, order, customer, and product summaries.
- Add unit tests for date parsing, discount-band boundaries, weighted margin, AOV distinct-order logic, repeat-customer logic, product grain, and row-count preservation.
- Add one integration test that runs the pipeline into a temporary output directory.
- Final review commands: `ruff check .`, `pytest -q`, and full pipeline run.

## Acceptance Criteria

- A clean environment can install and run the project from documented commands.
- All generated metrics reproduce `CONTEXT.md` baseline values within tolerance.
- All business questions in `CONTEXT.md` are answered with tables, charts, and business implications.
- Reports and dashboard do not overclaim beyond Furniture-only data and do not imply causality from correlation.
- Recommendations include scope, numeric evidence, action, KPI to monitor, and limitation.
- Final artifacts are reviewed for correctness, readability, and chart clarity before handoff.
