"""
General-purpose helper utilities for Data Storytelling AI.
"""

import re
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Column classification
# ---------------------------------------------------------------------------

def classify_columns(df: pd.DataFrame) -> dict:
    """
    Classify dataframe columns into numerical, categorical, datetime, and
    potential target metrics.
    """
    numerical = []
    categorical = []
    datetime_cols = []
    target_candidates = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numerical.append(col)
            # Heuristic: columns with many unique numeric values may be targets
            if df[col].nunique() > 10 and df[col].nunique() < len(df) * 0.5:
                target_candidates.append(col)
        elif pd.api.types.is_string_dtype(df[col]) or isinstance(
                df[col].dtype, pd.CategoricalDtype):
            categorical.append(col)
        else:
            # Try to parse as datetime
            try:
                pd.to_datetime(df[col], errors="raise", format="mixed")
                datetime_cols.append(col)
            except Exception:
                categorical.append(col)

    # If no explicit target, pick the first numeric with high cardinality
    if not target_candidates and numerical:
        target_candidates = sorted(
            numerical,
            key=lambda c: df[c].nunique(),
            reverse=True
        )[:2]

    return {
        "numerical": numerical,
        "categorical": categorical,
        "datetime": datetime_cols,
        "target_candidates": target_candidates,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_number(val, decimals: int = 2) -> str:
    """Format a number with commas and fixed decimals."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    if isinstance(val, (int, np.integer)):
        return f"{val:,}"
    if isinstance(val, (float, np.floating)):
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:,.{decimals}f}M"
        if abs(val) >= 1_000:
            return f"{val / 1_000:,.{decimals}f}K"
        return f"{val:,.{decimals}f}"
    return str(val)


def fmt_pct(val, decimals: int = 1) -> str:
    """Format a value as a percentage string."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    return f"{val:+.{decimals}f}%"


def fmt_currency(val, symbol: str = "$", decimals: int = 2) -> str:
    """Format a number as currency."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    return f"{symbol}{fmt_number(val, decimals)}"


# ---------------------------------------------------------------------------
# Data quality score
# ---------------------------------------------------------------------------

def data_quality_score(df: pd.DataFrame) -> float:
    """
    Compute a 0-100 data quality score based on completeness,
    duplicate ratio, and type consistency.
    """
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0

    missing = df.isnull().sum().sum()
    completeness = 1 - (missing / total_cells)

    dup_ratio = df.duplicated().sum() / max(len(df), 1)

    # Type consistency: penalise columns with mixed types
    type_penalty = 0
    for col in df.columns:
        types = df[col].dropna().apply(type).nunique()
        if types > 2:
            type_penalty += 0.05

    score = (completeness * 0.5 + (1 - dup_ratio) * 0.3 +
             max(0, 1 - type_penalty) * 0.2) * 100
    return round(min(score, 100), 1)


# ---------------------------------------------------------------------------
# Outlier detection (IQR)
# ---------------------------------------------------------------------------

def detect_outliers_iqr(df: pd.DataFrame,
                        columns: List[str] = None) -> dict:
    """Return outlier counts per column using IQR method."""
    results = {}
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    for col in cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        results[col] = {
            "count": outlier_count,
            "pct": round(outlier_count / len(df) * 100, 2) if len(df) else 0,
            "lower_bound": round(lower, 4),
            "upper_bound": round(upper, 4),
        }
    return results


# ---------------------------------------------------------------------------
# Smart column guessers
# ---------------------------------------------------------------------------

def guess_revenue_column(df: pd.DataFrame,
                         numerical_cols: List[str]) -> Optional[str]:
    """Try to find a revenue/sales/amount column."""
    keywords = ["revenue", "sales", "amount", "total", "income", "price"]
    for col in numerical_cols:
        if any(kw in col.lower() for kw in keywords):
            return col
    # Fall back to the column with the largest sum
    if numerical_cols:
        return max(numerical_cols, key=lambda c: df[c].sum())
    return None


def guess_date_column(df: pd.DataFrame,
                      datetime_cols: List[str]) -> Optional[str]:
    """Try to find the primary date column."""
    keywords = ["date", "time", "period", "month", "year", "day"]
    for col in datetime_cols:
        if any(kw in col.lower() for kw in keywords):
            return col
    return datetime_cols[0] if datetime_cols else None


def guess_category_column(df: pd.DataFrame,
                          categorical_cols: List[str]) -> Optional[str]:
    """Try to find a primary category/segment column."""
    keywords = ["category", "segment", "region", "product", "type", "group"]
    for col in categorical_cols:
        if any(kw in col.lower() for kw in keywords):
            return col
    return categorical_cols[0] if categorical_cols else None


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def snake_to_title(text: str) -> str:
    """Convert snake_case or camelCase to Title Case."""
    text = re.sub(r"[_-]", " ", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return text.title()


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate text with ellipsis."""
    return text[:max_len] + "..." if len(text) > max_len else text
