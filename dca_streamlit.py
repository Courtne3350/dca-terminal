import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# ============================================================
FMP_API_KEY = st.secrets.get("FMP_API_KEY", "")
# ============================================================

st.set_page_config(page_title="DCA Terminal", page_icon="◆", layout="wide")

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "MSTR"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.stApp, .stApp p, .stApp span, .stApp div, .stApp label, .stApp li {
    font-family: 'Inter', sans-serif !important;
    color: #EDEFF3;
}
h1, h2, h3, h4, .term-title, .ticker-name {
    font-family: 'Space Grotesk', sans-serif !important;
}
.metric-value, .mono, .ticker-price, .fv-value, .btc-card .metric-value,
.peer-table, .holder-row, .ticker-meta, .section-label, .metric-label,
.btc-label, .fv-label, .fv-note, .status, code {
    font-family: 'IBM Plex Mono', monospace !important;
    font-variant-numeric: tabular-nums;
}

.stApp { background: #0A0C10; }

.ticker-wrap {
    background: linear-gradient(90deg, #0d1117, #12151b, #0d1117);
    border-top: 1px solid #232833; border-bottom: 1px solid #232833;
    overflow: hidden; white-space: nowrap; margin: 0 0 18px 0; padding: 10px 0;
}
.ticker-track { display: inline-block; animation: ticker-scroll 55s linear infinite;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.88rem; }
.ticker-item { display: inline-block; margin-right: 42px; color: #C8CDD8; }
.ticker-item .sym { color: #E8A33D; font-weight: 600; margin-right: 6px; }
.ticker-item .up { color: #3ECF8E; }
.ticker-item .down { color: #FF6B6B; }
@keyframes ticker-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

.term-header { display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #232833; padding-bottom: 14px; margin-bottom: 16px; }
.term-dot { width: 9px; height: 9px; border-radius: 50%; background: #E8A33D; box-shadow: 0 0 10px #E8A33D; }
.term-title { font-size: 1.55rem; font-weight: 700; color: #EDEFF3; }
.term-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #7C8494; }

.ticker-bar { background: linear-gradient(180deg, #171b23, #12151b); border: 1px solid #232833; border-left: 3px solid #E8A33D; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.ticker-name { font-size: 1.3rem; font-weight: 600; color: #EDEFF3; }
.ticker-meta { font-size: 0.8rem; color: #7C8494; margin-top: 3px; }
.ticker-price { font-size: 1.7rem; font-weight: 600; cursor: help; color: #EDEFF3; }

.section-label { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: #7C8494; border-bottom: 1px solid #232833; padding-bottom: 7px; margin: 8px 0 14px 0; }

.metric-card {
    background: #12151b; border: 1px solid #232833; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 14px; min-height: 92px;
}
.metric-card.status-green { border-color: #3ECF8E; box-shadow: 0 0 0 1px rgba(62,207,142,0.45), 0 0 12px rgba(62,207,142,0.25); }
.metric-card.status-orange { border-color: #E8A33D; box-shadow: 0 0 0 1px rgba(232,163,61,0.45), 0 0 12px rgba(232,163,61,0.25); }
.metric-card.status-red { border-color: #FF6B6B; box-shadow: 0 0 0 1px rgba(255,107,107,0.45), 0 0 12px rgba(255,107,107,0.25); }
.metric-card.status-gray { border-color: #4B5160; }

.metric-label { color: #7C8494; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.metric-row { display: flex; justify-content: space-between; align-items: baseline; }
.metric-value { font-size: 1.45rem; font-weight: 600; color: #EDEFF3; }
.status { font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px; }
.status-green { color: #3ECF8E; background: rgba(62,207,142,0.12); }
.status-red { color: #FF6B6B; background: rgba(255,107,107,0.12); }
.status-orange { color: #E8A33D; background: rgba(232,163,61,0.12); }
.status-gray { color: #7C8494; background: rgba(75,81,96,0.15); }

.fv-card { background: linear-gradient(165deg, #171b23, #12151b); border: 1px solid #232833; border-left: 3px solid #E8A33D; border-radius: 10px; padding: 16px 18px; margin-bottom: 12px; }
.fv-label { color: #7C8494; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.fv-value { font-size: 1.6rem; font-weight: 600; color: #E8A33D; }
.fv-note { font-size: 0.72rem; color: #7C8494; margin-top: 4px; }

.btc-card {
    background: linear-gradient(165deg, #1a1208, #12151b);
    border: 1px solid #3d2e1a; border-left: 3px solid #E8A33D;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 14px;
    min-height: 110px; display: flex; flex-direction: column; justify-content: space-between;
    cursor: help;
}
.btc-label { color: #E8A33D; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }

.desc-box {
    background: #12151b; border: 1px solid #232833; border-radius: 10px;
    padding: 16px 18px; margin-bottom: 20px; font-size: 0.92rem;
    line-height: 1.55; color: #C8CDD8; position: relative; cursor: help;
}
.desc-box:hover::after {
    content: attr(data-full); position: absolute; left: 0; top: 100%; z-index: 100;
    background: #1a1e27; border: 1px solid #E8A33D; border-radius: 10px;
    padding: 16px 18px; width: 100%; max-width: 900px; color: #EDEFF3;
    font-size: 0.9rem; line-height: 1.6; box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    white-space: pre-wrap;
}

.holder-row {
    display: flex; justify-content: space-between; padding: 8px 0;
    border-bottom: 1px solid #1e222b; font-size: 0.85rem;
}

.signal-banner { font-family: 'Space Grotesk', sans-serif !important; font-weight: 600; padding: 14px 18px; border-radius: 10px; margin: 18px 0; display: flex; justify-content: space-between; align-items: center; }
.signal-green { background: rgba(62,207,142,0.10); border: 1px solid rgba(62,207,142,0.35); color: #3ECF8E; }
.signal-orange { background: rgba(232,163,61,0.10); border: 1px solid rgba(232,163,61,0.35); color: #E8A33D; }
.signal-red { background: rgba(255,107,107,0.10); border: 1px solid rgba(255,107,107,0.35); color: #FF6B6B; }

.peer-table {
    width: 100%; border-collapse: collapse; font-size: 0.85rem;
    background: #12151b; border: 1px solid #232833; border-radius: 10px; overflow: hidden;
}
.peer-table th {
    background: #171b23; color: #E8A33D; text-align: left; padding: 12px 14px;
    border-bottom: 1px solid #232833; font-weight: 600; text-transform: uppercase;
    font-size: 0.72rem; letter-spacing: 0.05em;
}
.peer-table td { padding: 11px 14px; border-bottom: 1px solid #1e222b; color: #EDEFF3; }
.peer-table tr:last-child td { border-bottom: none; }
.peer-table tr:hover td { background: #1a1e27; }

div[data-testid="stRadio"] label p {
    color: #EDEFF3 !important;
    font-size: 0.95rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

section[data-testid="stSidebar"] { background: #12151b !important; border-right: 1px solid #232833; }
.stButton > button { background: #E8A33D !important; color: #0A0C10 !important; border: none; border-radius: 8px; font-family: 'Space Grotesk', sans-serif !important; font-weight: 600; width: 100%; }
.stSidebar label, .stSidebar p, .stSidebar .stMarkdown, .stSidebar span { color: #EDEFF3 !important; }
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
MARKET_SYMBOLS = {
    "^GSPC": "S&P 500", "QQQ": "Nasdaq-100", "^RUT": "Russell 2000", "^DJI": "Dow Jones", "^VIX": "VIX",
    "XLK": "Tech", "XLF": "Financials", "XLE": "Energy", "XLV": "Healthcare", "XLI": "Industrials",
    "XLY": "Cons. Disc.", "XLP": "Cons. Staples", "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate",
    "GC=F": "Gold", "SI=F": "Silver", "CL=F": "Crude Oil", "HG=F": "Copper", "BTC-USD": "Bitcoin",
    "^TNX": "10Y Yield",
}

TOP_SP_STOCKS = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK-B", "AVGO", "TSLA", "JPM",
                 "LLY", "V", "UNH", "XOM", "MA", "COST", "HD", "PG", "JNJ", "ABBV"]
SECTOR_ETFS = {"XLK": "Technology", "XLF": "Financials", "XLE": "Energy", "XLV": "Healthcare",
               "XLI": "Industrials", "XLY": "Cons. Disc.", "XLP": "Cons. Staples",
               "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate", "XLC": "Comm. Services"}
TOP_CRYPTOS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", "ADA-USD", "DOGE-USD",
               "AVAX-USD", "DOT-USD", "LINK-USD", "MATIC-USD", "LTC-USD", "ATOM-USD", "NEAR-USD"]

NAME_MAP = {
    "strategy": "MSTR", "microstrategy": "MSTR", "mstr": "MSTR",
    "metaplanet": "3350.T", "twenty one": "XXI", "strive": "ASST",
    "marathon": "MARA", "bullish": "BLSH", "riot": "RIOT", "cleanspark": "CLSK",
    "tesla": "TSLA", "hut 8": "HUT", "block": "XYZ", "coinbase": "COIN",
    "trump media": "DJT", "galaxy": "GLXY", "gamestop": "GME", "nakamoto": "NAKA",
    "apple": "AAPL", "microsoft": "MSFT", "nvidia": "NVDA", "amazon": "AMZN",
    "google": "GOOGL", "meta": "META", "adobe": "ADBE", "adbe": "ADBE",
    "h100": "H100.L", "h100 group": "H100.L", "iren": "IREN",
}

KNOWN_BTC_HOLDINGS = {
    "MSTR": 840447, "XXI": 43514, "3350.T": 43000, "MARA": 35577,
    "ASST": 20167, "BLSH": 24300, "COIN": 17311, "RIOT": 15680,
    "CLSK": 13924, "TSLA": 11509, "HUT": 10275, "XYZ": 9117,
    "DJT": 14139, "GLXY": 6328, "GME": 4710, "NAKA": 4467,
}

KNOWN_SENIOR_CLAIMS = {"MSTR": 21_200_000_000}

PEER_GROUPS = {
    "MSTR": ["ASST", "3350.T", "XXI", "MARA"],
    "ASST": ["MSTR", "3350.T", "XXI"],
    "3350.T": ["MSTR", "ASST", "XXI"],
    "XXI": ["MSTR", "ASST", "3350.T"],
    "MARA": ["RIOT", "CLSK", "HUT"],
    "RIOT": ["MARA", "CLSK", "HUT"],
    "CLSK": ["MARA", "RIOT", "HUT"],
}

def fetch_one(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        if hist.empty: return None
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
        chg = ((last - prev) / prev) * 100 if prev else 0
        return {"symbol": symbol, "name": MARKET_SYMBOLS.get(symbol, symbol), "price": last, "chg": chg}
    except: return None

@st.cache_data(ttl=300)
def get_market_snapshot():
    with ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(fetch_one, MARKET_SYMBOLS.keys()))
    return [r for r in results if r]

def build_ticker_html(data):
    items = []
    for d in data:
        cls = "up" if d["chg"] >= 0 else "down"
        sign = "+" if d["chg"] >= 0 else ""
        if "Yield" in d["name"]:
            price_str = f"{d['price']:.2f}%"
        elif d["symbol"] in ("BTC-USD", "GC=F", "SI=F", "CL=F", "HG=F"):
            price_str = f"${d['price']:,.1f}"
        else:
            price_str = f"{d['price']:,.2f}"
        items.append(f'<span class="ticker-item"><span class="sym">{d["name"]}</span>{price_str} <span class="{cls}">{sign}{d["chg"]:.2f}%</span></span>')
    content = "".join(items)
    return f'<div class="ticker-wrap"><div class="ticker-track">{content}{content}</div></div>'

def fetch_heatmap_item(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="5d")
        if hist.empty or len(hist) < 2: return None
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        chg = ((last - prev) / prev) * 100
        info = t.info
        mcap = info.get("marketCap") or 1e9
        name = symbol.replace("-USD", "")
        return {"symbol": symbol, "name": name, "change": chg, "market_cap": mcap, "price": last}
    except: return None

@st.cache_data(ttl=300)
def get_heatmap_data(mode="sp"):
    symbols = TOP_SP_STOCKS + list(SECTOR_ETFS.keys()) if mode == "sp" else TOP_CRYPTOS
    with ThreadPoolExecutor(max_workers=15) as ex:
        results = list(ex.map(fetch_heatmap_item, symbols))
    return [r for r in results if r]

def create_heatmap(data, title):
    if not data: return None
    df = pd.DataFrame(data)
    df["label"] = df.apply(lambda r: f"{r['name']}<br>{r['change']:+.0f}%", axis=1)

    fig = px.treemap(
        df, path=["name"], values="market_cap", color="change",
        color_continuous_scale=["#FF4D4D", "#2A2F3A", "#3ECF8E"],
        color_continuous_midpoint=0,
    )
    fig.update_traces(
        texttemplate="%{label}",
        textfont=dict(size=15, family="IBM Plex Mono", color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><extra></extra>",
        marker=dict(line=dict(width=2, color="#0A0C10")),
        textposition="middle center"
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#EDEFF3", family="Space Grotesk")),
        height=440, margin=dict(t=55, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EDEFF3", family="IBM Plex Mono"),
        coloraxis_colorbar=dict(
            title=dict(text="1-Day % Change", font=dict(color="#7C8494", size=12)),
            tickfont=dict(color="#7C8494", size=11), thickness=14, len=0.65
        )
    )
    return fig

@st.cache_data(ttl=600)
def get_crypto_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8).json()
        d = r["data"][0]
        return int(d["value"]), d["value_classification"]
    except: return None, None

@st.cache_data(ttl=600)
def get_stock_fear_greed():
    try:
        vix = yf.Ticker("^VIX").history(period="5d")["Close"].iloc[-1]
        score = max(0, min(100, int(100 - (vix - 12) * 3.5)))
        if score <= 20: label = "Extreme Fear"
        elif score <= 40: label = "Fear"
        elif score <= 60: label = "Neutral"
        elif score <= 80: label = "Greed"
        else: label = "Extreme Greed"
        return score, label + " (VIX proxy)"
    except: return None, None

def create_fear_greed_gauge(score, title):
    if score is None: return None
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        domain={'x': [0.05, 0.95], 'y': [0.05, 0.85]},
        title={'text': title, 'font': {'size': 13, 'color': '#7C8494', 'family': 'IBM Plex Mono'}},
        number={'font': {'size': 36, 'color': '#EDEFF3', 'family': 'IBM Plex Mono'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#4B5160", 'tickfont': {'color': '#7C8494', 'size': 11}},
            'bar': {'color': "rgba(0,0,0,0)"}, 'bgcolor': "#12151b", 'borderwidth': 0,
            'steps': [
                {'range': [0, 25],  'color': 'rgba(255, 107, 107, 0.55)'},
                {'range': [25, 45], 'color': 'rgba(232, 163, 61, 0.45)'},
                {'range': [45, 55], 'color': 'rgba(200, 205, 216, 0.25)'},
                {'range': [55, 75], 'color': 'rgba(62, 207, 142, 0.45)'},
                {'range': [75, 100],'color': 'rgba(0, 200, 83, 0.55)'},
            ],
            'threshold': {'line': {'color': "#EDEFF3", 'width': 4}, 'thickness': 0.85, 'value': score}
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=20),
                      paper_bgcolor="#12151b", plot_bgcolor="#12151b", font={'color': "#EDEFF3"})
    return fig

@st.cache_data(ttl=3600)
def get_revenue_and_price(ticker):
    revenue_data = []
    price_data = None
    if FMP_API_KEY:
        try:
            url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=20&apikey={FMP_API_KEY}"
            res = requests.get(url, timeout=10).json()
            if isinstance(res, list):
                for item in reversed(res):
                    date = item.get("date")
                    rev = item.get("revenue")
                    if date and rev is not None:
                        revenue_data.append({"date": date, "revenue": rev})
        except: pass
    try:
        hist = yf.Ticker(ticker).history(period="5y")
        if not hist.empty:
            price_data = hist[["Close"]].reset_index()
            price_data.columns = ["date", "price"]
    except: pass
    return revenue_data, price_data

def create_revenue_price_chart(revenue_data, price_data, ticker):
    if not revenue_data or price_data is None or price_data.empty:
        return None
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    rev_dates = [r["date"] for r in revenue_data]
    rev_values = [r["revenue"] for r in revenue_data]
    fig.add_trace(go.Bar(x=rev_dates, y=rev_values, name="Revenue", marker_color="#E8A33D", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=price_data["date"], y=price_data["price"], name="Stock Price",
                             line=dict(color="#FF6B6B", width=2)), secondary_y=True)
    fig.update_layout(title=dict(text=f"{ticker} — Revenue vs Stock Price", font=dict(size=14, color="#EDEFF3")),
                      height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#EDEFF3", family="IBM Plex Mono"),
                      legend=dict(orientation="h", y=1.12), margin=dict(t=60, b=40))
    fig.update_yaxes(title_text="Revenue", secondary_y=False, gridcolor="#232833")
    fig.update_yaxes(title_text="Stock Price", secondary_y=True, gridcolor="#232833")
    fig.update_xaxes(gridcolor="#232833")
    latest_rev = rev_values[-1] if rev_values else None
    min_rev = min(rev_values) if rev_values else None
    max_rev = max(rev_values) if rev_values else None
    return fig, latest_rev, min_rev, max_rev

def resolve(text):
    t = text.strip().lower()
    if t in NAME_MAP:
        return NAME_MAP[t]
    # Common suffixes for international tickers
    if t.isdigit() and len(t) in (3, 4):
        return t + ".T"
    # Allow commodities and ETFs directly
    if any(x in t for x in ["=f", "-usd", ".l", ".de", ".pa", ".as"]):
        return text.strip().upper()
    return text.strip().upper()

def format_large_number(val, show_dollar=False):
    if val is None: return "—", ""
    try: v = float(val)
    except: return "—", ""
    abs_v = abs(v)
    prefix = "$" if show_dollar else ""
    if abs_v >= 1e12: return f"{prefix}{v/1e12:.2f}", "trillion"
    elif abs_v >= 1e9: return f"{prefix}{v/1e9:.2f}", "billion"
    elif abs_v >= 1e6: return f"{prefix}{v/1e6:.2f}", "million"
    elif abs_v >= 1e3: return f"{prefix}{v:,.1f}", ""
    return f"{prefix}{v:.2f}", ""

def get_status(val, good, ok=None, reverse=False, pct=False):
    if val is None: return "gray", "—"
    try: v = float(val)
    except: return "gray", "—"
    if reverse:
        status = "green" if v <= good else ("orange" if ok and v <= ok else "red")
    else:
        status = "green" if v >= good else ("orange" if ok and v >= ok else "red")
    display = f"{v*100:.1f}" if pct else f"{v:.1f}"
    return status, display

def get_btc_price():
    try: return yf.Ticker("BTC-USD").info.get("regularMarketPrice")
    except: return None

def get_shares_outstanding(ticker):
    try: return yf.Ticker(ticker).info.get("sharesOutstanding")
    except: return None

def get_fx_rate(currency):
    if not currency or currency.upper() == "USD": return 1.0
    try:
        rate = yf.Ticker(f"{currency.upper()}=X").info.get("regularMarketPrice")
        if rate and rate > 0:
            return float(rate)
    except: pass
    if currency.upper() == "JPY":
        return 0.00675
    return 1.0

def get_company_extra(ticker):
    summary, holders = None, []
    try:
        t = yf.Ticker(ticker)
        summary = t.info.get("longBusinessSummary")
        ih = t.institutional_holders
        if ih is not None and not ih.empty:
            for _, row in ih.head(8).iterrows():
                name = row.get("Holder") or "Unknown"
                pct = row.get("% Out") or row.get("pctOut")
                pct_str = f"{float(pct)*100:.1f}%" if pct and float(pct) < 1 else (f"{float(pct):.1f}%" if pct else "—")
                holders.append((str(name), pct_str))
    except: pass
    return summary, holders

def get_data(ticker):
    data = {
        "name": ticker, "sector": "", "source": "Yahoo",
        "forward_pe": None, "ev_ebitda": None, "fcf_yield": None,
        "roe": None, "operating_margin": None, "gross_margin": None,
        "debt_equity": None, "rev_growth": None, "current_price": None,
        "market_cap": None, "free_cashflow": None, "total_cash": None,
        "total_debt": None, "net_cash": None, "currency": "USD",
        "price_usd": None, "original_price": None
    }
    try:
        info = yf.Ticker(ticker).info
        data["name"] = info.get("shortName") or info.get("longName") or ticker
        data["sector"] = info.get("sector", "") or info.get("quoteType", "")
        data["forward_pe"] = info.get("forwardPE") or info.get("trailingPE")
        data["ev_ebitda"] = info.get("enterpriseToEbitda")
        data["market_cap"] = info.get("marketCap")
        data["fcf_yield"] = (info.get("freeCashflow") / info.get("marketCap")) if info.get("freeCashflow") and info.get("marketCap") else None
        data["roe"] = info.get("returnOnEquity")
        data["operating_margin"] = info.get("operatingMargins")
        data["gross_margin"] = info.get("grossMargins")
        data["debt_equity"] = info.get("debtToEquity")
        data["rev_growth"] = info.get("revenueGrowth")
        data["current_price"] = info.get("currentPrice") or info.get("regularMarketPrice")
        data["free_cashflow"] = info.get("freeCashflow")
        data["total_cash"] = info.get("totalCash")
        data["total_debt"] = info.get("totalDebt")
        data["currency"] = (info.get("currency") or "USD").upper()
    except: pass

    data["original_price"] = data["current_price"]

    # Force conversion for Japanese stocks
    is_japanese = ticker.endswith(".T") or data["currency"] in ["JPY", "¥"]
    if is_japanese or ticker == "3350.T":
        fx = get_fx_rate("JPY")
        if data["current_price"]:
            data["price_usd"] = data["current_price"] * fx
            data["currency"] = "JPY"
        if data.get("market_cap") and data["market_cap"] > 1e12:
            data["market_cap"] = data["market_cap"] * fx
    else:
        fx = get_fx_rate(data["currency"])
        if data["current_price"] and data["currency"] != "USD":
            data["price_usd"] = data["current_price"] * fx
        else:
            data["price_usd"] = data["current_price"]

    if data["total_cash"] is not None and data["total_debt"] is not None:
        data["net_cash"] = data["total_cash"] - data["total_debt"]
    return data

def get_peer_metrics(tickers, btc_price):
    rows = []
    for t in tickers:
        try:
            d = get_data(t)
            holdings = KNOWN_BTC_HOLDINGS.get(t)
            mcap = d.get("market_cap")
            price = d.get("price_usd")
            mnav = None
            if holdings and btc_price and mcap and mcap > 0:
                mnav = mcap / (holdings * btc_price)
            fcf_y = d.get("fcf_yield")
            pe = d.get("forward_pe")
            rows.append({
                "Ticker": t,
                "Price": f"${price:,.2f}" if price else "—",
                "mNAV": f"{mnav:.2f}x" if mnav else "—",
                "BTC Holdings": f"{holdings:,.0f}" if holdings else "—",
                "FCF Yield": f"{fcf_y*100:.1f}%" if fcf_y is not None else "—",
                "Fwd P/E": f"{pe:.1f}" if pe else "—",
            })
        except: continue
    return rows

def render_peer_table(rows):
    if not rows: return
    html = ['<table class="peer-table"><thead><tr>']
    headers = ["Ticker", "Price", "mNAV", "BTC Holdings", "FCF Yield", "Fwd P/E"]
    for h in headers: html.append(f"<th>{h}</th>")
    html.append("</tr></thead><tbody>")
    for r in rows:
        html.append("<tr>")
        for key in headers: html.append(f"<td>{r.get(key, '—')}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)

def count_greens(data):
    checks = [
        (data.get("forward_pe"), 18, 25, True),
        (data.get("ev_ebitda"), 12, 16, True),
        (data.get("fcf_yield"), 0.04, 0.03, False),
        (data.get("roe"), 0.12, 0.08, False),
        (data.get("operating_margin"), 0.15, 0.08, False),
        (data.get("gross_margin"), 0.30, 0.20, False),
        (data.get("rev_growth"), 0.05, 0, False),
        (data.get("debt_equity"), 1.0, 1.5, True),
    ]
    return sum(1 for val, good, ok, rev in checks if get_status(val, good, ok, rev)[0] == "green")

# ---------- HEADER ----------
st.markdown("""
<div class="term-header">
    <div class="term-dot"></div>
    <div class="term-title">DCA Terminal</div>
    <div class="term-sub">/ value screener + bitcoin treasury + market pulse</div>
</div>
""", unsafe_allow_html=True)

market_data = get_market_snapshot()
if market_data:
    st.markdown(build_ticker_html(market_data), unsafe_allow_html=True)

# Fear & Greed
stock_score, stock_label = get_stock_fear_greed()
crypto_score, crypto_label = get_crypto_fear_greed()
fg1, fg2 = st.columns(2)
with fg1:
    gauge = create_fear_greed_gauge(stock_score, "STOCK MARKET FEAR & GREED")
    if gauge:
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        if stock_label:
            st.markdown(f"<div style='text-align:center; font-family:Space Grotesk,sans-serif; font-size:0.95rem; color:#E8A33D; margin-top:-12px;'>{stock_label}</div>", unsafe_allow_html=True)
with fg2:
    gauge = create_fear_greed_gauge(crypto_score, "CRYPTO FEAR & GREED")
    if gauge:
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        if crypto_label:
            st.markdown(f"<div style='text-align:center; font-family:Space Grotesk,sans-serif; font-size:0.95rem; color:#E8A33D; margin-top:-12px;'>{crypto_label}</div>", unsafe_allow_html=True)

# Heatmap
st.markdown('<div class="section-label">Market Heatmap</div>', unsafe_allow_html=True)
heatmap_mode = st.radio("Select view", ["S&P Top 20 + Sectors", "Crypto"], horizontal=True, key="heatmap_mode")
hm_data = get_heatmap_data("sp" if heatmap_mode.startswith("S&P") else "crypto")
fig = create_heatmap(hm_data, f"{heatmap_mode} — Size by Market Cap · Color by 1-Day % Change")
if fig:
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.caption("Box size = Market Cap · Color = 1-day percentage price change")

st.markdown("")

# ---------- SIDEBAR ----------
st.sidebar.markdown("### Lookup")
ticker_input = st.sidebar.text_input("Ticker or company name", value=st.session_state.selected_ticker, key="ticker_input")
run = st.sidebar.button("Analyze", use_container_width=True)

if run and ticker_input:
    st.session_state.selected_ticker = resolve(ticker_input)

st.sidebar.markdown("---")
st.sidebar.markdown("### Bitcoin Treasury")
live_btc = get_btc_price()
st.sidebar.markdown(f"**Live BTC Price:** `${live_btc:,.0f}`" if live_btc else "**Live BTC Price:** —")
st.sidebar.caption("Leave BTC Holdings at 0 to use known public figure")
btc_holdings_input = st.sidebar.number_input("BTC Holdings", min_value=0.0, value=0.0, step=1.0, label_visibility="collapsed")
custom_btc_price = st.sidebar.number_input("Custom BTC Price (0 = live)", min_value=0.0, value=0.0, step=100.0, label_visibility="collapsed")

if FMP_API_KEY:
    st.sidebar.success("FMP key detected")
else:
    st.sidebar.info("No FMP key → limited revenue data")

# ---------- MAIN ----------
ticker = st.session_state.selected_ticker
data = get_data(ticker)
summary, holders = get_company_extra(ticker)

# Even if fundamentals are missing (ETFs / commodities), still show price
if not data.get("current_price") and not data.get("price_usd"):
    st.error(f"No price data found for **{ticker}**. Try a different ticker.")
else:
    price_usd = data.get("price_usd")
    original = data.get("original_price")
    currency = data.get("currency", "USD")
    price_str = f"${price_usd:,.2f}" if price_usd else "—"
    hover = f"Original: {original:,.2f} {currency}" if currency != "USD" and original else "USD"

    st.markdown(f"""
    <div class="ticker-bar">
        <div>
            <div class="ticker-name">{data["name"]}</div>
            <div class="ticker-meta">{ticker} · {data.get("sector") or "—"} · {data["source"]}</div>
        </div>
        <div class="ticker-price" title="{hover}">{price_str}</div>
    </div>""", unsafe_allow_html=True)

    if summary:
        short = summary[:480] + "…" if len(summary) > 480 else summary
        full_escaped = summary.replace('"', '&quot;')
        st.markdown(f"""
        <div class="section-label">Company Description</div>
        <div class="desc-box" data-full="{full_escaped}">{short}</div>
        """, unsafe_allow_html=True)

    # Bitcoin Treasury
    btc_price = custom_btc_price if custom_btc_price > 0 else live_btc
    btc_holdings = btc_holdings_input if btc_holdings_input > 0 else KNOWN_BTC_HOLDINGS.get(ticker)
    market_cap = data.get("market_cap")
    shares = get_shares_outstanding(ticker)
    net_senior_claims = KNOWN_SENIOR_CLAIMS.get(ticker, 0)

    if btc_holdings and btc_holdings > 0 and btc_price and market_cap and shares:
        btc_value = btc_holdings * btc_price
        mnav = market_cap / btc_value if btc_value else None
        btc_per_share = btc_holdings / shares
        mnav_status = "green" if mnav and mnav < 1.0 else ("orange" if mnav and mnav < 1.5 else "red")
        source_note = "manual" if btc_holdings_input > 0 else "known public figure"

        cebe_sats = cebe_mnav = claims_pct = None
        if net_senior_claims > 0:
            net_claims_btc = net_senior_claims / btc_price
            common_equity_btc = max(btc_holdings - net_claims_btc, 0)
            cebe_btc_per_share = common_equity_btc / shares
            cebe_sats = cebe_btc_per_share * 1e8
            cebe_nav = cebe_btc_per_share * btc_price
            cebe_mnav = data["price_usd"] / cebe_nav if cebe_nav > 0 else None
            claims_pct = (net_claims_btc / btc_holdings) * 100

        st.markdown('<div class="section-label">Bitcoin Treasury Metrics</div>', unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown(f"""
            <div class="btc-card" title="Market Cap ÷ BTC Holdings Value. Below 1.0x = discount to Bitcoin held.">
                <div class="btc-label">Current mNAV</div>
                <div class="metric-value">{f"{mnav:.2f}x" if mnav else "—"}</div>
                <div class="status status-{mnav_status}">{mnav_status.upper()}</div>
            </div>""", unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="btc-card" title="Total Bitcoin held by the company.">
                <div class="btc-label">BTC Holdings</div>
                <div class="metric-value">{btc_holdings:,.0f}</div>
                <div style="font-size:0.72rem; color:#7C8494;">{source_note}</div>
            </div>""", unsafe_allow_html=True)
        with b3:
            st.markdown(f"""
            <div class="btc-card" title="Bitcoin held per share.">
                <div class="btc-label">BTC per Share</div>
                <div class="metric-value">{f"{btc_per_share:.6f}"}</div>
            </div>""", unsafe_allow_html=True)
        with b4:
            main, unit = format_large_number(btc_value, show_dollar=True)
            st.markdown(f"""
            <div class="btc-card" title="Market value of all Bitcoin held.">
                <div class="btc-label">BTC Value</div>
                <div class="metric-value">{main} <span style="font-size:0.68rem; color:#7C8494;">{unit}</span></div>
                <div style="font-size:0.72rem; color:#7C8494;">@ ${btc_price:,.0f}</div>
            </div>""", unsafe_allow_html=True)

        if cebe_sats is not None:
            st.markdown('<div class="section-label">CEBE — Common Equity Bitcoin Exposure</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="btc-card" title="Sats belonging to common shareholders after senior claims.">
                    <div class="btc-label">CEBE</div>
                    <div class="metric-value">{cebe_sats:,.0f}</div>
                    <div style="font-size:0.72rem; color:#7C8494;">sats / share</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                status = "green" if cebe_mnav and cebe_mnav < 1.1 else ("orange" if cebe_mnav and cebe_mnav < 1.5 else "red")
                st.markdown(f"""
                <div class="btc-card" title="More accurate mNAV after senior claims.">
                    <div class="btc-label">CEBE mNAV</div>
                    <div class="metric-value">{f"{cebe_mnav:.2f}x" if cebe_mnav else "—"}</div>
                    <div class="status status-{status}">{status.upper()}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="btc-card" title="% of Bitcoin claimed by debt / preferred.">
                    <div class="btc-label">Claims %</div>
                    <div class="metric-value">{f"{claims_pct:.1f}%"}</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                sats_per_100 = (cebe_sats / data["price_usd"] * 100) if data.get("price_usd") else None
                st.markdown(f"""
                <div class="btc-card" title="Sats of common-equity Bitcoin per $100 invested.">
                    <div class="btc-label">Sats / $100</div>
                    <div class="metric-value">{f"{sats_per_100:,.0f}" if sats_per_100 else "—"}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-label">Implied Share Price by mNAV</div>', unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        for col, mult, label, tip in zip(
            [s1, s2, s3], [0.80, 1.15, 1.80],
            ["Bear · 0.80×", "Base · 1.15×", "Bull · 1.80×"],
            ["Share price at 0.80× Bitcoin value", "Share price at 1.15× premium", "Share price at 1.80× premium"]
        ):
            price = (btc_value * mult) / shares
            with col:
                st.markdown(f"""
                <div class="btc-card" title="{tip}">
                    <div class="btc-label">{label}</div>
                    <div class="metric-value">${price:,.2f}</div>
                </div>""", unsafe_allow_html=True)

        peers = PEER_GROUPS.get(ticker, [])
        if peers:
            st.markdown('<div class="section-label">Peer Comparison (Bitcoin Treasury)</div>', unsafe_allow_html=True)
            peer_rows = get_peer_metrics([ticker] + peers, btc_price)
            render_peer_table(peer_rows)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Click a ticker to analyze:")
            cols = st.columns(len([ticker] + peers))
            for i, p in enumerate([ticker] + peers):
                with cols[i]:
                    if st.button(p, key=f"peer_btn_{p}", use_container_width=True):
                        st.session_state.selected_ticker = p
                        st.rerun()

    # Metrics
    fair_value_pe = None
    if data.get("forward_pe") and data.get("price_usd") and data["forward_pe"] > 0:
        fair_value_pe = data["price_usd"] * (18 / data["forward_pe"])

    # Only use P/E method for the chart (Owner Earnings removed when negative)
    fair_value = fair_value_pe

    def card(title, value, status, suffix="", raw_value=None, tooltip="", is_money=False):
        if raw_value is not None:
            main, unit = format_large_number(raw_value, show_dollar=is_money)
            display_value = main
            unit_html = f'<span style="font-size:0.68rem; color:#7C8494; margin-left:5px;">{unit}</span>' if unit else ""
        else:
            display_value = value
            unit_html = ""
        st.markdown(f"""
        <div class="metric-card status-{status}" title="{tooltip}">
            <div class="metric-label">{title}</div>
            <div class="metric-row">
                <div class="metric-value">{display_value}{suffix if value != "—" else ""}{unit_html}</div>
                <div class="status status-{status}">{status.upper()}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="section-label">Valuation</div>', unsafe_allow_html=True)
        s, v = get_status(data.get("forward_pe"), 18, 25, reverse=True)
        card("Forward P/E", v, s, tooltip="Price ÷ expected future earnings")
        s, v = get_status(data.get("ev_ebitda"), 12, 16, reverse=True)
        card("EV / EBITDA", v, s, tooltip="Enterprise Value ÷ EBITDA")
        s, v = get_status(data.get("fcf_yield"), 0.04, 0.03, pct=True)
        card("FCF Yield", v, s, suffix="%", tooltip="Free Cash Flow ÷ Market Cap")

    with col2:
        st.markdown('<div class="section-label">Quality</div>', unsafe_allow_html=True)
        s, v = get_status(data.get("roe"), 0.12, 0.08, pct=True)
        card("ROE", v, s, suffix="%", tooltip="Return on Equity")
        s, v = get_status(data.get("operating_margin"), 0.15, 0.08, pct=True)
        card("Operating Margin", v, s, suffix="%", tooltip="Operating income ÷ Revenue")
        s, v = get_status(data.get("gross_margin"), 0.30, 0.20, pct=True)
        card("Gross Margin", v, s, suffix="%", tooltip="Gross profit ÷ Revenue")

    with col3:
        st.markdown('<div class="section-label">Balance & Cash</div>', unsafe_allow_html=True)
        card("Market Cap", "", "gray", raw_value=data.get("market_cap"), tooltip="Total market value", is_money=True)
        card("Cash & Equivalents", "", "gray", raw_value=data.get("total_cash"), tooltip="Cash + short-term investments", is_money=True)
        net = data.get("net_cash")
        if net is not None:
            card("Net Cash" if net >= 0 else "Net Debt", "", "green" if net >= 0 else "orange",
                 raw_value=abs(net), tooltip="Cash minus total debt", is_money=True)
        else:
            card("Net Cash / Debt", "—", "gray")
        card("Free Cash Flow", "", "gray", raw_value=data.get("free_cashflow"), tooltip="Cash after capex", is_money=True)

    # Fair Value (only P/E method now)
    if fair_value_pe:
        st.markdown('<div class="section-label">Fair Value Estimate</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="fv-card" title="Target forward P/E of 18">
            <div class="fv-label">P/E Method (target 18×)</div>
            <div class="fv-value">${fair_value_pe:.1f}</div>
            <div class="fv-note">Simple earnings multiple</div>
        </div>""", unsafe_allow_html=True)

    greens = count_greens(data)
    cls = "signal-green" if greens >= 5 else ("signal-orange" if greens >= 3 else "signal-red")
    label = "GREEN LIGHT — Strong candidate for DCA" if greens >= 5 else ("YELLOW — Acceptable" if greens >= 3 else "RED — Not ideal")
    st.markdown(f"""
    <div class="signal-banner {cls}">
        <span>{label}</span>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.8rem; opacity:0.8">{greens}/8 GREEN</span>
    </div>""", unsafe_allow_html=True)

    # Fair Value Iceberg Chart (only if we have a positive fair value)
    if fair_value and price_usd and fair_value > 0:
        st.markdown('<div class="section-label">Fair Value Chart</div>', unsafe_allow_html=True)
        try:
            hist = yf.Ticker(ticker).history(period="2y")
            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(hist.index) + list(hist.index[::-1]),
                    y=list(np.minimum(hist["Close"], fair_value)) + [fair_value] * len(hist),
                    fill="toself", fillcolor="rgba(62,207,142,0.18)", line=dict(width=0),
                    name="Below Fair Value", hoverinfo="skip"
                ))
                fig.add_trace(go.Scatter(
                    x=list(hist.index) + list(hist.index[::-1]),
                    y=list(np.maximum(hist["Close"], fair_value)) + [fair_value] * len(hist),
                    fill="toself", fillcolor="rgba(255,107,107,0.14)", line=dict(width=0),
                    name="Above Fair Value", hoverinfo="skip"
                ))
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist["Close"], mode="lines", name="Price",
                    line=dict(color="#7DD8FF", width=2.2)
                ))
                fig.add_hline(
                    y=fair_value, line_dash="dash", line_color="#E8A33D", line_width=1.6,
                    annotation_text=f"Fair Value ${fair_value:.0f}",
                    annotation_position="top left",
                    annotation_font_color="#E8A33D"
                )
                fig.update_layout(
                    height=460, template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=20),
                    legend=dict(orientation="h", y=1.1, font=dict(color="#EDEFF3")),
                    font=dict(color="#EDEFF3", family="IBM Plex Mono")
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except:
            st.info("Fair value chart not available")

    # Revenue vs Price
    st.markdown('<div class="section-label">Revenue vs Stock Price</div>', unsafe_allow_html=True)
    with st.spinner("Loading revenue data..."):
        rev_data, price_data = get_revenue_and_price(ticker)
        result = create_revenue_price_chart(rev_data, price_data, ticker)
    if result:
        fig, latest_rev, min_rev, max_rev = result
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            main, unit = format_large_number(latest_rev, show_dollar=True)
            st.metric("Latest Revenue", f"{main} {unit}")
        with c2:
            main, unit = format_large_number(min_rev, show_dollar=True)
            st.metric("Min (period)", f"{main} {unit}")
        with c3:
            main, unit = format_large_number(max_rev, show_dollar=True)
            st.metric("Max (period)", f"{main} {unit}")
        with c4:
            if latest_rev and min_rev and min_rev > 0:
                growth = ((latest_rev / min_rev) - 1) * 100
                st.metric("Total Change", f"+{growth:.0f}%")
    else:
        st.info("Revenue history not available for this ticker.")

    if holders:
        st.markdown('<div class="section-label">Major & Institutional Holders</div>', unsafe_allow_html=True)
        st.markdown('<div class="desc-box">', unsafe_allow_html=True)
        for name, pct in holders[:8]:
            st.markdown(f'<div class="holder-row"><span>{name}</span><span style="color:#E8A33D;">{pct}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

