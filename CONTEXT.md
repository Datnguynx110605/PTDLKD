# Coding Agent Context — Furniture Sales: Revenue & Profit Optimization

> **Document purpose:** This document is the single source of truth for a coding agent that must build a reproducible analysis and/or dashboard from `stores_sales_forecasting.csv`. It combines the business objective, dataset contract, confirmed baseline facts, metric definitions, analytical rules, and expected outputs.
>
> **Language:** Vietnamese for business-facing artifacts; English identifiers, file names, and code symbols are acceptable and preferred for maintainability.
>
> **Dataset file:** `stores_sales_forecasting.csv`  
> **Input encoding:** `cp1252`  
> **SHA-256:** `64764de9612919ec940f08191bb728bcb5579e682a630706ee624f8f13d7dc4f`  
> **Analysis grain:** one row = one product line within an order, not one order.

---

## 1. Mission and decision context

The business goal is to analyze retail sales data to **increase revenue without sacrificing profitability**. The dataset covers only the `Furniture` category, so the solution must not make claims about the company’s whole retail business. Its focus is:

1. Identify where Furniture revenue and profit are created or destroyed.
2. Determine which product groups, geographic areas, customers, and discount practices should be prioritized.
3. Surface loss-making transactions and patterns early enough for pricing or promotion decisions.
4. Produce an auditable analysis that a business user can reproduce from the supplied CSV.

The primary decision question is:

> **How should the retailer change product, geographic, and discount decisions to improve Furniture profit while preserving or increasing sustainable revenue?**

### 1.1 Required analytical posture

The agent must distinguish between:

- **Observed facts:** directly computed from this dataset.
- **Evidence-backed hypotheses:** plausible explanations supported by patterns, but not directly proven because key cost fields are missing.
- **Recommendations:** actions derived from findings, explicitly labeled as recommendations rather than established facts.

Do **not** claim that a variable causes another variable merely because they correlate. In particular, the data indicates a strong association between high discount levels and losses, but it does not include detailed product cost, freight cost, marketing spend, or returns; therefore the full causal mechanism cannot be proven.

---

## 2. Scope, non-scope, and constraints

### In scope

- Data ingestion, validation, profiling, cleaning, and feature engineering.
- Descriptive, diagnostic, and prioritization analysis of Furniture sales.
- Sales, profit, margin, discount, product, customer, regional, state, and time analysis.
- Reproducible charts/tables and, where requested, an interactive dashboard.
- A recommendations report tied to quantified evidence.

### Out of scope

- Company-wide analysis outside Furniture.
- Exact gross-margin or unit-cost reconstruction; no cost-of-goods field exists.
- Marketing attribution, inventory optimization, stockout modeling, returns analysis, and channel performance analysis; corresponding fields are absent.
- Causal experimentation, price elasticity estimation, or an automated pricing engine.
- Forecasting as a business truth. Any forecast is optional, must be clearly labeled as exploratory, and requires temporal validation.

### Non-negotiable constraints

- Use **only** the supplied data for factual claims unless an additional data source is explicitly provided.
- Read the CSV with `encoding="cp1252"`.
- Parse dates with the explicit format `"%m/%d/%Y"`.
- Never sum `Sales` or `Profit` after joining the fact table to a non-deduplicated dimension table.
- Do not average row-level profit margins to create an aggregate margin. Use weighted margin: `SUM(Profit) / SUM(Sales)`.
- Count orders with `nunique(Order ID)`; count customers with `nunique(Customer ID)`; do not count lines.
- Preserve the original raw file unchanged. All transformed data must be written separately.

---

## 3. Dataset profile — confirmed baseline

### 3.1 Dataset size and temporal coverage

| Property | Confirmed value |
|---|---:|
| Rows / transaction lines | 2,121 |
| Columns | 21 |
| Unique orders | 1,764 |
| Unique customers | 707 |
| Unique product IDs | 375 |
| Unique product names | 380 |
| Unique states | 48 |
| Unique cities | 371 |
| Unique regions | 4 |
| Customer segments | 3 |
| Ship modes | 4 |
| Order date coverage | 2014-01-06 to 2017-12-30 |
| Ship date coverage | 2014-01-10 to 2018-01-05 |
| Category coverage | Furniture only |
| Missing values | 0 |
| Fully duplicated rows | 0 |
| Duplicate `Row ID` values | 0 |
| Ship dates before order dates | 0 |

### 3.2 Baseline business KPIs

| KPI | Value |
|---|---:|
| Total sales | $741,999.80 |
| Total profit | $18,451.27 |
| Overall profit margin | 2.49% |
| Total quantity | 8,028 |
| Average order value | $420.63 |
| Average profit per order | $10.46 |
| Loss-making transaction lines | 714 of 2,121 |
| Loss-making line rate | 33.66% |
| Customers with 2+ orders | 516 of 707 (72.99%) |
| Share of orders from repeat customers | 89.17% |

### 3.3 Category and sub-category coverage

`Category` is constant and equal to `Furniture` for every row. Use `Sub-Category` as the highest useful product grouping.

| Sub-Category | Transaction lines | Sales | Profit | Profit margin |
|---|---:|---:|---:|---:|
| Chairs | 617 | $328,449.10 | $26,590.17 | 8.10% |
| Tables | 319 | $206,965.53 | -$17,725.48 | -8.56% |
| Bookcases | 228 | $114,880.00 | -$3,472.56 | -3.02% |
| Furnishings | 957 | $91,705.16 | $13,059.14 | 14.24% |

### 3.4 Region baseline

| Region | Sales | Profit | Profit margin | Mean row discount | Loss-making line rate |
|---|---:|---:|---:|---:|---:|
| West | $252,612.74 | $11,504.95 | 4.55% | 13.14% | 21.92% |
| East | $208,291.20 | $3,046.17 | 1.46% | 15.41% | 30.62% |
| Central | $163,797.16 | -$2,871.05 | -1.75% | 29.74% | 65.90% |
| South | $117,298.68 | $6,771.21 | 5.77% | 12.15% | 17.47% |

### 3.5 Annual baseline

| Year | Sales | Profit | Profit margin | Sales growth vs. prior year | Profit growth vs. prior year |
|---|---:|---:|---:|---:|---:|
| 2014 | $157,192.85 | $5,457.73 | 3.47% | — | — |
| 2015 | $170,518.24 | $3,015.20 | 1.77% | 8.48% | -44.75% |
| 2016 | $198,901.44 | $6,959.95 | 3.50% | 16.65% | 130.83% |
| 2017 | $215,387.27 | $3,018.39 | 1.40% | 8.29% | -56.63% |

### 3.6 Discount baseline — highest-priority risk signal

The `Discount` field is stored as a decimal fraction. Example: `0.20` means 20%.

| Discount level | Sales | Profit | Profit margin | Transaction lines | Loss-making line rate |
|---|---:|---:|---:|---:|---:|
| 0% | $256,025.27 | $58,133.08 | 22.71% | 836 | 0.00% |
| 10% | $46,634.25 | $7,111.01 | 15.25% | 76 | 5.26% |
| 15% | $27,558.52 | $1,418.99 | 5.15% | 52 | 32.69% |
| 20% | $216,631.02 | $6,265.95 | 2.89% | 615 | 26.99% |
| 30% | $99,470.35 | -$10,695.32 | -10.75% | 222 | 93.24% |
| >30% combined | $95,680.39 | -$43,782.44 | -45.76% | 320 | 100.00% |

Transactions with discount **30% or higher** represent 26.30% of sales, generate **-$54,477.76** in profit, and 97.23% of those lines are loss-making. Treat this as a priority diagnostic, not a proven single-cause conclusion.

---

## 4. Raw data contract

### 4.1 Source fields

| Field | Type after ingestion | Business meaning | Validation / handling |
|---|---|---|---|
| `Row ID` | integer | Unique raw line identifier | Must be unique and non-null. |
| `Order ID` | string | Order identifier; multiple lines per order are expected | Non-null; use `nunique` for order counts. |
| `Order Date` | datetime | Date the order was made | Parse `%m/%d/%Y`; non-null. |
| `Ship Date` | datetime | Date the order was shipped | Parse `%m/%d/%Y`; must be >= order date. |
| `Ship Mode` | categorical string | Shipping service level | Expected: Standard Class, Second Class, First Class, Same Day. |
| `Customer ID` | string | Customer identifier | Use for customer-level aggregation. |
| `Customer Name` | string | Customer label | PII-like descriptive data; do not show unnecessarily. |
| `Segment` | categorical string | Customer segment | Expected: Consumer, Corporate, Home Office. |
| `Country` | categorical string | Country | Constant: United States. |
| `City` | string | City of sale | Validate non-null. |
| `State` | string | State of sale | Validate non-null. |
| `Postal Code` | nullable string or integer | Postal code | Store as string in output to preserve leading zeroes if present. |
| `Region` | categorical string | Region of sale | Expected: Central, East, South, West. |
| `Product ID` | string | Product SKU-like identifier | Use with `Product Name` for product reporting. |
| `Category` | categorical string | Main product category | Constant: Furniture. Assert this explicitly. |
| `Sub-Category` | categorical string | Product grouping | Expected: Bookcases, Chairs, Furnishings, Tables. |
| `Product Name` | string | Product display label | May map non-1:1 to product IDs; do not assume uniqueness. |
| `Sales` | float | Line revenue | Must be non-negative. |
| `Quantity` | integer | Units on the line | Must be positive. |
| `Discount` | float | Discount fraction | Must fall in [0, 1]. Format as percentage for presentation. |
| `Profit` | float | Line profit supplied by source | May be negative; do not remove negative values. |

### 4.2 Safe ingestion contract

```python
import pandas as pd

RAW_PATH = "data/raw/stores_sales_forecasting.csv"
DATE_COLUMNS = ["Order Date", "Ship Date"]

df = pd.read_csv(RAW_PATH, encoding="cp1252")
for column in DATE_COLUMNS:
    df[column] = pd.to_datetime(df[column], format="%m/%d/%Y", errors="raise")

df["Postal Code"] = df["Postal Code"].astype("string")
```

Never rely on automatic date parsing for this file; it can silently switch day/month interpretation on ambiguous values.

---

## 5. Required derived fields

The processed fact table must retain all raw columns and add the following standardized columns. Prefer snake_case for new columns while retaining a clear raw-to-clean field map.

| New field | Definition | Type | Rule |
|---|---|---|---|
| `order_year` | year of `Order Date` | integer | `order_date.dt.year` |
| `order_quarter` | calendar quarter | string | `YYYY-QN` recommended |
| `order_month` | month start date | datetime | `order_date.to_period('M').to_timestamp()` |
| `order_month_label` | human readable month | string | e.g. `2017-11` for stable sorting |
| `order_weekday` | day name | ordered category | Monday through Sunday |
| `shipping_days` | elapsed days between order and ship | integer | `ship_date - order_date`; must be >= 0 |
| `profit_margin` | row-level margin | float | `profit / sales` only where sales > 0 |
| `is_loss_line` | row loss flag | boolean | `profit < 0` |
| `is_zero_profit_line` | zero-profit flag | boolean | `profit == 0` with numerical tolerance if needed |
| `discount_pct` | presentation-friendly discount | float | `discount * 100` |
| `discount_band` | grouped discount level | ordered category | See exact band rules below |
| `sales_per_unit` | line sales per unit | float | `sales / quantity` where quantity > 0 |
| `profit_per_unit` | line profit per unit | float | `profit / quantity` where quantity > 0 |
| `product_label` | product display key | string | `Product ID + ' — ' + Product Name` |
| `is_repeat_customer` | repeat-customer flag | boolean | customer has >= 2 distinct orders across full data window |
| `customer_order_count` | lifetime orders in data window | integer | `nunique(Order ID)` per customer |
| `customer_sales` | lifetime customer sales | float | sum of line sales per customer |
| `customer_profit` | lifetime customer profit | float | sum of line profit per customer |
| `customer_last_order_date` | latest customer order | datetime | max order date per customer |
| `customer_recency_days` | days since latest order to analysis cutoff | integer | `cutoff - customer_last_order_date`; cutoff = max overall order date |

### 5.1 Mandatory discount bands

Use these exact, non-overlapping bands for the core reporting layer:

| Label | Inclusive lower bound | Inclusive upper bound |
|---|---:|---:|
| `0%` | 0.00 | 0.00 |
| `1-10%` | >0.00 | 0.10 |
| `11-20%` | >0.10 | 0.20 |
| `21-30%` | >0.20 | 0.30 |
| `>30%` | >0.30 | 1.00 |

When showing `30%+` as a management threshold, calculate it independently as `Discount >= 0.30`; it intentionally crosses the reporting-band boundary.

---

## 6. Metric dictionary and aggregation rules

### 6.1 Core measures

| Metric | Definition | Valid aggregation |
|---|---|---|
| `total_sales` | `SUM(Sales)` | Sum across selected lines |
| `total_profit` | `SUM(Profit)` | Sum across selected lines |
| `profit_margin` | `SUM(Profit) / SUM(Sales)` | Weighted; never mean of margins |
| `orders` | count distinct `Order ID` | Distinct count |
| `customers` | count distinct `Customer ID` | Distinct count |
| `quantity` | `SUM(Quantity)` | Sum |
| `average_order_value` | `SUM(Sales) / COUNT_DISTINCT(Order ID)` | Aggregate metric only |
| `profit_per_order` | `SUM(Profit) / COUNT_DISTINCT(Order ID)` | Aggregate metric only |
| `loss_line_count` | count rows where `Profit < 0` | Sum of boolean flag |
| `loss_line_rate` | `loss_line_count / row_count` | Ratio |
| `average_discount` | arithmetic mean of `Discount` over lines | Only label as line-weighted mean |
| `discounted_sales_share` | `SUM(Sales where Discount > 0) / SUM(Sales)` | Ratio |
| `sales_growth` | `(sales_t - sales_t-1) / sales_t-1` | Only comparable periods |
| `profit_growth` | `(profit_t - profit_t-1) / abs(profit_t-1)` | Prefer this robust denominator when prior profit could be negative; label clearly |
| `shipping_days_avg` | average `shipping_days` | Mean |

### 6.2 Margin safeguards

- Display profit margin as a percentage with at least one decimal point in dashboards; use two decimals in tables.
- For groups with `Sales == 0`, render margin as `N/A`, not 0%.
- Do not rank product margins without a sales-volume minimum; tiny sales amounts can create misleading percentage rankings.
- Use the source `Profit` field as supplied. Do not recompute profit from sales and discount because price/cost inputs are not available.

### 6.3 Customer metrics scope

Customer frequency, recency, and monetary measures are **within-window measures** for 2014-01-06 to 2017-12-30. They do not represent lifetime customer behavior outside the supplied dataset.

---

## 7. Business questions to answer

The implementation must answer the following in a traceable way. Every answer should be supported by a metric, table, or chart and end with a business implication.

### A. Executive performance

1. How do sales, profit, and weighted profit margin move by month, quarter, and year?
2. Does sales growth translate into profit growth?
3. Which periods have the largest divergence between sales and profit?
4. What proportion of transaction lines loses money?

### B. Product and assortment performance

1. Which sub-categories drive sales, profit, and margin?
2. Which products have high sales but low or negative profit?
3. Which products are profitable but underrepresented in sales?
4. Which products or sub-categories have the largest total losses?
5. Which sub-category × region combinations create or destroy profit?

### C. Discount and pricing risk

1. How do profit and loss rate differ by discount level and discount band?
2. At what discount threshold does the dataset first show aggregate negative profit?
3. Which products, sub-categories, regions, and states are most exposed to high discounts?
4. Which loss-making patterns occur even without high discounts, indicating an additional issue beyond discounts?

### D. Geographic performance

1. Which regions and states are profitable after considering margin, not only sales?
2. Which states generate material sales but negative profit?
3. Do loss-heavy states have unusually high discounts, particular sub-categories, or both?
4. Which regional product combinations should be expanded, protected, reviewed, or reduced?

### E. Customer and segment performance

1. How do Consumer, Corporate, and Home Office differ in sales, profit, margin, and discount?
2. What share of activity comes from repeat customers?
3. Which customers have high sales but low/negative profit?
4. Which customer groups are candidates for profitable cross-sell rather than broad discounts?

### F. Fulfillment context

1. Do shipping modes or shipping days show material differences in sales, profit, or loss rate?
2. Treat these as descriptive relationships only. The dataset has no freight-cost field.

---

## 8. Known high-priority findings to reproduce and investigate

These are baseline facts generated from the supplied file. The agent must validate them in the pipeline; any mismatch should be surfaced rather than silently ignored.

1. **Profit quality weakened in 2017.** Sales reached $215,387.27, but profit was $3,018.39 and weighted margin was 1.40%, versus 3.50% in 2016.
2. **Tables and Bookcases are unprofitable overall.** Tables lost $17,725.48 and Bookcases lost $3,472.56.
3. **Central is the only unprofitable region overall.** It lost $2,871.05 while carrying the highest mean row discount at 29.74%.
4. **High discounts are strongly associated with losses.** All lines above 30% discount are loss-making in this data; 30% discount alone has a 93.24% loss-line rate.
5. **East × Tables is the most severe region/sub-category loss combination.** It lost $11,025.38 with a mean discount of 37.38%.
6. **Several high-sales states are deeply unprofitable.** Texas, Illinois, Pennsylvania, and Ohio require a drill-down by product and discount.
7. **The best margin source is Furnishings, not the largest sales source.** Furnishings has a 14.24% margin, whereas Chairs generates the largest sales and profit dollars.
8. **Repeat activity is meaningful.** Customers with at least two orders account for 89.17% of unique orders in the dataset window.

---

## 9. Required deliverables

The coding agent should produce these artifacts unless the execution environment explicitly limits a format.

### 9.1 Data artifacts

- `data/processed/furniture_sales_clean.parquet` — cleaned, typed, feature-engineered fact table.
- `data/processed/customer_summary.parquet` — one row per customer.
- `data/processed/product_summary.parquet` — one row per product ID and product name.
- `data/processed/order_summary.parquet` — one row per order.
- `data/processed/metric_baseline.json` — key validation values and analysis metadata.

### 9.2 Analysis artifacts

- `reports/data_quality_report.md`
- `reports/executive_summary.md`
- `reports/recommendations.md`
- `reports/tables/*.csv` for principal drill-down tables.
- `reports/figures/*.png` or interactive HTML equivalents.

### 9.3 Dashboard or visualization requirements

A dashboard implementation, if requested, must include:

- A global date filter.
- Filters for region, state, segment, sub-category, discount band, and ship mode.
- KPI cards: Sales, Profit, Margin, Orders, Customers, AOV, Loss Line Rate.
- A distinction between sales ranking and profit ranking.
- A tooltip or annotation defining weighted profit margin.
- A visual warning when the filtered data contains negative total profit or a high loss-line rate.

### 9.4 Minimum visualization set

1. Monthly sales and profit trend.
2. Monthly or quarterly sales with weighted profit margin overlay.
3. Sub-category sales vs. profit comparison.
4. Profit margin by discount band.
5. State-level sales vs. profit scatter or ranked bar chart.
6. Region × Sub-Category profit heatmap.
7. Product sales vs. profit scatter, with a clear zero-profit line.
8. Top loss-making products table.
9. Segment performance comparison.
10. Optional: Customer frequency vs. total sales scatter with privacy-safe labels.

---

## 10. Analytical design rules

### 10.1 Product classification matrix

At product and sub-category level, classify items using sales and profit dimensions:

| Classification | Rule | Suggested action |
|---|---|---|
| Grow | High sales, positive profit, acceptable margin | Protect availability and test targeted growth. |
| Repair | High sales, low/negative profit | Review price, discount, product cost, and state exposure. |
| Scale selectively | Low/moderate sales, high margin | Improve discoverability and cross-sell. |
| Rationalize | Low sales, low/negative profit | Review for reduced promotion, pricing change, or discontinuation. |

The exact high/low threshold must be configurable. Default recommendation: use median sales among products with at least three transaction lines, then document the rule used.

### 10.2 State prioritization score

Create a transparent priority score for a management worklist. A recommended starting rule:

- Add points for negative total profit.
- Add points for sales above the state median.
- Add points for high mean discount.
- Add points for high loss-line rate.
- Add points for material absolute loss.

Do not present this as a statistical model. It is a triage mechanism whose formula must be visible in the report.

### 10.3 Recommendation discipline

Every recommendation must name:

- The affected scope: product / sub-category / state / region / segment / discount band.
- The evidence: a specific KPI or ranked result.
- The proposed business action.
- The intended KPI change.
- A risk or limitation.

Example format:

> **Scope:** Tables in East. **Evidence:** -$11,025.38 profit and 37.38% mean line discount. **Action:** pause blanket discounting and require margin review for discounts ≥30%. **Expected KPI:** reduce loss-line rate and improve total profit. **Limitation:** cost and freight details are unavailable, so profitability drivers cannot be fully decomposed.

---

## 11. Data-quality and validation requirements

### 11.1 Assertions that must fail loudly

```text
- Raw row count == 2,121
- Raw column count == 21
- No missing values in supplied baseline file
- Row ID is unique
- Category has exactly one value: Furniture
- Sales >= 0 for every row
- Quantity > 0 for every row
- 0 <= Discount <= 1 for every row
- Ship Date >= Order Date for every row
- Total sales is approximately 741,999.7953 (tolerance: 0.01)
- Total profit is approximately 18,451.2728 (tolerance: 0.01)
- Unique Order ID count == 1,764
- Unique Customer ID count == 707
```

### 11.2 Reconciliation checks

The following must reconcile within rounding tolerance:

- Sum of annual sales/profit equals dataset total.
- Sum of regional sales/profit equals dataset total.
- Sum of sub-category sales/profit equals dataset total.
- Sum of discount-band sales/profit equals dataset total.
- Sum of order-level sales/profit equals line-level sales/profit.
- Customer-level sales/profit sums equal line-level sales/profit.

### 11.3 Missing-data policy for future refreshes

The supplied file has no missing values, but future refreshes may. Apply this policy:

- Critical IDs and dates missing: quarantine rows, report row count and reason; do not silently impute.
- Missing geographic or segment fields: preserve row for totals, label as `Unknown` in grouped reporting.
- Missing numeric financial fields: do not replace with zero without an explicit business rule.
- Invalid date format: fail the build unless a controlled parser and audit log are implemented.

---

## 12. Implementation conventions for the coding agent

### 12.1 Reproducibility

- Use a deterministic pipeline and a fixed raw input path configured via environment variable or configuration file.
- Record source file name, SHA-256, processing timestamp, row counts, and configuration version in the baseline JSON.
- Use one canonical transformation function; avoid repeating feature logic in dashboard callbacks and notebooks.
- Keep raw data, processed data, figures, reports, and code separate.

### 12.2 Code quality

- Use typed functions where practical.
- Separate I/O, transformation, aggregation, visualization, and reporting logic.
- Use functions with stable, testable inputs and outputs.
- Avoid hidden global state.
- Make thresholds/configuration parameters explicit.
- Use user-facing Vietnamese labels where business stakeholders see them.
- Ensure money formatting uses `$` and two decimal places in detailed tables.

### 12.3 Privacy and presentation

- Customer names are not necessary for executive outputs. Prefer customer IDs or anonymized labels.
- Never expose raw postal code if it is not relevant to the view.
- Limit product labels in charts to top-N or filtered selections to preserve readability.
- Do not use 3D charts.
- Avoid pie charts with more than five slices; the four sub-categories are the only acceptable pie/donut use case.

---

## 13. Definition of done

The work is complete when all of the following are true:

1. The raw dataset is ingested using the correct encoding and explicit date format.
2. Automated validation checks pass and reproduce the principal baseline totals.
3. Cleaned and summarized datasets are generated from a single transformation pipeline.
4. The required business questions have evidence-backed answers.
5. The core visualizations are generated and read correctly at a glance.
6. Key recommendations identify the scope, evidence, proposed action, metric target, and limitation.
7. The project can be rerun from a clean environment using documented commands.
8. No conclusion expands beyond the Furniture-only dataset or presents correlation as confirmed causation.

---

## 14. Suggested final narrative for business users

The analysis should lead with this framing, supported by the reproducible results:

> Furniture sales grew over the observed period, but profit did not scale with sales. The central management issue is not simply demand generation; it is profit quality. Tables and Bookcases, high-discount transactions, and several high-revenue states are major loss sources. Chairs and Furnishings provide the most credible paths to profitable growth, while discounts of 30% or more should be treated as a margin-control exception rather than a routine lever.
