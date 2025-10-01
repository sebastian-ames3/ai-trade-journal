import pytest
from src.data.fetchers import fetch_history, PriceRequest

def test_fetch_raises_for_bad_symbol(monkeypatch):
    # Use an unlikely symbol to trigger empty result
    with pytest.raises(Exception):
        fetch_history(PriceRequest(symbol="ZZZ_NOT_A_TICKER", period="5d", interval="1d"))
