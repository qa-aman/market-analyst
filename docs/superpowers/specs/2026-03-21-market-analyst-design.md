# Market Analyst - Multi-Agent Stock Analysis System

## Context

Build an AI-powered Indian stock market analyst that answers three types of queries:
1. Single stock analysis ("How is Reliance doing?")
2. Multi-stock analysis ("Analyze Tata Motors, Mahindra, Infosys together") - user selects multiple stocks from a dropdown, no persistent portfolio storage.
3. Stock comparison ("Compare Tata Motors vs Mahindra, which should I buy?")

The system uses a multi-agent architecture where specialized analyst agents run in parallel and a master node compiles their results into a Buy/Sell/Hold recommendation with confidence scoring.

## Tech Stack

| Component | Choice |
|-----------|--------|
| LLM | Google Gemini API |
| Orchestration | LangGraph (Python) |
| Market data | yfinance (Yahoo Finance) |
| Web search | duckduckgo-search |
| Storage | None (stateless) |
| UI | Streamlit |
| Backend | FastAPI |
| Package manager | uv / pip |

## Architecture

Single-process embedded architecture. LangGraph StateGraph runs inside the FastAPI process. Streamlit calls FastAPI via HTTP. No job queue, no worker process, no streaming.

```
Streamlit UI (port 8501)
    |  HTTP
    v
FastAPI (port 8000)
    |  graph.ainvoke()
    v
LangGraph StateGraph (in-process)
    |
    +-- orchestrator_node (Gemini: parse query -> symbols + type)
    |       |
    |       | Send() fan-out (parallel)
    |       +---> fundamental_agent
    |       +---> technical_agent
    |       +---> sentiment_agent
    |       |
    |       v  (merge via Annotated reducers)
    +-- compile_node (Gemini: synthesize -> Buy/Sell/Hold)
    |
    v
JSON response
```

### Graph Topology

```python
graph = StateGraph(MarketAnalystState)

# Register nodes
graph.add_node("orchestrator_node", orchestrator_fn)
graph.add_node("fundamental_agent", fundamental_fn)
graph.add_node("technical_agent", technical_fn)
graph.add_node("sentiment_agent", sentiment_fn)
graph.add_node("compile_node", compile_fn)

# Edges
graph.add_edge(START, "orchestrator_node")
graph.add_conditional_edges(
    "orchestrator_node",
    fan_out_agents,  # returns list of Send() objects
    ["fundamental_agent", "technical_agent", "sentiment_agent"]
)
graph.add_edge("fundamental_agent", "compile_node")
graph.add_edge("technical_agent", "compile_node")
graph.add_edge("sentiment_agent", "compile_node")
graph.add_edge("compile_node", END)

app = graph.compile()
```

The `fan_out_agents` function returns a list of `Send()` objects - one per agent per symbol. For a single stock, 3 Send() calls. For a portfolio with 5 stocks, 15 Send() calls. LangGraph waits for all Send() targets to complete before routing to `compile_node`.

### Parallel Execution

`max_concurrency` is set to 9 at graph compile time as a rate-limit ceiling to stay within yfinance and DuckDuckGo throttling limits. This is independent of portfolio size - a 10-stock portfolio emits 30 Send() calls, but only 9 execute concurrently.

### Error Handling

Each agent wraps its logic in try/except. On failure, it writes to `state["errors"][f"{agent}_{symbol}"]` and returns partial state. The compile node checks errors and either degrades gracefully ("sentiment unavailable - based on fundamental and technical only") or adjusts confidence downward.

## State Schema

```python
class MarketAnalystState(TypedDict):
    # Input
    query: str                                     # Raw user query
    symbols: list[str]                             # ["RELIANCE.NS", "TATAMOTORS.NS"]
    query_type: str                                # "single" | "multi" | "compare"

    # Agent outputs (Annotated reducers merge parallel writes)
    # Each agent writes {symbol: data}, reducer merges by dict union
    fundamental_results: Annotated[dict, merge]    # {symbol: {pe, pb, revenue_growth, ...}}
    technical_results: Annotated[dict, merge]       # {symbol: {rsi, macd, sma_50, ...}}
    sentiment_results: Annotated[dict, merge]       # {symbol: {score, headlines, summary}}

    # Error tracking
    errors: Annotated[dict, merge]                  # {agent_symbol: error_msg}

# Reducer definition:
# def merge(existing: dict, new: dict) -> dict:
#     return {**existing, **new}
# Each agent writes to a unique symbol key, so no cross-agent key collisions.

    # Final output
    report: dict                                    # Compiled analysis + recommendation
```

## Agents

### Fundamental Analyst
- **Input**: Stock symbol
- **Data source**: `yfinance.Ticker(symbol).info`
- **Metrics**: P/E ratio, P/B ratio, market cap, revenue growth, debt-to-equity, dividend yield
- **LLM step**: Gemini interprets ratios, compares to sector context
- **Output**: Score (1-10) + analysis text per symbol

### Technical Analyst
- **Input**: Stock symbol
- **Data source**: `yfinance.Ticker(symbol).history(period="6mo")`
- **Indicators**: SMA(50), EMA(20), RSI(14), MACD (12,26,9), volume trend
- **LLM step**: Gemini interprets signals (oversold, trend reversal, momentum)
- **Output**: Score (1-10) + signal summary per symbol

### Sentiment Analyst
- **Input**: Stock symbol + company name (company name resolved via `yfinance.Ticker(symbol).info["longName"]` if not provided)
- **Data source**: DuckDuckGo search filtered to financial domains (Moneycontrol, Economic Times, LiveMint, Reuters, Bloomberg, NDTV Profit)
- **Process**: Top 5-8 headlines + snippets from filtered results, Gemini classifies each as bullish/bearish/neutral
- **Output**: Score (1-10) + sentiment summary + key headlines per symbol

### Compile Node (Master)
- **Input**: All three agent results + errors dict
- **Process**: Gemini synthesizes scores, weighs fundamentals (40%), technicals (30%), sentiment (30%)
- **Output per stock**: Buy/Sell/Hold recommendation, confidence (0-100%), 2-3 sentence reasoning
- **Multi-stock mode**: Per-stock verdicts + overall group summary
- **Compare mode**: Per-stock verdicts + head-to-head comparison + "which to buy" recommendation

## Project Structure

```
market-analyst/
├── pyproject.toml
├── .env.example                # GEMINI_API_KEY
├── src/
│   ├── graph/
│   │   ├── state.py            # MarketAnalystState TypedDict
│   │   ├── graph.py            # StateGraph build + compile
│   │   └── nodes.py            # orchestrator + compile nodes
│   ├── agents/
│   │   ├── fundamental.py      # yfinance fundamentals + Gemini
│   │   ├── technical.py        # price history + indicators + Gemini
│   │   └── sentiment.py        # DuckDuckGo + Gemini classify
│   ├── tools/
│   │   ├── yahoo.py            # yfinance wrapper (get_info, get_history)
│   │   ├── search.py           # DuckDuckGo wrapper
│   │   └── indicators.py       # SMA, EMA, RSI, MACD pure math
│   ├── api/
│   │   ├── main.py             # FastAPI app + routes
│   │   └── schemas.py          # Pydantic request/response models
│   ├── ui/
│   │   └── app.py              # Streamlit entrypoint
│   └── config.py               # Settings + STOCK_LIST (Nifty 50)
└── tests/
    ├── test_agents.py
    ├── test_graph.py
    └── test_api.py
```

## API Endpoints

- `POST /analyze` - Analyze one or more stocks. Body: `{"symbols": ["RELIANCE.NS"], "query_type": "single"}`. Also handles multi-stock: `{"symbols": ["RELIANCE.NS", "INFY.NS", "TATAMOTORS.NS"], "query_type": "multi"}`.
- `POST /compare` - Compare two stocks. Body: `{"symbols": ["TATAMOTORS.NS", "M&M.NS"]}`. Returns side-by-side analysis with winner.
- `GET /stocks` - Returns predefined stock list (Nifty 50 components) for UI dropdowns.

### Response Shapes

**Single stock** (`POST /analyze`):
```json
{
  "symbols": ["RELIANCE.NS"],
  "query_type": "single",
  "results": {
    "RELIANCE.NS": {
      "fundamental": {"score": 7, "analysis": "..."},
      "technical": {"score": 6, "analysis": "..."},
      "sentiment": {"score": 8, "analysis": "..."},
      "recommendation": "BUY",
      "confidence": 72,
      "reasoning": "Strong fundamentals with improving sentiment..."
    }
  }
}
```

**Multi-stock** (`POST /analyze` with query_type "multi"):
```json
{
  "symbols": ["RELIANCE.NS", "TATAMOTORS.NS", "INFY.NS"],
  "query_type": "multi",
  "results": {
    "RELIANCE.NS": { "fundamental": {...}, "technical": {...}, "sentiment": {...}, "recommendation": "BUY", "confidence": 72, "reasoning": "..." },
    "TATAMOTORS.NS": { "...same shape..." },
    "INFY.NS": { "...same shape..." }
  },
  "summary": {
    "strong_picks": ["RELIANCE.NS"],
    "concerns": ["TATAMOTORS.NS"],
    "overview": "2 of 3 stocks rated Buy. Reliance strongest on fundamentals..."
  }
}
```

**Compare** (`POST /compare`):
```json
{
  "symbols": ["TATAMOTORS.NS", "M&M.NS"],
  "query_type": "compare",
  "results": {
    "TATAMOTORS.NS": { "...same per-stock shape..." },
    "M&M.NS": { "...same per-stock shape..." }
  },
  "comparison": {
    "winner": "M&M.NS",
    "reasoning": "M&M shows stronger fundamentals and better momentum...",
    "key_differences": ["P/E: TATAMOTORS 18.2 vs M&M 22.5", "RSI: TATAMOTORS 42 vs M&M 58"]
  }
}
```

## Stock List

A predefined list of popular Indian stocks (Nifty 50 components) is stored in `src/config.py` as `STOCK_LIST`. Each entry has: symbol (e.g., "RELIANCE.NS"), display name (e.g., "Reliance Industries"), and sector. This populates the UI dropdowns.

## Streamlit UI

Three pages mapping to the three query types:

1. **Stock Analysis** - Single stock dropdown selector from predefined list, analyze button, results as 3 cards (fundamental/technical/sentiment) with scores, large Buy/Sell/Hold badge, confidence meter, reasoning text.

2. **Multi-Stock Analysis** - Multi-select dropdown from predefined list, "Analyze All" button, per-stock score cards + overall group summary.

3. **Compare Stocks** - Two stock dropdown selectors from predefined list, side-by-side result cards, comparison table, "which should I buy" verdict.

## Key Dependencies

```
langgraph
langchain-google-genai
yfinance
duckduckgo-search
fastapi
uvicorn
streamlit
pydantic
```

## Indian Stock Symbol Convention

Yahoo Finance uses `.NS` suffix for NSE-listed stocks (e.g., `RELIANCE.NS`, `TATAMOTORS.NS`, `INFY.NS`). The orchestrator node handles mapping common names to Yahoo Finance symbols using Gemini.
