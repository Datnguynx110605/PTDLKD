# Furniture Sales Revenue & Profit Optimization

Reproducible Python analysis for the Furniture-only sales dataset in `Dataset.csv`.

## Setup

```bash
python -m pip install -e ".[dev]"
```

## Run

```bash
python scripts/validate_data.py
python scripts/run_pipeline.py
streamlit run app/dashboard.py
pytest -q
ruff check .
```

## Outputs

- Cleaned data and summaries: `data/processed/`
- Reports: `reports/*.md`
- Drill-down tables: `reports/tables/`
- Figures: `reports/figures/`

All business-facing reports and dashboard labels are written in Vietnamese. Metrics are computed from `Dataset.csv` only, using weighted profit margin and distinct order/customer counts.
