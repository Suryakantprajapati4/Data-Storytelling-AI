"""
Data processing module for Data Storytelling AI.
Handles file upload, validation, profiling, and preprocessing.
"""

import io
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from utils.helpers import (
    classify_columns,
    data_quality_score,
    detect_outliers_iqr,
    fmt_number,
    fmt_pct,
)


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def load_uploaded_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load a CSV or XLSX file from a Streamlit UploadedFile object.
    Returns a DataFrame or None on failure.
    """
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, parse_dates=True)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            return None
    except Exception:
        return None

    # Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Data profiling
# ---------------------------------------------------------------------------

def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive data profile including missing values,
    duplicates, quality score, distributions, outliers, and correlations.
    """
    col_info = classify_columns(df)

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Column": df.columns,
        "Missing": missing.values,
        "Missing_%": missing_pct.values,
    }).sort_values("Missing_%", ascending=False).reset_index(drop=True)

    # Duplicates
    dup_count = int(df.duplicated().sum())
    dup_pct = round(dup_count / len(df) * 100, 2) if len(df) else 0

    # Quality score
    quality = data_quality_score(df)

    # Summary statistics
    summary_stats = df.describe(include="all").round(4)

    # Distribution analysis for numerical columns
    distributions = {}
    for col in col_info["numerical"]:
        if col in df.columns:
            distributions[col] = {
                "mean": round(df[col].mean(), 4),
                "median": round(df[col].median(), 4),
                "std": round(df[col].std(), 4),
                "min": round(df[col].min(), 4),
                "max": round(df[col].max(), 4),
                "skewness": round(df[col].skew(), 4),
                "kurtosis": round(df[col].kurtosis(), 4),
            }

    # Outlier detection
    outliers = detect_outliers_iqr(df, col_info["numerical"])

    # Correlation matrix (numerical only)
    corr_matrix = None
    if len(col_info["numerical"]) >= 2:
        corr_matrix = df[col_info["numerical"]].corr().round(4)

    return {
        "shape": df.shape,
        "row_count": df.shape[0],
        "col_count": df.shape[1],
        "columns": col_info,
        "missing_df": missing_df,
        "dup_count": dup_count,
        "dup_pct": dup_pct,
        "quality_score": quality,
        "summary_stats": summary_stats,
        "distributions": distributions,
        "outliers": outliers,
        "corr_matrix": corr_matrix,
        "dtypes": df.dtypes.astype(str).to_dict(),
    }


# ---------------------------------------------------------------------------
# Date parsing helper
# ---------------------------------------------------------------------------

def try_parse_dates(df: pd.DataFrame,
                    date_cols: list) -> pd.DataFrame:
    """Attempt to parse date columns to datetime."""
    df = df.copy()
    for col in date_cols:
        if col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col], format="mixed",
                                         errors="coerce")
            except Exception:
                pass
    return df


# ---------------------------------------------------------------------------
# Smart aggregation helpers
# ---------------------------------------------------------------------------

def top_categories(df: pd.DataFrame, cat_col: str, value_col: str,
                   n: int = 5, ascending: bool = False) -> pd.DataFrame:
    """Return top/bottom N categories by aggregated value."""
    agg = (df.groupby(cat_col)[value_col]
           .sum()
           .sort_values(ascending=ascending)
           .head(n)
           .reset_index())
    agg.columns = [cat_col, value_col]
    return agg


def time_series_agg(df: pd.DataFrame, date_col: str, value_col: str,
                    freq: str = "ME") -> pd.DataFrame:
    """Aggregate a value column over time at the given frequency."""
    tmp = df[[date_col, value_col]].copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    tmp = tmp.set_index(date_col)
    agg = tmp[value_col].resample(freq).sum().reset_index()
    agg.columns = [date_col, value_col]
    return agg


def compute_growth(series: pd.Series) -> float:
    """Compute percentage growth from first to last non-null value."""
    s = series.dropna()
    if len(s) < 2 or s.iloc[0] == 0:
        return 0.0
    return round((s.iloc[-1] - s.iloc[0]) / abs(s.iloc[0]) * 100, 2)
