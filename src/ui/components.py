import streamlit as st
from src.data.fetchers import fetch_history, PriceRequest

def header():
    st.title("AI Trader / Journal App")
    st.caption("Structured like a real product: tests, retries, and change control.")

def journal_sidebar():
    st.sidebar.header("Journal Filters")
    st.sidebar.text_input("Tag search", placeholder="#theta, #earnings")
    st.sidebar.date_input("Date range")  # TODO: wire up

def data_section(settings):
    st.subheader("Market Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        sym = st.text_input("Symbol", value="SPY")
    with col2:
        period = st.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)
    with col3:
        interval = st.selectbox("Interval", ["1d", "1h", "30m", "15m"], index=0)

    if st.button("Fetch"):
        try:
            df = fetch_history(PriceRequest(symbol=sym, period=period, interval=interval))
            st.dataframe(df.tail(30))
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
