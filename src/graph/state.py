from typing import Any
from typing_extensions import TypedDict, Annotated


def merge_dicts(existing: dict, new: dict) -> dict:
    """Reducer that merges dicts by key union. Used for parallel agent writes."""
    if existing is None:
        existing = {}
    if new is None:
        return existing
    return {**existing, **new}


class AgentInput(TypedDict):
    """State passed to each individual agent via Send()."""
    symbol: str
    agent_type: str


class MarketAnalystState(TypedDict):
    # Input
    symbols: list[str]
    query_type: str  # "single" | "multi" | "compare"

    # Agent outputs - each keyed by symbol, merged via reducer
    fundamental_results: Annotated[dict[str, Any], merge_dicts]
    technical_results: Annotated[dict[str, Any], merge_dicts]
    sentiment_results: Annotated[dict[str, Any], merge_dicts]

    # Error tracking
    errors: Annotated[dict[str, str], merge_dicts]

    # Final output from compile node
    report: dict
