"""
Export Report page - Generate and download PDF report.
"""

import streamlit as st

from utils.styling import page_title_bar_html
from utils.pdf_export import generate_pdf_report
from utils.visualization import compute_kpis, generate_all_charts
from ai.insight_generator import generate_insights
from ai.recommendation_engine import generate_recommendations
from ai.story_generator import generate_story_report


def render():
    st.markdown(page_title_bar_html(
        "Export Report",
        "Generate a professional PDF report with all insights"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    # --- Report configuration ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### Report Configuration")

    col1, col2 = st.columns(2)
    with col1:
        include_charts = st.checkbox("Include charts in PDF", value=True)
        include_insights = st.checkbox("Include AI insights", value=True)
        include_recs = st.checkbox("Include recommendations", value=True)
    with col2:
        include_story = st.checkbox("Include story report", value=True)
        include_kpis = st.checkbox("Include KPI summary", value=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- Generate PDF ---
    if st.button("📄 Generate PDF Report", type="primary",
                 use_container_width=True):
        with st.spinner("Building your professional report..."):
            try:
                # Gather components
                kpis = compute_kpis(df) if include_kpis else {}

                insights = []
                if include_insights:
                    insights = (st.session_state.get("insights")
                                or generate_insights(df))

                recs = []
                if include_recs:
                    recs = (st.session_state.get("recommendations")
                            or generate_recommendations(df))

                story = {}
                if include_story:
                    story = (st.session_state.get("story_report")
                             or generate_story_report(df))

                charts = {}
                if include_charts:
                    charts = (st.session_state.get("charts")
                              or generate_all_charts(df))

                pdf_bytes = generate_pdf_report(
                    kpis=kpis,
                    insights=insights,
                    recommendations=recs,
                    story_sections=story,
                    charts=charts if include_charts else None,
                )

                st.session_state["pdf_bytes"] = pdf_bytes
                st.success("Report generated successfully!")

            except Exception as e:
                st.error(f"Error generating report: {e}")
                st.info("This may happen if the Kaleido package (for "
                        "chart export) is not installed. Try running "
                        "`pip install kaleido`.")

    # --- Download ---
    pdf_bytes = st.session_state.get("pdf_bytes")
    if pdf_bytes:
        # Ensure we have bytes, not bytearray (fpdf2 may return bytearray)
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)

        st.markdown("---")
        st.markdown("#### Download Report")

        filename = (f"report_{st.session_state.get('filename', 'data')}"
                    f".pdf").replace(".csv", "").replace(".xlsx", "")

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

        st.info(f"File size: {len(pdf_bytes) / 1024:.1f} KB")

    # --- Report preview ---
    st.markdown("---")
    st.markdown("#### Report Contents")
    contents = [
        ("📋", "Cover Page", "Branded company-style cover"),
        ("📊", "KPI Summary", "Key performance indicators"),
        ("💡", "AI Insights", "Findings, opportunities, risks, trends"),
        ("📖", "Story Report", "Full business narrative"),
        ("🎯", "Recommendations", "Actionable business advice"),
        ("📈", "Charts", "Interactive visualizations (as images)"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(contents):
        with cols[i % 3]:
            st.markdown(
                f'<div class="section-box" style="text-align:center">'
                f'<div style="font-size:28px">{icon}</div>'
                f'<div style="font-weight:700;font-size:14px">'
                f'{title}</div>'
                f'<div style="font-size:12px;color:#6b7b8d">'
                f'{desc}</div></div>',
                unsafe_allow_html=True,
            )
