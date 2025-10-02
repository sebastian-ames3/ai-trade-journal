from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential
import yfinance as yf
import pandas as pd

@dataclass
class PriceRequest:
    symbol: str
    period: str = "1mo"
    interval: str = "1d"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def fetch_history(req: PriceRequest) -> pd.DataFrame:
    """Fetch OHLCV with simple retry/backoff for transient errors (e.g., 429)."""
    ticker = yf.Ticker(req.symbol)
    df = ticker.history(period=req.period, interval=req.interval)
    if df is None or df.empty:
        raise RuntimeError(f"No data for {req.symbol}")
    return df.reset_index()
