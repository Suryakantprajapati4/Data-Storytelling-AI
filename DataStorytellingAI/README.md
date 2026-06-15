# Data Storytelling AI Assistant

> **Transform raw CSV/Excel data into business insights, visualizations, executive summaries, and interactive data conversations — powered by AI.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

Data Storytelling AI is a production-ready analytics platform that automatically converts raw datasets into comprehensive business intelligence. Upload any CSV or Excel file and instantly receive:

- **Automated Data Profiling** — missing values, duplicates, quality scores, outlier detection
- **Smart Analytics** — trend detection, seasonal patterns, anomaly identification, correlation analysis
- **AI-Generated Insights** — key findings, opportunities, risks, trends, performance highlights
- **Business Story Report** — a complete executive narrative written like a real business analyst
- **Recommendation Engine** — dynamic, context-aware business recommendations
- **Chat With Your Data** — ask questions in plain English, get charts and answers instantly
- **PDF Export** — generate professional branded reports ready for stakeholders

---

## Architecture

```
DataStorytellingAI/
│
├── app.py                      # Main Streamlit application
├── pages/                      # Page modules
│   ├── dashboard.py            # Upload & KPI overview
│   ├── analytics.py            # Data profiling & analysis
│   ├── visualizations.py       # Interactive Plotly charts
│   ├── ai_insights.py          # AI insight cards
│   ├── story_report.py         # Business narrative
│   ├── recommendations.py      # Actionable recommendations
│   ├── chat_data_page.py       # Chat interface
│   └── export_report.py        # PDF generation
│
├── ai/                         # AI & analytics modules
│   ├── analytics_engine.py     # Automated analytics
│   ├── insight_generator.py    # Insight generation
│   ├── story_generator.py      # Story report creation
│   ├── recommendation_engine.py# Recommendation logic
│   └── chat_data.py            # Natural language querying
│
├── utils/                      # Utilities
│   ├── styling.py              # Custom CSS (light/dark)
│   ├── helpers.py              # Column classification, formatting
│   ├── data_processor.py       # File loading & profiling
│   ├── visualization.py        # Plotly chart generators
│   └── pdf_export.py           # PDF report builder
│
├── database/                   # SQLite database
│   └── db.py                   # DB operations & schema
│
├── data/                       # Data storage
├── assets/                     # Static assets
├── reports/                    # Generated reports
├── charts/                     # Chart exports
├── screenshots/                # UI screenshots
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Dataset Upload** | CSV/XLSX with drag-and-drop, instant preview |
| **Data Profiling** | Missing values, duplicates, quality score, distributions, outliers |
| **Smart Analytics** | Trends, seasonality, anomalies, correlations, key metrics |
| **AI Insights** | Key Findings, Opportunities, Risks, Trends, Performance Highlights |
| **Visualization** | Bar, Line, Pie, Histogram, Box Plot, Heatmap, Time Series (Plotly) |
| **Story Report** | Executive Summary → Recommendations (full narrative) |
| **Recommendations** | Dynamic, priority-ranked business recommendations |
| **Chat With Data** | Natural language queries with charts and explanations |
| **PDF Export** | Branded multi-page reports with charts |
| **Dark/Light Mode** | Toggle between professional themes |
| **SQLite Database** | Persistent file history, reports, insights, chat |

---

## Screenshots

| Dashboard | Analytics |
|:---------:|:---------:|
| ![Dashboard](screenshots/dashboard.png) | ![Analytics](screenshots/analytics.png) |

| Chat With Data | AI Insights |
|:---------:|:---------:|
| ![Chat](screenshots/chat.png) | ![Insights](screenshots/insights.png) |

---

## Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/DataStorytellingAI.git
cd DataStorytellingAI

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Add your OpenAI API key
# Edit .env and replace your_api_key_here with your actual key
# The app works without it using local logic

# 5. Run the application
streamlit run app.py
```

---

## Usage

1. **Upload Data** — Navigate to Dashboard and upload a CSV or Excel file
2. **Explore Analytics** — Check the Analytics page for automated profiling
3. **View Charts** — Browse interactive visualizations
4. **Read Insights** — Review AI-generated insight cards
5. **Read Story** — Get a complete business narrative report
6. **Get Recommendations** — See prioritized action items
7. **Chat** — Ask questions about your data in plain English
8. **Export** — Generate a professional PDF report

### Supported Data Formats
- CSV files (.csv)
- Excel files (.xlsx, .xls)

### Example Datasets
The app works with any structured tabular data. Good examples include:
- Sales/Revenue datasets
- Customer transaction data
- Financial reports
- Marketing campaign data
- Inventory/operations data

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| ML & Analytics | Scikit-Learn |
| AI Layer | OpenAI API (optional) |
| Reports | FPDF2, ReportLab |
| Database | SQLite |
| Styling | Custom CSS |

---

## Configuration

### OpenAI Integration (Optional)

Set your OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Without an API key, the app uses intelligent local logic for all features.

---

## Future Enhancements

- [ ] Multi-file comparison mode
- [ ] Scheduled report generation
- [ ] User authentication & multi-tenant support
- [ ] Time-series forecasting (Prophet/ARIMA)
- [ ] Advanced NLP for chat (fine-tuned models)
- [ ] Export to PowerPoint
- [ ] Real-time data source connections (APIs, databases)
- [ ] Collaborative annotation of insights
- [ ] Custom report templates
- [ ] Docker deployment

---

## License

MIT License — free for personal and commercial use.

---

## Acknowledgments

Built with [Streamlit](https://streamlit.io), [Plotly](https://plotly.com), and [Scikit-Learn](https://scikit-learn.org).
