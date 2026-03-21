import json
import math

import pandas as pd
from langchain_core.language_models import BaseChatModel

from src.tools.yahoo import get_price_history
from src.tools.indicators import calc_sma, calc_ema, calc_rsi, calc_macd, calc_volume_trend


def _safe_val(val) -> float | None:
    """Convert NaN/None to None, otherwise return float."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if pd.isna(val):
        return None
    return float(val)


def _fmt(val: float | None, decimals: int = 2) -> str:
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def run_technical_analysis(symbol: str, llm: BaseChatModel) -> dict:
    """Compute technical indicators and have Gemini interpret them."""
    df = get_price_history(symbol, period="6mo")

    if df.empty:
        return {
            "score": 5,
            "analysis": "No price data available for technical analysis.",
            "indicators": {},
        }

    close = df["Close"]
    volume = df["Volume"]

    sma_50 = calc_sma(close, 50)
    ema_20 = calc_ema(close, 20)
    rsi = calc_rsi(close, 14)
    macd = calc_macd(close)
    vol_trend = calc_volume_trend(volume)

    current_price = _safe_val(close.iloc[-1])
    sma_50_val = _safe_val(sma_50.iloc[-1]) if not sma_50.empty else None
    ema_20_val = _safe_val(ema_20.iloc[-1]) if not ema_20.empty else None
    rsi_val = _safe_val(rsi.iloc[-1]) if not rsi.empty else None
    macd_val = _safe_val(macd["macd_line"].iloc[-1]) if not macd["macd_line"].empty else None
    signal_val = _safe_val(macd["signal_line"].iloc[-1]) if not macd["signal_line"].empty else None
    histogram_val = _safe_val(macd["histogram"].iloc[-1]) if not macd["histogram"].empty else None

    price_change_1m = None
    if len(close) > 22:
        divisor = _safe_val(close.iloc[-22])
        if divisor and divisor != 0:
            price_change_1m = ((current_price / divisor) - 1) * 100

    price_change_3m = None
    if len(close) > 66:
        divisor = _safe_val(close.iloc[-66])
        if divisor and divisor != 0:
            price_change_3m = ((current_price / divisor) - 1) * 100

    price_vs_sma = "above" if (sma_50_val and current_price and current_price > sma_50_val) else "below"
    price_vs_ema = "above" if (ema_20_val and current_price and current_price > ema_20_val) else "below"

    indicators_text = (
        f"Stock: {symbol}\n"
        f"Current Price: {_fmt(current_price)}\n"
        f"SMA(50): {_fmt(sma_50_val)}\n"
        f"EMA(20): {_fmt(ema_20_val)}\n"
        f"RSI(14): {_fmt(rsi_val, 1)}\n"
        f"MACD Line: {_fmt(macd_val)}\n"
        f"Signal Line: {_fmt(signal_val)}\n"
        f"MACD Histogram: {_fmt(histogram_val)}\n"
        f"Volume Trend: {vol_trend}\n"
        f"1-Month Price Change: {_fmt(price_change_1m, 1)}%\n"
        f"3-Month Price Change: {_fmt(price_change_3m, 1)}%\n"
        f"Price vs SMA(50): {price_vs_sma}\n"
        f"Price vs EMA(20): {price_vs_ema}\n"
    )

    prompt = (
        "You are a technical stock analyst specializing in Indian equities.\n"
        "Analyze these technical indicators and provide your assessment.\n\n"
        f"{indicators_text}\n"
        "Consider:\n"
        "- RSI levels (below 30 = oversold, above 70 = overbought)\n"
        "- MACD signal (bullish when MACD crosses above signal line)\n"
        "- Price relative to moving averages (above = bullish trend)\n"
        "- Volume trend confirmation\n"
        "- Overall momentum direction\n\n"
        "Respond in valid JSON:\n"
        '{"score": <1-10>, "analysis": "<2-3 sentence assessment>"}\n'
        "Score guide: 1-3 bearish, 4-5 neutral/weak, 6-7 mildly bullish, 8-10 strongly bullish."
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

    result["indicators"] = {
        "current_price": current_price,
        "sma_50": round(sma_50_val, 2) if sma_50_val else None,
        "ema_20": round(ema_20_val, 2) if ema_20_val else None,
        "rsi": round(rsi_val, 1) if rsi_val else None,
        "macd": round(macd_val, 2) if macd_val else None,
        "macd_signal": round(signal_val, 2) if signal_val else None,
        "volume_trend": vol_trend,
        "price_change_1m": round(price_change_1m, 1) if price_change_1m else None,
        "price_change_3m": round(price_change_3m, 1) if price_change_3m else None,
    }
    return result
