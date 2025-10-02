import streamlit as st
from typing import List

from src.data.fetchers import fetch_history, PriceRequest
from src.journal.storage import create_entry, list_entries, update_entry, init_db

def header():
    st.title("AI Trader / Journal App")
    st.caption("Structured like a real product: tests, retries, and change control.")

def journal_sidebar():
    st.sidebar.header("Journal Filters")
    st.sidebar.text_input("Tag search", key="tag_search", placeholder="#theta, #earnings")
    st.sidebar.date_input("Date range")  # (MVP placeholder)

def data_section(settings):
    st.subheader("Market Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        sym = st.text_input("Symbol", value="SPY", key="data_symbol")
    with col2:
        period = st.selectbox("Period",
                              ["5d", "1mo", "3mo", "6mo", "1y"],
                              index=1, key="data_period")
    with col3:
        interval = st.selectbox("Interval",
                                ["1d", "1h", "30m", "15m"],
                                index=0, key="data_interval")

    if st.button("Fetch", key="data_fetch"):
        try:
            df = fetch_history(PriceRequest(symbol=sym, period=period, interval=interval))
            st.dataframe(df.tail(30))
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

def journal_section():
    st.subheader("Journal")
    init_db()

    with st.expander("Add entry", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            symbol = st.text_input("Symbol", value="SPY", key="journal_symbol")
        with c2:
            direction = st.selectbox("Direction",
                                     ["long", "short", "neutral"],
                                     index=0, key="journal_direction")
        with c3:
            strategy = st.text_input("Strategy", value="CSP", key="journal_strategy")  # credit put spread
        notes = st.text_area("Notes", placeholder="Why this trade? Plan? Risk?", key="journal_notes")
        tags_raw = st.text_input("Tags (comma-separated)", placeholder="#theta, #earnings", key="journal_tags")

        if st.button("Save entry", type="primary", key="journal_save"):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            try:
                entry = create_entry(symbol=symbol, direction=direction, strategy=strategy, notes=notes, tags=tags)
                st.success(f"Saved entry #{entry.id}")
            except Exception as e:
                st.error(f"Failed to save entry: {e}")

    st.markdown("---")
    tag_filter = st.session_state.get("tag_search") or None
    rows = list_entries(tag=tag_filter)
    if not rows:
        st.info("No entries yet.")
        return

    for e in rows:
        with st.container(border=True):
            st.markdown(f"**#{e.id}** · {e.symbol} · *{e.direction}* · {e.strategy}  ")
            st.caption(f"Created: {e.created_at} · Updated: {e.updated_at}")
            if e.tags:
                st.write("Tags:", ", ".join(e.tags))
            if e.notes:
                st.write(e.notes)
