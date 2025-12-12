from datetime import datetime
from pathlib import Path
from typing import Iterable
import pandas as pd


def load_timeseries_from_csv(path: str | Path, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """Load CSV and parse timestamps; raises if missing timestamp column."""
    df = pd.read_csv(path)
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing required column: {timestamp_col}")
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)
    return df


def summarize_timeseries(df: pd.DataFrame, value_columns: Iterable[str]) -> dict:
    """Return basic summary stats for quick validation."""
    summaries = {}
    for col in value_columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        summaries[col] = {
            "count": int(series.count()),
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "mean": float(series.mean()) if not series.empty else None,
        }
    time_min = df["timestamp"].min() if "timestamp" in df else None
    time_max = df["timestamp"].max() if "timestamp" in df else None
    if isinstance(time_min, (pd.Timestamp, datetime)):
        time_min = time_min.isoformat()
    if isinstance(time_max, (pd.Timestamp, datetime)):
        time_max = time_max.isoformat()
    return {"columns": summaries, "time_range": [time_min, time_max]}
