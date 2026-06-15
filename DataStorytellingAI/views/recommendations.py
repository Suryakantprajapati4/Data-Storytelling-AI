"""
Recommendations page - Actionable business recommendations.
"""

import streamlit as st

from utils.styling import page_title_bar_html, recommendation_card_html
from ai.recommendation_engine import generate_recommendations


PRIORITY_COLORS = {
    "high": "badge-red",
    "medium": "badge-amber",
    "low": "badge-green",
}


def render():
    st.markdown(page_title_bar_html(
        "Recommendations",
        "Data-driven actionable recommendations for your business"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    # Generate recommendations
    recs = st.session_state.get("recommendations")
    if not recs:
        with st.spinner("Generating recommendations..."):
            recs = generate_recommendations(df, use_openai=True)
            st.session_state["recommendations"] = recs

    if not recs:
        st.info("No recommendations generated.")
        return

    # --- Filter ---
    categories = sorted(set(r["category"] for r in recs))
    selected_cats = st.multiselect("Filter by category",
                                   categories, default=categories)
    priority_filter = st.multiselect("Filter by priority",
                                     ["high", "medium", "low"],
                                     default=["high", "medium", "low"])

    st.markdown("---")

    # --- Summary ---
    high_count = len([r for r in recs if r["priority"] == "high"])
    med_count = len([r for r in recs if r["priority"] == "medium"])
    low_count = len([r for r in recs if r["priority"] == "low"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-size:28px;font-weight:800">{len(recs)}</div>'
            f'<div style="font-size:11px;color:#6b7b8d;text-transform:uppercase">'
            f'Total Recommendations</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-size:28px;font-weight:800;color:#ef4444">'
            f'{high_count}</div>'
            f'<div style="font-size:11px;color:#6b7b8d;text-transform:uppercase">'
            f'High Priority</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-size:28px;font-weight:800;color:#f59e0b">'
            f'{med_count}</div>'
            f'<div style="font-size:11px;color:#6b7b8d;text-transform:uppercase">'
            f'Medium Priority</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-size:28px;font-weight:800;color:#10b981">'
            f'{low_count}</div>'
            f'<div style="font-size:11px;color:#6b7b8d;text-transform:uppercase">'
            f'Low Priority</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Display recommendations ---
    filtered = [
        r for r in recs
        if r["category"] in selected_cats and r["priority"] in priority_filter
    ]

    for i, rec in enumerate(filtered, 1):
        badge_cls = PRIORITY_COLORS.get(rec["priority"], "badge-blue")
        st.markdown(
            recommendation_card_html(
                icon=rec["icon"],
                title=f"{i}. {rec['title']}",
                body=f'{rec["body"]}<br/>'
                     f'<span class="badge {badge_cls}" '
                     f'style="margin-top:8px;display:inline-block">'
                     f'{rec["priority"].upper()} PRIORITY</span>',
            ),
            unsafe_allow_html=True,
        )
