import os
import streamlit as st
from src.settings import Settings
from src.ui.components import header, journal_sidebar, data_section

def main():
    st.set_page_config(page_title='AI Trader / Journal', layout='wide')
    header()

    settings = Settings.from_env()
    journal_sidebar()

    tab1, tab2 = st.tabs(["Data", "Journal"])  # TODO: add journal UI
    with tab1:
        data_section(settings=settings)
    with tab2:
        st.info("Journal UI coming soon. Create/read/update entries with tags.")

if __name__ == "__main__":
    main()
