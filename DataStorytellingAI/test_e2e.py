"""
End-to-end functional test for Data Storytelling AI.
Exercises every module: profiling, analytics, insights, recommendations,
story report, chat, visualizations, and PDF export.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import traceback

PASS = 0
FAIL = 0


def check(name, fn):
    global PASS, FAIL
    try:
        result = fn()
        print(f"  [PASS] {name}")
        PASS += 1
        return result
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        traceback.print_exc()
        FAIL += 1
        return None


# Load sample data
print("\n=== Loading sample data ===")
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv"),
                 parse_dates=["Date"])
print(f"Loaded {len(df)} rows, {df.shape[1]} columns")

# 1. Data profiling
print("\n=== 1. Data Profiling ===")
from utils.data_processor import profile_dataset
profile = check("profile_dataset", lambda: profile_dataset(df))
assert profile is not None, "Profiling failed"
print(f"  Quality score: {profile['quality_score']}")
print(f"  Missing: {int(df.isnull().sum().sum())}")
print(f"  Duplicates: {profile['dup_count']}")
print(f"  Numerical cols: {profile['columns']['numerical']}")
print(f"  Categorical cols: {profile['columns']['categorical']}")
print(f"  Datetime cols: {profile['columns']['datetime']}")

# 2. Analytics engine
print("\n=== 2. Analytics Engine ===")
from ai.analytics_engine import run_analytics
observations = check("run_analytics", lambda: run_analytics(df))
assert observations is not None
print(f"  Generated {len(observations)} observations")
for o in observations[:3]:
    print(f"    [{o['category']}] {o['text'][:80]}")

# 3. Insight generator
print("\n=== 3. AI Insight Generator ===")
from ai.insight_generator import generate_insights
insights = check("generate_insights", lambda: generate_insights(df, use_openai=False))
assert insights is not None
print(f"  Generated {len(insights)} insights")
for i in insights[:3]:
    print(f"    [{i['type']}] {i['title']}: {i['body'][:60]}")

# 4. Visualization engine
print("\n=== 4. Visualization Engine ===")
from utils.visualization import compute_kpis, generate_all_charts
kpis = check("compute_kpis", lambda: compute_kpis(df))
print(f"  KPIs: {kpis}")
charts = check("generate_all_charts", lambda: generate_all_charts(df))
assert charts is not None
print(f"  Generated {len(charts)} charts: {list(charts.keys())}")

# 5. Story report
print("\n=== 5. Story Report Generator ===")
from ai.story_generator import generate_story_report
story = check("generate_story_report", lambda: generate_story_report(df, use_openai=False))
assert story is not None
print(f"  Generated {len(story)} sections: {list(story.keys())}")
print(f"  Executive Summary: {story['executive_summary'][:120]}...")

# 6. Recommendation engine
print("\n=== 6. Recommendation Engine ===")
from ai.recommendation_engine import generate_recommendations
recs = check("generate_recommendations", lambda: generate_recommendations(df, use_openai=False))
assert recs is not None
print(f"  Generated {len(recs)} recommendations")
for r in recs[:3]:
    print(f"    [{r['priority']}] {r['title']}: {r['body'][:60]}")

# 7. Chat with data
print("\n=== 7. Chat With Data ===")
from ai.chat_data import chat_with_data
queries = [
    "Which category performed best?",
    "Show monthly sales trend",
    "What is the total revenue?",
    "Show distribution of revenue",
    "What are the key insights?",
    "Compare all categories",
    "Show correlation between metrics",
]
for q in queries:
    result = check(f"Chat: '{q}'", lambda q=q: chat_with_data(q, df, use_openai=False))
    if result:
        has_chart = "Yes" if result.get("chart") else "No"
        print(f"    Answer: {result['answer'][:80]}")
        print(f"    Chart: {has_chart}")

# 8. PDF export
print("\n=== 8. PDF Export ===")
from utils.pdf_export import generate_pdf_report
pdf_bytes = check("generate_pdf_report", lambda: generate_pdf_report(
    kpis=kpis or {},
    insights=insights or [],
    recommendations=recs or [],
    story_sections=story or {},
    charts=None,  # Skip chart images for speed
))
if pdf_bytes:
    print(f"  PDF size: {len(pdf_bytes) / 1024:.1f} KB")
    out_path = os.path.join(os.path.dirname(__file__), "reports", "test_report.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  Saved to {out_path}")

# 9. Database
print("\n=== 9. Database ===")
from database.db import (
    init_db, save_file_record, get_file_history,
    save_report, get_reports, save_insight, get_insights,
    save_chat_message, get_chat_history, log_activity,
    get_activity, get_dashboard_stats,
)
check("init_db", init_db)
fid = check("save_file_record", lambda: save_file_record("test.csv", 1024, 500, 7))
check("save_report", lambda: save_report("test", "Test Report", "content", fid))
check("save_insight", lambda: save_insight(fid, "Key Finding", "Test insight"))
check("save_chat_message", lambda: save_chat_message(fid, "test?", "answer"))
check("log_activity", lambda: log_activity("test", "test action"))
stats = check("get_dashboard_stats", get_dashboard_stats)
if stats:
    print(f"  Stats: {stats}")

# Summary
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
print(f"{'='*50}")

if FAIL > 0:
    sys.exit(1)
print("\nAll tests passed!")
