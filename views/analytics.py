"""
Analytics page - Automated data profiling and analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.styling import page_title_bar_html, metric_tile_html, section_box_html
from utils.helpers import classify_columns, fmt_number, snake_to_title
from ai.analytics_engine import run_analytics


def render():
    st.markdown(page_title_bar_html(
        "Analytics",
        "Automated data profiling and deep analysis"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    profile = st.session_state.get("profile")
    if profile is None:
        st.warning("Dataset profile not available. Re-upload on Dashboard.")
        return

    col_info = profile["columns"]

    # --- Data Types Overview ---
    st.markdown("#### Column Classification")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_tile_html("Numerical",
                                     str(len(col_info["numerical"]))),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(metric_tile_html("Categorical",
                                     str(len(col_info["categorical"]))),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(metric_tile_html("Datetime",
                                     str(len(col_info["datetime"]))),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(metric_tile_html("Target Candidates",
                                     str(len(col_info["target_candidates"]))),
                    unsafe_allow_html=True)

    st.markdown("---")

    # --- Missing Values ---
    st.markdown("#### Missing Value Report")
    missing_df = profile["missing_df"]
    missing_any = missing_df[missing_df["Missing"] > 0]
    if len(missing_any) > 0:
        st.dataframe(missing_any, use_container_width=True, hide_index=True)
    else:
        st.success("No missing values detected! Your data is complete.")

    st.markdown("---")

    # --- Duplicates ---
    st.markdown("#### Duplicate Analysis")
    dup_count = profile["dup_count"]
    dup_pct = profile["dup_pct"]
    if dup_count > 0:
        st.warning(f"Found **{dup_count}** duplicate rows ({dup_pct}% "
                   f"of dataset).")
    else:
        st.success("No duplicate rows found.")

    st.markdown("---")

    # --- Summary Statistics ---
    st.markdown("#### Summary Statistics")
    st.dataframe(profile["summary_stats"], use_container_width=True)

    st.markdown("---")

    # --- Distribution Analysis ---
    if profile["distributions"]:
        st.markdown("#### Distribution Analysis")
        for col_name, stats in profile["distributions"].items():
            with st.expander(f"📊 {snake_to_title(col_name)}", expanded=False):
                cols = st.columns(4)
                for i, (key, val) in enumerate(stats.items()):
                    with cols[i % 4]:
                        st.markdown(metric_tile_html(
                            key.capitalize(), str(val)),
                            unsafe_allow_html=True)

    st.markdown("---")

    # --- Outlier Detection ---
    if profile["outliers"]:
        st.markdown("#### Outlier Detection (IQR Method)")
        outlier_data = []
        for col_name, info in profile["outliers"].items():
            outlier_data.append({
                "Column": snake_to_title(col_name),
                "Outliers": info["count"],
                "Outlier %": f"{info['pct']}%",
                "Lower Bound": info["lower_bound"],
                "Upper Bound": info["upper_bound"],
            })
        st.dataframe(pd.DataFrame(outlier_data),
                     use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- Correlation Analysis ---
    if profile["corr_matrix"] is not None:
        st.markdown("#### Correlation Matrix")
        st.dataframe(profile["corr_matrix"], use_container_width=True)

    st.markdown("---")

    # --- Automated Observations ---
    st.markdown("#### Automated Business Observations")
    with st.spinner("Running analytics engine..."):
        observations = run_analytics(df)
        st.session_state["observations"] = observations

    if observations:
        categories = {}
        for obs in observations:
            cat = obs["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(obs)

        for cat, obs_list in categories.items():
            with st.expander(f"🏷️ {cat.replace('_', ' ').title()} "
                             f"({len(obs_list)})", expanded=True):
                for obs in obs_list:
                    sentiment_badge = "badge-green"
                    if obs["sentiment"] == "negative":
                        sentiment_badge = "badge-red"
                    elif obs["sentiment"] == "neutral":
                        sentiment_badge = "badge-blue"
                    st.markdown(
                        f'<div class="insight-card">'
                        f'<div class="ic-body">{obs["text"]} '
                        f'<span class="badge {sentiment_badge}">'
                        f'{obs["sentiment"]}</span></div></div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.info("No observations generated.")
