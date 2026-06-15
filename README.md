# 📊 Data Storytelling AI Assistant

> Transform raw CSV/Excel data into business insights, visualizations, executive summaries, and interactive data conversations.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Overview

Data Storytelling AI Assistant is an end-to-end analytics platform built with Python and Streamlit that helps users convert raw datasets into meaningful business insights.

The application automates key steps of the analytics workflow, including data profiling, KPI generation, visualization, insight generation, reporting, and data exploration through a conversational interface.

Upload any CSV or Excel dataset and instantly generate:

- Automated Data Profiling
- KPI Dashboards
- Interactive Visualizations
- Business Insights
- Executive Story Reports
- Recommendations
- PDF Reports
- Data Conversations

---

## 🎯 Project Motivation

Business users often spend hours cleaning data, creating charts, and preparing reports before they can make informed decisions.

This project was developed to simplify that process by providing a single platform that can:

- Analyze datasets automatically
- Generate business-focused insights
- Visualize important trends
- Create stakeholder-ready reports
- Support data-driven decision making

---

## 🏗️ Architecture

```text
DataStorytellingAI/
│
├── app.py                      # Main Streamlit application
│
├── views/
│   ├── dashboard.py            # Upload & KPI overview
│   ├── analytics.py            # Data profiling & analysis
│   ├── visualizations.py       # Interactive charts
│   ├── ai_insights.py          # Insight generation
│   ├── story_report.py         # Business narrative report
│   ├── recommendations.py      # Recommendations engine
│   ├── chat_data_page.py       # Data conversation interface
│   └── export_report.py        # PDF export
│
├── ai/
│   ├── analytics_engine.py
│   ├── insight_generator.py
│   ├── story_generator.py
│   ├── recommendation_engine.py
│   └── chat_data.py
│
├── utils/
│   ├── styling.py
│   ├── helpers.py
│   ├── data_processor.py
│   ├── visualization.py
│   └── pdf_export.py
│
├── database/
│   └── db.py
│
├── data/
├── reports/
├── screenshots/
├── assets/
│
├── requirements.txt
└── README.md
```

---

## ✨ Features

| Feature | Description |
|----------|-------------|
| 📁 Dataset Upload | Upload CSV/XLSX datasets |
| 📊 Dashboard | KPI overview and dataset summary |
| 🔍 Data Profiling | Missing values, duplicates, quality analysis |
| 📈 Visualizations | Interactive Plotly charts |
| 💡 Insights | Business-focused observations |
| 📖 Story Report | Executive-style narrative summaries |
| 🎯 Recommendations | Actionable suggestions |
| 💬 Chat With Data | Ask questions about your dataset |
| 📄 PDF Export | Download reports and summaries |
| 🗄️ SQLite Storage | Persistent storage for reports and history |

---

## 📊 Example Workflow

```text
CSV / Excel Upload
        ↓
Data Profiling
        ↓
KPI Calculation
        ↓
Visualization Generation
        ↓
Insight Generation
        ↓
Story Report Creation
        ↓
PDF Export
```

---

## 💼 Business Value

The platform helps users:

- Understand data faster
- Detect quality issues
- Track business KPIs
- Explore trends visually
- Generate executive summaries
- Reduce manual reporting effort

---

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Analytics
![Analytics](screenshots/analytics.png)

### AI Insights
![Insights](screenshots/insights.png)

### Chat With Data
![Chat](screenshots/chat.png)

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+
- pip

### Clone Repository

```bash
git clone https://github.com/yourusername/Data-Storytelling-AI.git

cd Data-Storytelling-AI
```

### Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

## 📋 Usage

1. Upload a CSV or Excel dataset
2. Explore Dashboard metrics
3. Review Analytics results
4. Generate Visualizations
5. Read Insights
6. View Story Report
7. Download PDF Report

---

## 🛠️ Tech Stack

| Layer | Technology |
|---------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Analytics | Scikit-Learn |
| Database | SQLite |
| Reporting | FPDF, ReportLab |
| Styling | Custom CSS |

---

## 👨‍💻 Skills Demonstrated

This project demonstrates:

- Python Development
- Data Analysis
- Exploratory Data Analysis (EDA)
- Data Visualization
- Dashboard Development
- Business Intelligence Reporting
- SQL & Database Integration
- Report Automation
- Streamlit Development
- Problem Solving

---

## 🔮 Future Improvements

- Predictive Analytics
- Forecasting Models
- Real-Time Data Sources
- User Authentication
- Cloud Deployment
- PowerPoint Export
- Advanced Natural Language Querying
- Multi-Dataset Comparison

---

## 👤 Author

**Suryakant Prajapati**

Aspiring Data Analyst

**Skills:** SQL • Excel • Python • Power BI • Data Visualization • Business Analytics

---

## 📄 License

MIT License

---

## ⭐ Project Status

Completed and actively improving.
