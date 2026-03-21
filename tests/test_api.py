"""Tests for the FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient

from src.api.main import api
from src.config import STOCK_LIST


client = TestClient(api)


class TestHealthEndpoint:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestStocksEndpoint:
    def test_list_stocks(self):
        resp = client.get("/stocks")
        assert resp.status_code == 200
        data = resp.json()
        assert "stocks" in data
        assert len(data["stocks"]) == len(STOCK_LIST)

    def test_stock_has_required_fields(self):
        resp = client.get("/stocks")
        stock = resp.json()["stocks"][0]
        assert "symbol" in stock
        assert "name" in stock
        assert "sector" in stock

    def test_stock_symbols_end_with_ns(self):
        resp = client.get("/stocks")
        for stock in resp.json()["stocks"]:
            assert stock["symbol"].endswith(".NS"), f"{stock['symbol']} missing .NS suffix"


class TestAnalyzeEndpoint:
    def test_empty_symbols_returns_400(self):
        resp = client.post("/analyze", json={"symbols": [], "query_type": "single"})
        assert resp.status_code == 400

    def test_single_symbol_accepted(self):
        """Test that the endpoint accepts valid input (may fail on rate limit)."""
        resp = client.post("/analyze", json={"symbols": ["RELIANCE.NS"], "query_type": "single"})
        # Accept 200 (success) or 429 (rate limit) - both mean the endpoint works
        assert resp.status_code in [200, 429]

    def test_multi_type_auto_detected(self):
        """Multiple symbols with query_type=single should auto-upgrade to multi."""
        resp = client.post(
            "/analyze",
            json={"symbols": ["RELIANCE.NS", "INFY.NS"], "query_type": "single"},
        )
        assert resp.status_code in [200, 429]
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("query_type") == "multi"


class TestCompareEndpoint:
    def test_wrong_symbol_count_returns_400(self):
        resp = client.post("/compare", json={"symbols": ["RELIANCE.NS"]})
        assert resp.status_code == 400

    def test_three_symbols_returns_400(self):
        resp = client.post("/compare", json={"symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]})
        assert resp.status_code == 400

    def test_two_symbols_accepted(self):
        resp = client.post("/compare", json={"symbols": ["RELIANCE.NS", "TCS.NS"]})
        assert resp.status_code in [200, 429]
