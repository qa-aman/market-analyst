import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import AnalyzeRequest, CompareRequest, StockInfo, StockListResponse
from src.graph.graph import app as graph_app
from src.config import STOCK_LIST

logger = logging.getLogger(__name__)

api = FastAPI(title="Market Analyst API", version="0.1.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_graph(initial_state: dict) -> dict:
    """Run the LangGraph and handle errors gracefully."""
    try:
        result = graph_app.invoke(initial_state)
        return result.get("report", {})
    except Exception as e:
        error_msg = str(e)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "rate_limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="LLM API rate limit exceeded. Please wait a minute and try again.",
            )
        logger.exception("Graph execution failed")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error_msg[:200]}",
        )


@api.get("/stocks", response_model=StockListResponse)
def list_stocks():
    """Return predefined stock list for UI dropdowns."""
    return StockListResponse(
        stocks=[StockInfo(**s) for s in STOCK_LIST]
    )


@api.post("/analyze")
def analyze(request: AnalyzeRequest):
    """Analyze one or more stocks."""
    if not request.symbols:
        raise HTTPException(status_code=400, detail="At least one symbol is required")

    query_type = request.query_type
    if len(request.symbols) > 1 and query_type == "single":
        query_type = "multi"

    initial_state = {
        "symbols": request.symbols,
        "query_type": query_type,
        "fundamental_results": {},
        "technical_results": {},
        "sentiment_results": {},
        "errors": {},
        "report": {},
    }

    return _run_graph(initial_state)


@api.post("/compare")
def compare(request: CompareRequest):
    """Compare two stocks side by side."""
    if len(request.symbols) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 symbols required for comparison")

    initial_state = {
        "symbols": request.symbols,
        "query_type": "compare",
        "fundamental_results": {},
        "technical_results": {},
        "sentiment_results": {},
        "errors": {},
        "report": {},
    }

    return _run_graph(initial_state)


@api.get("/health")
def health():
    return {"status": "ok"}
