"""Tests for the LangGraph state and graph structure."""
import pytest

from src.graph.state import MarketAnalystState, merge_dicts


class TestMergeReducer:
    def test_merge_two_dicts(self):
        result = merge_dicts({"A": 1}, {"B": 2})
        assert result == {"A": 1, "B": 2}

    def test_merge_with_none_existing(self):
        result = merge_dicts(None, {"B": 2})
        assert result == {"B": 2}

    def test_merge_with_none_new(self):
        result = merge_dicts({"A": 1}, None)
        assert result == {"A": 1}

    def test_merge_overlapping_keys(self):
        result = merge_dicts({"A": 1}, {"A": 2})
        assert result == {"A": 2}  # new overwrites

    def test_merge_empty(self):
        result = merge_dicts({}, {})
        assert result == {}


class TestGraphImports:
    def test_state_schema_importable(self):
        from src.graph.state import MarketAnalystState
        assert MarketAnalystState is not None

    def test_graph_importable(self):
        from src.graph.graph import app
        assert app is not None

    def test_nodes_importable(self):
        from src.graph.nodes import (
            orchestrator_node,
            fundamental_agent_node,
            technical_agent_node,
            sentiment_agent_node,
            compile_node,
            fan_out_agents,
        )
        assert all([
            orchestrator_node,
            fundamental_agent_node,
            technical_agent_node,
            sentiment_agent_node,
            compile_node,
            fan_out_agents,
        ])

    def test_orchestrator_returns_empty(self):
        from src.graph.nodes import orchestrator_node
        result = orchestrator_node({
            "symbols": ["RELIANCE.NS"],
            "query_type": "single",
        })
        assert result == {}

    def test_fan_out_single_stock(self):
        from src.graph.nodes import fan_out_agents
        sends = fan_out_agents({
            "symbols": ["RELIANCE.NS"],
            "query_type": "single",
        })
        assert len(sends) == 3  # fundamental, technical, sentiment

    def test_fan_out_multi_stock(self):
        from src.graph.nodes import fan_out_agents
        sends = fan_out_agents({
            "symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS"],
            "query_type": "multi",
        })
        assert len(sends) == 9  # 3 stocks x 3 agents

    def test_fan_out_compare(self):
        from src.graph.nodes import fan_out_agents
        sends = fan_out_agents({
            "symbols": ["RELIANCE.NS", "TCS.NS"],
            "query_type": "compare",
        })
        assert len(sends) == 6  # 2 stocks x 3 agents
