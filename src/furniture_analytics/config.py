"""Configuration loading for paths, validation baselines, and analysis thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PathSettings:
    raw_csv: Path
    processed_dir: Path
    reports_dir: Path
    figures_dir: Path
    tables_dir: Path


@dataclass
class InputSettings:
    encoding: str
    date_format: str


@dataclass
class AnalysisSettings:
    currency: str
    analysis_cutoff: str
    top_n_products: int
    min_product_line_count_for_margin_ranking: int
    high_discount_review_threshold: float
    high_loss_line_rate_threshold: float
    product_high_low_method: str
    significant_state_sales_threshold: str


@dataclass
class ValidationSettings:
    tolerance: float
    expected_rows: int
    expected_columns: int
    expected_orders: int
    expected_customers: int
    expected_total_sales: float
    expected_total_profit: float
    expected_loss_lines: int
    expected_sha256: str


@dataclass
class Settings:
    paths: PathSettings
    input: InputSettings
    analysis: AnalysisSettings
    validation: ValidationSettings

    def ensure_output_dirs(self) -> None:
        for directory in [
            self.paths.processed_dir,
            self.paths.reports_dir,
            self.paths.figures_dir,
            self.paths.tables_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


def _path(value: str | Path, base_dir: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def load_settings(
    settings_path: str | Path = "config/settings.yaml",
    *,
    raw_csv: str | Path | None = None,
    processed_dir: str | Path | None = None,
    reports_dir: str | Path | None = None,
    figures_dir: str | Path | None = None,
    tables_dir: str | Path | None = None,
) -> Settings:
    """Load project settings and optionally override output paths."""

    settings_file = Path(settings_path)
    base_dir = settings_file.parent.parent if settings_file.parent.name == "config" else Path.cwd()
    data: dict[str, Any] = yaml.safe_load(settings_file.read_text(encoding="utf-8"))

    path_data = data["paths"]
    paths = PathSettings(
        raw_csv=_path(raw_csv or path_data["raw_csv"], base_dir),
        processed_dir=_path(processed_dir or path_data["processed_dir"], base_dir),
        reports_dir=_path(reports_dir or path_data["reports_dir"], base_dir),
        figures_dir=_path(figures_dir or path_data["figures_dir"], base_dir),
        tables_dir=_path(tables_dir or path_data["tables_dir"], base_dir),
    )
    return Settings(
        paths=paths,
        input=InputSettings(**data["input"]),
        analysis=AnalysisSettings(**data["analysis"]),
        validation=ValidationSettings(**data["validation"]),
    )
