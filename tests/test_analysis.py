from __future__ import annotations

from furniture_analytics.analysis import build_analysis_outputs, build_summaries
from furniture_analytics.validation import validate_analysis_reconciliations, validate_summaries


def test_summary_grains_and_reconciliation(fact_df, settings):
    summaries = build_summaries(fact_df, settings)
    assert summaries["order_summary"]["order_id"].is_unique
    assert summaries["customer_summary"]["customer_id"].is_unique
    assert not summaries["product_summary"].duplicated(
        ["product_id", "product_name", "sub_category"]
    ).any()
    validate_summaries(fact_df, summaries, settings)


def test_required_analysis_outputs_exist(fact_df, settings):
    summaries = build_summaries(fact_df, settings)
    outputs = build_analysis_outputs(fact_df, summaries, settings)
    for name in [
        "monthly_performance",
        "yearly_performance",
        "sub_category_performance",
        "discount_band_performance",
        "region_sub_category_performance",
        "state_priority_worklist",
        "segment_performance",
        "ship_mode_performance",
    ]:
        assert name in outputs
        assert not outputs[name].empty
    validate_analysis_reconciliations(fact_df, outputs, settings)
