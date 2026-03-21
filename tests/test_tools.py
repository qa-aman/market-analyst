"""Tests for the tool layer - yahoo, indicators, and search."""
import pandas as pd
import pytest

from src.tools.indicators import calc_sma, calc_ema, calc_rsi, calc_macd, calc_volume_trend
from src.tools.yahoo import get_stock_info, get_price_history
from src.tools.search import search_stock_news


# --- Indicator tests (pure math, no external calls) ---

class TestSMA:
    def test_basic(self):
        prices = pd.Series([10, 20, 30, 40, 50])
        result = calc_sma(prices, 3)
        assert result.iloc[-1] == pytest.approx(40.0)

    def test_window_larger_than_data(self):
        prices = pd.Series([10, 20])
        result = calc_sma(prices, 5)
        assert pd.isna(result.iloc[-1])


class TestEMA:
    def test_basic(self):
        prices = pd.Series([10, 20, 30, 40, 50])
        result = calc_ema(prices, 3)
        assert result.iloc[-1] > 0
        assert not pd.isna(result.iloc[-1])


class TestRSI:
    def test_all_gains(self):
        prices = pd.Series(range(1, 20))
        result = calc_rsi(prices, 14)
        last = result.iloc[-1]
        assert last > 90  # all gains -> RSI near 100

    def test_all_losses(self):
        prices = pd.Series(range(20, 1, -1))
        result = calc_rsi(prices, 14)
        last = result.iloc[-1]
        assert last < 10  # all losses -> RSI near 0

    def test_mixed(self):
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115])
        result = calc_rsi(prices, 14)
        last = result.iloc[-1]
        assert 0 <= last <= 100


class TestMACD:
    def test_returns_three_series(self):
        prices = pd.Series(range(1, 50))
        result = calc_macd(prices)
        assert "macd_line" in result
        assert "signal_line" in result
        assert "histogram" in result
        assert len(result["macd_line"]) == len(prices)


class TestVolumeTrend:
    def test_stable(self):
        volume = pd.Series([100] * 30)
        assert calc_volume_trend(volume) == "stable"

    def test_increasing(self):
        volume = pd.Series([100] * 20 + [200] * 5)
        assert calc_volume_trend(volume) == "increasing"

    def test_decreasing(self):
        volume = pd.Series([200] * 20 + [50] * 5)
        assert calc_volume_trend(volume) == "decreasing"

    def test_insufficient_data(self):
        volume = pd.Series([100, 200])
        assert calc_volume_trend(volume, window=20) == "insufficient_data"


# --- Yahoo Finance tests (live API calls) ---

class TestYahooFinance:
    def test_get_stock_info_valid_symbol(self):
        info = get_stock_info("RELIANCE.NS")
        assert info["symbol"] == "RELIANCE.NS"
        assert "Reliance" in info.get("name", "")
        assert info.get("pe_ratio") is not None or info.get("current_price") is not None

    def test_get_stock_info_invalid_symbol(self):
        info = get_stock_info("INVALIDXYZ123.NS")
        # Should not crash, should return something
        assert info["symbol"] == "INVALIDXYZ123.NS"

    def test_get_price_history_valid(self):
        df = get_price_history("RELIANCE.NS", period="1mo")
        assert not df.empty
        assert "Close" in df.columns
        assert len(df) > 5

    def test_get_price_history_invalid_symbol(self):
        df = get_price_history("INVALIDXYZ123.NS", period="1mo")
        assert df.empty

    def test_multiple_stocks_data_available(self):
        """Test that key stocks in STOCK_LIST actually return data."""
        symbols = ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "M&M.NS", "TCS.NS"]
        for symbol in symbols:
            df = get_price_history(symbol, period="1mo")
            assert not df.empty, f"{symbol} returned no price history"
            assert "Close" in df.columns, f"{symbol} missing Close column"


# --- DuckDuckGo search tests ---

class TestSearch:
    def test_search_returns_results(self):
        results = search_stock_news("Reliance Industries", max_results=3)
        assert len(results) > 0
        assert "title" in results[0]
        assert "body" in results[0]

    def test_search_empty_query(self):
        results = search_stock_news("xyznonexistentstockqwerty", max_results=3)
        # May return 0 or some results, but should not crash
        assert isinstance(results, list)
