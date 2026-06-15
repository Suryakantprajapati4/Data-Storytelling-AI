"""
Story Report page - AI-generated business narrative.
"""

import streamlit as st
import re

from utils.styling import page_title_bar_html
from ai.story_generator import generate_story_report
from database.db import save_report


SECTION_ORDER = [
    ("executive_summary", "Executive Summary", "📋"),
    ("dataset_overview", "Dataset Overview", "📊"),
    ("key_insights", "Key Insights", "💡"),
    ("trend_analysis", "Trend Analysis", "📈"),
    ("risks", "Risk Assessment", "⚠️"),
    ("opportunities", "Opportunities", "🚀"),
    ("recommendations", "Strategic Recommendations", "🎯"),
    ("conclusion", "Conclusion", "✅"),
]


def render():
    st.markdown(page_title_bar_html(
        "AI Story Report",
        "Complete business narrative generated from your data"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    # Generate story report
    story = st.session_state.get("story_report")
    if not story:
        with st.spinner("Crafting your business story..."):
            story = generate_story_report(df, use_openai=True)
            st.session_state["story_report"] = story

            # Save to DB
            file_id = st.session_state.get("file_id")
            try:
                full_text = "\n\n".join(
                    f"## {title}\n{story.get(key, '')}"
                    for key, title, _ in SECTION_ORDER
                )
                save_report("story_report", "AI Business Story",
                            full_text, file_id)
            except Exception:
                pass

    if not story:
        st.info("Could not generate story report.")
        return

    # --- Table of Contents ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### Table of Contents")
    toc_cols = st.columns(4)
    for i, (key, title, icon) in enumerate(SECTION_ORDER):
        with toc_cols[i % 4]:
            st.markdown(f"{icon} **{title}**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- Sections ---
    for key, title, icon in SECTION_ORDER:
        text = story.get(key, "")
        if not text:
            continue

        # Build full HTML for one section (open + content + close)
        paragraphs_html = ""
        for p in text.split("\n\n"):
            p = p.strip()
            # Convert markdown bold to HTML bold
            p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
            if p:
                paragraphs_html += f"<p>{p}</p>"

        st.markdown(
            f'<div class="story-section">'
            f'<h4>{icon} {title}</h4>'
            f'{paragraphs_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # --- Full text download ---
    st.markdown("---")
    full_report = "\n\n".join(
        f"# {title}\n\n{story.get(key, '')}"
        for key, title, _ in SECTION_ORDER
    )
    st.download_button(
        label="📥 Download Story Report (TXT)",
        data=full_report,
        file_name="story_report.txt",
        mime="text/plain",
    )
