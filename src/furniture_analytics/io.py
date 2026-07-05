"""Input/output helpers for raw data, processed data, and metadata."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def file_sha256(path: str | Path) -> str:
    """Return the SHA-256 digest for a file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_metadata(path: str | Path, source_hash: str | None = None) -> dict[str, Any]:
    """Return reproducibility metadata for the raw source file."""

    raw_path = Path(path)
    return {
        "source_file": raw_path.name,
        "source_path": str(raw_path),
        "source_bytes": raw_path.stat().st_size,
        "sha256": source_hash or file_sha256(raw_path),
        "processed_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def load_raw_sales(path: str | Path, *, encoding: str, date_format: str) -> pd.DataFrame:
    """Load the raw sales file with strict encoding and date parsing."""

    df = pd.read_csv(path, encoding=encoding)
    for column in ["Order Date", "Ship Date"]:
        df[column] = pd.to_datetime(df[column], format=date_format, errors="raise")
    df["Postal Code"] = df["Postal Code"].astype("string")
    return df


def write_parquet(df: pd.DataFrame, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def write_json(data: dict[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
