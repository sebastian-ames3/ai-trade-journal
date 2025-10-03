import streamlit as st
import numpy as np
from typing import List
from datetime import date

from src.data.fetchers import fetch_history, PriceRequest
from src.journal.storage import create_entry, list_entries, update_entry, init_db, close_entry, delete_entry, list_entries_by_status
from src.data.vol import realized_vol, compare_iv_hv
from src.journal.models import JournalEntry


def header():
    st.title("AI Trader / Journal App")
    st.caption("Structured like a real product: tests, retries, and change control.")

def journal_sidebar():
    st.sidebar.header("Journal Filters")
    st.sidebar.text_input("Tag search", key="tag_search", placeholder="#theta, #earnings")
    st.sidebar.date_input("Date range")  # (MVP placeholder)

def data_section(settings):
    import streamlit as st
    from src.data.fetchers import fetch_history, PriceRequest

    st.subheader("Market Data")

    # --- Top controls (existing) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        sym = st.text_input("Symbol", value=st.session_state.get("data_symbol", "SPY"), key="data_symbol")
    with col2:
        period = st.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="data_period")
    with col3:
        interval = st.selectbox("Interval", ["1d", "1h", "30m", "15m"], index=0, key="data_interval")

    if st.button("Fetch", key="data_fetch"):
        try:
            df = fetch_history(PriceRequest(symbol=sym, period=period, interval=interval))
            st.dataframe(df.tail(30))
            st.session_state["last_df"] = df  # optional cache
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

    st.markdown("---")

    # ================== Volatility Context lives on DATA tab ==================
    st.markdown("### Volatility Context")
    c0, c1, c2, c3 = st.columns([1, 1, 1, 1])
    with c0:
        vol_symbol = st.text_input("Symbol (for vol)", value=sym, key="data_vol_symbol")
    with c1:
        iv_decimal = st.number_input("Current IV (decimal, e.g., 0.55)", min_value=0.0, max_value=5.0, step=0.01, format="%.2f", key="data_iv_decimal")
    with c2:
        hv_window = st.selectbox("HV window", [10, 20, 30], index=1, key="data_hv_window")
    with c3:
        compute_now = st.button("Compute IV vs HV", key="data_compute_iv_hv")

    if compute_now and vol_symbol.strip():
        try:
            # Ensure we have daily data for HV calculation
            df = fetch_history(PriceRequest(symbol=vol_symbol.strip(), period="6mo", interval="1d"))
            # realized_vol expects a price series (Close); use the helper in vol.py
            # Convert returned %/decimal appropriately: we want HV as DECIMAL here (e.g., 0.42)
            # Our realized_vol returns decimal (0.25 = 25%)
            hv_dec = realized_vol(df["Close"], window=int(hv_window))
            iv_dec = float(iv_decimal)

            if np.isnan(hv_dec):
                st.error("Not enough price data to compute HV. Try a longer period or different symbol.")
            else:
                # Display as percentages for humans
                colA, colB, colC = st.columns(3)
                colA.metric("IV (user)", f"{iv_dec:.1%}")
                colB.metric(f"HV{hv_window}", f"{hv_dec:.1%}")
                # difference in percentage points (IV% - HV%)
                diff_pp = (iv_dec - hv_dec) * 100.0
                colC.metric("IV − HV", f"{diff_pp:+.1f} pp")

                # Text interpretation
                msg = compare_iv_hv(iv_dec, hv_dec)
                # Color hint
                if "expensive" in msg.lower():
                    st.warning(msg)
                elif "cheap" in msg.lower():
                    st.success(msg)
                else:
                    st.info(msg)

                # Persist for Journal tab to consume (no recompute there)
                st.session_state["iv_user_decimal"] = iv_dec
                st.session_state["hv_decimal"] = hv_dec
                st.session_state["hv_window_last"] = int(hv_window)
                st.session_state["vol_symbol_last"] = vol_symbol.strip()

        except Exception as e:
            st.error(f"Failed to compute volatility context: {e}")


def journal_section():
    st.subheader("Journal")
    init_db()

     # ───────────────────────────── Add Entry (only reads vol from session) ─────────────────────────────
    with st.expander("Add entry", expanded=True):
         
            # Row 1: symbol + entry_action + strategy
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            symbol = st.text_input("Symbol", value="", key="journal_symbol")
        with c2:
             entry_action = st.radio(
                "Open action",
                options=["BTO", "STO"],
                index=0,  # default BTO
                help="BTO=Buy to open (debit). STO=Sell to open (credit).",
                horizontal=True,
            )
        with c3:
            strategy = st.text_input("Strategy", value="", key="journal_strategy")
        
            # Row 2: entry date + price + contracts
        c4, c5, c6 = st.columns([2, 2, 2])
        with c4:
            entry_date = st.date_input("Entry date", value=date.today())
        with c5:
            entry_price = st.number_input("Entry price (option premium)", min_value=0.0, step=0.01)
        with c6:
            size = st.number_input("Contracts", min_value=1, step=1, value=1)

             # Notes
        notes = st.text_area("Notes", placeholder="Why this trade? Plan? Risk?", key="journal_notes")
           # Metadata row: tags + direction (moved down here)
        c7, c8 = st.columns([2, 2])
        with c7:
            tags_csv = st.text_input("Tags (comma-separated)", placeholder="#theta, #earnings")
        with c8:
            direction = st.selectbox(
                "Direction (metadata)",
                options=["neutral", "long", "short"],
                index=0,
                help="Just metadata for filtering; not used in P&L.",
            )

        # Build a one-line context if the DATA tab computed it
        vol_line = None
        iv_dec = st.session_state.get("iv_user_decimal")
        hv_dec = st.session_state.get("hv_decimal")
        hv_win = st.session_state.get("hv_window_last")
        if iv_dec is not None and hv_dec is not None and hv_win:
            try:
                diff_pp = (iv_dec - hv_dec) * 100.0
                ratio_pct = ((iv_dec / hv_dec) - 1.0) * 100.0 if hv_dec > 0 else float("inf")
                vol_line = (
                    f"[vol] IV(user)={iv_dec:.1%} | HV{hv_win}={hv_dec:.1%} | "
                    f"Δ={diff_pp:+.1f}pp ({ratio_pct:+.0f}%)"
                )
            except Exception:
                vol_line = None

        
        
        if st.button("Save entry", type="primary", key="journal_save"):
            # Normalize tags into a clean CSV string (no spaces, no empties)
            tags_norm = ",".join([t.strip() for t in (tags_csv or "").split(",") if t.strip()])

            # Auto-embed the context line above the user's notes
            final_notes = f"{vol_line}\n{notes}" if vol_line else notes

        try:
            entry = create_entry(
                symbol=symbol,
                strategy=strategy,
                entry_action=entry_action,   # "BTO" or "STO"
                entry_date=entry_date,
                entry_price=entry_price,
                size=size,
                direction=direction,
                notes=final_notes,
                tags_csv=tags_norm,
            )
            st.success(f"Saved entry #{entry.id}")
        except Exception as e:
            st.error(f"Failed to save entry: {e}")

    st.markdown("---")
    tag_filter = st.session_state.get("tag_search") or None
    entries = list_entries(tag=tag_filter)
    if not entries:
        st.info("No entries yet.")
    else:
        for entry in entries:
            with st.container(border=True):
                st.markdown(f"**#{entry.id}** {entry.symbol}  *{entry.direction}*  ({entry.strategy})")
                st.caption(f"Created: {entry.created_at}   •   Updated: {entry.updated_at}")
                if entry.tags_csv:
                    st.write("Tags:", entry.tags_csv)
                if entry.notes:
                    st.write(entry.notes)

    st.subheader("Open trades")

    open_entries = list_entries_by_status("open")
    if not open_entries:
        st.info("No open trades.")
    else:
        for entry in open_entries:
            header = f"#{entry.id} {entry.symbol} {entry.entry_action} @ {entry.entry_price} (contracts {entry.size})"
            with st.expander(header):
                col1, col2, col3 = st.columns(3)
                with col1:
                    exit_price = st.number_input(
                        f"Exit price (#{entry.id})",
                        min_value=0.0,
                        value=float(entry.entry_price),
                        step=0.01,
                    )
                with col2:
                    exit_dt = st.date_input(f"Exit date (#{entry.id})", value=date.today())
                with col3:
                    if st.button(f"Mark closed (#{entry.id})"):
                        close_entry(entry.id, exit_price=exit_price, exit_date=exit_dt)
                        st.success("Closed. Reload the page to refresh lists.")

                if st.button(f"Delete trade (#{entry.id})", type="secondary"):
                    delete_entry(entry.id)
                    st.warning("Deleted. Reload to refresh.")

    st.subheader("Closed trades & stats")
    closed_entries = list_entries_by_status("closed")

    if not closed_entries:
        st.info("No closed trades yet.")
    else:
        # table
        rows = []
        wins = 0
        total_pl = 0.0
        for entry in closed_entries:
            pl = entry.realized_pl or 0.0
            total_pl += pl
            if pl > 0:
                wins += 1
            rows.append({
                "id": entry.id,
                "symbol": entry.symbol,
                "action": entry.entry_action,     # BTO/STO
                "direction": entry.direction,     # metadata
                "entry": entry.entry_price,
                "exit": entry.exit_price,
                "contracts": entry.size,
                "P&L": pl,
                "R": entry.r_multiple,
                "days": entry.holding_days,
                "tags": entry.tags_csv,
        })
        st.dataframe(rows, use_container_width=True)

        # quick KPIs
        win_rate = round(100 * wins / len(closed_entries), 1)
        st.metric("Closed trades", len(closed_entries))
        st.metric("Win rate", f"{win_rate}%")
        st.metric("Realized P&L", f"{round(total_pl, 2)}")
