# src/data/vol.py
from __future__ import annotations

import numpy as np
import pandas as pd

def realized_vol(prices: pd.Series, window: int = 20) -> float:
    """
    Annualized realized volatility (decimal) using close-to-close log returns.
    Example return 0.25 => 25%.
    """
    s = pd.Series(prices, dtype="float64").dropna()
    log_ret = np.log(s / s.shift(1)).dropna()
    if len(log_ret) < window:
        return float("nan")
    daily_std = log_ret.rolling(window).std().iloc[-1]
    return float(daily_std * np.sqrt(252)) if daily_std is not None else float("nan")

def compare_iv_hv(iv_decimal: float, hv_decimal: float) -> str:
    if pd.isna(hv_decimal):
        return "Not enough data to compute realized volatility."

    if hv_decimal <= 0:
        return f"IV ({iv_decimal:.2%}) vs HV (non-positive)."

    diff_pct = (iv_decimal - hv_decimal) / hv_decimal * 100.0
    if diff_pct > 20:
        return f"IV ({iv_decimal:.2%}) is {diff_pct:.1f}% higher than HV ({hv_decimal:.2%}). Options look expensive."
    elif diff_pct < -20:
        return f"IV ({iv_decimal:.2%}) is {abs(diff_pct):.1f}% lower than HV ({hv_decimal:.2%}). Options look cheap."
    else:
        return f"IV ({iv_decimal:.2%}) is close to HV ({hv_decimal:.2%}). Options appear fairly priced."
