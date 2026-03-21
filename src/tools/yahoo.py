import yfinance as yf
import pandas as pd


def get_stock_info(symbol: str) -> dict:
    """Fetch fundamental data for a stock from Yahoo Finance."""
    ticker = yf.Ticker(symbol)
    info = ticker.info

    if not info or info.get("quoteType") is None:
        return {
            "symbol": symbol,
            "name": symbol,
            "error": f"No data found for {symbol}. Symbol may be invalid or delisted.",
        }

    return {
        "symbol": symbol,
        "name": info.get("longName", symbol),
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "dividend_yield": info.get("dividendYield"),
        "debt_to_equity": info.get("debtToEquity"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "profit_margin": info.get("profitMargins"),
        "roe": info.get("returnOnEquity"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "beta": info.get("beta"),
    }


def get_price_history(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch historical price data for technical analysis."""
    ticker = yf.Ticker(symbol)
    try:
        df = ticker.history(period=period)
    except Exception:
        df = pd.DataFrame()
    return df
