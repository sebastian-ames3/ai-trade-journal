# AI Trader / Journal

A disciplined trading journal with real-time market data, rate-limit-aware fetchers, and a production-minded Python layout.

## Stack

- **Python** 3.11+ (works on 3.10; prefer 3.11)
- **Streamlit** (UI)
- **SQLModel + SQLite** (storage)
- **yfinance** (market data; with retry/backoff)
- **pytest** (tests)
- **ruff + black + pre-commit** (lint/format)

### What is Streamlit?

This app is built with [**Streamlit**](https://streamlit.io/), a Python framework for creating interactive web apps directly from scripts.  
Instead of writing HTML, CSS, or JavaScript, you write standard Python and Streamlit renders a browser-based UI for you.

## Why this exists (MVP)

- **Capture trades quickly** (ticker, direction, size, thesis, tags).
- **Auto-enrich** with basic market context (price, HV/IV snapshots).
- **Browse & filter** past trades (search by tag/ticker/date).
- **Stay durable**: SQLite file DB (easy to ship), typed models, tests.

## Running the application

First install pyenv for managing python installs:

```bash
$ cd ./ai-trade-journal
$ pyenv install -s 3.11.10
$ pyenv local 3.11.10
```

It's best practice to use a python virtual environment:

```bash
# Create a project-local virtualenv
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create your env file
cp .env.example .env
```

After installing dependencies and activating your virtual environment, run the app with:

```bash
streamlit run src/app.py
```

## Directory layout (current & planned)

```bash
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
```
