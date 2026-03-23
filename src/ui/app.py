import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Market Analyst",
    page_icon="https://img.icons8.com/fluency/48/combo-chart.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS - Dark financial terminal aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #0a0e17;
    --bg-card: #111827;
    --bg-card-hover: #1a2332;
    --bg-surface: #0d1320;
    --border: #1e293b;
    --border-subtle: #162032;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-green: #10b981;
    --accent-green-dim: rgba(16, 185, 129, 0.12);
    --accent-red: #ef4444;
    --accent-red-dim: rgba(239, 68, 68, 0.12);
    --accent-amber: #f59e0b;
    --accent-amber-dim: rgba(245, 158, 11, 0.12);
    --accent-blue: #3b82f6;
    --accent-blue-dim: rgba(59, 130, 246, 0.12);
    --accent-cyan: #06b6d4;
}

/* Global overrides */
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stApp > header { background-color: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1420 0%, #091018 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: var(--text-secondary) !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio [aria-checked="true"] ~ label {
    background: var(--accent-blue-dim) !important;
    color: var(--accent-blue) !important;
}

/* Headings */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, span, li, .stMarkdown p {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-secondary) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    padding: 10px 32px !important;
    transition: all 0.25s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, var(--accent-blue) 0%, #2563eb 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Select boxes */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Dividers */
hr {
    border-color: var(--border-subtle) !important;
    opacity: 0.5 !important;
}

/* Spinner */
.stSpinner > div { color: var(--accent-blue) !important; }

/* Alert boxes */
.stAlert {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    border: none !important;
}

/* Hide Streamlit deploy button, main menu, and decoration */
.stDeployButton, .stAppDeployButton,
[data-testid="stDecoration"],
[data-testid="stMainMenu"],
[data-testid="stAppDeployButton"] { display: none !important; }

/* Ensure the sidebar expand button in the toolbar remains visible */
[data-testid="stExpandSidebarButton"] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Preserve Material Icons font for Streamlit icon elements */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] * {
    font-family: 'Material Symbols Rounded' !important;
}

/* Sidebar collapse/expand buttons - ensure icons render and are visible */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    overflow: hidden !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Sidebar expanded state width */
section[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 280px !important;
    width: 280px !important;
}
section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 280px !important;
}

/* Sidebar collapsed state - allow it to collapse and show expand button */
section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    width: 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Score bar animation */
@keyframes score-fill {
    from { width: 0%; }
    to { width: var(--score-width); }
}

/* Recommendation badge pulse */
@keyframes badge-glow {
    0%, 100% { box-shadow: 0 0 12px var(--glow-color); }
    50% { box-shadow: 0 0 24px var(--glow-color); }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def handle_api_error(e: Exception):
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 429:
            st.error("Rate limit exceeded. Please wait a minute and try again.")
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


def render_page_header(title: str, subtitle: str):
    st.markdown(f"""
    <div style="margin-bottom:32px;">
        <h1 style="margin:0 0 4px 0;font-size:28px;letter-spacing:-0.03em;
                    background:linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {title}
        </h1>
        <p style="margin:0;font-size:14px;color:#64748b;font-weight:400;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_recommendation_badge(rec: str, confidence: int):
    config = {
        "BUY": ("#10b981", "rgba(16,185,129,0.15)", "#d1fae5"),
        "SELL": ("#ef4444", "rgba(239,68,68,0.15)", "#fecaca"),
        "HOLD": ("#f59e0b", "rgba(245,158,11,0.15)", "#fef3c7"),
    }
    color, bg, text_c = config.get(rec, ("#64748b", "rgba(100,116,139,0.15)", "#cbd5e1"))
    arrow = {"BUY": "^", "SELL": "v", "HOLD": "-"}.get(rec, "?")

    conf_bar_color = color
    if confidence < 40:
        conf_bar_color = "#ef4444"
    elif confidence < 70:
        conf_bar_color = "#f59e0b"

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin:12px 0 20px 0;">
        <div style="display:inline-flex;align-items:center;gap:8px;background:{bg};
                    padding:10px 24px;border-radius:10px;border:1px solid {color}22;
                    --glow-color:{color}40;animation:badge-glow 3s ease-in-out infinite;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:22px;
                         font-weight:700;color:{text_c};letter-spacing:0.05em;">
                {arrow} {rec}
            </span>
        </div>
        <div style="flex:1;max-width:200px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                             color:#64748b;text-transform:uppercase;letter-spacing:0.08em;">
                    Confidence
                </span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:12px;
                             font-weight:600;color:{conf_bar_color};">
                    {confidence}%
                </span>
            </div>
            <div style="background:#1e293b;border-radius:4px;height:6px;overflow:hidden;">
                <div style="width:{confidence}%;height:100%;border-radius:4px;
                            background:linear-gradient(90deg, {conf_bar_color}, {conf_bar_color}cc);
                            animation:score-fill 1s ease-out forwards;
                            --score-width:{confidence}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_score_card(title: str, data: dict, color: str, icon: str):
    score = data.get("score", "N/A")
    analysis = data.get("analysis", "No data available")
    score_val = score if isinstance(score, (int, float)) else 0
    score_pct = min(score_val * 10, 100)

    score_color = color
    if isinstance(score, (int, float)):
        if score >= 7:
            score_color = "#10b981"
        elif score >= 4:
            score_color = "#f59e0b"
        else:
            score_color = "#ef4444"

    st.markdown(f"""
    <div style="background:linear-gradient(145deg, #111827 0%, #0f172a 100%);
                border:1px solid #1e293b;border-radius:12px;padding:20px;
                height:100%;transition:all 0.3s ease;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg, transparent, {color}, transparent);
                    opacity:0.6;"></div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
            <span style="font-size:16px;">{icon}</span>
            <span style="font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;
                         color:{color};text-transform:uppercase;letter-spacing:0.06em;">
                {title}
            </span>
        </div>
        <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:12px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:32px;
                         font-weight:700;color:{score_color};line-height:1;">
                {score}
            </span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:14px;
                         color:#475569;">/10</span>
        </div>
        <div style="background:#0a0e17;border-radius:4px;height:4px;margin-bottom:14px;
                    overflow:hidden;">
            <div style="width:{score_pct}%;height:100%;border-radius:4px;
                        background:{score_color};
                        animation:score-fill 1.2s ease-out forwards;
                        --score-width:{score_pct}%;"></div>
        </div>
        <p style="font-size:13px;color:#94a3b8;line-height:1.6;margin:0;
                  font-family:'DM Sans',sans-serif;">
            {analysis}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_stock_result(symbol: str, result: dict):
    stock_name = stock_options.get(symbol, symbol)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #111827 0%, #0d1320 100%);
                border:1px solid #1e293b;border-radius:14px;padding:28px;
                margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;
                         font-weight:500;color:#3b82f6;background:rgba(59,130,246,0.12);
                         padding:4px 10px;border-radius:6px;letter-spacing:0.05em;">
                {symbol}
            </span>
            <span style="font-family:'DM Sans',sans-serif;font-size:18px;
                         font-weight:600;color:#e2e8f0;">
                {stock_name}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_recommendation_badge(
        result.get("recommendation", "N/A"),
        result.get("confidence", 0),
    )

    reasoning = result.get("reasoning", "")
    if reasoning:
        st.markdown(f"""
        <div style="background:#0d1320;border:1px solid #1e293b;border-radius:10px;
                    padding:16px 20px;margin-bottom:20px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                        color:#475569;text-transform:uppercase;letter-spacing:0.08em;
                        margin-bottom:8px;">Analysis Summary</div>
            <p style="font-size:14px;color:#cbd5e1;line-height:1.7;margin:0;
                      font-family:'DM Sans',sans-serif;">
                {reasoning}
            </p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        render_score_card("Fundamental", result.get("fundamental", {}), "#10b981", "F")
    with col2:
        render_score_card("Technical", result.get("technical", {}), "#3b82f6", "T")
    with col3:
        render_score_card("Sentiment", result.get("sentiment", {}), "#f59e0b", "S")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 24px 0;border-bottom:1px solid #1e293b;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#3b82f6,#06b6d4);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;font-weight:bold;color:#fff;
                        font-family:'JetBrains Mono',monospace;">M</div>
            <div>
                <div style="font-family:'DM Sans',sans-serif;font-size:16px;
                            font-weight:700;color:#e2e8f0;letter-spacing:-0.02em;">
                    Market Analyst</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                            color:#475569;letter-spacing:0.05em;">
                    AI-POWERED ANALYSIS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

stocks = fetch_stock_list()
stock_options = {s["symbol"]: f"{s['name']} ({s['symbol']})" for s in stocks}

with st.sidebar:
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                color:#475569;text-transform:uppercase;letter-spacing:0.1em;
                margin-bottom:8px;padding-left:4px;">Navigation</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Stock Analysis", "Multi-Stock Analysis", "Compare Stocks"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div style="margin-top:40px;border-top:1px solid #1e293b;padding-top:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                    color:#334155;text-align:center;letter-spacing:0.05em;">
            Built with LangGraph + Groq
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Stock Analysis
# ---------------------------------------------------------------------------
if page == "Stock Analysis":
    render_page_header(
        "Stock Analysis",
        "Select a stock and get a comprehensive Buy / Sell / Hold recommendation"
    )

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        selected = st.selectbox(
            "Select a stock",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
            label_visibility="collapsed",
        )
    with col_btn:
        analyze_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

    if analyze_clicked:
        with st.spinner("Running multi-agent analysis..."):
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


# ---------------------------------------------------------------------------
# Page: Multi-Stock Analysis
# ---------------------------------------------------------------------------
elif page == "Multi-Stock Analysis":
    render_page_header(
        "Multi-Stock Analysis",
        "Analyze multiple stocks together and get a group summary"
    )

    selected_multi = st.multiselect(
        "Select stocks",
        options=list(stock_options.keys()),
        format_func=lambda x: stock_options[x],
        label_visibility="collapsed",
        placeholder="Choose stocks to analyze...",
    )

    if selected_multi:
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                    color:#475569;margin:4px 0 12px 0;">
            {len(selected_multi)} stock{'s' if len(selected_multi) != 1 else ''} selected
        </div>
        """, unsafe_allow_html=True)

    if st.button("Analyze All", type="primary"):
        if not selected_multi:
            st.warning("Select at least one stock.")
        else:
            with st.spinner(f"Analyzing {len(selected_multi)} stocks..."):
                try:
                    resp = httpx.post(
                        f"{API_URL}/analyze",
                        json={"symbols": selected_multi, "query_type": "multi"},
                        timeout=300,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    summary = data.get("summary", {})
                    if summary:
                        st.markdown("""
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:#475569;text-transform:uppercase;
                                    letter-spacing:0.08em;margin-bottom:8px;">
                            Group Summary</div>
                        """, unsafe_allow_html=True)

                        overview = summary.get("overview", "")
                        if overview:
                            st.markdown(f"""
                            <div style="background:#0d1320;border:1px solid #1e293b;
                                        border-radius:10px;padding:16px 20px;margin-bottom:16px;">
                                <p style="font-size:14px;color:#cbd5e1;line-height:1.7;margin:0;">
                                    {overview}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            strong = summary.get("strong_picks", [])
                            if strong:
                                picks_html = " ".join(
                                    f'<span style="background:rgba(16,185,129,0.15);color:#10b981;'
                                    f'padding:4px 10px;border-radius:6px;font-size:12px;'
                                    f'font-family:JetBrains Mono,monospace;'
                                    f'font-weight:500;">{p}</span>'
                                    for p in strong
                                )
                                st.markdown(f"""
                                <div style="margin-bottom:12px;">
                                    <div style="font-size:11px;color:#475569;
                                                text-transform:uppercase;letter-spacing:0.08em;
                                                font-family:'JetBrains Mono',monospace;
                                                margin-bottom:8px;">Strong Picks</div>
                                    <div style="display:flex;gap:8px;flex-wrap:wrap;">
                                        {picks_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        with col2:
                            concerns = summary.get("concerns", [])
                            if concerns:
                                concern_html = " ".join(
                                    f'<span style="background:rgba(239,68,68,0.15);color:#ef4444;'
                                    f'padding:4px 10px;border-radius:6px;font-size:12px;'
                                    f'font-family:JetBrains Mono,monospace;'
                                    f'font-weight:500;">{c}</span>'
                                    for c in concerns
                                )
                                st.markdown(f"""
                                <div style="margin-bottom:12px;">
                                    <div style="font-size:11px;color:#475569;
                                                text-transform:uppercase;letter-spacing:0.08em;
                                                font-family:'JetBrains Mono',monospace;
                                                margin-bottom:8px;">Concerns</div>
                                    <div style="display:flex;gap:8px;flex-wrap:wrap;">
                                        {concern_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

                    for symbol in selected_multi:
                        if symbol in data.get("results", {}):
                            render_stock_result(symbol, data["results"][symbol])

                    if data.get("errors"):
                        st.warning(f"Some analyses had issues: {data['errors']}")

                except httpx.ConnectError:
                    st.error("Cannot connect to the API server. Make sure it's running on port 8000.")
                except Exception as e:
                    st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Page: Compare Stocks
# ---------------------------------------------------------------------------
elif page == "Compare Stocks":
    render_page_header(
        "Compare Stocks",
        "Compare two stocks side by side to decide which to invest in"
    )

    col1, col_vs, col2 = st.columns([5, 1, 5])
    with col1:
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                    color:#475569;text-transform:uppercase;letter-spacing:0.1em;
                    margin-bottom:4px;">Stock A</div>
        """, unsafe_allow_html=True)
        stock_a = st.selectbox(
            "Stock A",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
            key="stock_a",
            label_visibility="collapsed",
        )
    with col_vs:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;
                    height:100%;padding-top:20px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:14px;
                         font-weight:700;color:#334155;">VS</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                    color:#475569;text-transform:uppercase;letter-spacing:0.1em;
                    margin-bottom:4px;">Stock B</div>
        """, unsafe_allow_html=True)
        remaining = [s for s in stock_options.keys() if s != stock_a]
        stock_b = st.selectbox(
            "Stock B",
            options=remaining,
            format_func=lambda x: stock_options[x],
            key="stock_b",
            label_visibility="collapsed",
        )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    if st.button("Compare", type="primary", use_container_width=True):
        with st.spinner("Running comparison analysis..."):
            try:
                resp = httpx.post(
                    f"{API_URL}/compare",
                    json={"symbols": [stock_a, stock_b]},
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()

                comparison = data.get("comparison", {})
                if comparison:
                    winner = comparison.get("winner", "")
                    winner_name = stock_options.get(winner, winner)
                    reasoning = comparison.get("reasoning", "")

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg, rgba(16,185,129,0.08) 0%,
                                rgba(6,182,212,0.06) 100%);
                                border:1px solid rgba(16,185,129,0.2);border-radius:14px;
                                padding:24px;margin:20px 0;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:#475569;text-transform:uppercase;
                                    letter-spacing:0.08em;margin-bottom:10px;">
                            Verdict</div>
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;
                                         font-weight:600;color:#10b981;
                                         background:rgba(16,185,129,0.15);
                                         padding:4px 12px;border-radius:6px;">WINNER</span>
                            <span style="font-family:'DM Sans',sans-serif;font-size:18px;
                                         font-weight:700;color:#e2e8f0;">
                                {winner_name}</span>
                        </div>
                        <p style="font-size:14px;color:#94a3b8;line-height:1.7;margin:0;">
                            {reasoning}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    diffs = comparison.get("key_differences", [])
                    if diffs:
                        diffs_html = "".join(
                            f'<div style="display:flex;align-items:flex-start;gap:8px;'
                            f'padding:8px 0;border-bottom:1px solid #1e293b22;">'
                            f'<span style="color:#3b82f6;font-size:8px;margin-top:6px;">&#9679;</span>'
                            f'<span style="font-size:13px;color:#94a3b8;line-height:1.5;">{d}</span>'
                            f'</div>'
                            for d in diffs
                        )
                        st.markdown(f"""
                        <div style="background:#0d1320;border:1px solid #1e293b;
                                    border-radius:10px;padding:16px 20px;margin-bottom:24px;">
                            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                        color:#475569;text-transform:uppercase;
                                        letter-spacing:0.08em;margin-bottom:10px;">
                                Key Differences</div>
                            {diffs_html}
                        </div>
                        """, unsafe_allow_html=True)

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
