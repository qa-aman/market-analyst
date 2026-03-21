import json

from langchain_core.language_models import BaseChatModel

from src.tools.yahoo import get_stock_info


def run_fundamental_analysis(symbol: str, llm: BaseChatModel) -> dict:
    """Fetch fundamental data and have Gemini interpret it."""
    info = get_stock_info(symbol)

    metrics_text = (
        f"Stock: {info['name']} ({symbol})\n"
        f"Sector: {info['sector']} | Industry: {info['industry']}\n"
        f"Current Price: {info['current_price']}\n"
        f"Market Cap: {info['market_cap']}\n"
        f"P/E Ratio (TTM): {info['pe_ratio']}\n"
        f"Forward P/E: {info['forward_pe']}\n"
        f"P/B Ratio: {info['pb_ratio']}\n"
        f"Dividend Yield: {info['dividend_yield']}\n"
        f"Debt-to-Equity: {info['debt_to_equity']}\n"
        f"Revenue Growth: {info['revenue_growth']}\n"
        f"Earnings Growth: {info['earnings_growth']}\n"
        f"Profit Margin: {info['profit_margin']}\n"
        f"ROE: {info['roe']}\n"
        f"Beta: {info['beta']}\n"
        f"52-Week High: {info['fifty_two_week_high']}\n"
        f"52-Week Low: {info['fifty_two_week_low']}\n"
    )

    prompt = (
        "You are a fundamental stock analyst specializing in Indian equities.\n"
        "Analyze these financial metrics and provide your assessment.\n\n"
        f"{metrics_text}\n"
        "Consider:\n"
        "- Whether valuation ratios are attractive relative to the sector\n"
        "- Growth trajectory (revenue and earnings)\n"
        "- Financial health (debt levels, profitability)\n"
        "- Dividend attractiveness\n\n"
        "Respond in valid JSON:\n"
        '{"score": <1-10>, "analysis": "<2-3 sentence assessment>"}\n'
        "Score guide: 1-3 weak, 4-5 below average, 6-7 good, 8-10 strong."
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

    result["metrics"] = info
    return result
