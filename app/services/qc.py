"""Data quality control checks for time series."""

import pandas as pd
import numpy as np


def check_range(series: pd.Series, min_val: float, max_val: float) -> pd.Series:
    """Flag values outside expected range."""
    return (series < min_val) | (series > max_val)


def check_spike(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Detect spikes using z-score method."""
    if len(series) < 3:
        return pd.Series([False] * len(series), index=series.index)
    z_scores = np.abs((series - series.mean()) / series.std())
    return z_scores > threshold


def check_flatline(series: pd.Series, window: int = 10, tolerance: float = 0.001) -> pd.Series:
    """Detect flat-line periods (consecutive identical or near-identical values)."""
    if len(series) < window:
        return pd.Series([False] * len(series), index=series.index)
    rolling_std = series.rolling(window=window, center=True).std()
    return rolling_std < tolerance


def check_missing(df: pd.DataFrame, timestamp_col: str = "timestamp", freq: str = "15min") -> dict:
    """Identify missing timestamps based on expected frequency."""
    df = df.sort_values(timestamp_col)
    expected_range = pd.date_range(
        start=df[timestamp_col].min(), end=df[timestamp_col].max(), freq=freq
    )
    actual_set = set(df[timestamp_col])
    missing = [ts for ts in expected_range if ts not in actual_set]
    return {"missing_count": len(missing), "missing_timestamps": [ts.isoformat() for ts in missing[:100]]}


def run_qc_checks(
    df: pd.DataFrame,
    parameter: str,
    min_val: float | None = None,
    max_val: float | None = None,
    spike_threshold: float = 3.0,
    flatline_window: int = 10,
) -> pd.DataFrame:
    """Run all QC checks on a time series parameter and return flagged DataFrame."""
    df = df.copy()
    flags = pd.Series(["OK"] * len(df), index=df.index)

    if min_val is not None and max_val is not None:
        range_flags = check_range(df[parameter], min_val, max_val)
        flags[range_flags] = "RANGE"

    spike_flags = check_spike(df[parameter], threshold=spike_threshold)
    flags[spike_flags] = "SPIKE"

    flat_flags = check_flatline(df[parameter], window=flatline_window)
    flags[flat_flags] = "FLAT"

    df["qc_flag"] = flags
    return df
