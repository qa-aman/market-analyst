import streamlit as st
import httpx

API_URL = "http://localhost:8000"


st.set_page_config(page_title="Market Analyst", page_icon="📊", layout="wide")


def handle_api_error(e: Exception):
    """Display user-friendly error messages."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 429:
            st.error("Gemini API rate limit exceeded. Please wait a minute and try again.")
        else:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            st.error(f"Error: {detail}")
    elif isinstance(e, httpx.ConnectError):
        st.error("Cannot connect to the API server. Make sure it's running on port 8000.")
    else:
        st.error(f"Error: {e}")


@st.cache_data(ttl=3600)
def fetch_stock_list():
    try:
        resp = httpx.get(f"{API_URL}/stocks", timeout=10)
        resp.raise_for_status()
        return resp.json()["stocks"]
    except Exception:
        return []


def render_recommendation_badge(rec: str, confidence: int):
    colors = {"BUY": "#00b894", "SELL": "#e17055", "HOLD": "#fdcb6e"}
    color = colors.get(rec, "#636e72")
    text_color = "#2d3436" if rec == "HOLD" else "#ffffff"
    st.markdown(
        f'<div style="display:inline-block;background:{color};color:{text_color};'
        f'padding:8px 24px;border-radius:8px;font-size:20px;font-weight:bold;">'
        f'{rec} ({confidence}% confidence)</div>',
        unsafe_allow_html=True,
    )


def render_score_card(title: str, data: dict, color: str):
    score = data.get("score", "N/A")
    analysis = data.get("analysis", "No data available")
    st.markdown(
        f'<div style="border-left:4px solid {color};padding:12px 16px;margin-bottom:12px;'
        f'background:#1a1a2e;border-radius:4px;">'
        f'<strong style="color:{color};">{title}</strong> '
        f'<span style="color:#dfe6e9;">Score: {score}/10</span><br>'
        f'<span style="color:#b2bec3;font-size:14px;">{analysis}</span></div>',
        unsafe_allow_html=True,
    )


def render_stock_result(symbol: str, result: dict):
    st.subheader(symbol)
    render_recommendation_badge(
        result.get("recommendation", "N/A"),
        result.get("confidence", 0),
    )
    st.write(result.get("reasoning", ""))
    col1, col2, col3 = st.columns(3)
    with col1:
        render_score_card("Fundamental", result.get("fundamental", {}), "#00b894")
    with col2:
        render_score_card("Technical", result.get("technical", {}), "#0984e3")
    with col3:
        render_score_card("Sentiment", result.get("sentiment", {}), "#e17055")


# Sidebar navigation
stocks = fetch_stock_list()
stock_options = {s["symbol"]: f"{s['name']} ({s['symbol']})" for s in stocks}

page = st.sidebar.radio("Navigation", ["Stock Analysis", "Multi-Stock Analysis", "Compare Stocks"])

# Page 1: Single Stock Analysis
if page == "Stock Analysis":
    st.title("Stock Analysis")
    st.write("Select a stock and get a comprehensive Buy/Sell/Hold recommendation.")

    selected = st.selectbox("Select a stock", options=list(stock_options.keys()), format_func=lambda x: stock_options[x])

    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing... (this takes 10-20 seconds)"):
            try:
                resp = httpx.post(
                    f"{API_URL}/analyze",
                    json={"symbols": [selected], "query_type": "single"},
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()

                if selected in data.get("results", {}):
                    render_stock_result(selected, data["results"][selected])
                else:
                    st.error("No results returned for the selected stock.")

                if data.get("errors"):
                    st.warning(f"Some analyses had issues: {data['errors']}")

            except Exception as e:
                handle_api_error(e)

# Page 2: Multi-Stock Analysis
elif page == "Multi-Stock Analysis":
    st.title("Multi-Stock Analysis")
    st.write("Select multiple stocks to analyze together.")

    selected_multi = st.multiselect(
        "Select stocks",
        options=list(stock_options.keys()),
        format_func=lambda x: stock_options[x],
    )

    if st.button("Analyze All", type="primary"):
        if not selected_multi:
            st.warning("Select at least one stock.")
        else:
            with st.spinner(f"Analyzing {len(selected_multi)} stocks... (this may take a while)"):
                try:
                    resp = httpx.post(
                        f"{API_URL}/analyze",
                        json={"symbols": selected_multi, "query_type": "multi"},
                        timeout=300,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    # Summary section
                    summary = data.get("summary", {})
                    if summary:
                        st.subheader("Group Summary")
                        st.write(summary.get("overview", ""))

                        col1, col2 = st.columns(2)
                        with col1:
                            strong = summary.get("strong_picks", [])
                            if strong:
                                st.success(f"Strong picks: {', '.join(strong)}")
                        with col2:
                            concerns = summary.get("concerns", [])
                            if concerns:
                                st.warning(f"Concerns: {', '.join(concerns)}")

                    st.divider()

                    # Per-stock results
                    for symbol in selected_multi:
                        if symbol in data.get("results", {}):
                            render_stock_result(symbol, data["results"][symbol])
                            st.divider()

                    if data.get("errors"):
                        st.warning(f"Some analyses had issues: {data['errors']}")

                except httpx.ConnectError:
                    st.error("Cannot connect to the API server. Make sure it's running on port 8000.")
                except Exception as e:
                    st.error(f"Error: {e}")

# Page 3: Compare Stocks
elif page == "Compare Stocks":
    st.title("Compare Stocks")
    st.write("Compare two stocks side by side to decide which to buy.")

    col1, col2 = st.columns(2)
    with col1:
        stock_a = st.selectbox("Stock A", options=list(stock_options.keys()), format_func=lambda x: stock_options[x], key="stock_a")
    with col2:
        remaining = [s for s in stock_options.keys() if s != stock_a]
        stock_b = st.selectbox("Stock B", options=remaining, format_func=lambda x: stock_options[x], key="stock_b")

    if st.button("Compare", type="primary"):
        with st.spinner("Comparing stocks..."):
            try:
                resp = httpx.post(
                    f"{API_URL}/compare",
                    json={"symbols": [stock_a, stock_b]},
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()

                # Comparison verdict
                comparison = data.get("comparison", {})
                if comparison:
                    winner = comparison.get("winner", "")
                    st.subheader("Verdict")
                    winner_name = stock_options.get(winner, winner)
                    st.success(f"Winner: {winner_name}")
                    st.write(comparison.get("reasoning", ""))

                    diffs = comparison.get("key_differences", [])
                    if diffs:
                        st.subheader("Key Differences")
                        for d in diffs:
                            st.write(f"- {d}")

                st.divider()

                # Side by side results
                col1, col2 = st.columns(2)
                with col1:
                    if stock_a in data.get("results", {}):
                        render_stock_result(stock_a, data["results"][stock_a])
                with col2:
                    if stock_b in data.get("results", {}):
                        render_stock_result(stock_b, data["results"][stock_b])

                if data.get("errors"):
                    st.warning(f"Some analyses had issues: {data['errors']}")

            except Exception as e:
                handle_api_error(e)
