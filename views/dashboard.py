"""
Dashboard page - Upload dataset and display KPI overview.
"""

import streamlit as st
import numpy as np
import pandas as pd

from utils.styling import (
    page_title_bar_html, kpi_card_html, metric_tile_html, insight_card_html,
)
from utils.data_processor import load_uploaded_file, profile_dataset
from utils.helpers import classify_columns, fmt_number, data_quality_score
from utils.visualization import compute_kpis, generate_all_charts
from database.db import save_file_record, get_dashboard_stats, log_activity


def render():
    st.markdown(page_title_bar_html(
        "Dashboard",
        "Upload your data and get an instant business overview"
    ), unsafe_allow_html=True)

    # --- Upload section ---
  
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Drag & drop or browse for a CSV / Excel file",
            type=["csv", "xlsx", "xls"],
            key="dashboard_upload",
        )
    with col2:
        st.markdown(
            '<div style="text-align:center;padding-top:30px;">'
            '<span class="badge badge-blue">Supports CSV, XLSX</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded is not None:
        with st.spinner("Loading dataset..."):
            df = load_uploaded_file(uploaded)

        if df is None:
            st.error("Failed to read the file. Please check the format.")
            return

        st.session_state["df"] = df
        st.session_state["filename"] = uploaded.name

        # Save to DB
        try:
            file_id = save_file_record(
                filename=uploaded.name,
                file_size=uploaded.size,
                row_count=len(df),
                col_count=df.shape[1],
            )
            st.session_state["file_id"] = file_id
        except Exception:
            pass

        # Profile
        with st.spinner("Profiling dataset..."):
            profile = profile_dataset(df)
            st.session_state["profile"] = profile

        # --- Dataset meta tiles ---
        st.markdown("#### Dataset Snapshot")
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.markdown(metric_tile_html("Rows", fmt_number(profile["row_count"])),
                        unsafe_allow_html=True)
        with mc2:
            st.markdown(metric_tile_html("Columns", str(profile["col_count"])),
                        unsafe_allow_html=True)
        with mc3:
            st.markdown(metric_tile_html("Quality Score",
                                         f"{profile['quality_score']}%"),
                        unsafe_allow_html=True)
        with mc4:
            st.markdown(metric_tile_html("Duplicates",
                                         str(profile["dup_count"])),
                        unsafe_allow_html=True)
        with mc5:
            st.markdown(metric_tile_html("Missing",
                                         str(int(df.isnull().sum().sum()))),
                        unsafe_allow_html=True)

        st.markdown("---")

        # --- KPI Cards ---
        st.markdown("#### Key Metrics")
        kpis = compute_kpis(df)
        cols = st.columns(min(len(kpis), 4))
        kpi_icons = {
            "Total Revenue": "💰",
            "Avg per Record": "📊",
            "Total Profit": "📈",
            "Total Orders": "📦",
            "Total Records": "🗃️",
            "Growth %": "🚀",
        }
        for i, (label, value) in enumerate(kpis.items()):
            with cols[i % len(cols)]:
                icon = kpi_icons.get(label, "📌")
                if isinstance(value, (int, float, np.integer, np.floating)):
                    display = fmt_number(value)
                else:
                    display = str(value)
                change = ""
                positive = True
                if "%" in label:
                    positive = value >= 0 if isinstance(value, (int, float, np.integer, np.floating)) else True
                    change = f"{value:+.1f}% vs start" if isinstance(value, (int, float, np.integer, np.floating)) else ""
                st.markdown(kpi_card_html(icon, label, display,
                                          change, positive),
                            unsafe_allow_html=True)

        st.markdown("---")

        # --- Quick Charts ---
        st.markdown("#### Quick Visualizations")
        with st.spinner("Generating charts..."):
            charts = generate_all_charts(df)
            st.session_state["charts"] = charts

        if charts:
            chart_list = list(charts.items())
            for i in range(0, len(chart_list), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(chart_list):
                        name, fig = chart_list[idx]
                        with col:
                            st.plotly_chart(fig, use_container_width=True,
                                            config={"displaylogo": False})

        # --- Preview ---
        with st.expander("Preview Dataset", expanded=False):
            st.dataframe(df.head(50), use_container_width=True)

    else:
        # No file uploaded - show stats if available
        st.info("Upload a dataset to get started.")
        try:
            stats = get_dashboard_stats()
            if stats["total_files"] > 0:
                st.markdown("#### Previous Sessions")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(metric_tile_html("Files Analyzed",
                                                 str(stats["total_files"])),
                                unsafe_allow_html=True)
                with c2:
                    st.markdown(metric_tile_html("Reports Generated",
                                                 str(stats["total_reports"])),
                                unsafe_allow_html=True)
                with c3:
                    st.markdown(metric_tile_html("Insights Created",
                                                 str(stats["total_insights"])),
                                unsafe_allow_html=True)
                with c4:
                    st.markdown(metric_tile_html("Chat Messages",
                                                 str(stats["total_chats"])),
                                unsafe_allow_html=True)
        except Exception:
            pass
