# ✅ Revised MVP Checklist

-   1\. Manual IV Entry + IV/HV Comparison

<!-- -->

-   \- User manually enters IV (from broker, scanner, estimate).

-   \- System computes HV automatically.

-   \- Displays IV vs HV with interpretation (e.g., IV=55, HV20=42 → IV
    is 30% higher).

<!-- -->

-   2\. Chain/Spread Data for Liquidity & Structure

<!-- -->

-   \- Use yfinance to fetch bid/ask, open interest, volume.

-   \- Highlight liquidity and execution quality.

<!-- -->

-   3\. Risk-Based Option Position Sizing

<!-- -->

-   \- Contract-based sizing by risk %, not shares.

-   \- Output: maximum contracts allowed.

<!-- -->

-   4\. Trade Rationale & Journal Logging

<!-- -->

-   \- Snapshot at entry: symbol, strikes, HV/IV, tags, rationale, risk
    size.

-   \- Exit logging: P&L, exit date/time, trade duration.

<!-- -->

-   5\. Go/No-Go Precheck

<!-- -->

-   \- Flags outlier risks: low liquidity, extreme IV, unusual spreads,
    major events.

-   \- Guides user to do deeper analysis, not trade execution.

# ❌ What NOT to Include in MVP

-   \- Skew analysis (strike vs IV).

-   \- Term structure (contango/backwardation).

-   \- IV percentile or rank.

-   \- Historical IV surfaces.

-   ⚠ These require institutional-grade APIs (ORATS, Amberdata, etc.).

# 🔑 Bottom Line for MVP

-   \- Deliver automated HV, manual IV input, basic chain display,
    risk-based sizing, and journal logging.

-   \- Keep the UI clean and emphasize consistent data capture + IV/HV
    comparison.

-   \- Advanced analytics (skew, term structure, IV rank) can be
    deferred until robust options APIs are integrated.
