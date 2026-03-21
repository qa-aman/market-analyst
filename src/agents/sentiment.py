import json

from langchain_core.language_models import BaseChatModel

from src.tools.search import search_stock_news
from src.tools.yahoo import get_stock_info


def run_sentiment_analysis(
    symbol: str,
    company_name: str,
    llm: BaseChatModel,
) -> dict:
    """Search financial news and classify sentiment."""
    # Resolve company name from yfinance if generic
    if company_name == symbol.replace(".NS", ""):
        try:
            info = get_stock_info(symbol)
            company_name = info.get("name", company_name)
        except Exception:
            pass

    headlines = search_stock_news(company_name, max_results=8)

    if not headlines:
        return {
            "score": 5,
            "analysis": "No recent news found from financial sources.",
            "headlines": [],
        }

    headlines_text = "\n".join(
        f"- {h['title']}: {h['body'][:150]}" for h in headlines
    )

    prompt = (
        "You are a sentiment analyst specializing in Indian stock markets.\n"
        "Analyze these recent news headlines and assess the market sentiment.\n\n"
        f"Company: {company_name} ({symbol})\n\n"
        f"Recent headlines from financial sources:\n{headlines_text}\n\n"
        "For each headline, classify as bullish, bearish, or neutral.\n"
        "Then provide an overall sentiment assessment.\n\n"
        "Respond in valid JSON:\n"
        '{"score": <1-10>, "analysis": "<2-3 sentence sentiment summary>", '
        '"headline_sentiments": [{"title": "...", "sentiment": "bullish|bearish|neutral"}]}\n'
        "Score guide: 1-3 bearish, 4-5 neutral, 6-7 mildly bullish, 8-10 very bullish."
    )

    response = llm.invoke(prompt)
    content = response.content

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    try:
        result = json.loads(content.strip())
    except json.JSONDecodeError:
        result = {"score": 5, "analysis": f"Raw LLM response: {response.content[:200]}"}

    result["headlines"] = [h["title"] for h in headlines]
    return result
