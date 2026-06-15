"""
PDF Export module for Data Storytelling AI.
Generates professional PDF reports with cover page, KPIs, charts,
insights, recommendations, and story narrative.
"""

import io
import os
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF


def _sanitize(text: str) -> str:
    """Remove characters outside Latin-1 (emoji, CJK, etc.)."""
    # Strip markdown bold
    text = text.replace("**", "")
    # Remove any character that can't be encoded in latin-1
    return text.encode("latin-1", errors="ignore").decode("latin-1")

from utils.helpers import fmt_number


# ---------------------------------------------------------------------------
# PDF Builder class
# ---------------------------------------------------------------------------

class StorytellingPDF(FPDF):
    """Custom PDF class with branded header/footer."""

    BRAND_BLUE = (30, 58, 95)
    BRAND_LIGHT = (59, 130, 246)
    TEXT_DARK = (30, 30, 30)
    TEXT_GRAY = (100, 116, 139)

    def header(self):
        if self.page_no() == 1:
            return  # Skip header on cover page
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.TEXT_GRAY)
        self.cell(0, 8, "Data Storytelling AI  |  Confidential Report",
                  align="L")
        self.cell(0, 8, datetime.now().strftime("%d %b %Y"), align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.line(10, 14, 200, 14)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.TEXT_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # --- Section helpers ---

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.BRAND_BLUE)
        self.cell(0, 10, _sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*self.BRAND_LIGHT)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.TEXT_DARK)
        self.multi_cell(0, 6, _sanitize(text))
        self.ln(3)

    def bullet(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.TEXT_DARK)
        x = self.get_x()
        self.cell(6, 6, "-")
        self.multi_cell(0, 6, _sanitize(text))
        self.ln(1)

    def kpi_row(self, kpis: Dict[str, str]):
        """Render KPI tiles in a row."""
        n = len(kpis)
        if n == 0:
            return
        w = 190 / n
        start_x = self.get_x()
        y = self.get_y()
        for label, value in kpis.items():
            self.set_xy(start_x, y)
            self.set_fill_color(240, 244, 248)
            self.set_draw_color(200, 210, 225)
            self.rect(start_x, y, w - 4, 22, style="DF")
            self.set_xy(start_x + 2, y + 2)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*self.TEXT_GRAY)
            self.cell(w - 8, 5, _sanitize(label.upper()), align="C")
            self.set_xy(start_x + 2, y + 9)
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*self.BRAND_BLUE)
            self.cell(w - 8, 8, _sanitize(str(value)), align="C")
            start_x += w
        self.set_y(y + 28)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(
    kpis: Dict[str, any],
    insights: List[Dict[str, str]],
    recommendations: List[Dict[str, str]],
    story_sections: Dict[str, str],
    charts: Dict[str, go.Figure] = None,
) -> bytes:
    """
    Build and return a PDF report as bytes.
    """
    pdf = StorytellingPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- Cover Page ---
    _add_cover_page(pdf)

    # --- KPI Summary ---
    if kpis:
        pdf.add_page()
        pdf.section_title("Key Performance Indicators")
        formatted = {}
        for k, v in kpis.items():
            if isinstance(v, (int, float, np.integer, np.floating)):
                formatted[k] = fmt_number(v)
            else:
                formatted[k] = str(v)
        # Render in rows of up to 4
        items = list(formatted.items())
        for i in range(0, len(items), 4):
            pdf.kpi_row(dict(items[i:i + 4]))

    # --- Story Report sections ---
    section_order = [
        ("executive_summary", "Executive Summary"),
        ("dataset_overview", "Dataset Overview"),
        ("key_insights", "Key Insights"),
        ("trend_analysis", "Trend Analysis"),
        ("risks", "Risk Assessment"),
        ("opportunities", "Opportunities"),
        ("recommendations", "Strategic Recommendations"),
        ("conclusion", "Conclusion"),
    ]
    for key, title in section_order:
        text = story_sections.get(key, "")
        if text:
            pdf.add_page()
            pdf.section_title(title)
            paragraphs = text.split("\n\n")
            for p in paragraphs:
                p = p.strip()
                if p:
                    pdf.body_text(p)

    # --- Insights Cards ---
    if insights:
        pdf.add_page()
        pdf.section_title("AI-Generated Insights")
        for ins in insights:
            icon = ins.get("icon", "")
            title = ins.get("title", "")
            body = ins.get("body", "")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*StorytellingPDF.BRAND_BLUE)
            pdf.cell(0, 7, _sanitize(f"{icon}  {title}"),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(body)

    # --- Recommendations ---
    if recommendations:
        pdf.add_page()
        pdf.section_title("Recommendations")
        for i, rec in enumerate(recommendations, 1):
            icon = rec.get("icon", "")
            title = rec.get("title", "")
            body = rec.get("body", "")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*StorytellingPDF.BRAND_BLUE)
            pdf.cell(0, 7, _sanitize(f"{i}. {icon}  {title}"),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(body)

    # --- Charts (as images) ---
    if charts:
        for chart_name, fig in charts.items():
            try:
                img_bytes = fig.to_image(format="png", width=800,
                                         height=450, scale=2)
                pdf.add_page()
                pdf.section_title(chart_name)
                # Write to temp file since FPDF needs a file path
                with tempfile.NamedTemporaryFile(suffix=".png",
                                                 delete=False) as tmp:
                    tmp.write(img_bytes)
                    tmp_path = tmp.name
                pdf.image(tmp_path, x=10, w=190)
                os.unlink(tmp_path)
            except Exception:
                pass  # Skip chart if kaleido not available

    # Output as bytes (fpdf2 returns bytearray; Streamlit needs bytes)
    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Cover Page
# ---------------------------------------------------------------------------

def _add_cover_page(pdf: StorytellingPDF):
    pdf.add_page()
    # Blue background rectangle
    pdf.set_fill_color(*StorytellingPDF.BRAND_BLUE)
    pdf.rect(0, 0, 210, 297, style="F")

    # Title
    pdf.set_y(80)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 16, "Data Storytelling AI", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(200, 215, 235)
    pdf.cell(0, 10, "Automated Business Intelligence Report", align="C",
             new_x="LMARGIN", new_y="NEXT")

    # Divider line
    pdf.set_draw_color(59, 130, 246)
    pdf.set_line_width(1)
    pdf.line(60, 130, 150, 130)

    # Date
    pdf.set_y(145)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(200, 215, 235)
    pdf.cell(0, 8,
             f"Generated on {datetime.now().strftime('%d %B %Y')}",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # Footer text
    pdf.set_y(250)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 170, 200)
    pdf.cell(0, 6,
             "Powered by Data Storytelling AI Assistant",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Confidential  |  For Internal Use Only",
             align="C", new_x="LMARGIN", new_y="NEXT")
