# AI Trader / Journal

A disciplined trading journal with real-time market data, rate-limit-aware fetchers, and a production-minded Python layout.

---

## Why this exists (MVP)
- **Capture trades quickly** (ticker, direction, size, thesis, tags).
- **Auto-enrich** with basic market context (price, HV/IV snapshots).
- **Browse & filter** past trades (search by tag/ticker/date).
- **Stay durable**: SQLite file DB (easy to ship), typed models, tests.

> MVP rule: “working > perfect.” We’ll polish UX after the core flow (create → auto-enrich → view/search) is solid.

---
## Running the App

After installing dependencies and activating your virtual environment, run the app with:

```bash
streamlit run src/app.py


## Stack
- **Python** 3.11+ (works on 3.10; prefer 3.11)
- **Streamlit** (UI)
- **SQLModel + SQLite** (storage)
- **yfinance** (market data; with retry/backoff)
- **pytest** (tests)
- **ruff + black + pre-commit** (lint/format)

---

## Directory layout (current & planned)
ai-trade-journal/
├─ app.py # Streamlit entry (MVP)
├─ requirements.txt
├─ src/ # (in-progress) production layout
│ ├─ data/ # fetchers, retry/backoff
│ ├─ journal/ # models, storage
│ ├─ ui/ # components
│ └─ settings.py
├─ tests/
│ ├─ test_fetchers.py
│ └─ test_journal.py
├─ .github/ISSUE_TEMPLATE/ # bug/feature templates
├─ CHANGELOG.md
└─ README.md