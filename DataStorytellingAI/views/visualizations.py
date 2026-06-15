"""
Visualizations page - Interactive Plotly charts gallery.
"""

import streamlit as st

from utils.styling import page_title_bar_html
from utils.visualization import generate_all_charts
from utils.helpers import classify_columns, guess_revenue_column, \
    guess_date_column, guess_category_column
from utils.visualization import (
    bar_top_categories, line_time_series, pie_category_share,
    histogram_distribution, box_plot, correlation_heatmap,
    multi_metric_time_series,
)


def render():
    st.markdown(page_title_bar_html(
        "Visualizations",
        "Interactive charts and data exploration"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.info("📁 **No dataset found.** Please upload a dataset on the **Home** page to start exploring visualizations.", icon="ℹ️")
        return

    # Use cached charts or generate
    charts = st.session_state.get("charts")
    if not charts:
        with st.spinner("✨ Generating visualizations..."):
            charts = generate_all_charts(df)
            st.session_state["charts"] = charts

    col_info = classify_columns(df)

    # --- Chart type filter ---
    chart_names = list(charts.keys())
    if not chart_names:
        st.warning("No charts could be generated from this dataset. Try a different dataset.", icon="⚠️")
        return

    st.markdown("### 📊 Auto-Generated Insights")
    st.markdown("Explore these pre-built charts based on your dataset's structure.")
    selected = st.multiselect("Filter charts to display",
                              chart_names, default=chart_names)

    st.markdown("<br>", unsafe_allow_html=True)

    if selected:
        # Use gap="large" for better spacing between charts
        for i in range(0, len(selected), 2):
            cols = st.columns(2, gap="large")
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(selected):
                    name = selected[idx]
                    fig = charts.get(name)
                    if fig:
                        with col:
                            # Wrap in a container for a pseudo-card look
                            with st.container():
                                st.plotly_chart(fig, use_container_width=True,
                                                config={
                                                    "displaylogo": False,
                                                    "toImageButtonOptions": {
                                                        "format": "png",
                                                        "filename": name,
                                                        "scale": 2,
                                                    }
                                                })
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # --- Custom Chart Builder ---
    st.markdown("### 🛠️ Custom Chart Builder")
    st.markdown("Build your own visualizations by selecting specific metrics and chart types.")
    
    # Wrap builder in a distinct container
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        chart_type = col1.selectbox("Chart Type",
                                    ["Bar", "Line", "Pie", "Histogram", "Box Plot"])
        x_col = col2.selectbox("X / Category", df.columns.tolist())
        
        # Safe handling if numerical columns are empty
        num_cols = col_info["numerical"]
        y_col = col3.selectbox("Y / Value",
                               num_cols,
                               index=0 if num_cols else None)
        
        color_col = col4.selectbox("Color By (optional)",
                                   [None] + col_info["categorical"])

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Center the button or make it full width in a smaller column
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            generate_btn = st.button("✨ Generate Custom Chart", use_container_width=True)

    if generate_btn:
        try:
            import plotly.express as px
            fig = None
            
            with st.spinner("Rendering custom chart..."):
                if chart_type == "Bar" and y_col:
                    fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                                 title=f"{y_col} by {x_col}", template="plotly_white")
                elif chart_type == "Line" and y_col:
                    fig = px.line(df, x=x_col, y=y_col, color=color_col,
                                  title=f"{y_col} over {x_col}", template="plotly_white")
                elif chart_type == "Pie" and y_col:
                    fig = px.pie(df, names=x_col, values=y_col,
                                 title=f"{y_col} share by {x_col}", template="plotly_white")
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_col, color=color_col,
                                       title=f"Distribution of {x_col}", template="plotly_white")
                elif chart_type == "Box Plot" and y_col:
                    fig = px.box(df, x=x_col, y=y_col, color=color_col,
                                 title=f"{y_col} by {x_col}", template="plotly_white")
                else:
                    st.warning("Please select a valid 'Y / Value' column for this chart type.")
                
                if fig:
                    # Add a nice top margin and display
                    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
                    
        except Exception as e:
            st.error(f"Error generating chart: {e}")