"""
Analytics Engine for Data Storytelling AI.
Performs automated business analytics: trends, anomalies, correlations,
seasonal patterns, and key metric identification.
"""

from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from utils.helpers import (
    classify_columns,
    fmt_number,
    fmt_pct,
    guess_revenue_column,
    guess_date_column,
    guess_category_column,
    snake_to_title,
)
from utils.data_processor import top_categories, time_series_agg, compute_growth


class AnalyticsEngine:
    """Automated analytics engine that generates business observations."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.col_info = classify_columns(self.df)
        self.revenue_col = guess_revenue_column(
            self.df, self.col_info["numerical"])
        self.date_col = guess_date_column(
            self.df, self.col_info["datetime"])
        self.category_col = guess_category_column(
            self.df, self.col_info["categorical"])
        self.observations: List[Dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_all(self) -> List[Dict[str, str]]:
        """Execute all analytics analyses and return observations."""
        self.observations = []
        self._analyze_top_categories()
        self._analyze_bottom_categories()
        self._analyze_trends()
        self._analyze_seasonality()
        self._analyze_anomalies()
        self._analyze_correlations()
        self._analyze_key_metrics()
        self._analyze_concentration()
        return self.observations

    # ------------------------------------------------------------------
    # Internal analyses
    # ------------------------------------------------------------------

    def _add(self, category: str, text: str,
             sentiment: str = "neutral") -> None:
        self.observations.append({
            "category": category,
            "text": text,
            "sentiment": sentiment,
        })

    def _analyze_top_categories(self) -> None:
        if not (self.category_col and self.revenue_col):
            return
        top = top_categories(self.df, self.category_col,
                             self.revenue_col, n=3, ascending=False)
        total = self.df[self.revenue_col].sum()
        for _, row in top.iterrows():
            cat = row[self.category_col]
            val = row[self.revenue_col]
            pct = val / total * 100 if total else 0
            self._add(
                "top_performer",
                f"{snake_to_title(str(cat))} contributes "
                f"{pct:.1f}% of total {self.revenue_col.lower()} "
                f"({fmt_number(val)}).",
                "positive",
            )

    def _analyze_bottom_categories(self) -> None:
        if not (self.category_col and self.revenue_col):
            return
        bottom = top_categories(self.df, self.category_col,
                                self.revenue_col, n=3, ascending=True)
        total = self.df[self.revenue_col].sum()
        for _, row in bottom.iterrows():
            cat = row[self.category_col]
            val = row[self.revenue_col]
            pct = val / total * 100 if total else 0
            self._add(
                "bottom_performer",
                f"{snake_to_title(str(cat))} is underperforming with only "
                f"{pct:.1f}% share of {self.revenue_col.lower()} "
                f"({fmt_number(val)}).",
                "negative",
            )

    def _analyze_trends(self) -> None:
        if not (self.date_col and self.revenue_col):
            return
        ts = time_series_agg(self.df, self.date_col,
                             self.revenue_col, freq="ME")
        if len(ts) < 3:
            return
        growth = compute_growth(ts[self.revenue_col])
        if growth > 5:
            self._add(
                "trend",
                f"{snake_to_title(self.revenue_col)} shows an upward trend "
                f"with {fmt_pct(growth)} growth over the observed period.",
                "positive",
            )
        elif growth < -5:
            self._add(
                "trend",
                f"{snake_to_title(self.revenue_col)} is declining at "
                f"{fmt_pct(growth)} over the observed period.",
                "negative",
            )
        else:
            self._add(
                "trend",
                f"{snake_to_title(self.revenue_col)} remained relatively "
                f"stable ({fmt_pct(growth)} change) during the period.",
                "neutral",
            )

        # Linear regression trend
        X = np.arange(len(ts)).reshape(-1, 1)
        y = ts[self.revenue_col].values
        try:
            lr = LinearRegression().fit(X, y)
            slope = lr.coef_[0]
            if slope > 0:
                self._add(
                    "trend",
                    f"Linear trend analysis confirms a positive trajectory "
                    f"with average monthly increase of {fmt_number(abs(slope))}.",
                    "positive",
                )
            elif slope < 0:
                self._add(
                    "trend",
                    f"Linear trend analysis indicates a decline of "
                    f"{fmt_number(abs(slope))} per period on average.",
                    "negative",
                )
        except Exception:
            pass

    def _analyze_seasonality(self) -> None:
        if not (self.date_col and self.revenue_col):
            return
        tmp = self.df[[self.date_col, self.revenue_col]].copy()
        tmp[self.date_col] = pd.to_datetime(tmp[self.date_col],
                                            errors="coerce")
        tmp = tmp.dropna()
        if len(tmp) < 12:
            return
        tmp["month"] = tmp[self.date_col].dt.month
        monthly = tmp.groupby("month")[self.revenue_col].mean()
        peak_month = monthly.idxmax()
        low_month = monthly.idxmin()
        month_names = {1: "January", 2: "February", 3: "March",
                       4: "April", 5: "May", 6: "June",
                       7: "July", 8: "August", 9: "September",
                       10: "October", 11: "November", 12: "December"}
        self._add(
            "seasonal",
            f"Seasonal pattern detected: {self.revenue_col.lower()} "
            f"peaks in {month_names.get(peak_month, peak_month)} and "
            f"is lowest in {month_names.get(low_month, low_month)}.",
            "neutral",
        )

        # Quarter analysis
        tmp["quarter"] = tmp[self.date_col].dt.quarter
        qtr = tmp.groupby("quarter")[self.revenue_col].sum()
        best_q = qtr.idxmax()
        self._add(
            "seasonal",
            f"Q{best_q} recorded the highest aggregate "
            f"{self.revenue_col.lower()} at {fmt_number(qtr[best_q])}.",
            "positive",
        )

    def _analyze_anomalies(self) -> None:
        if not self.revenue_col:
            return
        col = self.revenue_col
        mean = self.df[col].mean()
        std = self.df[col].std()
        if std == 0:
            return
        threshold = 2.5
        anomalies = self.df[
            (self.df[col] > mean + threshold * std) |
            (self.df[col] < mean - threshold * std)
        ]
        n_anomalies = len(anomalies)
        if n_anomalies > 0:
            pct = n_anomalies / len(self.df) * 100
            self._add(
                "anomaly",
                f"Detected {n_anomalies} anomalous records "
                f"({pct:.1f}% of data) in {snake_to_title(col)} "
                f"that deviate significantly from the mean.",
                "negative",
            )

    def _analyze_correlations(self) -> None:
        num_cols = self.col_info["numerical"]
        if len(num_cols) < 2:
            return
        corr = self.df[num_cols].corr()
        pairs_seen = set()
        for c1 in num_cols:
            for c2 in num_cols:
                if c1 >= c2:
                    continue
                pair = tuple(sorted([c1, c2]))
                if pair in pairs_seen:
                    continue
                pairs_seen.add(pair)
                val = corr.loc[c1, c2]
                if abs(val) >= 0.7:
                    direction = "positive" if val > 0 else "negative"
                    self._add(
                        "correlation",
                        f"Strong {direction} correlation ({val:.2f}) between "
                        f"{snake_to_title(c1)} and {snake_to_title(c2)}.",
                        "neutral",
                    )

    def _analyze_key_metrics(self) -> None:
        if self.revenue_col:
            total = self.df[self.revenue_col].sum()
            avg = self.df[self.revenue_col].mean()
            self._add(
                "kpi",
                f"Total {snake_to_title(self.revenue_col)}: "
                f"{fmt_number(total)}. "
                f"Average per record: {fmt_number(avg)}.",
                "neutral",
            )

        # Record count
        self._add(
            "kpi",
            f"Dataset contains {fmt_number(len(self.df))} records "
            f"across {self.df.shape[1]} dimensions.",
            "neutral",
        )

    def _analyze_concentration(self) -> None:
        """Check if a small number of categories dominate the metric."""
        if not (self.category_col and self.revenue_col):
            return
        agg = (self.df.groupby(self.category_col)[self.revenue_col]
               .sum()
               .sort_values(ascending=False))
        total = agg.sum()
        if total == 0:
            return
        cum = agg.cumsum() / total * 100
        top_n = (cum <= 80).sum() + 1
        total_cats = len(agg)
        if top_n < total_cats * 0.3:
            self._add(
                "concentration",
                f"High concentration: top {top_n} of {total_cats} "
                f"{self.category_col.lower()} categories account for "
                f"80%+ of {self.revenue_col.lower()}. "
                f"Consider diversification.",
                "negative",
            )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def run_analytics(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Run the full analytics pipeline and return observations."""
    engine = AnalyticsEngine(df)
    return engine.run_all()
