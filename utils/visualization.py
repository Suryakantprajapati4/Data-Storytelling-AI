"""
Visualization Engine for Data Storytelling AI.
Generates professional Plotly charts: bar, line, pie, histogram,
box plot, heatmap, and time series.
"""

from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.helpers import (
    classify_columns,
    guess_revenue_column,
    guess_date_column,
    guess_category_column,
    snake_to_title,
)
from utils.data_processor import top_categories, time_series_agg

# Professional colour palette
PALETTE = [
    "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
    "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#06b6d4",
]

LAYOUT_BASE = dict(
    font=dict(family="Inter, sans-serif", size=12),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="#1e293b", font_size=12,
                    font_family="Inter"),
)


def _apply_layout(fig, title: str = "", height: int = 420, **kwargs):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15)),
        height=height,
        **LAYOUT_BASE,
        **kwargs,
    )
    return fig


# ---------------------------------------------------------------------------
# KPI helpers
# ---------------------------------------------------------------------------

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return dict of KPI values from the dataframe."""
    col_info = classify_columns(df)
    rev_col = guess_revenue_column(df, col_info["numerical"])
    num_cols = col_info["numerical"]

    kpis = {}
    if rev_col:
        total = df[rev_col].sum()
        kpis["Total Revenue"] = total
        kpis["Avg per Record"] = df[rev_col].mean()

    # Try to find profit column
    profit_col = None
    for c in num_cols:
        if "profit" in c.lower() or "margin" in c.lower():
            profit_col = c
            break
    if profit_col:
        kpis["Total Profit"] = df[profit_col].sum()

    # Orders / count
    order_col = None
    for c in num_cols:
        if any(k in c.lower() for k in ["order", "quantity", "count", "units"]):
            order_col = c
            break
    if order_col:
        kpis["Total Orders"] = df[order_col].sum()
    else:
        kpis["Total Records"] = len(df)

    # Growth
    date_col = guess_date_column(df, col_info["datetime"])
    if date_col and rev_col:
        ts = time_series_agg(df, date_col, rev_col, freq="ME")
        if len(ts) >= 2:
            first = ts[rev_col].iloc[0]
            last = ts[rev_col].iloc[-1]
            if first != 0:
                kpis["Growth %"] = (last - first) / abs(first) * 100

    return kpis


# ---------------------------------------------------------------------------
# Chart generators
# ---------------------------------------------------------------------------

def bar_top_categories(df: pd.DataFrame, cat_col: str = None,
                       value_col: str = None, n: int = 10,
                       title: str = "Top Categories") -> go.Figure:
    col_info = classify_columns(df)
    cat = cat_col or guess_category_column(df, col_info["categorical"])
    val = value_col or guess_revenue_column(df, col_info["numerical"])
    if not cat or not val:
        return go.Figure()
    data = top_categories(df, cat, val, n=n)
    fig = px.bar(data, x=cat, y=val, color_discrete_sequence=PALETTE,
                 text_auto=".2s")
    fig.update_traces(marker=dict(cornerradius=6))
    _apply_layout(fig, title)
    return fig


def line_time_series(df: pd.DataFrame, date_col: str = None,
                     value_col: str = None, freq: str = "ME",
                     title: str = "Trend Over Time") -> go.Figure:
    col_info = classify_columns(df)
    dt = date_col or guess_date_column(df, col_info["datetime"])
    val = value_col or guess_revenue_column(df, col_info["numerical"])
    if not dt or not val:
        return go.Figure()
    ts = time_series_agg(df, dt, val, freq=freq)
    fig = px.line(ts, x=dt, y=val, markers=True,
                  color_discrete_sequence=[PALETTE[0]])
    fig.update_traces(line=dict(width=3),
                      marker=dict(size=7))
    _apply_layout(fig, title)
    return fig


def pie_category_share(df: pd.DataFrame, cat_col: str = None,
                       value_col: str = None, n: int = 8,
                       title: str = "Category Share") -> go.Figure:
    col_info = classify_columns(df)
    cat = cat_col or guess_category_column(df, col_info["categorical"])
    val = value_col or guess_revenue_column(df, col_info["numerical"])
    if not cat or not val:
        return go.Figure()
    data = top_categories(df, cat, val, n=n)
    fig = px.pie(data, names=cat, values=val,
                 color_discrete_sequence=PALETTE,
                 hole=0.4)
    fig.update_traces(textposition="inside", textinfo="label+percent+value",
                      pull=[0.04] + [0] * (len(data) - 1))
    _apply_layout(fig, title)
    return fig


def histogram_distribution(df: pd.DataFrame, col: str = None,
                           title: str = "Distribution") -> go.Figure:
    col_info = classify_columns(df)
    c = col or guess_revenue_column(df, col_info["numerical"])
    if not c:
        return go.Figure()
    fig = px.histogram(df, x=c, nbins=30,
                       color_discrete_sequence=[PALETTE[0]],
                       marginal="box")
    _apply_layout(fig, f"Distribution of {snake_to_title(c)}")
    return fig


def box_plot(df: pd.DataFrame, cat_col: str = None,
             value_col: str = None,
             title: str = "Box Plot") -> go.Figure:
    col_info = classify_columns(df)
    cat = cat_col or guess_category_column(df, col_info["categorical"])
    val = value_col or guess_revenue_column(df, col_info["numerical"])
    if not cat or not val:
        return go.Figure()
    fig = px.box(df, x=cat, y=val, color=cat,
                 color_discrete_sequence=PALETTE)
    _apply_layout(fig, title, showlegend=False)
    return fig


def correlation_heatmap(df: pd.DataFrame,
                        title: str = "Correlation Heatmap") -> go.Figure:
    col_info = classify_columns(df)
    num_cols = col_info["numerical"]
    if len(num_cols) < 2:
        return go.Figure()
    corr = df[num_cols].corr()
    labels = [snake_to_title(c) for c in num_cols]
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale="RdBu_r",
        zmid=0,
        text=corr.values.round(2),
        texttemplate="%{text}",
        hoverongaps=False,
    ))
    _apply_layout(fig, title, height=500)
    return fig


def multi_metric_time_series(df: pd.DataFrame, date_col: str = None,
                             value_cols: List[str] = None,
                             title: str = "Multi-Metric Trends"
                             ) -> go.Figure:
    col_info = classify_columns(df)
    dt = date_col or guess_date_column(df, col_info["datetime"])
    vals = value_cols or col_info["numerical"][:3]
    if not dt or not vals:
        return go.Figure()
    fig = go.Figure()
    for i, v in enumerate(vals):
        ts = time_series_agg(df, dt, v, freq="ME")
        fig.add_trace(go.Scatter(
            x=ts[dt], y=ts[v], mode="lines+markers",
            name=snake_to_title(v),
            line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
            marker=dict(size=6),
        ))
    _apply_layout(fig, title)
    return fig


# ---------------------------------------------------------------------------
# Auto-generate all charts
# ---------------------------------------------------------------------------

def generate_all_charts(df: pd.DataFrame) -> dict:
    """Return a dict of chart_name -> go.Figure for the dashboard."""
    charts = {}
    col_info = classify_columns(df)
    rev_col = guess_revenue_column(df, col_info["numerical"])
    date_col = guess_date_column(df, col_info["datetime"])
    cat_col = guess_category_column(df, col_info["categorical"])

    if cat_col and rev_col:
        charts["Top Categories"] = bar_top_categories(df, cat_col, rev_col)
        charts["Category Share"] = pie_category_share(df, cat_col, rev_col)
        charts["Box Plot"] = box_plot(df, cat_col, rev_col)

    if date_col and rev_col:
        charts["Trend Over Time"] = line_time_series(df, date_col, rev_col)

    if rev_col:
        charts["Distribution"] = histogram_distribution(df, rev_col)

    if len(col_info["numerical"]) >= 2:
        charts["Correlation Heatmap"] = correlation_heatmap(df)

    if date_col and len(col_info["numerical"]) >= 2:
        charts["Multi-Metric Trends"] = multi_metric_time_series(
            df, date_col, col_info["numerical"][:3])

    return charts
