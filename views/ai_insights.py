"""
AI Insights page - Structured insight cards with icons.
"""

import streamlit as st

from utils.styling import page_title_bar_html, insight_card_html
from ai.insight_generator import generate_insights, INSIGHT_TYPES, ICONS
from database.db import save_insights_batch


def render():
    st.markdown(page_title_bar_html(
        "AI Insights",
        "Intelligent findings, opportunities, risks, and trends"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    # Generate insights if not cached
    insights = st.session_state.get("insights")
    if not insights:
        with st.spinner("Generating AI insights..."):
            insights = generate_insights(df, use_openai=True)
            st.session_state["insights"] = insights

            # Save to DB
            file_id = st.session_state.get("file_id")
            try:
                db_list = [{"type": i["type"], "text": f"{i['title']}: {i['body']}",
                            "severity": "info"} for i in insights]
                save_insights_batch(file_id, db_list)
            except Exception:
                pass

    if not insights:
        st.info("No insights generated.")
        return

    # --- Filter by type ---
    selected_types = st.multiselect("Filter by insight type",
                                    INSIGHT_TYPES,
                                    default=INSIGHT_TYPES)

    st.markdown("---")

    # --- Display insight cards grouped by type ---
    for itype in INSIGHT_TYPES:
        if itype not in selected_types:
            continue
        type_insights = [i for i in insights if i["type"] == itype]
        if not type_insights:
            continue

        icon = ICONS.get(itype, "💡")
        st.markdown(f"### {icon} {itype}s")

        for ins in type_insights:
            st.markdown(
                insight_card_html(
                    icon=ins["icon"],
                    title=ins["title"],
                    body=ins["body"],
                    card_type=ins.get("css_class", ""),
                ),
                unsafe_allow_html=True,
            )

        st.markdown("")  # spacing

    # --- Summary stats ---
    st.markdown("---")
    st.markdown("#### Insight Summary")
    cols = st.columns(len(INSIGHT_TYPES))
    for i, itype in enumerate(INSIGHT_TYPES):
        count = len([x for x in insights if x["type"] == itype])
        icon = ICONS.get(itype, "💡")
        with cols[i]:
            st.markdown(
                f'<div style="text-align:center">'
                f'<div style="font-size:24px">{icon}</div>'
                f'<div style="font-size:22px;font-weight:800">{count}</div>'
                f'<div style="font-size:11px;color:#6b7b8d;'
                f'text-transform:uppercase">{itype}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
