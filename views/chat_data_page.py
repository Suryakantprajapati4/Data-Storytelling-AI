"""
Chat With Data page - Natural language data querying.
"""

import streamlit as st

from utils.styling import page_title_bar_html
from ai.chat_data import chat_with_data
from database.db import save_chat_message


def render():
    st.markdown(page_title_bar_html(
        "Chat With Your Data",
        "Ask questions in plain English and get instant answers with charts"
    ), unsafe_allow_html=True)

    df = st.session_state.get("df")
    if df is None:
        st.warning("Please upload a dataset on the Dashboard page first.")
        return

    # --- Suggested questions ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### 💡 Try These Questions")
    suggestions = [
        "Which category performed best?",
        "Show monthly sales trend",
        "What are the key insights?",
        "Show distribution of revenue",
        "What is the total revenue?",
        "Which region contributed most?",
        "Compare all categories",
        "Show correlation between metrics",
    ]
    cols = st.columns(4)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 4]:
            if st.button(suggestion, key=f"sug_{i}",
                         use_container_width=True):
                st.session_state["chat_input"] = suggestion
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- Chat input ---
    user_query = st.text_input(
        "Ask a question about your data:",
        value=st.session_state.get("chat_input", ""),
        key="chat_text_input",
        placeholder="e.g., Which region had the highest sales?",
    )

    # Clear suggestion input after it's been picked up
    if st.session_state.get("chat_input"):
        st.session_state.pop("chat_input", None)

    # --- Chat history ---
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Only process when the query is new (not already the last processed)
    if user_query and user_query != st.session_state.get("_last_chat_query"):
        st.session_state["_last_chat_query"] = user_query
        with st.spinner("Analysing your question..."):
            result = chat_with_data(user_query, df, use_openai=True)

        # Save to DB
        file_id = st.session_state.get("file_id")
        try:
            save_chat_message(file_id, user_query,
                              result.get("answer", ""))
        except Exception:
            pass

        # Add to session history
        st.session_state["chat_history"].append({
            "query": user_query,
            "answer": result.get("answer", ""),
            "explanation": result.get("explanation", ""),
            "chart": result.get("chart"),
        })

    # --- Display chat history ---
    st.markdown("---")
    st.markdown("#### Conversation")

    for msg in reversed(st.session_state.get("chat_history", [])):
        # User message
        st.markdown(
            f'<div class="chat-user">{msg["query"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="clear:both"></div>',
                    unsafe_allow_html=True)

        # AI response
        st.markdown(
            f'<div class="chat-ai">{msg["answer"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="clear:both"></div>',
                    unsafe_allow_html=True)

        # Explanation
        if msg.get("explanation"):
            st.markdown(
                f'<div style="font-size:11px;color:#6b7b8d;'
                f'margin:4px 0 8px 12px;font-style:italic">'
                f'ℹ️ {msg["explanation"]}</div>',
                unsafe_allow_html=True,
            )

        # Chart
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True,
                            config={"displaylogo": False})

        st.markdown('<div style="margin-bottom:16px"></div>',
                    unsafe_allow_html=True)

    # --- Clear chat ---
    if st.session_state.get("chat_history"):
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state["chat_history"] = []
            st.rerun()
