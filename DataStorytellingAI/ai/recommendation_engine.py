"""
Recommendation Engine for Data Storytelling AI.
Generates dynamic, context-aware business recommendations based on
data analysis results.
"""

import os
from typing import List, Dict

import pandas as pd

from ai.analytics_engine import AnalyticsEngine
from utils.helpers import (
    classify_columns,
    fmt_number,
    fmt_pct,
    guess_revenue_column,
    guess_category_column,
    guess_date_column,
    snake_to_title,
)
from utils.data_processor import top_categories, time_series_agg, compute_growth

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


# ---------------------------------------------------------------------------
# Recommendation structure
# ---------------------------------------------------------------------------

ICONS = {
    "marketing": "📣",
    "inventory": "📦",
    "product": "🎯",
    "customer": "👥",
    "operations": "⚙️",
    "finance": "💰",
    "data_quality": "📊",
    "strategy": "🧭",
}


def _make_rec(category: str, title: str, body: str,
              priority: str = "medium") -> Dict[str, str]:
    return {
        "category": category,
        "icon": ICONS.get(category, "💡"),
        "title": title,
        "body": body,
        "priority": priority,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_recommendations(df: pd.DataFrame,
                             use_openai: bool = True
                             ) -> List[Dict[str, str]]:
    """Return a list of actionable recommendation dicts."""
    engine = AnalyticsEngine(df)
    observations = engine.run_all()
    col_info = classify_columns(df)
    rev_col = guess_revenue_column(df, col_info["numerical"])
    cat_col = guess_category_column(df, col_info["categorical"])
    date_col = guess_date_column(df, col_info["datetime"])

    recs: List[Dict[str, str]] = []

    # 1. Underperforming categories
    bottom = [o for o in observations if o["category"] == "bottom_performer"]
    if bottom:
        names = [o["text"].split(" is ")[0] for o in bottom[:2]]
        recs.append(_make_rec(
            "marketing",
            "Increase Marketing in Underperforming Segments",
            f"Increase marketing spend in underperforming segments such as "
            f"{', '.join(names)}. Targeted campaigns and promotional "
            f"offers can help capture untapped demand and improve "
            f"overall market share.",
            "high",
        ))

    # 2. High-performing categories — double down
    top = [o for o in observations if o["category"] == "top_performer"]
    if top:
        names = [o["text"].split(" contributes")[0] for o in top[:2]]
        recs.append(_make_rec(
            "inventory",
            "Focus Inventory on High Performers",
            f"Prioritise inventory and supply chain investment in "
            f"{', '.join(names)}, which are the top revenue contributors. "
            f"Ensure stock availability meets projected demand.",
            "high",
        ))

    # 3. Declining trends
    declining = [o for o in observations
                 if o["category"] == "trend" and o["sentiment"] == "negative"]
    if declining:
        recs.append(_make_rec(
            "product",
            "Address Declining Products",
            "Conduct a root-cause analysis on declining product lines. "
            "Evaluate whether repositioning, bundling, or sunsetting "
            "is the appropriate strategy. Reduce dependency on "
            "products with sustained downward trends.",
            "high",
        ))

    # 4. Revenue concentration risk
    concentration = [o for o in observations
                     if o["category"] == "concentration"]
    if concentration:
        recs.append(_make_rec(
            "strategy",
            "Diversify Revenue Streams",
            "Reduce dependency on a small number of categories or "
            "segments. Explore adjacent markets, new product lines, "
            "or strategic partnerships to diversify the revenue base.",
            "medium",
        ))

    # 5. Seasonality
    seasonal = [o for o in observations if o["category"] == "seasonal"]
    if seasonal:
        recs.append(_make_rec(
            "operations",
            "Plan for Seasonal Demand",
            "Build demand forecasts that account for seasonal peaks and "
            "troughs. Pre-position inventory ahead of peak periods and "
            "consider counter-seasonal promotions during low months.",
            "medium",
        ))

    # 6. Anomalies
    anomalies = [o for o in observations if o["category"] == "anomaly"]
    if anomalies:
        recs.append(_make_rec(
            "data_quality",
            "Investigate Data Anomalies",
            "Review anomalous records for data entry errors, fraud, "
            "or genuine outliers. Implement validation rules to "
            "flag unusual values in real time.",
            "medium",
        ))

    # 7. Customer retention
    recs.append(_make_rec(
        "customer",
        "Improve Customer Retention",
        "Segment customers by value and engagement. Deploy loyalty "
        "programs, personalised offers, and proactive support for "
        "at-risk accounts to improve retention and lifetime value.",
        "medium",
    ))

    # 8. Growth trend — capitalise
    growing = [o for o in observations
               if o["category"] == "trend" and o["sentiment"] == "positive"]
    if growing:
        recs.append(_make_rec(
            "finance",
            "Capitalise on Growth Momentum",
            "Reinvest a portion of incremental revenue from growing "
            "segments into R&D and expansion. Lock in favourable "
            "supplier contracts while volumes are increasing.",
            "medium",
        ))

    # 9. Correlation-driven
    corrs = [o for o in observations if o["category"] == "correlation"]
    if corrs:
        recs.append(_make_rec(
            "strategy",
            "Leverage Key Correlations",
            f"{corrs[0]['text']} Use this relationship to build "
            f"predictive models and optimise resource allocation.",
            "low",
        ))

    # 10. Always include data governance
    recs.append(_make_rec(
        "data_quality",
        "Establish Data Governance Framework",
        "Implement standardised data collection, validation, and "
        "documentation practices to ensure consistent, trustworthy "
        "analytics across the organisation.",
        "low",
    ))

    # Optional OpenAI enrichment
    if use_openai and _HAS_OPENAI:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            try:
                extra = _openai_recommendations(observations, api_key)
                recs.extend(extra)
            except Exception:
                pass

    return recs


# ---------------------------------------------------------------------------
# OpenAI enrichment
# ---------------------------------------------------------------------------

def _openai_recommendations(observations: List[Dict],
                            api_key: str) -> List[Dict[str, str]]:
    """Use OpenAI to generate additional nuanced recommendations."""
    client = OpenAI(api_key=api_key)
    summary = "\n".join(o["text"] for o in observations[:12])
    prompt = (
        "You are a senior management consultant. Based on these data "
        "observations, generate exactly 3 additional actionable business "
        "recommendations. Format each as: CATEGORY | TITLE | BODY\n"
        "Categories: marketing, inventory, product, customer, "
        "operations, finance, data_quality, strategy.\n\n"
        f"Observations:\n{summary}\n\n"
        "Respond only with the 3 lines."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500,
    )
    content = resp.choices[0].message.content.strip()
    results = []
    for line in content.split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            cat = parts[0].lower().replace(" ", "_")
            if cat not in ICONS:
                cat = "strategy"
            results.append(_make_rec(cat, parts[1], parts[2]))
    return results
