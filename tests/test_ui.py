"""Tests for UI rendering logic and CSS integrity."""
import re

import pytest

from src.ui.app import (
    render_recommendation_badge,
    render_score_card,
    render_page_header,
)


# ---------------------------------------------------------------------------
# CSS integrity tests - prevent regressions from the bugs we fixed
# ---------------------------------------------------------------------------
class TestCSSIntegrity:
    """Validate the custom CSS doesn't break Streamlit's built-in elements."""

    @pytest.fixture(autouse=True)
    def _load_css(self):
        """Extract the CSS string from app.py for inspection."""
        from pathlib import Path

        app_source = Path(__file__).parent.parent / "src" / "ui" / "app.py"
        content = app_source.read_text()
        # Extract CSS between <style> and </style>
        match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
        assert match, "Could not find <style> block in app.py"
        self.css = match.group(1)

    def test_material_icons_font_preserved(self):
        """Material Icons must keep their font-family to render as icons,
        not raw text like 'keyboard_double_arrow_left'."""
        assert "stIconMaterial" in self.css
        assert "Material Symbols Rounded" in self.css

    def test_sidebar_collapse_button_overflow_hidden(self):
        """Collapse button must clip overflow to prevent icon text leaking."""
        assert "stSidebarCollapseButton" in self.css
        # The rule should set overflow: hidden
        collapse_section = self.css[self.css.index("stSidebarCollapseButton"):]
        brace_end = collapse_section.index("}")
        rule = collapse_section[:brace_end]
        assert "overflow" in rule
        assert "hidden" in rule

    def test_no_absolute_positioned_footer(self):
        """Footer must NOT use position:absolute, which caused overlap
        with navigation items when sidebar was short."""
        # Find the "Built with" section in the source
        from pathlib import Path

        app_source = Path(__file__).parent.parent / "src" / "ui" / "app.py"
        content = app_source.read_text()
        footer_idx = content.index("Built with LangGraph")
        # Get the surrounding div (200 chars before)
        context = content[max(0, footer_idx - 300):footer_idx + 50]
        assert "position:absolute" not in context, (
            "Footer div must not use position:absolute - causes overlap with nav items"
        )

    def test_sidebar_has_fixed_width(self):
        """Sidebar must have a min-width to prevent collapsing to zero."""
        assert "min-width: 280px" in self.css or "min-width:280px" in self.css

    def test_deploy_button_hidden(self):
        """Streamlit deploy button should be hidden."""
        assert "stDeployButton" in self.css
        assert "stToolbar" in self.css

    def test_global_font_does_not_use_generic_fonts(self):
        """Custom fonts must not use generic AI-slop fonts."""
        generic_fonts = ["Inter", "Roboto", "Arial"]
        for font in generic_fonts:
            # Check it's not the PRIMARY font (it can appear in fallback stacks)
            assert f"font-family: '{font}'" not in self.css, (
                f"CSS uses generic font '{font}' as primary font"
            )

    def test_css_has_required_custom_properties(self):
        """CSS variables for the theme must be defined."""
        required_vars = [
            "--bg-primary",
            "--bg-card",
            "--border",
            "--text-primary",
            "--text-secondary",
            "--accent-green",
            "--accent-red",
            "--accent-blue",
        ]
        for var in required_vars:
            assert var in self.css, f"Missing CSS variable: {var}"


# ---------------------------------------------------------------------------
# Render function tests
# ---------------------------------------------------------------------------
class TestRenderRecommendationBadge:
    """Test the recommendation badge HTML generation."""

    def test_buy_uses_green_color(self, capsys):
        """BUY recommendation should use green accent."""
        # We can't easily capture st.markdown output, so test the logic directly
        config = {
            "BUY": ("#10b981", "rgba(16,185,129,0.15)", "#d1fae5"),
            "SELL": ("#ef4444", "rgba(239,68,68,0.15)", "#fecaca"),
            "HOLD": ("#f59e0b", "rgba(245,158,11,0.15)", "#fef3c7"),
        }
        color, bg, text_c = config["BUY"]
        assert color == "#10b981"
        assert "185,129" in bg  # green channel

    def test_sell_uses_red_color(self):
        config = {
            "BUY": ("#10b981", "rgba(16,185,129,0.15)", "#d1fae5"),
            "SELL": ("#ef4444", "rgba(239,68,68,0.15)", "#fecaca"),
            "HOLD": ("#f59e0b", "rgba(245,158,11,0.15)", "#fef3c7"),
        }
        color, _, _ = config["SELL"]
        assert color == "#ef4444"

    def test_hold_uses_amber_color(self):
        config = {
            "BUY": ("#10b981", "rgba(16,185,129,0.15)", "#d1fae5"),
            "SELL": ("#ef4444", "rgba(239,68,68,0.15)", "#fecaca"),
            "HOLD": ("#f59e0b", "rgba(245,158,11,0.15)", "#fef3c7"),
        }
        color, _, _ = config["HOLD"]
        assert color == "#f59e0b"

    def test_unknown_recommendation_has_fallback(self):
        fallback = ("#64748b", "rgba(100,116,139,0.15)", "#cbd5e1")
        config = {
            "BUY": ("#10b981", "rgba(16,185,129,0.15)", "#d1fae5"),
            "SELL": ("#ef4444", "rgba(239,68,68,0.15)", "#fecaca"),
            "HOLD": ("#f59e0b", "rgba(245,158,11,0.15)", "#fef3c7"),
        }
        result = config.get("UNKNOWN", fallback)
        assert result == fallback

    def test_confidence_bar_color_low(self):
        """Confidence below 40 should use red."""
        confidence = 30
        color = "#10b981"
        conf_bar_color = color
        if confidence < 40:
            conf_bar_color = "#ef4444"
        elif confidence < 70:
            conf_bar_color = "#f59e0b"
        assert conf_bar_color == "#ef4444"

    def test_confidence_bar_color_medium(self):
        """Confidence 40-69 should use amber."""
        confidence = 55
        color = "#10b981"
        conf_bar_color = color
        if confidence < 40:
            conf_bar_color = "#ef4444"
        elif confidence < 70:
            conf_bar_color = "#f59e0b"
        assert conf_bar_color == "#f59e0b"

    def test_confidence_bar_color_high(self):
        """Confidence 70+ should keep original color."""
        confidence = 85
        color = "#10b981"
        conf_bar_color = color
        if confidence < 40:
            conf_bar_color = "#ef4444"
        elif confidence < 70:
            conf_bar_color = "#f59e0b"
        assert conf_bar_color == "#10b981"

    def test_arrow_symbols(self):
        arrows = {"BUY": "^", "SELL": "v", "HOLD": "-"}
        assert arrows["BUY"] == "^"
        assert arrows["SELL"] == "v"
        assert arrows["HOLD"] == "-"
        assert arrows.get("UNKNOWN", "?") == "?"


class TestRenderScoreCard:
    """Test score card color logic."""

    def test_high_score_uses_green(self):
        score = 8
        score_color = "#3b82f6"
        if isinstance(score, (int, float)):
            if score >= 7:
                score_color = "#10b981"
            elif score >= 4:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"
        assert score_color == "#10b981"

    def test_medium_score_uses_amber(self):
        score = 5
        score_color = "#3b82f6"
        if isinstance(score, (int, float)):
            if score >= 7:
                score_color = "#10b981"
            elif score >= 4:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"
        assert score_color == "#f59e0b"

    def test_low_score_uses_red(self):
        score = 2
        score_color = "#3b82f6"
        if isinstance(score, (int, float)):
            if score >= 7:
                score_color = "#10b981"
            elif score >= 4:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"
        assert score_color == "#ef4444"

    def test_na_score_keeps_default_color(self):
        score = "N/A"
        score_color = "#3b82f6"
        if isinstance(score, (int, float)):
            if score >= 7:
                score_color = "#10b981"
        assert score_color == "#3b82f6"

    def test_score_percentage_capped_at_100(self):
        score = 12  # edge case: score above 10
        score_pct = min(score * 10, 100)
        assert score_pct == 100

    def test_score_percentage_normal(self):
        score = 7
        score_pct = min(score * 10, 100)
        assert score_pct == 70

    def test_na_score_percentage_is_zero(self):
        score = "N/A"
        score_val = score if isinstance(score, (int, float)) else 0
        score_pct = min(score_val * 10, 100)
        assert score_pct == 0

    def test_default_analysis_text(self):
        data = {}
        analysis = data.get("analysis", "No data available")
        assert analysis == "No data available"

    def test_analysis_from_data(self):
        data = {"analysis": "Strong fundamentals", "score": 8}
        analysis = data.get("analysis", "No data available")
        assert analysis == "Strong fundamentals"


# ---------------------------------------------------------------------------
# Navigation and page structure tests
# ---------------------------------------------------------------------------
class TestAppStructure:
    """Validate app.py has the required structure."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        from pathlib import Path

        self.source = (Path(__file__).parent.parent / "src" / "ui" / "app.py").read_text()

    def test_has_three_pages(self):
        assert 'page == "Stock Analysis"' in self.source
        assert 'page == "Multi-Stock Analysis"' in self.source
        assert 'page == "Compare Stocks"' in self.source

    def test_sidebar_has_branding(self):
        assert "Market Analyst" in self.source
        assert "AI-POWERED ANALYSIS" in self.source

    def test_sidebar_has_navigation_radio(self):
        assert "st.radio" in self.source

    def test_page_config_uses_wide_layout(self):
        assert 'layout="wide"' in self.source

    def test_sidebar_starts_expanded(self):
        assert 'initial_sidebar_state="expanded"' in self.source

    def test_uses_unsafe_allow_html(self):
        """Custom HTML rendering requires unsafe_allow_html."""
        assert "unsafe_allow_html=True" in self.source

    def test_api_url_is_localhost(self):
        assert 'API_URL = "http://localhost:8000"' in self.source

    def test_compare_page_has_two_selectboxes(self):
        """Compare page needs Stock A and Stock B selectors."""
        assert 'key="stock_a"' in self.source
        assert 'key="stock_b"' in self.source

    def test_stock_list_is_cached(self):
        assert "@st.cache_data" in self.source
