from __future__ import annotations

from furniture_analytics.config import load_settings
from furniture_analytics.pipeline import run_pipeline


def test_pipeline_runs_end_to_end_without_figures(tmp_path):
    settings = load_settings(
        "config/settings.yaml",
        processed_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        figures_dir=tmp_path / "reports" / "figures",
        tables_dir=tmp_path / "reports" / "tables",
    )
    result = run_pipeline(settings, generate_figures=False)
    baseline = result["metric_baseline"]
    assert round(baseline["kpis"]["total_sales"], 4) == 741999.7953
    assert round(baseline["kpis"]["total_profit"], 4) == 18451.2728
    assert (tmp_path / "processed" / "furniture_sales_clean.parquet").exists()
    assert (tmp_path / "reports" / "data_quality_report.md").exists()
