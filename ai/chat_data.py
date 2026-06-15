"""
Chat With Data module for Data Storytelling AI.
Allows users to ask natural-language questions about their data and
receives answers, explanations, and optional charts.
"""

import re
import os
from typing import Optional, Tuple, Dict, Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import (
    classify_columns,
    fmt_number,
    fmt_pct,
    guess_revenue_column,
    guess_date_column,
    guess_category_column,
    snake_to_title,
)
from utils.data_processor import top_categories, time_series_agg
from utils.visualization import (
    bar_top_categories,
    line_time_series,
    pie_category_share,
    histogram_distribution,
    PALETTE,
    _apply_layout,
)

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


# ---------------------------------------------------------------------------
# Query intent detection
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    "top": ["best", "top", "highest", "most", "leading", "largest",
            "maximum", "peak"],
    "bottom": ["worst", "bottom", "lowest", "least", "smallest",
               "minimum", "underperforming"],
    "trend": ["trend", "over time", "monthly", "yearly", "growth",
              "change", "pattern", "evolution"],
    "compare": ["compare", "versus", "vs", "difference", "between"],
    "total": ["total", "sum", "overall", "aggregate", "all"],
    "average": ["average", "mean", "avg", "typical"],
    "count": ["count", "how many", "number of", "quantity"],
    "distribution": ["distribution", "spread", "histogram", "range"],
    "correlation": ["correlation", "correlated", "relationship",
                    "associated"],
    "insight": ["insight", "finding", "interesting", "summary",
                "what can you find", "tell me"],
    "share": ["share", "percentage", "proportion", "breakdown",
              "split", "composition"],
}


def _detect_intent(query: str) -> str:
    q = query.lower()
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score > 0:
            scores[intent] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"


def _find_mentioned_column(query: str, columns: list) -> Optional[str]:
    """Find a column name mentioned in the query."""
    q = query.lower()
    for col in columns:
        if col.lower() in q or snake_to_title(col).lower() in q:
            return col
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat_with_data(query: str, df: pd.DataFrame,
                   use_openai: bool = True
                   ) -> Dict[str, Any]:
    """
    Process a natural-language query against the dataframe.
    Returns dict with:
      answer  (str)        - direct answer text
      explanation (str)    - explanation of how the answer was derived
      chart (go.Figure|None) - optional Plotly chart
    """
    query = query.strip()
    if not query:
        return {"answer": "Please enter a question.",
                "explanation": "", "chart": None}

    col_info = classify_columns(df)
    intent = _detect_intent(query)

    rev_col = guess_revenue_column(df, col_info["numerical"])
    date_col = guess_date_column(df, col_info["datetime"])
    cat_col = guess_category_column(df, col_info["categorical"])

    # Allow query to override column detection
    mentioned_col = _find_mentioned_column(query, df.columns.tolist())
    if mentioned_col:
        if mentioned_col in col_info["numerical"]:
            rev_col = mentioned_col
        elif mentioned_col in col_info["categorical"]:
            cat_col = mentioned_col
        elif mentioned_col in col_info["datetime"]:
            date_col = mentioned_col

    result = {"answer": "", "explanation": "", "chart": None}

    # --- Intent handlers ---
    if intent == "top":
        result = _handle_top(df, query, cat_col, rev_col, col_info)
    elif intent == "bottom":
        result = _handle_bottom(df, query, cat_col, rev_col, col_info)
    elif intent == "trend":
        result = _handle_trend(df, query, date_col, rev_col, col_info)
    elif intent == "total":
        result = _handle_total(df, query, rev_col, col_info)
    elif intent == "average":
        result = _handle_average(df, query, rev_col, col_info)
    elif intent == "count":
        result = _handle_count(df, query, col_info)
    elif intent == "distribution":
        result = _handle_distribution(df, query, rev_col, col_info)
    elif intent == "share":
        result = _handle_share(df, query, cat_col, rev_col, col_info)
    elif intent == "correlation":
        result = _handle_correlation(df, query, col_info)
    elif intent == "insight":
        result = _handle_insight(df, query, col_info)
    elif intent == "compare":
        result = _handle_compare(df, query, cat_col, rev_col, col_info)
    else:
        # Try OpenAI or fall back to general summary
        if use_openai and _HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                try:
                    result = _openai_chat(query, df, api_key)
                except Exception:
                    result = _handle_general(df, query, col_info)
            else:
                result = _handle_general(df, query, col_info)
        else:
            result = _handle_general(df, query, col_info)

    return result


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _handle_top(df, query, cat_col, rev_col, col_info) -> Dict:
    if not cat_col or not rev_col:
        return _no_cols("categorical and numerical")
    data = top_categories(df, cat_col, rev_col, n=5)
    top_name = data.iloc[0][cat_col]
    top_val = data.iloc[0][rev_col]
    chart = bar_top_categories(df, cat_col, rev_col, n=10,
                               title=f"Top {snake_to_title(cat_col)}")
    return {
        "answer": (
            f"The best performing {snake_to_title(cat_col).lower()} is "
            f"**{top_name}** with {snake_to_title(rev_col).lower()} of "
            f"**{fmt_number(top_val)}**."
        ),
        "explanation": (
            f"Aggregated {snake_to_title(rev_col)} by "
            f"{snake_to_title(cat_col)} and sorted descending. "
            f"Showing top 10 in the chart."
        ),
        "chart": chart,
    }


def _handle_bottom(df, query, cat_col, rev_col, col_info) -> Dict:
    if not cat_col or not rev_col:
        return _no_cols("categorical and numerical")
    data = top_categories(df, cat_col, rev_col, n=5, ascending=True)
    bot_name = data.iloc[0][cat_col]
    bot_val = data.iloc[0][rev_col]
    chart = bar_top_categories(df, cat_col, rev_col, n=10,
                               title=f"Bottom {snake_to_title(cat_col)}")
    return {
        "answer": (
            f"The lowest performing {snake_to_title(cat_col).lower()} is "
            f"**{bot_name}** with {snake_to_title(rev_col).lower()} of "
            f"**{fmt_number(bot_val)}**."
        ),
        "explanation": (
            f"Aggregated {snake_to_title(rev_col)} by "
            f"{snake_to_title(cat_col)} and sorted ascending."
        ),
        "chart": chart,
    }


def _handle_trend(df, query, date_col, rev_col, col_info) -> Dict:
    if not date_col or not rev_col:
        return _no_cols("datetime and numerical")
    ts = time_series_agg(df, date_col, rev_col, freq="ME")
    if len(ts) < 2:
        return {"answer": "Not enough time data to compute trend.",
                "explanation": "", "chart": None}
    growth = (ts[rev_col].iloc[-1] - ts[rev_col].iloc[0]) / abs(
        ts[rev_col].iloc[0]) * 100 if ts[rev_col].iloc[0] != 0 else 0
    direction = "increased" if growth > 0 else "decreased"
    chart = line_time_series(df, date_col, rev_col)
    return {
        "answer": (
            f"{snake_to_title(rev_col)} has **{direction}** by "
            f"**{fmt_pct(growth)}** over the observed period."
        ),
        "explanation": (
            f"Computed monthly aggregates of {snake_to_title(rev_col)} "
            f"from {ts[date_col].iloc[0].strftime('%Y-%m')} to "
            f"{ts[date_col].iloc[-1].strftime('%Y-%m')}."
        ),
        "chart": chart,
    }


def _handle_total(df, query, rev_col, col_info) -> Dict:
    if not rev_col:
        return _no_cols("numerical")
    total = df[rev_col].sum()
    return {
        "answer": f"Total {snake_to_title(rev_col).lower()} is **{fmt_number(total)}**.",
        "explanation": f"Summed all values in the {rev_col} column.",
        "chart": None,
    }


def _handle_average(df, query, rev_col, col_info) -> Dict:
    if not rev_col:
        return _no_cols("numerical")
    avg = df[rev_col].mean()
    return {
        "answer": f"Average {snake_to_title(rev_col).lower()} is **{fmt_number(avg)}**.",
        "explanation": f"Computed mean of the {rev_col} column across {len(df)} records.",
        "chart": None,
    }


def _handle_count(df, query, col_info) -> Dict:
    return {
        "answer": f"The dataset contains **{fmt_number(len(df))}** records.",
        "explanation": f"Counted the number of rows in the dataset.",
        "chart": None,
    }


def _handle_distribution(df, query, rev_col, col_info) -> Dict:
    if not rev_col:
        return _no_cols("numerical")
    chart = histogram_distribution(df, rev_col)
    return {
        "answer": (
            f"The distribution of {snake_to_title(rev_col).lower()} has a "
            f"mean of **{fmt_number(df[rev_col].mean())}** and median of "
            f"**{fmt_number(df[rev_col].median())}**."
        ),
        "explanation": "Generated a histogram with 30 bins.",
        "chart": chart,
    }


def _handle_share(df, query, cat_col, rev_col, col_info) -> Dict:
    if not cat_col or not rev_col:
        return _no_cols("categorical and numerical")
    chart = pie_category_share(df, cat_col, rev_col)
    total = df[rev_col].sum()
    agg = df.groupby(cat_col)[rev_col].sum().sort_values(ascending=False)
    top_cat = agg.index[0]
    top_pct = agg.iloc[0] / total * 100 if total else 0
    return {
        "answer": (
            f"**{top_cat}** has the largest share at "
            f"**{top_pct:.1f}%** of total {snake_to_title(rev_col).lower()}."
        ),
        "explanation": "Computed percentage share by category.",
        "chart": chart,
    }


def _handle_correlation(df, query, col_info) -> Dict:
    num_cols = col_info["numerical"]
    if len(num_cols) < 2:
        return {"answer": "Not enough numerical columns for correlation.",
                "explanation": "", "chart": None}
    corr = df[num_cols].corr()
    # Find strongest pair
    best_pair, best_val = None, 0
    for i, c1 in enumerate(num_cols):
        for j, c2 in enumerate(num_cols):
            if i >= j:
                continue
            v = abs(corr.loc[c1, c2])
            if v > best_val:
                best_val = v
                best_pair = (c1, c2)
    from utils.visualization import correlation_heatmap
    chart = correlation_heatmap(df)
    return {
        "answer": (
            f"The strongest correlation is between "
            f"**{snake_to_title(best_pair[0])}** and "
            f"**{snake_to_title(best_pair[1])}** "
            f"(r = {corr.loc[best_pair[0], best_pair[1]]:.3f})."
        ),
        "explanation": "Computed Pearson correlation matrix.",
        "chart": chart,
    }


def _handle_insight(df, query, col_info) -> Dict:
    from ai.analytics_engine import run_analytics
    obs = run_analytics(df)
    if not obs:
        return {"answer": "No notable insights found.",
                "explanation": "", "chart": None}
    parts = []
    for o in obs[:5]:
        parts.append(f"• {o['text']}")
    return {
        "answer": "\n".join(parts),
        "explanation": "Ran automated analytics engine.",
        "chart": None,
    }


def _handle_compare(df, query, cat_col, rev_col, col_info) -> Dict:
    if not cat_col or not rev_col:
        return _no_cols("categorical and numerical")
    chart = bar_top_categories(df, cat_col, rev_col, n=10,
                               title=f"Comparison by {snake_to_title(cat_col)}")
    agg = df.groupby(cat_col)[rev_col].sum().sort_values(ascending=False)
    top = agg.index[0]
    bottom = agg.index[-1]
    diff = agg.iloc[0] - agg.iloc[-1]
    return {
        "answer": (
            f"**{top}** leads with {fmt_number(agg.iloc[0])}, while "
            f"**{bottom}** trails at {fmt_number(agg.iloc[-1])}. "
            f"Difference: **{fmt_number(diff)}**."
        ),
        "explanation": f"Compared {snake_to_title(rev_col)} across categories.",
        "chart": chart,
    }


def _handle_general(df, query, col_info) -> Dict:
    return {
        "answer": (
            f"I analysed your question but couldn't map it to a specific "
            f"query. Here's a quick overview: the dataset has "
            f"**{len(df)}** rows, **{df.shape[1]}** columns, with "
            f"**{len(col_info['numerical'])}** numerical and "
            f"**{len(col_info['categorical'])}** categorical features."
        ),
        "explanation": "General fallback response.",
        "chart": None,
    }


def _no_cols(col_type: str) -> Dict:
    return {
        "answer": f"This query requires {col_type} columns, but none were detected.",
        "explanation": "Check that your dataset contains the required column types.",
        "chart": None,
    }


# ---------------------------------------------------------------------------
# OpenAI chat fallback
# ---------------------------------------------------------------------------

def _openai_chat(query: str, df: pd.DataFrame,
                 api_key: str) -> Dict[str, Any]:
    """Use OpenAI to interpret and answer a query about the data."""
    client = OpenAI(api_key=api_key)

    # Provide a compact summary of the dataframe
    sample = df.head(5).to_string(index=False)
    cols = ", ".join(df.columns.tolist())
    prompt = (
        f"You are a data analyst. The dataset has columns: {cols}\n"
        f"Here are the first 5 rows:\n{sample}\n\n"
        f"User question: {query}\n\n"
        "Provide a concise, accurate answer based on the data structure. "
        "If you cannot determine the answer, say so. Do not hallucinate "
        "specific numbers."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )
    answer = resp.choices[0].message.content.strip()
    return {
        "answer": answer,
        "explanation": "Generated using AI analysis of dataset structure.",
        "chart": None,
    }
