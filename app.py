import streamlit as st
from src.settings import Settings
from src.ui.components import header, journal_sidebar, data_section, journal_section
from src.journal.storage import init_db
init_db()  # safe; it’s guarded


def main():
    st.set_page_config(page_title='AI Trader / Journal', layout='wide')
    header()

    settings = Settings.from_env()
    journal_sidebar()

    tab1, tab2 = st.tabs(["Data", "Journal"])
    with tab1:
        data_section(settings=settings)
    with tab2:
        journal_section()

if __name__ == "__main__":
    main()
