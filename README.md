# Market Analyst

Multi-agent Indian stock market analyst that produces Buy / Sell / Hold recommendations for Nifty 50 stocks by running fundamental, technical, and sentiment agents in parallel via LangGraph.

## Stack

- **Orchestration:** LangGraph (parallel agent execution)
- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **Market data:** yfinance
- **News / sentiment:** DuckDuckGo search, filtered to financial domains (Moneycontrol, ET, LiveMint, Reuters, Bloomberg, NDTV Profit)
- **API:** FastAPI
- **UI:** Streamlit (dark financial terminal theme)
- **State:** stateless, no database

## How it works

Three agents run in parallel for the selected ticker:

1. **Fundamental** - pulls financials via yfinance, reasons over ratios.
2. **Technical** - computes indicators (RSI, MACD, moving averages) on price history.
3. **Sentiment** - scrapes recent headlines from allowed financial domains, classifies tone.

Results are combined with a **40 / 30 / 30** weighting (fundamental / technical / sentiment) into a single recommendation.

## Project layout

```
src/
  agents/       fundamental.py, technical.py, sentiment.py
  graph/        graph.py, nodes.py, state.py      # LangGraph wiring
  tools/        yahoo.py, indicators.py, search.py
  api/          main.py, schemas.py               # FastAPI
  ui/           app.py                            # Streamlit
  config.py                                       # Nifty 50 list, model, domains
tests/
docs/superpowers/specs/                            # design spec
```

## Setup

Requires Python 3.11+.

```bash
pip install -e .
cp .env.example .env   # then set GROQ_API_KEY
```

## Run

**API:**
```bash
uvicorn src.api.main:app --reload
```

**UI:**
```bash
streamlit run src/ui/app.py
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Configuration

Edit `src/config.py` for the stock universe, LLM model, concurrency limit, and allowed news domains.

## Disclaimer

For research and educational use. Not investment advice.
