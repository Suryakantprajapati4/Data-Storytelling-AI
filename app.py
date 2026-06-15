"""Data Storytelling AI  v5.0 — Horizontal top-navigation dashboard.
Light theme only.  Primary: #4F46E5  |  BG: #F5F7FA
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

from database.db import init_db
from utils.styling import get_css

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Storytelling AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Environment & DB
# ---------------------------------------------------------------------------
load_dotenv()
init_db()

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(get_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Top navigation bar
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("🔍", "Analytics"),
    ("📈", "Visualizations"),
    ("✨", "AI Insights"),
    ("📖", "Story Report"),
    ("💡", "Recommendations"),
    ("💬", "Chat With Data"),
    ("📄", "Export Report"),
]
NAV_KEYS = [k for _, k in NAV_ITEMS]

# Brand header
st.markdown(
    '<div class="app-brand-bar">'
    '<div class="app-brand-icon">📊</div>'
    '<div>'
    '<div class="app-brand-text">Data Storytelling AI</div>'
    '<div class="app-brand-sub">Transform data into stories</div>'
    '</div></div>',
    unsafe_allow_html=True,
)

# Horizontal navigation radio (styled as nav bar via CSS)
selected = st.radio(
    "Navigate",
    NAV_KEYS,
    horizontal=True,
    label_visibility="collapsed",
    key="nav_radio",
)

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
page_key = selected.lower().replace(" ", "_")

if page_key == "dashboard":
    from views.dashboard import render; render()
elif page_key == "analytics":
    from views.analytics import render; render()
elif page_key == "visualizations":
    from views.visualizations import render; render()
elif page_key == "ai_insights":
    from views.ai_insights import render; render()
elif page_key == "story_report":
    from views.story_report import render; render()
elif page_key == "recommendations":
    from views.recommendations import render; render()
elif page_key == "chat_with_data":
    from views.chat_data_page import render; render()
elif page_key == "export_report":
    from views.export_report import render; render()
