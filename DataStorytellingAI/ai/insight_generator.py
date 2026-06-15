"""
AI Insight Generator for Data Storytelling AI.
Generates structured insights: Key Findings, Opportunities, Risks, Trends,
and Performance Highlights.  Falls back to local heuristic logic when the
OpenAI API key is unavailable.
"""

import os
from typing import List, Dict, Any

import pandas as pd

from ai.analytics_engine import AnalyticsEngine
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

# Optional OpenAI import
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


# ---------------------------------------------------------------------------
# Insight card structure
# ---------------------------------------------------------------------------

INSIGHT_TYPES = [
    "Key Finding",
    "Opportunity",
    "Risk",
    "Trend",
    "Performance Highlight",
]

ICONS = {
    "Key Finding": "🔍",
    "Opportunity": "🚀",
    "Risk": "⚠️",
    "Trend": "📈",
    "Performance Highlight": "🏆",
}

CARD_CSS_CLASS = {
    "Key Finding": "",
    "Opportunity": "opportunity",
    "Risk": "risk",
    "Trend": "trend",
    "Performance Highlight": "highlight",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_insights(df: pd.DataFrame,
                      use_openai: bool = True) -> List[Dict[str, str]]:
    """
    Generate a list of insight dicts with keys:
      type, icon, title, body, css_class
    """
    engine = AnalyticsEngine(df)
    observations = engine.run_all()

    insights: List[Dict[str, str]] = []

    # --- Key Findings ---
    kpis = [o for o in observations if o["category"] == "kpi"]
    top_perfs = [o for o in observations if o["category"] == "top_performer"]
    if kpis:
        insights.append(_make_insight(
            "Key Finding",
            "Dataset Overview",
            kpis[0]["text"],
        ))
    if top_perfs:
        insights.append(_make_insight(
            "Key Finding",
            "Top Performer",
            top_perfs[0]["text"],
        ))

    # --- Opportunities ---
    bottom = [o for o in observations if o["category"] == "bottom_performer"]
    concentration = [o for o in observations
                     if o["category"] == "concentration"]
    if bottom:
        insights.append(_make_insight(
            "Opportunity",
            "Growth Opportunity",
            f"{bottom[0]['text']} Targeted investment could unlock growth.",
        ))
    if concentration:
        insights.append(_make_insight(
            "Opportunity",
            "Diversification Opportunity",
            concentration[0]["text"],
        ))

    # --- Risks ---
    anomalies = [o for o in observations if o["category"] == "anomaly"]
    declining = [o for o in observations
                 if o["category"] == "trend" and o["sentiment"] == "negative"]
    if anomalies:
        insights.append(_make_insight(
            "Risk",
            "Data Anomalies Detected",
            anomalies[0]["text"],
        ))
    if declining:
        insights.append(_make_insight(
            "Risk",
            "Declining Trend",
            declining[0]["text"],
        ))

    # --- Trends ---
    trends = [o for o in observations
              if o["category"] in ("trend", "seasonal")]
    for t in trends[:3]:
        insights.append(_make_insight(
            "Trend",
            "Trend Analysis" if t["category"] == "trend" else "Seasonality",
            t["text"],
        ))

    # --- Performance Highlights ---
    corrs = [o for o in observations if o["category"] == "correlation"]
    for c in corrs[:2]:
        insights.append(_make_insight(
            "Performance Highlight",
            "Strong Correlation",
            c["text"],
        ))
    if len(top_perfs) > 1:
        insights.append(_make_insight(
            "Performance Highlight",
            "Category Leaders",
            top_perfs[1]["text"],
        ))

    # --- OpenAI enrichment (optional) ---
    if use_openai and _HAS_OPENAI:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            try:
                ai_insights = _openai_insights(df, observations, api_key)
                insights.extend(ai_insights)
            except Exception:
                pass

    # Ensure at least one insight per type
    existing_types = {i["type"] for i in insights}
    for itype in INSIGHT_TYPES:
        if itype not in existing_types:
            insights.append(_make_insight(
                itype,
                itype,
                "No additional observations of this type were detected.",
            ))

    return insights


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_insight(insight_type: str, title: str, body: str) -> Dict[str, str]:
    return {
        "type": insight_type,
        "icon": ICONS.get(insight_type, "💡"),
        "title": title,
        "body": body,
        "css_class": CARD_CSS_CLASS.get(insight_type, ""),
    }


def _openai_insights(df: pd.DataFrame, observations: List[Dict],
                     api_key: str) -> List[Dict[str, str]]:
    """Call OpenAI to enrich insights with deeper narrative."""
    client = OpenAI(api_key=api_key)

    summary_text = "\n".join(o["text"] for o in observations[:10])
    prompt = (
        "You are a senior business analyst. Based on these data observations, "
        "generate exactly 3 additional concise business insights. "
        "Format each as: TYPE | TITLE | INSIGHT_TEXT\n"
        "Types must be one of: Key Finding, Opportunity, Risk, Trend, "
        "Performance Highlight.\n\n"
        f"Observations:\n{summary_text}\n\n"
        "Respond only with the 3 lines, no extra text."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=400,
    )

    content = response.choices[0].message.content.strip()
    results = []
    for line in content.split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3 and parts[0] in INSIGHT_TYPES:
            results.append(_make_insight(parts[0], parts[1], parts[2]))
    return results
