from langgraph.types import Send

from src.graph.state import MarketAnalystState
from src.agents.fundamental import run_fundamental_analysis
from src.agents.technical import run_technical_analysis
from src.agents.sentiment import run_sentiment_analysis
from src.config import SYMBOL_TO_NAME, get_groq_api_key, LLM_MODEL
from langchain_groq import ChatGroq


_llm = None


def get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=LLM_MODEL,
            api_key=get_groq_api_key(),
        )
    return _llm


def fan_out_agents(state: MarketAnalystState) -> list[Send]:
    """Fan out to all three agent types for each symbol."""
    sends = []
    for symbol in state["symbols"]:
        sends.append(Send("fundamental_agent", {"symbol": symbol, "agent_type": "fundamental"}))
        sends.append(Send("technical_agent", {"symbol": symbol, "agent_type": "technical"}))
        sends.append(Send("sentiment_agent", {"symbol": symbol, "agent_type": "sentiment"}))
    return sends


def orchestrator_node(state: MarketAnalystState) -> dict:
    """Entry node - validates symbols and prepares state.

    Symbols and query_type are already set by the API layer.
    This node just passes through to fan-out.
    """
    return {}


def fundamental_agent_node(state: dict) -> dict:
    """Run fundamental analysis for a single symbol."""
    symbol = state["symbol"]
    try:
        result = run_fundamental_analysis(symbol, get_llm())
        return {"fundamental_results": {symbol: result}}
    except Exception as e:
        return {"errors": {f"fundamental_{symbol}": str(e)}}


def technical_agent_node(state: dict) -> dict:
    """Run technical analysis for a single symbol."""
    symbol = state["symbol"]
    try:
        result = run_technical_analysis(symbol, get_llm())
        return {"technical_results": {symbol: result}}
    except Exception as e:
        return {"errors": {f"technical_{symbol}": str(e)}}


def sentiment_agent_node(state: dict) -> dict:
    """Run sentiment analysis for a single symbol."""
    symbol = state["symbol"]
    company_name = SYMBOL_TO_NAME.get(symbol, symbol.replace(".NS", ""))
    try:
        result = run_sentiment_analysis(symbol, company_name, get_llm())
        return {"sentiment_results": {symbol: result}}
    except Exception as e:
        return {"errors": {f"sentiment_{symbol}": str(e)}}


def compile_node(state: MarketAnalystState) -> dict:
    """Synthesize all agent results into final recommendation."""
    symbols = state["symbols"]
    query_type = state["query_type"]
    fundamental = state.get("fundamental_results", {})
    technical = state.get("technical_results", {})
    sentiment = state.get("sentiment_results", {})
    errors = state.get("errors", {})

    per_stock_summary = []
    for symbol in symbols:
        fund = fundamental.get(symbol, {})
        tech = technical.get(symbol, {})
        sent = sentiment.get(symbol, {})
        name = SYMBOL_TO_NAME.get(symbol, symbol)

        per_stock_summary.append(
            f"Stock: {name} ({symbol})\n"
            f"  Fundamental (score {fund.get('score', 'N/A')}/10): {fund.get('analysis', 'unavailable')}\n"
            f"  Technical (score {tech.get('score', 'N/A')}/10): {tech.get('analysis', 'unavailable')}\n"
            f"  Sentiment (score {sent.get('score', 'N/A')}/10): {sent.get('analysis', 'unavailable')}\n"
        )

    error_note = ""
    if errors:
        error_note = f"\nNote: some analyses failed: {errors}\nAdjust confidence accordingly."

    if query_type == "compare":
        prompt = (
            "You are a senior stock market analyst. Compare these stocks and recommend which to buy.\n\n"
            + "\n".join(per_stock_summary)
            + error_note
            + "\n\nFor each stock provide:\n"
            "1. recommendation: BUY, SELL, or HOLD\n"
            "2. confidence: 0-100\n"
            "3. reasoning: 2-3 sentences\n\n"
            "Then provide a comparison with:\n"
            "- winner: which stock symbol is better to buy now\n"
            "- reasoning: why\n"
            "- key_differences: list of 3-5 specific metric comparisons\n\n"
            "Weighting: fundamentals 40%, technicals 30%, sentiment 30%.\n"
            "Respond in valid JSON with this structure:\n"
            '{"results": {"SYMBOL": {"recommendation": "BUY", "confidence": 72, "reasoning": "..."}}, '
            '"comparison": {"winner": "SYMBOL", "reasoning": "...", "key_differences": ["..."]}}'
        )
    elif query_type == "multi":
        prompt = (
            "You are a senior stock market analyst. Analyze this group of stocks.\n\n"
            + "\n".join(per_stock_summary)
            + error_note
            + "\n\nFor each stock provide:\n"
            "1. recommendation: BUY, SELL, or HOLD\n"
            "2. confidence: 0-100\n"
            "3. reasoning: 2-3 sentences\n\n"
            "Then provide an overall summary with:\n"
            "- strong_picks: list of symbols rated BUY\n"
            "- concerns: list of symbols rated SELL or with low confidence\n"
            "- overview: 2-3 sentence summary of the group\n\n"
            "Weighting: fundamentals 40%, technicals 30%, sentiment 30%.\n"
            "Respond in valid JSON with this structure:\n"
            '{"results": {"SYMBOL": {"recommendation": "BUY", "confidence": 72, "reasoning": "..."}}, '
            '"summary": {"strong_picks": ["..."], "concerns": ["..."], "overview": "..."}}'
        )
    else:
        prompt = (
            "You are a senior stock market analyst. Provide your analysis.\n\n"
            + "\n".join(per_stock_summary)
            + error_note
            + "\n\nProvide:\n"
            "1. recommendation: BUY, SELL, or HOLD\n"
            "2. confidence: 0-100\n"
            "3. reasoning: 2-3 sentences\n\n"
            "Weighting: fundamentals 40%, technicals 30%, sentiment 30%.\n"
            "Respond in valid JSON with this structure:\n"
            '{"results": {"SYMBOL": {"recommendation": "BUY", "confidence": 72, "reasoning": "..."}}}'
        )

    import json
    response = get_llm().invoke(prompt)
    content = response.content

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    try:
        compiled = json.loads(content.strip())
    except json.JSONDecodeError:
        compiled = {
            "results": {
                s: {"recommendation": "HOLD", "confidence": 50, "reasoning": "Unable to parse LLM response"}
                for s in symbols
            }
        }

    # Merge agent details into results
    for symbol in symbols:
        if symbol in compiled.get("results", {}):
            compiled["results"][symbol]["fundamental"] = fundamental.get(symbol, {})
            compiled["results"][symbol]["technical"] = technical.get(symbol, {})
            compiled["results"][symbol]["sentiment"] = sentiment.get(symbol, {})

    report = {
        "symbols": symbols,
        "query_type": query_type,
        **compiled,
    }

    if errors:
        report["errors"] = errors

    return {"report": report}
