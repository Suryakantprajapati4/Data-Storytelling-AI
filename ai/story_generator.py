"""
AI Story Report Generator for Data Storytelling AI.
Generates a full business narrative combining analytics observations,
insights, and recommendations into a structured executive report.
"""

import os
from typing import List, Dict, Any

import pandas as pd

from ai.analytics_engine import AnalyticsEngine
from ai.insight_generator import generate_insights
from utils.helpers import (
    classify_columns,
    fmt_number,
    fmt_pct,
    guess_revenue_column,
    guess_date_column,
    guess_category_column,
    snake_to_title,
)
from utils.data_processor import time_series_agg, compute_growth

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_story_report(df: pd.DataFrame,
                          use_openai: bool = True) -> Dict[str, str]:
    """
    Return a dict with section_name -> narrative text.
    Sections: executive_summary, dataset_overview, key_insights,
              trend_analysis, risks, opportunities, recommendations,
              conclusion.
    """
    engine = AnalyticsEngine(df)
    observations = engine.run_all()
    insights = generate_insights(df, use_openai=False)
    col_info = classify_columns(df)
    rev_col = guess_revenue_column(df, col_info["numerical"])
    date_col = guess_date_column(df, col_info["datetime"])
    cat_col = guess_category_column(df, col_info["categorical"])

    sections: Dict[str, str] = {}

    # --- Executive Summary ---
    sections["executive_summary"] = _executive_summary(
        df, observations, rev_col, date_col, cat_col)

    # --- Dataset Overview ---
    sections["dataset_overview"] = _dataset_overview(df, col_info)

    # --- Key Insights ---
    sections["key_insights"] = _key_insights(observations)

    # --- Trend Analysis ---
    sections["trend_analysis"] = _trend_analysis(
        df, observations, rev_col, date_col)

    # --- Risks ---
    sections["risks"] = _risks(observations)

    # --- Opportunities ---
    sections["opportunities"] = _opportunities(observations)

    # --- Recommendations ---
    sections["recommendations"] = _recommendations(
        df, observations, cat_col, rev_col)

    # --- Conclusion ---
    sections["conclusion"] = _conclusion(observations, rev_col)

    # Optional OpenAI enrichment
    if use_openai and _HAS_OPENAI:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            try:
                enriched = _openai_enrich(sections, api_key)
                sections.update(enriched)
            except Exception:
                pass

    return sections


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def _executive_summary(df, observations, rev_col, date_col, cat_col) -> str:
    parts = [
        f"This report provides a comprehensive analysis of the dataset "
        f"containing {fmt_number(len(df))} records across "
        f"{df.shape[1]} dimensions."
    ]

    if rev_col:
        total = df[rev_col].sum()
        parts.append(
            f"Total {snake_to_title(rev_col)} stands at "
            f"{fmt_number(total)}."
        )

    # Growth
    if date_col and rev_col:
        ts = time_series_agg(df, date_col, rev_col, freq="ME")
        if len(ts) >= 2:
            growth = compute_growth(ts[rev_col])
            if growth > 0:
                parts.append(
                    f"During the analyzed period, the business experienced "
                    f"steady growth with {fmt_pct(growth)} increase in "
                    f"{snake_to_title(rev_col).lower()}."
                )
            elif growth < 0:
                parts.append(
                    f"The analyzed period saw a decline of "
                    f"{fmt_pct(abs(growth))} in "
                    f"{snake_to_title(rev_col).lower()}, "
                    f"warranting strategic attention."
                )

    # Top category
    top_obs = [o for o in observations if o["category"] == "top_performer"]
    if top_obs:
        parts.append(top_obs[0]["text"])

    # Seasonal
    seasonal = [o for o in observations if o["category"] == "seasonal"]
    if seasonal:
        parts.append(seasonal[0]["text"])

    parts.append(
        "The following sections provide detailed insights, trend analysis, "
        "and actionable recommendations to drive improved outcomes."
    )
    return " ".join(parts)


def _dataset_overview(df, col_info) -> str:
    lines = [
        f"The dataset comprises **{fmt_number(len(df))}** rows and "
        f"**{df.shape[1]}** columns.",
        f"Column breakdown: **{len(col_info['numerical'])}** numerical, "
        f"**{len(col_info['categorical'])}** categorical, "
        f"**{len(col_info['datetime'])}** datetime columns.",
        f"Missing values: **{df.isnull().sum().sum()}** total "
        f"({df.isnull().sum().sum() / (len(df) * df.shape[1]) * 100:.1f}%"
        f" of all cells).",
        f"Duplicate records: **{int(df.duplicated().sum())}**.",
    ]
    return "\n\n".join(lines)


def _key_insights(observations) -> str:
    interesting = [o for o in observations
                   if o["category"] in ("top_performer", "kpi",
                                        "correlation", "seasonal")]
    if not interesting:
        return "No significant key insights were identified."
    parts = []
    for i, obs in enumerate(interesting[:6], 1):
        parts.append(f"**{i}.** {obs['text']}")
    return "\n\n".join(parts)


def _trend_analysis(df, observations, rev_col, date_col) -> str:
    trends = [o for o in observations
              if o["category"] in ("trend", "seasonal")]
    if not trends:
        return "Insufficient time-series data to identify trends."
    parts = []
    for t in trends:
        parts.append(t["text"])
    return "\n\n".join(parts)


def _risks(observations) -> str:
    risks = [o for o in observations
             if o["category"] in ("anomaly", "concentration") or
             (o["category"] == "trend" and o["sentiment"] == "negative")]
    if not risks:
        return ("No significant risks were identified. The dataset appears "
                "healthy across key metrics.")
    parts = []
    for r in risks:
        parts.append(f"⚠️ {r['text']}")
    return "\n\n".join(parts)


def _opportunities(observations) -> str:
    opps = [o for o in observations
            if o["category"] in ("bottom_performer", "concentration")]
    if not opps:
        return "No major growth opportunities were flagged in this analysis."
    parts = []
    for o in opps:
        parts.append(f"🚀 {o['text']}")
    return "\n\n".join(parts)


def _recommendations(df, observations, cat_col, rev_col) -> str:
    recs = []
    bottom = [o for o in observations if o["category"] == "bottom_performer"]
    if bottom:
        recs.append(
            "**Increase targeted marketing** in underperforming segments "
            "to capture untapped demand."
        )
    declining = [o for o in observations
                 if o["category"] == "trend" and o["sentiment"] == "negative"]
    if declining:
        recs.append(
            "**Review pricing and positioning strategy** for declining "
            "metrics to reverse the negative trend."
        )
    concentration = [o for o in observations
                     if o["category"] == "concentration"]
    if concentration:
        recs.append(
            "**Diversify revenue streams** to reduce dependency on a "
            "small number of categories."
        )
    anomalies = [o for o in observations if o["category"] == "anomaly"]
    if anomalies:
        recs.append(
            "**Investigate and resolve data anomalies** to improve "
            "reporting accuracy."
        )
    # Generic but useful
    recs.append(
        "**Implement regular data quality monitoring** to maintain "
        "trustworthy analytics."
    )
    recs.append(
        "**Invest in customer segmentation analysis** to personalise "
        "outreach and improve conversion."
    )
    parts = []
    for i, r in enumerate(recs, 1):
        parts.append(f"{i}. {r}")
    return "\n\n".join(parts)


def _conclusion(observations, rev_col) -> str:
    positive = [o for o in observations if o["sentiment"] == "positive"]
    negative = [o for o in observations if o["sentiment"] == "negative"]
    parts = ["In conclusion,"]
    if positive:
        parts.append(
            f"the analysis identified **{len(positive)} positive signals** "
            f"indicating areas of strength."
        )
    if negative:
        parts.append(
            f"However, **{len(negative)} areas of concern** require "
            f"strategic intervention."
        )
    parts.append(
        "By acting on the recommendations outlined above, stakeholders "
        "can capitalise on growth opportunities while mitigating identified "
        "risks. Continued monitoring and iterative analysis are advised "
        "to sustain momentum."
    )
    return " ".join(parts)


# ---------------------------------------------------------------------------
# OpenAI enrichment
# ---------------------------------------------------------------------------

def _openai_enrich(sections: Dict[str, str],
                   api_key: str) -> Dict[str, str]:
    """Use OpenAI to polish the executive summary and conclusion."""
    client = OpenAI(api_key=api_key)
    enriched = {}
    for key in ("executive_summary", "conclusion"):
        prompt = (
            "You are a senior business analyst. Rewrite the following "
            "paragraph to sound more professional and insightful, "
            "keeping roughly the same length. Do not add facts not "
            "present in the original.\n\n"
            f"Text: {sections[key]}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500,
        )
        enriched[key] = resp.choices[0].message.content.strip()
    return enriched
