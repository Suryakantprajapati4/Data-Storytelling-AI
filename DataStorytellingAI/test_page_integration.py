"""
Full Page-Level Integration Test
Simulates each page's complete logic flow without requiring Streamlit UI.
Uses actual module signatures (auto-detect columns internally).
"""
import sys, os, traceback
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

PASS = 0
FAIL = 0
ERRORS = []

def test(name, fn):
    global PASS, FAIL, ERRORS
    try:
        fn()
        PASS += 1
        print(f"  [PASS] {name}")
    except Exception as e:
        FAIL += 1
        ERRORS.append((name, str(e), traceback.format_exc()))
        print(f"  [FAIL] {name}: {e}")

# ─── Load data ───────────────────────────────────────────────────────────────
print("=== Loading sample data ===")
csv_path = None
for p in ["sample_sales.csv", "data/sample_sales.csv", "data\\sample_sales.csv"]:
    if os.path.exists(p):
        csv_path = p
        break
if csv_path is None:
    print("ERROR: sample_sales.csv not found. Run create_sample.py first.")
    sys.exit(1)
df = pd.read_csv(csv_path, parse_dates=["Date"])
print(f"Loaded {len(df)} rows, {len(df.columns)} columns from {csv_path}")

# ─── 1. Dashboard Page Logic ─────────────────────────────────────────────────
print("\n=== 1. Dashboard Page Logic ===")

profile = None
def test_dashboard_profile():
    global profile
    from utils.data_processor import profile_dataset
    profile = profile_dataset(df)
    assert profile["shape"][0] == 500, f"Expected 500 rows, got {profile['shape'][0]}"
    assert profile["quality_score"] >= 80, f"Quality too low: {profile['quality_score']}"
    assert len(profile["distributions"]) > 0, "No distributions"
    assert profile["corr_matrix"] is not None, "No correlation matrix"
test("Dashboard: profile_dataset", test_dashboard_profile)

kpis = None
def test_dashboard_kpis():
    global kpis
    from utils.visualization import compute_kpis
    kpis = compute_kpis(df)
    assert "Total Revenue" in kpis, f"Missing Total Revenue: {list(kpis.keys())}"
    assert "Avg per Record" in kpis, f"Missing Avg per Record: {list(kpis.keys())}"
    for k, v in kpis.items():
        assert isinstance(v, (int, float, np.integer, np.floating)), \
            f"KPI '{k}' has unsupported type {type(v)}"
test("Dashboard: compute_kpis", test_dashboard_kpis)

charts = None
def test_dashboard_charts():
    global charts
    from utils.visualization import generate_all_charts
    charts = generate_all_charts(df)
    assert len(charts) >= 5, f"Expected >=5 charts, got {len(charts)}"
    for name, fig in charts.items():
        assert fig is not None, f"Chart '{name}' is None"
test("Dashboard: generate_all_charts", test_dashboard_charts)

# ─── 2. Analytics Page Logic ────────────────────────────────────────────────
print("\n=== 2. Analytics Page Logic ===")

observations = None
def test_analytics():
    global observations
    from ai.analytics_engine import run_analytics
    observations = run_analytics(df)
    assert len(observations) >= 5, f"Only {len(observations)} observations"
    categories = set(o.get("category", "") for o in observations)
    assert len(categories) >= 3, f"Only {len(categories)} categories: {categories}"
    for o in observations:
        assert "text" in o and "category" in o, f"Missing keys: {o}"
        assert len(o["text"]) > 10, f"Text too short: {o['text']}"
test("Analytics: run_analytics", test_analytics)

# ─── 3. Visualizations Page Logic ───────────────────────────────────────────
print("\n=== 3. Visualizations Page Logic ===")

from utils.helpers import classify_columns, guess_revenue_column, guess_date_column, guess_category_column
cols = classify_columns(df)
rev_col  = guess_revenue_column(df, cols["numerical"])
date_col = guess_date_column(df, cols["datetime"])
cat_col  = guess_category_column(df, cols["categorical"])

def test_viz_bar():
    from utils.visualization import bar_top_categories
    fig = bar_top_categories(df, cat_col, rev_col)
    assert fig is not None and len(fig.to_dict()["data"]) > 0
test("Viz: bar_top_categories", test_viz_bar)

def test_viz_line():
    from utils.visualization import line_time_series
    fig = line_time_series(df, date_col, rev_col)
    assert fig is not None and len(fig.to_dict()["data"]) > 0
test("Viz: line_time_series", test_viz_line)

def test_viz_pie():
    from utils.visualization import pie_category_share
    fig = pie_category_share(df, cat_col, rev_col)
    assert fig is not None
test("Viz: pie_category_share", test_viz_pie)

def test_viz_hist():
    from utils.visualization import histogram_distribution
    fig = histogram_distribution(df, rev_col)
    assert fig is not None
test("Viz: histogram_distribution", test_viz_hist)

def test_viz_box():
    from utils.visualization import box_plot
    fig = box_plot(df, cat_col, rev_col)
    assert fig is not None
test("Viz: box_plot", test_viz_box)

def test_viz_heatmap():
    from utils.visualization import correlation_heatmap
    fig = correlation_heatmap(df)
    assert fig is not None
test("Viz: correlation_heatmap", test_viz_heatmap)

def test_viz_multi():
    from utils.visualization import multi_metric_time_series
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    fig = multi_metric_time_series(df, date_col, num_cols[:3])
    assert fig is not None
test("Viz: multi_metric_time_series", test_viz_multi)

# ─── 4. AI Insights Page Logic ─────────────────────────────────────────────
print("\n=== 4. AI Insights Page Logic ===")

insights = None
def test_insights():
    global insights
    from ai.insight_generator import generate_insights
    insights = generate_insights(df, use_openai=False)
    assert len(insights) >= 3, f"Only {len(insights)} insights"
    for i in insights:
        assert "type" in i and "title" in i and "body" in i, f"Missing keys: {i}"
        assert len(i["body"]) > 5, f"Body too short: {i['body']}"
test("AI Insights: generate_insights", test_insights)

# ─── 5. Story Report Page Logic ─────────────────────────────────────────────
print("\n=== 5. Story Report Page Logic ===")

story = None
def test_story():
    global story
    from ai.story_generator import generate_story_report
    story = generate_story_report(df, use_openai=False)
    expected = ['executive_summary', 'dataset_overview', 'key_insights',
                'trend_analysis', 'risks', 'opportunities', 'recommendations', 'conclusion']
    for sec in expected:
        assert sec in story, f"Missing section: {sec}"
        assert len(story[sec]) > 20, f"Section '{sec}' too short ({len(story[sec])} chars)"
    assert any(c.isdigit() for c in story['executive_summary']), "Exec summary has no numbers"
test("Story Report: all 8 sections", test_story)

# ─── 6. Recommendations Page Logic ──────────────────────────────────────────
print("\n=== 6. Recommendations Page Logic ===")

recs = None
def test_recs():
    global recs
    from ai.recommendation_engine import generate_recommendations
    recs = generate_recommendations(df, use_openai=False)
    assert len(recs) >= 3, f"Only {len(recs)} recommendations"
    for r in recs:
        assert "priority" in r and "title" in r and "body" in r, f"Missing keys: {r}"
        assert r["priority"] in ("high", "medium", "low"), f"Invalid priority: {r['priority']}"
test("Recommendations: prioritized recs", test_recs)

# ─── 7. Chat With Data Logic ────────────────────────────────────────────────
print("\n=== 7. Chat With Data Logic ===")

chat_queries = [
    "Which category performed best?",
    "Show monthly sales trend",
    "What is the total revenue?",
    "Show distribution of revenue",
    "What are the key insights?",
    "Compare all categories",
    "Which region has the lowest sales?",
    "How many records are there?",
    "What is the average revenue?",
    "Show correlation between metrics",
    "What is the market share of each category?",
]

def test_chat():
    from ai.chat_data import chat_with_data
    for q in chat_queries:
        result = chat_with_data(q, df, use_openai=False)
        assert "answer" in result, f"No answer for '{q}': {result}"
        assert len(result["answer"]) > 5, f"Answer too short for '{q}': {result['answer']}"
        has_chart = "Yes" if result.get("chart") else "No"
        print(f"    Q: {q}")
        print(f"    A: {result['answer'][:120]}")
        print(f"    Chart: {has_chart}")
test("Chat: all 11 queries answered", test_chat)

# ─── 8. PDF Export Logic ─────────────────────────────────────────────────────
print("\n=== 8. PDF Export Logic ===")

def test_pdf():
    from utils.pdf_export import generate_pdf_report
    pdf_bytes = generate_pdf_report(
        kpis=kpis or {},
        insights=insights or [],
        recommendations=recs or [],
        story_sections=story or {},
        charts=charts,
    )
    assert pdf_bytes is not None, "PDF generation returned None"
    assert len(pdf_bytes) > 5000, f"PDF too small ({len(pdf_bytes)} bytes)"
    assert pdf_bytes[:5] == b"%PDF-", f"Not a valid PDF header: {pdf_bytes[:5]}"
    outpath = os.path.join("reports", "full_integration_test.pdf")
    os.makedirs("reports", exist_ok=True)
    with open(outpath, "wb") as f:
        f.write(pdf_bytes)
    print(f"    PDF: {len(pdf_bytes)/1024:.1f} KB at {outpath}")
test("PDF Export: valid PDF with all sections", test_pdf)

# ─── 9. Database Operations ─────────────────────────────────────────────────
print("\n=== 9. Database Operations ===")

def test_db():
    from database.db import (init_db, save_file_record, save_report,
                              save_insight, save_insights_batch, save_chat_message,
                              log_activity, get_dashboard_stats)
    init_db()
    save_file_record("integration_test.csv", 500, 7, 100.0)
    save_report("Integration Test Report", "exec_summary", "full_story")
    save_insight("Key Finding", "Test Insight", "Test Body", "test_insight")
    save_insights_batch(None, [
        {"type": "Risk", "title": "Risk 1", "body": "Body", "css_class": "risk"},
        {"type": "Opportunity", "title": "Opp 1", "body": "Body", "css_class": "opportunity"},
    ])
    save_chat_message(None, "Total?", "1M.")
    log_activity("upload", "integration_test.csv")
    stats = get_dashboard_stats()
    assert stats["total_files"] >= 1
    assert stats["total_reports"] >= 1
    assert stats["total_insights"] >= 1
test("Database: full CRUD cycle", test_db)

# ─── 10. Styling / HTML Components ──────────────────────────────────────────
print("\n=== 10. Styling & HTML Components ===")

def test_styling():
    from utils.styling import (kpi_card_html, insight_card_html,
                                recommendation_card_html, page_title_bar_html, metric_tile_html,
                                APP_CSS)
    kpi = kpi_card_html("fas fa-dollar-sign", "Revenue", "$1.2M")
    assert "<div" in kpi and "Revenue" in kpi and "$1.2M" in kpi
    insight = insight_card_html("fas fa-star", "Key Finding", "Test body", "key-finding")
    assert "<div" in insight and "Key Finding" in insight
    rec = recommendation_card_html("fas fa-lightbulb", "Rec Title", "Rec body")
    assert "<div" in rec and "Rec Title" in rec
    title = page_title_bar_html("Test Page", "Subtitle")
    assert "Test Page" in title
    tile = metric_tile_html("Metric", "42")
    assert "42" in tile
    assert len(APP_CSS) > 1000
test("Styling: HTML generators and CSS (light theme)", test_styling)

# ─── 11. Helpers Edge Cases ─────────────────────────────────────────────────
print("\n=== 11. Helpers Edge Cases ===")

def test_helpers():
    from utils.helpers import (data_quality_score, detect_outliers_iqr,
                                fmt_number, fmt_pct, fmt_currency)
    score = data_quality_score(df)
    assert 0 <= score <= 100, f"Quality out of range: {score}"
    outliers = detect_outliers_iqr(df, ["Revenue"])
    assert isinstance(outliers, dict)
    assert isinstance(fmt_number(1234567), str)
    assert isinstance(fmt_pct(0.1234), str)
    assert isinstance(fmt_currency(1234.56), str)
    empty_df = pd.DataFrame()
    cols_empty = classify_columns(empty_df)
    assert cols_empty["numerical"] == []
test("Helpers: edge cases and formatting", test_helpers)

# ─── 12. Page Import Verification ───────────────────────────────────────────
print("\n=== 12. Page Import Verification ===")

def test_page_imports():
    from views import dashboard, analytics, visualizations, ai_insights
    from views import story_report, recommendations, chat_data_page, export_report
    for mod, name in [(dashboard, "dashboard"), (analytics, "analytics"),
                       (visualizations, "visualizations"), (ai_insights, "ai_insights"),
                       (story_report, "story_report"), (recommendations, "recommendations"),
                       (chat_data_page, "chat_data_page"), (export_report, "export_report")]:
        assert hasattr(mod, 'render'), f"{name} missing render()"
test("Pages: all 8 modules import with render()", test_page_imports)

def test_app_import():
    import app
    assert hasattr(app, '__file__')
test("App: app.py imports cleanly", test_app_import)

# ─── Results ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
print("=" * 50)

if ERRORS:
    print("\n--- FAILURES ---")
    for name, err, tb in ERRORS:
        print(f"\n{name}:")
        print(tb)

if FAIL == 0:
    print("\nAll integration tests passed!")
else:
    print(f"\n{FAIL} test(s) failed!")
    sys.exit(1)
