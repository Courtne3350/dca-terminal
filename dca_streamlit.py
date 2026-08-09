import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor

# ============================================================
FMP_API_KEY = "EYvxgDDR8rkT4oLNN8UwawYcg2S8yofu"  # ← put your real key here
# ============================================================

st.set_page_config(page_title="DCA Terminal", page_icon="◆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.stApp { background: #0A0C10; color: #EDEFF3; font-family: 'Inter', sans-serif; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; color: #EDEFF3 !important; }
.metric-value, .mono { font-family: 'IBM Plex Mono', monospace; font-variant-numeric: tabular-nums; }

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
.term-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 700; color: #EDEFF3; }
.term-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #7C8494; }

.ticker-bar { background: linear-gradient(180deg, #171b23, #12151b); border: 1px solid #232833; border-left: 3px solid #E8A33D; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.ticker-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 600; }
.ticker-meta { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #7C8494; margin-top: 3px; }
.ticker-price { font-family: 'IBM Plex Mono', monospace; font-size: 1.7rem; font-weight: 600; }

.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: #7C8494; border-bottom: 1px solid #232833; padding-bottom: 7px; margin: 8px 0 14px 0; }

.metric-card {
    background: #12151b;
    border: 1px solid #232833;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 14px;
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
    min-height: 92px;
}
.metric-card.status-green {
    border-color: #3ECF8E;
    box-shadow: 0 0 0 1px rgba(62, 207, 142, 0.45),
                0 0 12px rgba(62, 207, 142, 0.25),
                0 0 24px rgba(62, 207, 142, 0.12);
}
.metric-card.status-orange {
    border-color: #E8A33D;
    box-shadow: 0 0 0 1px rgba(232, 163, 61, 0.45),
                0 0 12px rgba(232, 163, 61, 0.25),
                0 0 24px rgba(232, 163, 61, 0.12);
}
.metric-card.status-red {
    border-color: #FF6B6B;
    box-shadow: 0 0 0 1px rgba(255, 107, 107, 0.45),
                0 0 12px rgba(255, 107, 107, 0.25),
                0 0 24px rgba(255, 107, 107, 0.12);
}
.metric-card.status-gray {
    border-color: #4B5160;
    box-shadow: none;
}

.metric-label { color: #7C8494; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.metric-row { display: flex; justify-content: space-between; align-items: baseline; }
.metric-value { font-size: 1.45rem; font-weight: 600; color: #EDEFF3; }
.status { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px; }
.status-green { color: #3ECF8E; background: rgba(62,207,142,0.12); }
.status-red { color: #FF6B6B; background: rgba(255,107,107,0.12); }
.status-orange { color: #E8A33D; background: rgba(232,163,61,0.12); }
.status-gray { color: #7C8494; background: rgba(75,81,96,0.15); }

.fv-card { background: linear-gradient(165deg, #171b23, #12151b); border: 1px solid #232833; border-left: 3px solid #E8A33D; border-radius: 10px; padding: 16px 18px; }
.fv-label { color: #7C8494; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.fv-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.8rem; font-weight: 600; color: #E8A33D; }
.fv-note { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #7C8494; margin-top: 4px; }

.btc-card {
    background: linear-gradient(165deg, #1a1208, #12151b);
    border: 1px solid #3d2e1a;
    border-left: 3px solid #E8A33D;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 14px;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
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
    border-bottom: 1px solid #1e222b; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
}

.signal-banner { font-family: 'Space Grotesk', sans-serif; font-weight: 600; padding: 14px 18px; border-radius: 10px; margin: 18px 0; display: flex; justify-content: space-between; align-items: center; }
.signal-green { background: rgba(62,207,142,0.10); border: 1px solid rgba(62,207,142,0.35); color: #3ECF8E; }
.signal-orange { background: rgba(232,163,61,0.10); border: 1px solid rgba(232,163,61,0.35); color: #E8A33D; }
.signal-red { background: rgba(255,107,107,0.10); border: 1px solid rgba(255,107,107,0.35); color: #FF6B6B; }

section[data-testid="stSidebar"] { background: #12151b !important; border-right: 1px solid #232833; }
.stButton > button { background: #E8A33D !important; color: #0A0C10 !important; border: none; border-radius: 8px; font-family: 'Space Grotesk', sans-serif; font-weight: 600; width: 100%; }
.stSidebar label, .stSidebar p, .stSidebar .stMarkdown, .stSidebar span { color: #EDEFF3 !important; }
</style>
""", unsafe_allow_html=True)

# ---------- MARKET SNAPSHOT ----------
MARKET_SYMBOLS = {
    "^GSPC": "S&P 500", "QQQ": "Nasdaq-100", "^RUT": "Russell 2000", "^DJI": "Dow Jones", "^VIX": "VIX",
    "XLK": "Tech", "XLF": "Financials", "XLE": "Energy", "XLV": "Healthcare", "XLI": "Industrials",
    "XLY": "Cons. Disc.", "XLP": "Cons. Staples", "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate",
    "GC=F": "Gold", "SI=F": "Silver", "CL=F": "Crude Oil", "HG=F": "Copper", "BTC-USD": "Bitcoin",
    "^TNX": "10Y Yield", "^IRX": "13W Yield", "^TYX": "30Y Yield",
}

def fetch_one(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        if hist.empty:
            return None
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
        chg = ((last - prev) / prev) * 100 if prev else 0
        return {"symbol": symbol, "name": MARKET_SYMBOLS.get(symbol, symbol), "price": last, "chg": chg}
    except:
        return None

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
        items.append(
            f'<span class="ticker-item"><span class="sym">{d["name"]}</span>'
            f'{price_str} <span class="{cls}">{sign}{d["chg"]:.2f}%</span></span>'
        )
    content = "".join(items)
    return f'<div class="ticker-wrap"><div class="ticker-track">{content}{content}</div></div>'

# ---------- FEAR & GREED ----------
@st.cache_data(ttl=600)
def get_crypto_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8).json()
        d = r["data"][0]
        return int(d["value"]), d["value_classification"]
    except:
        return None, None

@st.cache_data(ttl=600)
def get_stock_fear_greed():
    try:
        r = requests.get("https://feargreedchart.com/api/?action=all", timeout=8).json()
        score = r.get("score", {}).get("score") or r.get("score")
        if score is not None:
            score = int(float(score))
            if score <= 20: label = "Extreme Fear"
            elif score <= 40: label = "Fear"
            elif score <= 60: label = "Neutral"
            elif score <= 80: label = "Greed"
            else: label = "Extreme Greed"
            return score, label
    except:
        pass
    try:
        vix = yf.Ticker("^VIX").history(period="5d")["Close"].iloc[-1]
        score = max(0, min(100, int(100 - (vix - 12) * 3.5)))
        if score <= 20: label = "Extreme Fear"
        elif score <= 40: label = "Fear"
        elif score <= 60: label = "Neutral"
        elif score <= 80: label = "Greed"
        else: label = "Extreme Greed"
        return score, label + " (VIX proxy)"
    except:
        return None, None

def create_fear_greed_gauge(score, title):
    if score is None:
        return None

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0.05, 0.95], 'y': [0.05, 0.85]},
        title={'text': title, 'font': {'size': 13, 'color': '#7C8494', 'family': 'IBM Plex Mono'}},
        number={'font': {'size': 36, 'color': '#EDEFF3', 'family': 'IBM Plex Mono'}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#4B5160",
                'tickfont': {'color': '#7C8494', 'size': 11}
            },
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "#12151b",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 25],  'color': 'rgba(255, 107, 107, 0.55)'},
                {'range': [25, 45], 'color': 'rgba(232, 163, 61, 0.45)'},
                {'range': [45, 55], 'color': 'rgba(200, 205, 216, 0.25)'},
                {'range': [55, 75], 'color': 'rgba(62, 207, 142, 0.45)'},
                {'range': [75, 100],'color': 'rgba(0, 200, 83, 0.55)'},
            ],
            'threshold': {
                'line': {'color': "#EDEFF3", 'width': 4},
                'thickness': 0.85,
                'value': score
            }
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=55, b=30),
        paper_bgcolor="#12151b",
        plot_bgcolor="#12151b",
        font={'color': "#EDEFF3"},
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color="#232833", width=1),
                fillcolor="rgba(0,0,0,0)"
            ),
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=0.008, y1=1,
                line=dict(width=0),
                fillcolor="#E8A33D"
            )
        ]
    )
    return fig

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

stock_score, stock_label = get_stock_fear_greed()
crypto_score, crypto_label = get_crypto_fear_greed()

fg1, fg2 = st.columns(2)
with fg1:
    gauge = create_fear_greed_gauge(stock_score, "STOCK MARKET FEAR & GREED")
    if gauge:
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        if stock_label:
            st.markdown(
                f"<div style='text-align:center; font-family:Space Grotesk; font-size:0.95rem; "
                f"color:#E8A33D; margin-top:-18px; margin-bottom:12px;'>{stock_label}</div>",
                unsafe_allow_html=True
            )

with fg2:
    gauge = create_fear_greed_gauge(crypto_score, "CRYPTO FEAR & GREED")
    if gauge:
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        if crypto_label:
            st.markdown(
                f"<div style='text-align:center; font-family:Space Grotesk; font-size:0.95rem; "
                f"color:#E8A33D; margin-top:-18px; margin-bottom:12px;'>{crypto_label}</div>",
                unsafe_allow_html=True
            )

st.markdown("")

NAME_MAP = {
    "strive": "ASST", "tesla": "TSLA", "apple": "AAPL", "walmart": "WMT",
    "microsoft": "MSFT", "nvidia": "NVDA", "siemens": "SIE.DE", "sap": "SAP.DE",
    "porsche": "P911.DE", "broadcom": "AVGO", "coca cola": "KO", "disney": "DIS",
    "meta": "META", "amazon": "AMZN", "google": "GOOGL", "metaplanet": "3350.T",
    "microstrategy": "MSTR", "strategy": "MSTR"
}

KNOWN_BTC_HOLDINGS = {
    "MSTR": 842138, "3350.T": 40177, "ASST": 19043, "TSLA": 11509,
}

def resolve(text):
    t = text.strip().lower()
    if t in NAME_MAP: return NAME_MAP[t]
    if t.isdigit() and len(t) in (3, 4): return t + ".T"
    if "." in text: return text.strip().upper()
    if FMP_API_KEY and FMP_API_KEY != "YOUR_KEY_HERE":
        try:
            res = requests.get(f"https://financialmodelingprep.com/api/v3/search?query={text}&limit=3&apikey={FMP_API_KEY}", timeout=6).json()
            if res: return res[0]["symbol"]
        except: pass
    try:
        res = requests.get("https://query1.finance.yahoo.com/v1/finance/search",
                           params={"q": text, "quotesCount": 3}, headers={"User-Agent": "Mozilla/5.0"}, timeout=6).json()
        for q in res.get("quotes", []):
            if q.get("quoteType") in ("EQUITY", "ETF"): return q["symbol"]
    except: pass
    return text.strip().upper()

def format_large_number(val):
    if val is None: return "—", ""
    try: v = float(val)
    except: return "—", ""
    abs_v = abs(v)
    if abs_v >= 1_000_000_000_000: return f"{v/1_000_000_000_000:.2f}", "trillion"
    elif abs_v >= 1_000_000_000: return f"{v/1_000_000_000:.2f}", "billion"
    elif abs_v >= 1_000_000: return f"{v/1_000_000:.2f}", "million"
    elif abs_v >= 1_000: return f"{v:,.1f}", ""
    else: return f"{v:.2f}", ""

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
    try:
        btc = yf.Ticker("BTC-USD").info
        return btc.get("regularMarketPrice") or btc.get("currentPrice")
    except: return None

def get_shares_outstanding(ticker):
    try: return yf.Ticker(ticker).info.get("sharesOutstanding")
    except: return None

def get_company_extra(ticker):
    summary, holders = None, []
    try:
        t = yf.Ticker(ticker)
        info = t.info
        summary = info.get("longBusinessSummary") or info.get("description")
        try:
            ih = t.institutional_holders
            if ih is not None and not ih.empty:
                for _, row in ih.head(8).iterrows():
                    name = row.get("Holder") or row.get("holder") or "Unknown"
                    pct = row.get("% Out") or row.get("pctOut") or row.get("pctHeld")
                    if pct is not None:
                        try: pct_str = f"{float(pct)*100:.1f}%" if float(pct) < 1 else f"{float(pct):.1f}%"
                        except: pct_str = str(pct)
                    else: pct_str = "—"
                    holders.append((str(name), pct_str))
        except: pass
    except: pass
    return summary, holders

def mini_bars(values=None):
    if values and len(values) >= 2:
        y = values
        bar_color = "#3ECF8E" if y[-1] > y[-2] else "#7DD8FF"
        caption = "TREND · LAST YEARS"
    else:
        y = [0.4, 0.55, 0.45, 0.6]
        bar_color = "#7DD8FF"
        caption = "NO TREND DATA"
    fig = go.Figure(go.Bar(x=[f"Y{i+1}" for i in range(len(y))], y=y,
                           marker=dict(color=bar_color, line=dict(width=0)), hoverinfo="skip"))
    fig.update_layout(height=70, margin=dict(l=0,r=0,t=4,b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig, caption

def get_data(ticker):
    data = {"name": ticker, "sector": "", "source": "Yahoo",
            "forward_pe": None, "ev_ebitda": None, "fcf_yield": None,
            "roe": None, "roic": None, "gross_margin": None,
            "debt_equity": None, "rev_growth": None, "current_price": None,
            "market_cap": None, "hist_roe": [], "hist_fcf": [], "hist_ev": []}
    if FMP_API_KEY and FMP_API_KEY != "YOUR_KEY_HERE":
        try:
            profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}", timeout=6).json()
            if profile:
                data["name"] = profile[0].get("companyName", ticker)
                data["sector"] = profile[0].get("sector", "")
                data["current_price"] = profile[0].get("price")
                data["market_cap"] = profile[0].get("mktCap")
                data["source"] = "FMP"
            metrics = requests.get(f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?limit=4&apikey={FMP_API_KEY}", timeout=6).json()
            if metrics:
                data["hist_roe"] = [m.get("roe") for m in reversed(metrics) if m.get("roe") is not None]
                data["hist_fcf"] = [m.get("freeCashFlowYield") for m in reversed(metrics) if m.get("freeCashFlowYield") is not None]
                data["hist_ev"] = [m.get("enterpriseValueOverEBITDA") for m in reversed(metrics) if m.get("enterpriseValueOverEBITDA") is not None]
                latest = metrics[0]
                data["roe"] = latest.get("roe")
                data["roic"] = latest.get("roic")
                data["fcf_yield"] = latest.get("freeCashFlowYield")
                data["ev_ebitda"] = latest.get("enterpriseValueOverEBITDA")
                data["debt_equity"] = latest.get("debtToEquity")
            ratios = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?limit=1&apikey={FMP_API_KEY}", timeout=6).json()
            if ratios:
                data["forward_pe"] = ratios[0].get("forwardPE") or ratios[0].get("priceEarningsRatio")
                data["gross_margin"] = ratios[0].get("grossProfitMargin")
                data["rev_growth"] = ratios[0].get("revenueGrowth")
            if data["current_price"] is not None: return data
        except: pass
    try:
        info = yf.Ticker(ticker).info
        data["name"] = info.get("shortName") or info.get("longName") or ticker
        data["sector"] = info.get("sector", "")
        data["source"] = "Yahoo"
        data["forward_pe"] = info.get("forwardPE") or info.get("trailingPE")
        data["ev_ebitda"] = info.get("enterpriseToEbitda")
        fcf = info.get("freeCashflow")
        mcap = info.get("marketCap")
        data["market_cap"] = mcap
        data["fcf_yield"] = (fcf / mcap) if fcf and mcap else None
        data["roe"] = info.get("returnOnEquity")
        data["roic"] = info.get("returnOnCapital") or info.get("returnOnAssets")
        data["gross_margin"] = info.get("grossMargins")
        data["debt_equity"] = info.get("debtToEquity")
        data["rev_growth"] = info.get("revenueGrowth")
        data["current_price"] = info.get("currentPrice") or info.get("regularMarketPrice")
    except: pass
    return data

def count_greens(data):
    return sum(1 for val, good, ok, rev in [
        (data.get("forward_pe"), 18, 25, True),
        (data.get("ev_ebitda"), 12, 16, True),
        (data.get("fcf_yield"), 0.04, 0.03, False),
        (data.get("roe"), 0.12, 0.08, False),
        (data.get("roic"), 0.10, 0.07, False),
        (data.get("gross_margin"), 0.30, 0.20, False),
        (data.get("rev_growth"), 0.05, 0, False),
        (data.get("debt_equity"), 1.0, 1.5, True),
    ] if get_status(val, good, ok, rev)[0] == "green")

# ---------- SIDEBAR ----------
st.sidebar.markdown("### Lookup")
ticker_input = st.sidebar.text_input("Ticker or company name", value="MSTR", label_visibility="collapsed")
run = st.sidebar.button("Analyze", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### Bitcoin Treasury")
live_btc = get_btc_price()
st.sidebar.markdown(f"**Live BTC Price:** `${live_btc:,.0f}`" if live_btc else "**Live BTC Price:** —")
st.sidebar.markdown("**BTC Holdings**")
st.sidebar.caption("Leave at 0 to use known public figure")
btc_holdings_input = st.sidebar.number_input("BTC Holdings", min_value=0.0, value=0.0, step=1.0, label_visibility="collapsed")
st.sidebar.markdown("**Custom BTC Price**")
st.sidebar.caption("Optional – leave 0 for live price")
custom_btc_price = st.sidebar.number_input("Custom BTC Price", min_value=0.0, value=0.0, step=100.0, label_visibility="collapsed")

if FMP_API_KEY and FMP_API_KEY != "YOUR_KEY_HERE":
    st.sidebar.success("FMP key detected")
else:
    st.sidebar.info("No FMP key → using Yahoo")

# ---------- MAIN ----------
if run and ticker_input:
    ticker = resolve(ticker_input)
    data = get_data(ticker)
    summary, holders = get_company_extra(ticker)

    if not data.get("name"):
        st.error(f"No data for **{ticker}**")
    else:
        price_str = f"${data['current_price']:.2f}" if data.get("current_price") else "—"
        st.markdown(f"""
        <div class="ticker-bar">
            <div>
                <div class="ticker-name">{data["name"]}</div>
                <div class="ticker-meta">{ticker} · {data.get("sector") or "—"} · {data["source"]}</div>
            </div>
            <div class="ticker-price">{price_str}</div>
        </div>""", unsafe_allow_html=True)

        if summary:
            short = summary[:480] + "…" if len(summary) > 480 else summary
            full_escaped = summary.replace('"', '&quot;').replace("'", "&#39;")
            st.markdown(f"""
            <div class="section-label">Company Description</div>
            <div class="desc-box" data-full="{full_escaped}" title="Hover for full description">{short}</div>
            """, unsafe_allow_html=True)

        btc_price = custom_btc_price if custom_btc_price > 0 else live_btc
        btc_holdings = btc_holdings_input if btc_holdings_input > 0 else KNOWN_BTC_HOLDINGS.get(ticker)
        market_cap = data.get("market_cap")
        shares = get_shares_outstanding(ticker)

        if btc_holdings and btc_holdings > 0 and btc_price and market_cap:
            btc_value = btc_holdings * btc_price
            mnav = market_cap / btc_value if btc_value > 0 else None
            btc_per_share = btc_holdings / shares if shares and shares > 0 else None
            mnav_status = "green" if mnav and mnav < 1.0 else ("orange" if mnav and mnav < 1.5 else "red")
            source_note = "manual" if btc_holdings_input > 0 else "known public figure"

            st.markdown('<div class="section-label">Bitcoin Treasury Metrics</div>', unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.markdown(f"""
                <div class="btc-card" title="mNAV = Market Cap ÷ BTC Holdings Value. Below 1.0x means the stock trades at a discount to its Bitcoin.">
                    <div class="btc-label">Current mNAV</div>
                    <div class="metric-value">{f"{mnav:.2f}x" if mnav else "—"}</div>
                    <div class="status status-{mnav_status}">{mnav_status.upper()}</div>
                </div>""", unsafe_allow_html=True)
            with b2:
                st.markdown(f"""
                <div class="btc-card" title="Total Bitcoin held by the company (manual input or known public figure).">
                    <div class="btc-label">BTC Holdings</div>
                    <div class="metric-value">{btc_holdings:,.0f}</div>
                    <div style="font-size:0.72rem; color:#7C8494; margin-top:4px;">{source_note}</div>
                </div>""", unsafe_allow_html=True)
            with b3:
                st.markdown(f"""
                <div class="btc-card" title="Bitcoin held per share outstanding. Useful for comparing treasury strength across companies.">
                    <div class="btc-label">BTC per Share</div>
                    <div class="metric-value">{f"{btc_per_share:.6f}" if btc_per_share else "—"}</div>
                </div>""", unsafe_allow_html=True)
            with b4:
                main, unit = format_large_number(btc_value)
                st.markdown(f"""
                <div class="btc-card" title="Current market value of the company's Bitcoin holdings.">
                    <div class="btc-label">BTC Value</div>
                    <div class="metric-value">{main} <span style="font-size:0.68rem; color:#7C8494;">{unit}</span></div>
                    <div style="font-size:0.72rem; color:#7C8494; margin-top:4px;">@ ${btc_price:,.0f}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-label">Implied Share Price by mNAV</div>', unsafe_allow_html=True)
            s1, s2, s3 = st.columns(3)
            bear = (btc_value * 0.80) / shares if shares else None
            base = (btc_value * 1.15) / shares if shares else None
            bull = (btc_value * 1.80) / shares if shares else None
            with s1:
                st.markdown(f"""
                <div class="btc-card" title="Implied share price if the stock trades at 0.80× the value of its Bitcoin (discount scenario).">
                    <div class="btc-label">Bear · 0.80×</div>
                    <div class="metric-value">${bear:,.2f}</div>
                    <div style="font-size:0.72rem; color:#7C8494; margin-top:4px;">discount</div>
                </div>""", unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                <div class="btc-card" title="Implied share price if the stock trades at 1.15× the value of its Bitcoin (modest premium).">
                    <div class="btc-label">Base · 1.15×</div>
                    <div class="metric-value">${base:,.2f}</div>
                    <div style="font-size:0.72rem; color:#7C8494; margin-top:4px;">modest premium</div>
                </div>""", unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                <div class="btc-card" title="Implied share price if the stock trades at 1.80× the value of its Bitcoin (high premium scenario).">
                    <div class="btc-label">Bull · 1.80×</div>
                    <div class="metric-value">${bull:,.2f}</div>
                    <div style="font-size:0.72rem; color:#7C8494; margin-top:4px;">high premium</div>
                </div>""", unsafe_allow_html=True)
            st.caption("Leave holdings at 0 to use the latest known public figure.")
            st.markdown("")

        fair_value = None
        if data.get("forward_pe") and data.get("current_price") and data["forward_pe"] > 0:
            fair_value = data["current_price"] * (18 / data["forward_pe"])

        def card(title, value, status, hist=None, suffix="", raw_value=None, tooltip=""):
            if raw_value is not None:
                main, unit = format_large_number(raw_value)
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

            fig, caption = mini_bars(hist)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=title)
            st.caption(caption)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="section-label">Valuation</div>', unsafe_allow_html=True)
            s, v = get_status(data.get("forward_pe"), 18, 25, reverse=True)
            card("Forward P/E", v, s, tooltip="Price divided by expected future earnings. Lower is generally better for value investors.")
            s, v = get_status(data.get("ev_ebitda"), 12, 16, reverse=True)
            card("EV / EBITDA", v, s, data.get("hist_ev"), tooltip="Enterprise Value / EBITDA. Measures valuation independent of capital structure. Lower is better.")
            s, v = get_status(data.get("fcf_yield"), 0.04, 0.03, pct=True)
            card("FCF Yield", v, s, data.get("hist_fcf"), suffix="%", tooltip="Free Cash Flow ÷ Market Cap. Higher yield means the company generates more cash relative to its price.")

        with col2:
            st.markdown('<div class="section-label">Quality</div>', unsafe_allow_html=True)
            s, v = get_status(data.get("roe"), 0.12, 0.08, pct=True)
            card("ROE", v, s, data.get("hist_roe"), suffix="%", tooltip="Return on Equity. How effectively the company uses shareholder capital. Higher is better.")
            s, v = get_status(data.get("roic"), 0.10, 0.07, pct=True)
            card("ROIC", v, s, suffix="%", tooltip="Return on Invested Capital. Measures true economic profitability after the cost of capital.")
            s, v = get_status(data.get("gross_margin"), 0.30, 0.20, pct=True)
            card("Gross Margin", v, s, suffix="%", tooltip="Gross Profit ÷ Revenue. Shows pricing power and production efficiency. Higher is better.")

        with col3:
            st.markdown('<div class="section-label">Balance & Growth</div>', unsafe_allow_html=True)
            card("Market Cap", "", "gray", raw_value=data.get("market_cap"),
                 tooltip="Total market value of all outstanding shares.")
            de_val = data.get("debt_equity")
            if de_val is not None and de_val > 100:
                card("Debt / Equity", "—", "gray", tooltip="Total Debt ÷ Shareholders' Equity. Lower leverage is generally safer.")
            else:
                s, v = get_status(de_val, 1.0, 1.5, reverse=True)
                card("Debt / Equity", v, s, raw_value=de_val,
                     tooltip="Total Debt ÷ Shareholders' Equity. Lower leverage is generally safer.")
            s, v = get_status(data.get("rev_growth"), 0.05, 0, pct=True)
            card("Revenue Growth", v, s, suffix="%", tooltip="Year-over-year growth in sales. Positive and accelerating growth is preferred.")

            if fair_value:
                st.markdown(f"""
                <div class="fv-card" title="Simple fair value estimate using a target Forward P/E of 18.">
                    <div class="fv-label">Est. Fair Value</div>
                    <div class="fv-value">${fair_value:.1f}</div>
                    <div class="fv-note">target P/E 18</div>
                </div>""", unsafe_allow_html=True)

        greens = count_greens(data)
        if greens >= 5:
            cls, label = "signal-green", "GREEN LIGHT — Strong candidate for DCA"
        elif greens >= 3:
            cls, label = "signal-orange", "YELLOW — Acceptable, consider smaller size"
        else:
            cls, label = "signal-red", "RED — Not ideal for DCA right now"
        st.markdown(f"""
        <div class="signal-banner {cls}"><span>{label}</span>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.8rem; opacity:0.8">{greens}/8 GREEN</span></div>""", unsafe_allow_html=True)

        if holders:
            st.markdown('<div class="section-label">Major & Institutional Holders</div>', unsafe_allow_html=True)
            st.markdown('<div class="desc-box">', unsafe_allow_html=True)
            for name, pct in holders[:8]:
                st.markdown(f'<div class="holder-row"><span>{name}</span><span style="color:#E8A33D;">{pct}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("Top institutional holders (proxy for large ETF / index ownership).")

        st.markdown('<div class="section-label">Price vs Fair Value</div>', unsafe_allow_html=True)
        try:
            hist = yf.Ticker(ticker).history(period="2y")
            if not hist.empty and fair_value is not None:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(hist.index)+list(hist.index[::-1]),
                    y=list(np.minimum(hist["Close"], fair_value))+[fair_value]*len(hist),
                    fill="toself", fillcolor="rgba(62,207,142,0.18)", line=dict(width=0),
                    name="Below Fair Value", hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=list(hist.index)+list(hist.index[::-1]),
                    y=list(np.maximum(hist["Close"], fair_value))+[fair_value]*len(hist),
                    fill="toself", fillcolor="rgba(255,107,107,0.14)", line=dict(width=0),
                    name="Above Fair Value", hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Price",
                    line=dict(color="#7DD8FF", width=2.2)))
                fig.add_hline(y=fair_value, line_dash="dash", line_color="#E8A33D", line_width=1.6,
                    annotation_text=f"Fair Value ${fair_value:.0f}", annotation_position="top left",
                    annotation_font_color="#E8A33D")
                fig.update_layout(height=460, template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=20), legend=dict(orientation="h", y=1.1, font=dict(color="#EDEFF3")),
                    font=dict(color="#EDEFF3"))
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart not available")
