from __future__ import annotations

from pathlib import Path

import pytest

from furniture_analytics.config import Settings, load_settings
from furniture_analytics.io import load_raw_sales
from furniture_analytics.transform import transform_sales

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings(ROOT / "config" / "settings.yaml")


@pytest.fixture(scope="session")
def raw_df(settings: Settings):
    return load_raw_sales(
        settings.paths.raw_csv,
        encoding=settings.input.encoding,
        date_format=settings.input.date_format,
    )


@pytest.fixture(scope="session")
def fact_df(raw_df):
    return transform_sales(raw_df)
