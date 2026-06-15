"""Custom CSS — Data Storytelling AI  v5.0
Horizontal top-navigation bar.  No sidebar.
Primary: #4F46E5  |  BG: #F5F7FA  |  Cards: white
"""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ══════ GLOBAL RESET ══════ */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { display: none !important; }

/* ══════ HIDE STREAMLIT CHROME ══════ */
header[data-testid="stHeader"]  { display: none !important; height: 0 !important; }
div[data-testid="stDecoration"] { display: none !important; height: 0 !important; }
div[data-testid="stToolbar"]    { display: none !important; height: 0 !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* Hide sidebar completely */
section[data-testid="stSidebar"] { display: none !important; }

/* ══════ APP BACKGROUND ══════ */
html, body                         { background: #F5F7FA !important; }
.stApp                             { background: #F5F7FA !important; }
section.main                       { background: #F5F7FA !important; }
section.main > div                 { background: #F5F7FA !important; }

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ══════════════════════════════════════
   BRAND BAR
══════════════════════════════════════ */
.app-brand-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0 8px;
    margin-bottom: 2px;
}
.app-brand-icon {
    width: 38px; height: 38px;
    background: #4F46E5;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    color: white;
}
.app-brand-text {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.3;
}
.app-brand-sub {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 400;
}

/* ══════════════════════════════════════
   HORIZONTAL NAVIGATION BAR
══════════════════════════════════════ */
/* Hide the 'Navigate' label */
.stRadio > label {
    color: transparent !important;
    font-size: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Radiogroup = horizontal flex container */
.stRadio div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 4px !important;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}

/* Each nav item */
.stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
    flex: 1;
    text-align: center;
    justify-content: center;
    padding: 10px 6px !important;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    color: #64748B;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    margin: 0 !important;
    white-space: nowrap;
}

/* Hide the default radio circle */
.stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* Hover */
.stRadio div[role="radiogroup"] label[data-baseweb="radio"]:hover {
    background: #F8FAFC;
    color: #1E293B;
    
}

/* Active state */
.stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: #4F46E5;
    color: white !important;
    font-weight: 700;
    border: 2px solid #4338CA;
    box-shadow: 0 4px 12px rgba(79,70,229,0.30);
}

.stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) * {
    color: white !important;
}

/* ══════════════════════════════════════
   HEADINGS
══════════════════════════════════════ */
h1 { color: #0F172A !important; font-weight: 800 !important; letter-spacing: -0.5px; font-size: 24px !important; }
h2 { color: #1E293B !important; font-weight: 700 !important; font-size: 18px !important; }
h3 { color: #334155 !important; font-weight: 600 !important; font-size: 15px !important; }

/* ══════════════════════════════════════
   PAGE TITLE BAR  —  clean, no gradient
══════════════════════════════════════ */
.page-title-bar {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    border-left: 4px solid #4F46E5;
}
.page-title-bar h1 {
    color: #0F172A !important;
    margin: 0;
    font-size: 22px !important;
    font-weight: 700;
}
.page-title-bar p {
    color: #64748B;
    font-size: 13px;
    margin: 4px 0 0 0;
}

/* ══════════════════════════════════════
   KPI CARD  —  executive metrics
══════════════════════════════════════ */
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
    text-align: center;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.kpi-card .kpi-icon  { font-size: 24px; margin-bottom: 8px; }
.kpi-card .kpi-value { font-size: 26px; font-weight: 800; color: #0F172A; margin: 4px 0; line-height: 1.2; }
.kpi-card .kpi-label { font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-card .kpi-change { font-size: 11px; font-weight: 600; margin-top: 8px; }
.kpi-change.positive { color: #059669; }
.kpi-change.negative { color: #EF4444; }

/* ══════════════════════════════════════
   INSIGHT CARD
══════════════════════════════════════ */
.insight-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #4F46E5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    transition: box-shadow 0.15s;
}
.insight-card:hover { box-shadow: 0 3px 12px rgba(0,0,0,0.07); }
.insight-card.opportunity { border-left-color: #059669; }
.insight-card.risk        { border-left-color: #EF4444; }
.insight-card.trend       { border-left-color: #7C3AED; }
.insight-card.highlight   { border-left-color: #D97706; }
.insight-card .ic-header {
    font-weight: 600; font-size: 13px; margin-bottom: 6px;
    display: flex; align-items: center; gap: 8px; color: #0F172A;
}
.insight-card .ic-body { font-size: 13px; color: #475569; line-height: 1.65; }

/* ══════════════════════════════════════
   RECOMMENDATION CARD
══════════════════════════════════════ */
.rec-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #4F46E5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    transition: box-shadow 0.15s;
}
.rec-card:hover { box-shadow: 0 3px 12px rgba(0,0,0,0.07); }
.rec-card .rec-icon  { font-size: 16px; margin-right: 6px; }
.rec-card .rec-title { font-weight: 600; font-size: 13px; color: #1E293B; margin-bottom: 4px; }
.rec-card .rec-body  { font-size: 13px; color: #475569; line-height: 1.65; }

/* ══════════════════════════════════════
   CHAT BUBBLES
══════════════════════════════════════ */
.chat-user {
    background: #4F46E5; color: white;
    padding: 10px 16px; border-radius: 14px 14px 4px 14px;
    margin: 5px 0; max-width: 75%; float: right; clear: both;
    font-size: 13px; box-shadow: 0 2px 6px rgba(79,70,229,0.25);
}
.chat-ai {
    background: #FFFFFF; color: #1E293B;
    padding: 10px 16px; border-radius: 14px 14px 14px 4px;
    margin: 5px 0; max-width: 75%; float: left; clear: both;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); font-size: 13px;
    border: 1px solid #E2E8F0;
}

/* ══════════════════════════════════════
   SECTION BOX
══════════════════════════════════════ */
.section-box {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ══════════════════════════════════════
   BADGES
══════════════════════════════════════ */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 5px;
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px;
}
.badge-blue   { background: #EEF2FF; color: #4338CA; }
.badge-green  { background: #ECFDF5; color: #065F46; }
.badge-red    { background: #FEF2F2; color: #991B1B; }
.badge-purple { background: #F5F3FF; color: #5B21B6; }
.badge-amber  { background: #FFFBEB; color: #92400E; }

/* ══════════════════════════════════════
   TABLES
══════════════════════════════════════ */
.dataframe { border-radius: 10px; overflow: hidden; border: 1px solid #E2E8F0 !important; }
.dataframe thead th {
    background: #F8FAFC !important;
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    padding: 10px 14px !important;
    border-bottom: 2px solid #E2E8F0 !important;
}
.dataframe tbody td { color: #334155 !important; font-size: 13px !important; }
.dataframe tbody tr:nth-child(even) { background: #FAFBFC; }
.dataframe tbody tr:hover { background: #EEF2FF; }

/* ══════════════════════════════════════
   METRIC TILE
══════════════════════════════════════ */
.metric-tile {
    background: #FFFFFF; border-radius: 10px; padding: 16px 18px;
    text-align: center; border: 1px solid #E2E8F0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    transition: transform 0.15s;
}
.metric-tile:hover { transform: translateY(-1px); }
.metric-tile .mt-value { font-size: 22px; font-weight: 800; color: #0F172A; }
.metric-tile .mt-label { font-size: 10px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }

/* ══════════════════════════════════════
   STORY SECTION
══════════════════════════════════════ */
.story-section {
    background: #FFFFFF; border-radius: 12px; padding: 20px 24px;
    margin-bottom: 12px; border: 1px solid #E2E8F0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.story-section h4 {
    color: #1E293B; font-weight: 700; margin-bottom: 10px;
    padding-bottom: 8px; border-bottom: 1px solid #F1F5F9; font-size: 15px;
}
.story-section p { color: #475569; line-height: 1.8; font-size: 14px; }

/* ══════════════════════════════════════
   UPLOAD ZONE
══════════════════════════════════════ */
.upload-card {
    background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04); overflow: hidden; margin-bottom: 16px;
}
.upload-card-header {
    padding: 14px 20px; border-bottom: 1px solid #F1F5F9;
}
.upload-card-title {
    font-size: 14px; font-weight: 600; color: #0F172A;
    display: flex; align-items: center; gap: 8px;
}
.drop-zone {
    margin: 16px; border: 2px dashed #D1D5DB; border-radius: 10px;
    padding: 40px 24px; text-align: center; background: #FAFBFC;
    transition: all 0.2s ease;
}
.drop-zone:hover { border-color: #4F46E5; background: #F5F3FF; }
.drop-icon-wrap {
    width: 48px; height: 48px; background: #EEF2FF; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; margin: 0 auto 14px;
}
.drop-title { font-size: 15px; font-weight: 600; color: #0F172A; margin-bottom: 4px; }
.drop-sub   { font-size: 13px; color: #64748B; margin-bottom: 14px; }
.format-pills { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }
.fpill {
    padding: 3px 10px; background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 5px; font-size: 11px; font-weight: 500; color: #475569;
}
.drop-zone-label {
    margin: 16px 16px 0; border: 2px dashed #D1D5DB; border-radius: 10px;
    padding: 32px 24px 24px; text-align: center; background: #FAFBFC;
}

/* ══════════════════════════════════════
   HERO / LANDING
══════════════════════════════════════ */
.hero-section { text-align: center; padding: 48px 24px 32px; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 14px; border-radius: 20px;
    background: #EEF2FF; border: 1px solid #C7D2FE;
    font-size: 12px; color: #4338CA; font-weight: 500; margin-bottom: 16px;
}
.hero-section h1 { font-size: 32px !important; font-weight: 800; color: #0F172A; margin-bottom: 10px; }
.hero-section h1 span { color: #4F46E5; }
.hero-section p { font-size: 15px; color: #64748B; max-width: 460px; margin: 0 auto 24px; line-height: 1.7; }

/* Stat cards on landing */
.stat-card {
    background: #FFFFFF; border-radius: 12px; padding: 18px;
    border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.stat-icon-wrap {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin-bottom: 12px;
}
.si-indigo { background: #EEF2FF; }
.si-green  { background: #ECFDF5; }
.si-violet { background: #F5F3FF; }
.si-amber  { background: #FFFBEB; }
.stat-val { font-size: 24px; font-weight: 800; color: #0F172A; margin-bottom: 2px; }
.stat-lbl { font-size: 11px; color: #64748B; font-weight: 500; }
.stat-delta { font-size: 11px; margin-top: 6px; font-weight: 500; }
.delta-up { color: #059669; }

/* ══════════════════════════════════════
   LOADING SPINNER
══════════════════════════════════════ */
.loading-spinner {
    border: 3px solid #EEF2FF; border-top: 3px solid #4F46E5;
    border-radius: 50%; width: 36px; height: 36px;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ══════════════════════════════════════
   STREAMLIT ELEMENT OVERRIDES
══════════════════════════════════════ */
/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 2px; }
.stTabs [data-baseweb="tab"] {
    padding: 8px 16px; border-radius: 8px 8px 0 0;
    font-size: 13px; font-weight: 500; color: #64748B;
    background: transparent; border: none;
}
.stTabs [aria-selected="true"] {
    color: #4F46E5 !important; background: #FFFFFF !important;
    border-bottom: 2px solid #4F46E5 !important; font-weight: 600;
}

/* Buttons */
.stButton > button {
    border-radius: 8px; font-weight: 500; font-size: 13px;
    border: 1px solid #E2E8F0; color: #475569; background: #FFFFFF;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #4F46E5; color: #4F46E5; background: #FAFAFE;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: #4F46E5 !important; color: #FFFFFF !important;
    border: none !important; font-weight: 600;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: #4338CA !important;
}

/* Selectbox / multiselect */
.stSelectbox label, .stMultiSelect label { font-size: 13px !important; font-weight: 500 !important; color: #475569 !important; }

/* Text input */
.stTextInput input, .stTextArea textarea {
    border-radius: 8px !important; border-color: #E2E8F0 !important;
    font-size: 13px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #4F46E5 !important; box-shadow: 0 0 0 1px #4F46E5 !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-size: 13px !important; font-weight: 600 !important; color: #1E293B !important;
}

/* ══════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 1100px) {
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
        font-size: 11px !important;
        padding: 8px 4px !important;
    }
}
@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    .stRadio div[role="radiogroup"] {
        flex-wrap: wrap !important;
    }
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
        flex: 0 0 calc(25% - 4px) !important;
        font-size: 11px !important;
        padding: 8px 4px !important;
    }
}
</style>
"""


def get_css():
    """Return the application CSS."""
    return APP_CSS


def kpi_card_html(icon, label, value, change="", positive=True):
    ch = f'<div class="kpi-change {"positive" if positive else "negative"}">{change}</div>' if change else ""
    return f'<div class="kpi-card"><div class="kpi-icon">{icon}</div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{ch}</div>'


def insight_card_html(icon, title, body, card_type=""):
    return f'<div class="insight-card {card_type}"><div class="ic-header">{icon} {title}</div><div class="ic-body">{body}</div></div>'


def recommendation_card_html(icon, title, body):
    return f'<div class="rec-card"><div class="rec-title">{icon} {title}</div><div class="rec-body">{body}</div></div>'


def page_title_bar_html(title, subtitle):
    return f'<div class="page-title-bar"><h1>{title}</h1><p>{subtitle}</p></div>'


def section_box_html(content):
    return f'<div class="section-box">{content}</div>'


def metric_tile_html(label, value):
    return f'<div class="metric-tile"><div class="mt-value">{value}</div><div class="mt-label">{label}</div></div>'
