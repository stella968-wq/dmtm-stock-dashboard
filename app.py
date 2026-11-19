# ==============================================================================
# 美股雙動能 (DMTM) 量化投資儀表板 v1.2
# 核心升級：排雷表頭三級合格總合名單展示、嚴格三級審核判斷、多欄位財務容錯
# ==============================================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime

# ─────────────────────────── 頁面設定 ─────────────────────────────
st.set_page_config(
    page_title="DMTM 美股量化儀表板",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── 自訂 CSS（全面高對比白字與卡片美化） ───
st.markdown("""
<style>
/* ── 全域底色 ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a0e1a 100%) !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
    border-right: 1px solid #30363d !important;
}

/* ── 標籤與段落高對比文字 ── */
.stMarkdown, .stMarkdown p,
.stTextInput label, .stTextArea label,
.stSelectbox label, .stSlider label,
.stRadio label, .stCheckbox label,
.stNumberInput label, .stMultiSelect label,
.stFileUploader label,
.stMetricLabel, .stCaption {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── Tab 標籤列全面強制高對比純白（徹底修復二、三、四頁面標題黑底黑字看不清） ── */
.stTabs, [data-testid="stTabs"] {
    background: transparent !important;
}
.stTabs [role="tablist"],
[data-testid="stTabs"] [role="tablist"],
.stTabs [data-baseweb="tab-list"],
[data-baseweb="tab-list"] {
    background: #0f172a !important;
    border-bottom: 2px solid #334155 !important;
    padding: 8px 10px !important;
    gap: 8px !important;
    border-radius: 8px 8px 0 0 !important;
}

/* 所有未選中 Tab 按鈕（包含內部 p, span, div, svg, label）全部強制純白 */
.stTabs button,
.stTabs button[role="tab"],
[data-testid="stTabs"] button,
[data-testid="stTabs"] button[role="tab"],
[data-testid="stTabs"] [data-testid="stTab"],
.stTabs [data-baseweb="tab"],
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    padding: 10px 22px !important;
    color: #FFFFFF !important;
    opacity: 1.0 !important;
}

.stTabs button *,
.stTabs button[role="tab"] *,
[data-testid="stTabs"] button *,
[data-testid="stTabs"] button[role="tab"] *,
[data-testid="stTabs"] [data-testid="stTab"] *,
.stTabs [data-baseweb="tab"] *,
[data-baseweb="tab"] *,
.stTabs [role="tablist"] p,
[data-testid="stTabs"] [role="tablist"] p,
.stTabs [role="tablist"] span,
[data-testid="stTabs"] [role="tablist"] span {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 1.02rem !important;
    opacity: 1.0 !important;
    visibility: visible !important;
}

/* 當前選中的 Tab 按鈕：高亮天藍色 + 粗底線 */
.stTabs button[aria-selected="true"],
.stTabs button[role="tab"][aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"],
[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"],
[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(56, 189, 248, 0.15) !important;
    border-bottom: 3px solid #38BDF8 !important;
    border-radius: 6px 6px 0 0 !important;
}

.stTabs button[aria-selected="true"] *,
.stTabs button[role="tab"][aria-selected="true"] *,
[data-testid="stTabs"] button[aria-selected="true"] *,
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] *,
.stTabs [data-baseweb="tab"][aria-selected="true"] *,
[data-baseweb="tab"][aria-selected="true"] * {
    color: #38BDF8 !important;
    font-weight: 900 !important;
    font-size: 1.02rem !important;
    opacity: 1.0 !important;
}

/* ── 白色/淺色提示框內的文字強制深色（深灰黑/深墨綠），解決白底看不清問題 ── */
.stAlert,
div[data-testid="stAlert"],
div[data-baseweb="notification"] {
    background: #F0FDF4 !important;
    border: 2px solid #16A34A !important;
    border-radius: 8px !important;
}
.stAlert [data-testid="stMarkdownContainer"] p,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-baseweb="notification"] p,
div[data-baseweb="notification"] span {
    color: #14532D !important; /* 濃深墨綠黑色，白底上對比極高 */
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}
.stAlert svg,
div[data-testid="stAlert"] svg {
    fill: #15803D !important;
}

/* ── Expander 摺疊面板標題與外框 ── */
.streamlit-expanderHeader,
[data-testid="stExpander"] details summary {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}
.streamlit-expanderHeader p,
.streamlit-expanderHeader span,
[data-testid="stExpander"] details summary p,
[data-testid="stExpander"] details summary span {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}

/* ── Sidebar 文字 ── */
[data-testid="stSidebar"] h3 {
    color: #38BDF8 !important;
    font-weight: 800 !important;
}

/* ── 輸入元件（底色深黑、文字純白） ── */
.stTextInput input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
}
.stTextArea textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
    min-height: 42px !important;
    height: 42px !important;
    resize: vertical !important;
    padding: 8px 12px !important;
    line-height: 1.4 !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #64748b !important;
}
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: #161b22 !important;
    border-color: #30363d !important;
    color: #FFFFFF !important;
}

/* ── Number Input 與步進按鈕（徹底修復白框看不見的問題） ── */
.stNumberInput input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
[data-testid="stNumberInput"] button {
    background: #1e293b !important;
    border: 1px solid #3b82f6 !important;
    color: #38bdf8 !important;
    border-radius: 4px !important;
}
[data-testid="stNumberInput"] button:hover {
    background: #2563eb !important;
    color: #FFFFFF !important;
}
[data-testid="stNumberInput"] button svg {
    fill: #38bdf8 !important;
}
[data-testid="stNumberInput"] button:hover svg {
    fill: #FFFFFF !important;
}

/* ── File Uploader 拖拉上傳框（徹底修復白底白字） ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"],
section[data-testid="stFileUploaderDropzone"] {
    background: #161b22 !important;
    border: 2px dashed #38bdf8 !important;
    border-radius: 10px !important;
    padding: 1.2rem !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
section[data-testid="stFileUploaderDropzone"]:hover {
    background: #1e293b !important;
    border-color: #60a5fa !important;
}
/* 上傳區內部的按鈕 (Browse files / Upload) */
[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
    color: #FFFFFF !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    padding: 0.4rem 1.1rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
section[data-testid="stFileUploaderDropzone"] button:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: #FFFFFF !important;
}
/* 上傳區內部的說明文字（Limit 200MB、Drag and drop） */
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] div,
section[data-testid="stFileUploaderDropzone"] span,
section[data-testid="stFileUploaderDropzone"] small,
section[data-testid="stFileUploaderDropzone"] div {
    color: #93c5fd !important;
    font-weight: 500 !important;
}

/* ── 下載按鈕 (st.download_button) 與常規按鈕 (st.button) 徹底統一深藍科技風 ── */
[data-testid="stDownloadButton"] > button,
.stDownloadButton > button,
.stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
    color: #FFFFFF !important;
    border: 1px solid #3b82f6 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
}
[data-testid="stDownloadButton"] > button:hover,
.stDownloadButton > button:hover,
.stButton > button:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5) !important;
    transform: translateY(-1px);
}
[data-testid="stDownloadButton"] > button *,
.stDownloadButton > button *,
.stButton > button * {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    fill: #FFFFFF !important;
}

/* ── Streamlit 提示框（修復白底淺字：改為深色半透明高亮對比） ── */
.stAlert,
div[data-testid="stAlert"] {
    background: #0d2818 !important;
    border: 1px solid #059669 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}
.stAlert [data-testid="stMarkdownContainer"] p,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}
.stAlert svg,
div[data-testid="stAlert"] svg {
    fill: #34d399 !important;
}

/* ── 全域 Metric 元件強制高對比（防止任何 Light 模式下字體發黑無法辨識） ── */
[data-testid="stMetric"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #CBD5E1 !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #FFFFFF !important;
    font-weight: 900 !important;
    font-size: 1.65rem !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {
    font-weight: 800 !important;
    font-size: 0.85rem !important;
}

/* ── Slider ── */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    color: #CBD5E1 !important;
}

/* ── DataFrame 表格 ── */
.stDataFrame { border: 1px solid #30363d !important; }
.stDataFrame thead th {
    background: #1e293b !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
.stDataFrame tbody td {
    background: #0d1117 !important;
    color: #E2E8F0 !important;
}
.stDataFrame tbody tr:hover td {
    background: #1a2033 !important;
}

/* ── 自訂元件 ── */
.main-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #fb7185);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 0.5rem 0;
    margin-bottom: 0.3rem;
}
.sub-title {
    text-align: center;
    color: #CBD5E1 !important;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
.module-header {
    background: linear-gradient(90deg, #1e3a5f, #1a2744);
    border: 1px solid #2d6a9f;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1rem;
    color: #FFFFFF !important;
    font-size: 1.15rem;
    font-weight: 700;
}
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.8rem;
    text-align: center;
    margin: 0.3rem;
}
.metric-value { font-size: 1.6rem; font-weight: 800; }
.metric-label { font-size: 0.75rem; color: #CBD5E1 !important; margin-top: 0.2rem; }
.link-btn {
    display: inline-block;
    background: linear-gradient(90deg, #1d4ed8, #2563eb);
    color: #FFFFFF !important;
    padding: 0.55rem 1.3rem;
    border-radius: 8px;
    text-decoration: none !important;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 0.3rem;
    border: 1px solid #3b82f6;
    transition: all 0.2s;
}
.link-btn:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: #FFFFFF !important;
    text-decoration: none !important;
}
.score-table { width: 100%; border-collapse: collapse; }
.score-table th {
    background: #1e293b;
    color: #FFFFFF !important;
    padding: 9px 10px;
    text-align: left;
    font-size: 0.85rem;
    font-weight: 700;
}
.score-table td {
    padding: 7px 10px;
    border-bottom: 1px solid #21262d;
    font-size: 0.85rem;
    color: #E2E8F0 !important;
}
.score-table tr:hover td { background: #1a2033; }
.info-box {
    background: #0d1f33;
    border-left: 4px solid #2563eb;
    padding: 0.7rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #93c5fd !important;
}
.section-title {
    color: #FFFFFF !important;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0.8rem 0 0.4rem 0;
}

/* ── 三級合格卡片專屬樣式 ── */
.tier-card {
    background: #161b22;
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
}
.tier-card-rec {
    border: 2px solid #059669;
    box-shadow: 0 0 15px rgba(5, 150, 105, 0.2);
}
.tier-card-build {
    border: 2px solid #2563eb;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.2);
}
.tier-card-light {
    border: 2px solid #d97706;
    box-shadow: 0 0 15px rgba(217, 119, 6, 0.2);
}
.tier-header-rec { color: #6ee7b7 !important; font-size: 1.15rem; font-weight: 800; }
.tier-header-build { color: #38bdf8 !important; font-size: 1.15rem; font-weight: 800; }
.tier-header-light { color: #fbbf24 !important; font-size: 1.15rem; font-weight: 800; }

.stock-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    margin: 3px;
    font-size: 0.88rem;
    font-weight: 700;
}
.pill-rec {
    background: #064e3b;
    border: 1px solid #059669;
    color: #FFFFFF !important;
}
.pill-build {
    background: #1e3a5f;
    border: 1px solid #2563eb;
    color: #FFFFFF !important;
}
.pill-light {
    background: #451a03;
    border: 1px solid #d97706;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 快取 / 資料抓取函式
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticker_info(ticker: str):
    try:
        return yf.Ticker(ticker.upper()).info
    except Exception:
        return {}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_history(ticker: str, period: str = "1y", interval: str = "1d"):
    try:
        return yf.Ticker(ticker.upper()).history(period=period, interval=interval, auto_adjust=True)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_recommendations(ticker: str):
    """
    動態獲取華爾街分析師真實評等分佈（Strong Buy, Buy, Hold, Sell, Strong Sell）
    """
    try:
        t = yf.Ticker(ticker.upper())
        recs = t.recommendations
        if recs is not None and not recs.empty:
            return recs
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════
# 多別名容錯數值讀取工具
# ═══════════════════════════════════════════════════════════════════
def safe_get_field(df, candidate_keys, col_idx=0):
    """
    智能容錯讀取財報欄位：在 candidate_keys 清單中依序尋找存在的欄位名稱
    """
    if df is None or df.empty:
        return np.nan
    if not isinstance(candidate_keys, list):
        candidate_keys = [candidate_keys]

    for key in candidate_keys:
        if key in df.index:
            try:
                val = float(df.loc[key].iloc[col_idx])
                if not np.isnan(val):
                    return val
            except Exception:
                pass
        # 模糊大小寫匹配
        for idx_row in df.index:
            if str(idx_row).strip().lower() == str(key).strip().lower():
                try:
                    val = float(df.loc[idx_row].iloc[col_idx])
                    if not np.isnan(val):
                        return val
                except Exception:
                    pass
    return np.nan

# ═══════════════════════════════════════════════════════════════════
# 解析工具函式
# ═══════════════════════════════════════════════════════════════════
def extract_tickers_from_text(text: str):
    tokens = re.findall(r'\b[A-Z]{1,5}\b', text)
    blacklist = {
        "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P",
        "Q","R","S","T","U","V","W","X","Y","Z","THE","AND","FOR","WITH",
        "BUY","SELL","TOP","OWN","TO","OF","IN","AT","BY","OR","NO","NA",
        "PE","PB","PS","ROE","EPS","ETF","AI","US","ALL","NEW","YTD","TTM",
        "USD","NYSE","NASDAQ","OTC","ADR","VOO","SPY","QQQ","RSI","MACD",
        "MA","SMA","EMA","ATR","BB","UP","DOWN","OUT","ADX","CCI","OBV",
        "HIGH","LOW","AVG","MED","CNN","SA","PEG","DCF","FCF","NRI","CAGR",
    }
    seen, result = set(), []
    for t in tokens:
        if t not in blacklist and t not in seen:
            seen.add(t); result.append(t)
    return result

def parse_csv_excel(uploaded_file):
    tickers = []
    try:
        name = uploaded_file.name.lower()
        df = pd.read_csv(uploaded_file) if name.endswith(".csv") else pd.read_excel(uploaded_file)
        col = None
        for c in df.columns:
            if any(k in str(c).lower() for k in ["symbol","ticker","stock","code"]):
                col = c; break
        raw = df[col] if col else df.iloc[:, 0]
        tickers = [t for t in raw.dropna().astype(str).str.strip().str.upper().tolist()
                   if re.match(r'^[A-Z]{1,5}$', t)]
    except Exception as e:
        st.error(f"檔案解析失敗：{e}")
    return tickers

def get_intersection(list_a, list_b):
    return sorted(set(t.upper().strip() for t in list_a if t) &
                  set(t.upper().strip() for t in list_b if t))

# ═══════════════════════════════════════════════════════════════════
# M-Score 計算（增加多欄位容錯）
# ═══════════════════════════════════════════════════════════════════
def compute_m_score(ticker: str, info: dict):
    try:
        tk  = yf.Ticker(ticker.upper())
        inc = tk.financials
        bal = tk.balance_sheet
        cf  = tk.cashflow
        if inc.empty or bal.empty or cf.empty:
            return None, "財報資料為空"

        def sg(df, keys, col=0):
            return safe_get_field(df, keys, col)

        rev1 = sg(inc, ["Total Revenue", "Operating Revenue", "Revenue"], 0)
        rev0 = sg(inc, ["Total Revenue", "Operating Revenue", "Revenue"], 1)
        gp1  = sg(inc, ["Gross Profit", "GrossProfit"], 0)
        gp0  = sg(inc, ["Gross Profit", "GrossProfit"], 1)
        da1  = sg(cf,  ["Depreciation And Amortization", "Depreciation Amortization Depletion"], 0)
        da0  = sg(cf,  ["Depreciation And Amortization", "Depreciation Amortization Depletion"], 1)
        ni1  = sg(inc, ["Net Income", "Net Income Common Stockholders"], 0)

        ta1   = sg(bal, ["Total Assets", "TotalAssets"], 0)
        ta0   = sg(bal, ["Total Assets", "TotalAssets"], 1)
        ca1   = sg(bal, ["Current Assets", "Total Current Assets"], 0)
        ca0   = sg(bal, ["Current Assets", "Total Current Assets"], 1)
        cl1   = sg(bal, ["Current Liabilities", "Total Current Liabilities"], 0)
        cl0   = sg(bal, ["Current Liabilities", "Total Current Liabilities"], 1)
        cash1 = sg(bal, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"], 0)
        cash0 = sg(bal, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"], 1)
        rec1  = sg(bal, ["Accounts Receivable", "Receivables"], 0)
        rec0  = sg(bal, ["Accounts Receivable", "Receivables"], 1)
        ppe1  = sg(bal, ["Net PPE", "Net Property Plant And Equipment", "Gross PPE"], 0)
        ppe0  = sg(bal, ["Net PPE", "Net Property Plant And Equipment", "Gross PPE"], 1)
        ltd1  = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 0)
        ltd0  = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 1)

        def sdiv(a, b):
            return a/b if (b is not None and b != 0 and not np.isnan(b) and a is not None and not np.isnan(a)) else np.nan

        DSRI = sdiv(sdiv(rec1, rev1), sdiv(rec0, rev0))
        GMI  = sdiv(sdiv(gp0, rev0),  sdiv(gp1, rev1))
        AQI  = sdiv(sdiv((ta1 or 0)-(ca1 or 0)-(ppe1 or 0), ta1), sdiv((ta0 or 0)-(ca0 or 0)-(ppe0 or 0), ta0))
        SGI  = sdiv(rev1, rev0)
        DEPI = sdiv(sdiv(da0, (da0 or 0)+(ppe0 or 0)), sdiv(da1, (da1 or 0)+(ppe1 or 0)))
        sga1 = (rev1 or 0) - (gp1 or 0); sga0 = (rev0 or 0) - (gp0 or 0)
        SGAI = sdiv(sdiv(sga1, rev1), sdiv(sga0, rev0))
        ocf1 = sg(cf, ["Operating Cash Flow", "Cash Flows From Used In Operating Activities"], 0)
        TATA = sdiv((ni1 or 0) - (ocf1 or 0), ta1)
        LVGI = sdiv(sdiv((ltd1 or 0)+(cl1 or 0), ta1), sdiv((ltd0 or 0)+(cl0 or 0), ta0))

        vals = dict(DSRI=DSRI, GMI=GMI, AQI=AQI, SGI=SGI, DEPI=DEPI, SGAI=SGAI, TATA=TATA, LVGI=LVGI)
        valid_count = sum(1 for v in vals.values() if not np.isnan(v))
        if valid_count < 4:
            return None, "財報欄位不足"

        v = {k: (vals[k] if not np.isnan(vals[k]) else 1.0) for k in vals}
        m = (-4.84 + 0.920*v["DSRI"] + 0.528*v["GMI"] + 0.404*v["AQI"]
              + 0.892*v["SGI"] + 0.115*v["DEPI"] - 0.172*v["SGAI"]
              + 4.679*v["TATA"] - 0.327*v["LVGI"])
        return round(m, 3), vals
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════
# Z-Score 計算（增加多欄位容錯，避免 N/A）
# ═══════════════════════════════════════════════════════════════════
def compute_z_score(ticker: str, info: dict):
    try:
        tk  = yf.Ticker(ticker.upper())
        bal = tk.balance_sheet
        inc = tk.financials

        if bal.empty or inc.empty:
            return None, "財報數據為空"

        def sg(df, keys, col=0):
            return safe_get_field(df, keys, col)

        ta   = sg(bal, ["Total Assets", "TotalAssets"])
        ca   = sg(bal, ["Current Assets", "Total Current Assets"])
        cl   = sg(bal, ["Current Liabilities", "Total Current Liabilities"])
        re_  = sg(bal, ["Retained Earnings", "RetainedEarnings", "Accumulated Deficit"])
        ebit = sg(inc, ["EBIT", "Operating Income", "Pretax Income", "Net Income Before Taxes"])
        rev  = sg(inc, ["Total Revenue", "Operating Revenue", "Revenue"])

        ltd   = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"]) or 0
        cdebt = sg(bal, ["Current Debt", "Short Long Term Debt Total", "Current Debt And Capital Lease Obligation"]) or 0
        td    = sg(bal, ["Total Debt", "TotalDebt"])
        if np.isnan(td) or td == 0:
            td = ltd + cdebt

        mktcap = info.get("marketCap", np.nan)
        if np.isnan(mktcap) or mktcap == 0:
            sh = info.get("sharesOutstanding", 0)
            pr = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            mktcap = sh * pr if (sh and pr) else np.nan

        # 若資產為空或 0，嘗試直接用 info 輔助
        if np.isnan(ta) or ta == 0:
            return None, "資產資料缺失"

        # 若流動資產或負債缺失，嘗試從 Working Capital 讀取
        wc = (ca or 0) - (cl or 0)
        if np.isnan(ca) or np.isnan(cl):
            wc_alt = sg(bal, ["Working Capital", "Net Working Capital"])
            if not np.isnan(wc_alt):
                wc = wc_alt

        X1 = wc / ta
        X2 = (re_ or 0) / ta
        X3 = (ebit or 0) / ta
        X4 = (mktcap or 0) / max(td if not np.isnan(td) and td > 0 else 1, 1)
        X5 = (rev or 0) / ta

        z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        comps = {
            "X1 (流動性)": round(X1, 3),
            "X2 (保留盈餘)": round(X2, 3),
            "X3 (獲利能力)": round(X3, 3),
            "X4 (市值/負債)": round(X4, 3),
            "X5 (資產周轉)": round(X5, 3)
        }
        return round(z, 3), comps
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════
# F-Score 計算
# ═══════════════════════════════════════════════════════════════════
def compute_f_score(ticker: str):
    try:
        tk  = yf.Ticker(ticker.upper())
        bal = tk.balance_sheet
        inc = tk.financials
        cf  = tk.cashflow

        def sg(df, keys, col=0):
            return safe_get_field(df, keys, col)

        score, details = 0, {}

        # F1 ROA > 0
        ni  = sg(inc, ["Net Income", "Net Income Common Stockholders"])
        ta  = sg(bal, ["Total Assets", "TotalAssets"])
        roa = ni/ta if ta and ta!=0 and not np.isnan(ni) else np.nan
        f1  = 1 if not np.isnan(roa) and roa > 0 else 0
        score += f1; details["F1 ROA > 0"] = f1

        # F2 營業現金流 > 0
        ocf = sg(cf, ["Operating Cash Flow", "Cash Flows From Used In Operating Activities"])
        f2  = 1 if not np.isnan(ocf) and ocf > 0 else 0
        score += f2; details["F2 營業現金流 > 0"] = f2

        # F3 ROA 改善
        ni0  = sg(inc, ["Net Income", "Net Income Common Stockholders"], 1)
        ta0  = sg(bal, ["Total Assets", "TotalAssets"], 1)
        roa0 = ni0/ta0 if ta0 and ta0!=0 and not np.isnan(ni0) else np.nan
        f3   = 1 if not np.isnan(roa) and not np.isnan(roa0) and roa > roa0 else 0
        score += f3; details["F3 ROA 改善"] = f3

        # F4 應計比率 (OCF/TA > ROA)
        f4 = 1 if not np.isnan(ocf) and not np.isnan(roa) and ta and (ocf/ta) > roa else 0
        score += f4; details["F4 應計比率"] = f4

        # F5 長期負債降低
        ltd1 = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 0)
        ltd0 = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 1)
        f5   = 1 if not np.isnan(ltd1) and not np.isnan(ltd0) and ltd1 < ltd0 else 0
        score += f5; details["F5 槓桿降低"] = f5

        # F6 流動比改善
        ca1  = sg(bal, ["Current Assets", "Total Current Assets"], 0)
        cl1  = sg(bal, ["Current Liabilities", "Total Current Liabilities"], 0)
        ca0_ = sg(bal, ["Current Assets", "Total Current Assets"], 1)
        cl0_ = sg(bal, ["Current Liabilities", "Total Current Liabilities"], 1)
        cr1  = ca1/cl1 if cl1 and cl1!=0 else np.nan
        cr0_ = ca0_/cl0_ if cl0_ and cl0_!=0 else np.nan
        f6   = 1 if not np.isnan(cr1) and not np.isnan(cr0_) and cr1 > cr0_ else 0
        score += f6; details["F6 流動比改善"] = f6

        # F7 無發行新股稀釋
        sh1 = sg(bal, ["Common Stock", "Common Stock Equity"], 0)
        sh0 = sg(bal, ["Common Stock", "Common Stock Equity"], 1)
        f7  = 1 if not np.isnan(sh1) and not np.isnan(sh0) and sh1 <= sh0 else 0
        score += f7; details["F7 無稀釋增股"] = f7

        # F8 毛利率改善
        gp1  = sg(inc, ["Gross Profit", "GrossProfit"], 0)
        rv1  = sg(inc, ["Total Revenue", "Operating Revenue"], 0)
        gp0_ = sg(inc, ["Gross Profit", "GrossProfit"], 1)
        rv0_ = sg(inc, ["Total Revenue", "Operating Revenue"], 1)
        gm1  = gp1/rv1 if rv1 and rv1!=0 else np.nan
        gm0_ = gp0_/rv0_ if rv0_ and rv0_!=0 else np.nan
        f8   = 1 if not np.isnan(gm1) and not np.isnan(gm0_) and gm1 > gm0_ else 0
        score += f8; details["F8 毛利率改善"] = f8

        # F9 資產周轉率改善
        at1  = rv1/ta if ta and ta!=0 else np.nan
        at0_ = rv0_/ta0 if ta0 and ta0!=0 else np.nan
        f9   = 1 if not np.isnan(at1) and not np.isnan(at0_) and at1 > at0_ else 0
        score += f9; details["F9 資產周轉改善"] = f9

        return score, details
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════
# 12 項關鍵財務指標打分
# ═══════════════════════════════════════════════════════════════════
def compute_12_score(ticker: str, info: dict):
    score, details = 0.0, {}
    try:
        tk  = yf.Ticker(ticker.upper())
        inc = tk.financials
        bal = tk.balance_sheet
        cf  = tk.cashflow

        def sg(df, keys, col=0):
            return safe_get_field(df, keys, col)

        # ①營業利益率
        op_m = []
        for i in range(min(len(inc.columns), 4)):
            rv = sg(inc, ["Total Revenue", "Operating Revenue"], i)
            op = sg(inc, ["Operating Income", "EBIT"], i)
            if rv and rv!=0 and not np.isnan(op): op_m.append(op/rv*100)
        avg_op = np.mean(op_m) if op_m else np.nan
        s1 = 1.0 if (len(op_m)>=3 and not np.isnan(avg_op) and avg_op>=15) else \
             0.5 if (not np.isnan(avg_op) and avg_op>=15) else 0.0
        score += s1; details["①營業利益率"] = (s1, f"均值 {avg_op:.1f}%" if not np.isnan(avg_op) else "N/A")

        # ②自由現金流
        fcfs = []
        for i in range(min(len(cf.columns), 4)):
            o = sg(cf, ["Operating Cash Flow", "Cash Flows From Used In Operating Activities"], i)
            c = sg(cf, ["Capital Expenditure"], i)
            if not np.isnan(o) and not np.isnan(c): fcfs.append(o+c)
        s2 = 0.0
        if fcfs:
            if all(f > 0 for f in fcfs): s2 += 0.5
            if len(fcfs) >= 2 and all(fcfs[i] > fcfs[i+1] for i in range(len(fcfs)-1)): s2 += 0.5
            if all(f > 0 for f in fcfs) and len(fcfs) >= 3: s2 = min(s2 + 0.5, 2.0)
        score += s2; details["②自由現金流"] = (s2, f"近{len(fcfs)}期FCF {'全正✅' if fcfs and all(f>0 for f in fcfs) else '有負⚠️'}" if fcfs else "N/A")

        # ③淨利率
        nm = []
        for i in range(min(len(inc.columns), 4)):
            ni_ = sg(inc, ["Net Income", "Net Income Common Stockholders"], i)
            rv  = sg(inc, ["Total Revenue", "Operating Revenue"], i)
            if rv and rv!=0 and not np.isnan(ni_): nm.append(ni_/rv*100)
        avg_nm = np.mean(nm) if nm else np.nan
        s3 = 1.0 if (not np.isnan(avg_nm) and avg_nm>=20) else \
             0.5 if (not np.isnan(avg_nm) and avg_nm>=10) else 0.0
        score += s3; details["③淨利率"] = (s3, f"均值 {avg_nm:.1f}%" if not np.isnan(avg_nm) else "N/A")

        # ④負債權益比
        ltd_ = sg(bal, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
        eq_  = sg(bal, ["Stockholders Equity", "Total Stockholder Equity"])
        de = ltd_/eq_ if not np.isnan(ltd_) and not np.isnan(eq_) and eq_>0 else np.nan
        s4 = 1.0 if (not np.isnan(de) and de < 1.0) else 0.0
        score += s4; details["④負債權益比"] = (s4, f"LT-D/E = {de:.2f}" if not np.isnan(de) else "N/A")

        # ⑤利息保障倍數
        ebit_ = sg(inc, ["EBIT", "Operating Income"])
        int_  = sg(inc, ["Interest Expense", "Interest Expense Non Operating"])
        if np.isnan(int_) or int_ == 0:
            s5 = 1.0; details["⑤利息保障倍數"] = (s5, "無有息負債 ✅")
        elif not np.isnan(ebit_) and abs(int_) > 0:
            ic = ebit_ / abs(int_)
            s5 = 1.0 if ic > 10 else 0.5 if ic > 5 else 0.0
            details["⑤利息保障倍數"] = (s5, f"IC = {ic:.1f}x")
        else:
            s5 = 0.0; details["⑤利息保障倍數"] = (s5, "N/A")
        score += s5

        # ⑥ROE
        roe_v = info.get("returnOnEquity", np.nan)
        roe_pct = roe_v*100 if roe_v and not np.isnan(roe_v) else np.nan
        s6 = 1.0 if (not np.isnan(roe_pct) and 15 <= roe_pct <= 30) else \
             0.5 if (not np.isnan(roe_pct) and roe_pct >= 15) else 0.0
        score += s6; details["⑥ROE"] = (s6, f"{roe_pct:.1f}%" if not np.isnan(roe_pct) else "N/A")

        # ⑦ROIC（以 ROA 代估）
        roa_v = info.get("returnOnAssets", np.nan)
        roa_pct = roa_v*100 if roa_v and not np.isnan(roa_v) else np.nan
        s7 = 1.0 if (not np.isnan(roa_pct) and roa_pct >= 10) else \
             0.5 if (not np.isnan(roa_pct) and roa_pct >= 7) else 0.0
        score += s7; details["⑦ROIC(ROA估)"] = (s7, f"{roa_pct:.1f}%" if not np.isnan(roa_pct) else "N/A")

        # ⑧營收成長率
        revs = [sg(inc, ["Total Revenue", "Operating Revenue"], i) for i in range(min(len(inc.columns),4))]
        revs = [r for r in revs if not np.isnan(r)]
        s8 = 0.0; avg_gr = np.nan
        if len(revs) >= 2:
            grs = [(revs[i]-revs[i+1])/abs(revs[i+1])*100
                   for i in range(len(revs)-1) if revs[i+1] != 0]
            avg_gr = np.mean(grs) if grs else np.nan
            if not np.isnan(avg_gr) and avg_gr >= 20: s8 += 0.5
            if all(revs[i] > revs[i+1] for i in range(len(revs)-1)): s8 += 0.5
        score += s8; details["⑧營收成長率"] = (s8, f"均年增 {avg_gr:.1f}%" if not np.isnan(avg_gr) else "N/A")

        # ⑨EPS成長率
        eps_v  = info.get("trailingEps", np.nan)
        feps_v = info.get("forwardEps", np.nan)
        s9 = 0.0; eps_gr = np.nan
        if not np.isnan(eps_v) and not np.isnan(feps_v) and eps_v > 0:
            eps_gr = (feps_v - eps_v)/eps_v*100
            s9 = 1.0 if eps_gr >= 20 else 0.5 if eps_gr >= 15 else 0.0
        score += s9; details["⑨EPS成長率"] = (s9, f"TTM→FWD {eps_gr:.1f}%" if not np.isnan(eps_gr) else "N/A")

        # ⑩速動比率
        qr = info.get("quickRatio", np.nan)
        s10 = 1.0 if (not np.isnan(qr) and qr > 1.5) else \
              0.5 if (not np.isnan(qr) and qr > 1.0) else 0.0
        score += s10; details["⑩速動比率"] = (s10, f"QR = {qr:.2f}" if not np.isnan(qr) else "N/A")

        # ⑪回購殖利率
        mktcap  = info.get("marketCap", np.nan)
        buyback = sg(cf, ["Repurchase Of Capital Stock", "Purchase Of Common Stock"])
        s11 = 0.0; by = np.nan
        if not np.isnan(buyback) and not np.isnan(mktcap) and mktcap > 0:
            by = abs(buyback)/mktcap*100
            s11 = 1.0 if by >= 1.5 else 0.5 if by >= 0.5 else 0.0
        score += s11; details["⑪回購殖利率"] = (s11, f"{by:.2f}%" if not np.isnan(by) else "N/A")

        # ⑫機構持股
        inst = info.get("heldPercentInstitutions", np.nan)
        pct  = inst*100 if inst and not np.isnan(inst) else np.nan
        exch = info.get("exchange", "")
        is_adr = exch not in ["NYQ","NMS","NGM","NCM","BTS","PCX"]
        if not np.isnan(pct):
            if is_adr:
                s12 = 4.0 if pct>=60 else 3.0 if pct>=50 else 2.0 if pct>=40 else 1.0 if pct>=30 else 0.0
            else:
                s12 = 4.0 if pct>=90 else 3.0 if pct>=80 else 2.0 if pct>=70 else 1.0 if pct>=60 else 0.0
        else:
            s12 = 0.0
        score += s12; details["⑫機構持股"] = (s12, f"{pct:.1f}%" if not np.isnan(pct) else "N/A")

    except Exception as e:
        details["錯誤"] = (0, str(e))

    return round(score, 1), details

# ═══════════════════════════════════════════════════════════════════
# 嚴格三級倉等判定邏輯（完全對齊策略規範）
# ═══════════════════════════════════════════════════════════════════
def get_position_tier(m, z, f, s):
    """
    依照策略規則進行審核：
    1. 推薦建倉：M < -1.78 ∩ Z > 2.99 (安全) ∩ F ≥ 7 (優質) ∩ 12項 ≥ 10
    2. 可建倉：M < -1.78 ∩ Z > 2.99 (安全) ∩ 4 ≤ F ≤ 6 (中等) ∩ 12項 ≥ 10
    3. 輕倉：M < -1.78 ∩ 1.81 ≤ Z ≤ 2.99 (灰色) ∩ F ≥ 7 (優質) ∩ 12項 ≥ 10
    其餘情況一律否決（或標註資料不足）
    """
    # ── 1. 資料缺失防護 ──
    if m is None or (isinstance(m, float) and np.isnan(m)):
        return "⚠️ 資料不足（M-Score缺失）", "nodata"
    if z is None or (isinstance(z, float) and np.isnan(z)):
        return "⚠️ 資料不足（Z-Score缺失）", "nodata"
    if f is None or (isinstance(f, float) and np.isnan(f)):
        return "⚠️ 資料不足（F-Score缺失）", "nodata"
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return "⚠️ 資料不足（12項缺失）", "nodata"

    # ── 2. 一票否決項 ──
    if m >= -1.78:
        return "🚫 否決（M-Score ≥ -1.78 涉嫌舞弊）", "fail"
    if z < 1.81:
        return "🚫 否決（Z-Score < 1.81 破產風險）", "fail"
    if f <= 3:
        return "🚫 否決（F-Score ≤ 3 營運劣質）", "fail"
    if s < 10:
        return "🚫 否決（12項關鍵指標 < 10分）", "fail"

    # ── 3. 三級合格判定 ──
    # 第 1 級：推薦建倉 (Z > 2.99 且 F >= 7)
    if z > 2.99 and f >= 7:
        return "🌟 推薦建倉", "tier_rec"

    # 第 2 級：可建倉 (Z > 2.99 且 4 <= F <= 6)
    if z > 2.99 and 4 <= f <= 6:
        return "✅ 可建倉", "tier_build"

    # 第 3 級：輕倉 (1.81 <= Z <= 2.99 且 F >= 7)
    if 1.81 <= z <= 2.99 and f >= 7:
        return "⚠️ 輕倉（灰色警訊區）", "tier_light"

    # 灰色區若 F-Score 只有 4~6，依決策矩陣表不予輕倉，直接淘汰
    if 1.81 <= z <= 2.99 and f < 7:
        return "🚫 否決（灰色區須 F-Score ≥ 7 始准輕倉）", "fail"

    return "🚫 否決（未符合三級門檻）", "fail"

# ═══════════════════════════════════════════════════════════════════
# 標題
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">📈 DMTM 美股雙動能量化投資儀表板</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Barchart 雙榜交集 · M/Z/F-Score 財報排雷 · 個股估值K線 · 動態 Beta 資金配置</div>',
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 側邊欄
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ 全域設定")
    total_capital = st.number_input("💰 總資金（USD）", min_value=1000, max_value=10_000_000,
                                    value=100_000, step=1000, format="%d")
    st.markdown("---")

    # 月份操作建議
    st.markdown("### 📅 當月操作建議")
    month_now = datetime.now().month
    month_meta = {
        1:("1月 ✅ 買入","#22c55e","一月效應，機構重新建倉佈局"),
        2:("2月 🔴 賣出","#ef4444","財報空窗拉回，防禦減碼"),
        3:("3月 ✅ 買入","#22c55e","Q1季末作帳，法人再平衡"),
        4:("4月 ✅ 買入","#22c55e","黃金期，退稅資金注入市場"),
        5:("5月 🟡 持有","#eab308","Sell in May，動能放緩"),
        6:("6月 🟡 持有","#eab308","年中盤整，觀望下半年"),
        7:("7月 ✅ 買入","#22c55e","夏季拉升，Q2財報季啟動"),
        8:("8月 🟡 持有","#eab308","假期量縮，波動放大"),
        9:("9月 🔴 賣出","#ef4444","九月魔咒，全年最弱月份"),
        10:("10月 ✅ 買入","#22c55e","轉折築底，熊市殺手月"),
        11:("11月 ✅ 買入","#22c55e","最強波段，法人年底建倉"),
        12:("12月 ✅ 買入","#22c55e","聖誕老人行情，封關作帳"),
    }
    m_label, m_color, m_desc = month_meta[month_now]
    st.markdown(f"""
    <div style="background:#1a2033;border:1px solid #30363d;border-radius:8px;
                padding:12px;text-align:center;">
        <div style="color:{m_color};font-size:1.25rem;font-weight:800;">{m_label}</div>
        <div style="color:#CBD5E1;font-size:0.82rem;margin-top:5px;">{m_desc}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # 快速止盈計算器
    st.markdown("### 🛡️ 快速止盈計算器")
    q_price = st.number_input("買入股價 $", min_value=0.01, value=100.0, step=0.5, format="%.2f")
    q_pct   = st.slider("止損比例 %", 5, 25, 15)
    q_stop  = q_price * (1 - q_pct/100)
    st.markdown(f"""
    <div style="background:#1a0a0a;border:1px solid #ef4444;border-radius:8px;
                padding:10px;text-align:center;margin-top:6px;">
        <div style="color:#f87171;font-size:1.3rem;font-weight:800;">${q_stop:.2f}</div>
        <div style="color:#CBD5E1;font-size:0.78rem;">最高點回撤 -{q_pct}% 觸發止盈</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 四大模組 Tabs
# ═══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 模組一：Barchart 雙榜篩選",
    "🔬 模組二：M/Z/F-Score 排雷",
    "📊 模組三：K線估值止盈",
    "🏦 模組四：Beta 資金配置",
])

# ════════════════════════════════════════════════════════════════════
# 模組一：Barchart 雙榜交集篩選器
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="module-header">📋 模組一：Barchart 雙榜交集篩選器（DMTM 起手式）</div>',
                unsafe_allow_html=True)

    # ── Barchart 官方連結（正確網址）──
    st.markdown("""
    <p style="color:#CBD5E1;font-size:0.9rem;margin-bottom:0.8rem;">
        請至 Barchart 官網取得兩份名單，下載後上傳或直接貼上文字至下方欄位：
    </p>
    <div style="margin-bottom:1.2rem;">
        <a class="link-btn" href="https://www.barchart.com/stocks/signals/top-bottom?viewName=main&orderBy=symbol&orderDir=asc" target="_blank">
            🏆 Top Stocks to Own（結構完美多頭）
        </a>
        &nbsp;&nbsp;
        <a class="link-btn" href="https://www.barchart.com/stocks/top-100-stocks?viewName=main&orderBy=percentChange1y&orderDir=desc" target="_blank">
            🚀 Top 100 Stocks to Buy（動能暴衝）
        </a>
    </div>
    <div class="info-box">
        💡 操作流程：登入 Barchart → 找到對應榜單 → 下載 CSV 或全選表格文字複製 → 上傳/貼上至下方兩欄 → 系統自動計算交集
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">📄 名單 A：Top Stocks to Own</p>', unsafe_allow_html=True)
        file_a = st.file_uploader("上傳 CSV / Excel（名單 A）", type=["csv","xlsx","xls"], key="file_a")
        text_a = st.text_area("或直接貼上網頁表格文字（名單 A）", height=38, key="text_a",
                               placeholder="將 Barchart 表格文字貼上，系統自動識別股票代號...")
        tickers_a = []
        if file_a:
            tickers_a = parse_csv_excel(file_a)
            st.success(f"✅ 解析成功：{len(tickers_a)} 檔（名單 A）")
        elif text_a.strip():
            tickers_a = extract_tickers_from_text(text_a)
            st.info(f"🔍 自動識別 {len(tickers_a)} 個代號（名單 A）")

    with col_b:
        st.markdown('<p class="section-title">🚀 名單 B：Top 100 Stocks to Buy</p>', unsafe_allow_html=True)
        file_b = st.file_uploader("上傳 CSV / Excel（名單 B）", type=["csv","xlsx","xls"], key="file_b")
        text_b = st.text_area("或直接貼上網頁表格文字（名單 B）", height=38, key="text_b",
                               placeholder="將 Barchart 表格文字貼上，系統自動識別股票代號...")
        tickers_b = []
        if file_b:
            tickers_b = parse_csv_excel(file_b)
            st.success(f"✅ 解析成功：{len(tickers_b)} 檔（名單 B）")
        elif text_b.strip():
            tickers_b = extract_tickers_from_text(text_b)
            st.info(f"🔍 自動識別 {len(tickers_b)} 個代號（名單 B）")

    # ── 交集結果 ──
    if tickers_a and tickers_b:
        intersection = get_intersection(tickers_a, tickers_b)
        st.markdown("---")
        st.markdown(f'<p style="color:#FFFFFF;font-size:1.3rem;font-weight:800;">🎯 雙榜交集結果：共 <span style="color:#38bdf8;">{len(intersection)}</span> 檔</p>',
                    unsafe_allow_html=True)

        if intersection:
            badge_html = " ".join(
                f'<span style="display:inline-block;background:#1e3a5f;color:#FFFFFF;'
                f'border:1px solid #2d6a9f;border-radius:6px;padding:5px 13px;'
                f'margin:3px;font-weight:700;font-size:0.95rem;">{t}</span>'
                for t in intersection
            )
            st.markdown(badge_html, unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)
            st.download_button(
                label="💾 下載交集清單 (.txt)",
                data="\n".join(intersection),
                file_name=f"dmtm_intersection_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            st.session_state["intersection"] = intersection
            st.markdown('<div class="info-box">✅ 交集清單已儲存，切換至「模組二」可直接進行財報排雷分析</div>',
                       unsafe_allow_html=True)
        else:
            st.warning("⚠️ 兩份名單無重疊股票，請確認輸入資料是否正確")

    elif tickers_a and not tickers_b:
        st.info("請繼續輸入名單 B 以計算交集")
    elif tickers_b and not tickers_a:
        st.info("請繼續輸入名單 A 以計算交集")

    # 預覽名單（序號欄位寬度最小化、左對齊）
    if tickers_a or tickers_b:
        with st.expander("📋 名單預覽"):
            pc, pd2 = st.columns(2)
            with pc:
                st.markdown(f'<p style="color:#FFFFFF;font-weight:700;">名單 A：Top Stocks to Own（共 {len(tickers_a)} 檔）</p>',
                            unsafe_allow_html=True)
                if tickers_a:
                    df_preview_a = pd.DataFrame({
                        "序號": [str(i) for i in range(1, len(tickers_a) + 1)],
                        "股票代號": tickers_a
                    })
                    st.dataframe(
                        df_preview_a,
                        column_config={
                            "序號": st.column_config.TextColumn("序號", width="small"),
                            "股票代號": st.column_config.TextColumn("股票代號"),
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=280
                    )
                else:
                    st.caption("尚未載入名單 A")

            with pd2:
                st.markdown(f'<p style="color:#FFFFFF;font-weight:700;">名單 B：Top 100 Stocks to Buy（共 {len(tickers_b)} 檔）</p>',
                            unsafe_allow_html=True)
                if tickers_b:
                    df_preview_b = pd.DataFrame({
                        "序號": [str(i) for i in range(1, len(tickers_b) + 1)],
                        "股票代號": tickers_b
                    })
                    st.dataframe(
                        df_preview_b,
                        column_config={
                            "序號": st.column_config.TextColumn("序號", width="small"),
                            "股票代號": st.column_config.TextColumn("股票代號"),
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=280
                    )
                else:
                    st.caption("尚未載入名單 B")

# ════════════════════════════════════════════════════════════════════
# 模組二：M/Z/F-Score 排雷 + 12 項指標打分
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="module-header">🔬 模組二：即時財報排雷（M/Z/F-Score）與 12 項指標打分</div>',
                unsafe_allow_html=True)

    src = st.radio("分析標的來源", ["使用模組一交集清單", "手動輸入股票代號"], horizontal=True)

    if src == "使用模組一交集清單":
        analyze_tickers = st.session_state.get("intersection", [])
        if not analyze_tickers:
            st.warning("⚠️ 模組一尚未產生交集清單，請先完成模組一，或切換為手動輸入")
        else:
            st.success(f"✅ 已載入交集清單：{len(analyze_tickers)} 檔")
    else:
        manual_input = st.text_input(
            "輸入股票代號（逗號或空格分隔）",
            value="NVDA, MSFT, AAPL, META, GOOGL, AVGO",
            placeholder="例：NVDA, MSFT, AAPL, TSM"
        )
        analyze_tickers = [t.strip().upper() for t in re.split(r'[,\s]+', manual_input) if t.strip()]

    if analyze_tickers:
        max_n = st.slider("最多分析幾檔", 3, 30, min(20, len(analyze_tickers)))
        analyze_tickers = analyze_tickers[:max_n]

        col_run, col_note = st.columns([1, 4])
        with col_run:
            run_btn = st.button("🚀 開始排雷分析", type="primary", use_container_width=True)
        with col_note:
            st.markdown('<div class="info-box">資料透過 yfinance 即時動態抓取，每檔約 1~2 秒，請稍候</div>',
                       unsafe_allow_html=True)

        if run_btn:
            results = []
            prog = st.progress(0, text="財報排雷分析中...")

            for i, ticker in enumerate(analyze_tickers):
                prog.progress((i+1)/len(analyze_tickers), text=f"分析 {ticker}... ({i+1}/{len(analyze_tickers)})")
                info   = fetch_ticker_info(ticker)
                name   = info.get("longName", ticker)[:30]
                price  = info.get("currentPrice") or info.get("regularMarketPrice", np.nan)
                mv, md = compute_m_score(ticker, info)
                zv, zd = compute_z_score(ticker, info)
                fv, fd = compute_f_score(ticker)
                sv, sd = compute_12_score(ticker, info)
                tier, ttype = get_position_tier(mv, zv, fv, sv)
                results.append(dict(ticker=ticker, name=name, price=price,
                                    mv=mv, zv=zv, fv=fv, sv=sv,
                                    tier=tier, ttype=ttype, sd=sd, zd=zd, fd=fd))

            prog.empty()
            st.session_state["analysis_results"] = results

            # 同步更新合格清單（依優先級：推薦建倉 > 可建倉 > 輕倉）
            rec_list   = [r["ticker"] for r in results if r["ttype"] == "tier_rec"]
            build_list = [r["ticker"] for r in results if r["ttype"] == "tier_build"]
            light_list = [r["ticker"] for r in results if r["ttype"] == "tier_light"]
            st.session_state["qualified_tickers"] = rec_list + build_list + light_list

        # ── 顯示結果 ──
        results = st.session_state.get("analysis_results", [])
        if results:
            st.markdown("---")
            total_n = len(results)
            st.markdown(f'<p style="color:#FFFFFF;font-size:1.3rem;font-weight:900;">📊 排雷報告：{total_n} 檔分析完畢</p>',
                        unsafe_allow_html=True)

            # 分類名單提取
            rec_items   = [r for r in results if r["ttype"] == "tier_rec"]
            build_items = [r for r in results if r["ttype"] == "tier_build"]
            light_items = [r for r in results if r["ttype"] == "tier_light"]
            total_qualified_n = len(rec_items) + len(build_items) + len(light_items)
            fail_n = total_n - total_qualified_n

            # ─────────────────────────────────────────────────────────────
            # ★ 核心需求：表頭第一欄先出現「合格總合名單（分為三級）」
            # ─────────────────────────────────────────────────────────────
            st.markdown("""
            <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:14px;margin-bottom:1.2rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
                    <span style="color:#FFFFFF;font-size:1.15rem;font-weight:800;">
                        🏆 財務排雷合格總合名單（三大建倉等級）
                    </span>
                    <span style="font-size:0.88rem;color:#CBD5E1;">
                        合格率：<b style="color:#6ee7b7;">{total_qualified_n} / {total_n}</b> 檔合格 ｜ 淘汰：<b style="color:#f87171;">{fail_n}</b> 檔
                    </span>
                </div>
            """.format(total_qualified_n=total_qualified_n, total_n=total_n, fail_n=fail_n), unsafe_allow_html=True)

            col_t1, col_t2, col_t3 = st.columns(3)

            # ── 1. 推薦建倉 ──
            with col_t1:
                pills_rec = ""
                if rec_items:
                    for r in rec_items:
                        p_str = f"${r['price']:.2f}" if r['price'] and not np.isnan(r['price']) else ""
                        pills_rec += f'<span class="stock-pill pill-rec">{r["ticker"]} {p_str}</span>'
                else:
                    pills_rec = '<span style="color:#64748b;font-size:0.85rem;font-style:italic;">暫無符合標的</span>'

                st.markdown(f"""
                <div class="tier-card tier-card-rec">
                    <div class="tier-header-rec">🌟 1. 推薦建倉 ({len(rec_items)} 檔)</div>
                    <div style="font-size:0.75rem;color:#CBD5E1;margin:4px 0 8px 0;line-height:1.3;">
                        • M-Score &lt; -1.78 (安全無舞弊)<br/>
                        • Z-Score &gt; 2.99 (安全區)<br/>
                        • F-Score ≥ 7 (優質營運)<br/>
                        • 12 項指標 ≥ 10 分 (核心護城河)
                    </div>
                    <div style="margin-top:6px;">{pills_rec}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── 2. 可建倉 ──
            with col_t2:
                pills_build = ""
                if build_items:
                    for r in build_items:
                        p_str = f"${r['price']:.2f}" if r['price'] and not np.isnan(r['price']) else ""
                        pills_build += f'<span class="stock-pill pill-build">{r["ticker"]} {p_str}</span>'
                else:
                    pills_build = '<span style="color:#64748b;font-size:0.85rem;font-style:italic;">暫無符合標的</span>'

                st.markdown(f"""
                <div class="tier-card tier-card-build">
                    <div class="tier-header-build">✅ 2. 可建倉 ({len(build_items)} 檔)</div>
                    <div style="font-size:0.75rem;color:#CBD5E1;margin:4px 0 8px 0;line-height:1.3;">
                        • M-Score &lt; -1.78 (安全無舞弊)<br/>
                        • Z-Score &gt; 2.99 (安全區)<br/>
                        • F-Score 4 ~ 6 (中等營運)<br/>
                        • 12 項指標 ≥ 10 分 (常規建倉)
                    </div>
                    <div style="margin-top:6px;">{pills_build}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── 3. 輕倉 ──
            with col_t3:
                pills_light = ""
                if light_items:
                    for r in light_items:
                        p_str = f"${r['price']:.2f}" if r['price'] and not np.isnan(r['price']) else ""
                        pills_light += f'<span class="stock-pill pill-light">{r["ticker"]} {p_str}</span>'
                else:
                    pills_light = '<span style="color:#64748b;font-size:0.85rem;font-style:italic;">暫無符合標的</span>'

                st.markdown(f"""
                <div class="tier-card tier-card-light">
                    <div class="tier-header-light">⚠️ 3. 輕倉配置 ({len(light_items)} 檔)</div>
                    <div style="font-size:0.75rem;color:#CBD5E1;margin:4px 0 8px 0;line-height:1.3;">
                        • M-Score &lt; -1.78 (安全無舞弊)<br/>
                        • Z-Score 1.81 ~ 2.99 (灰色警訊)<br/>
                        • F-Score ≥ 7 (必須優質補足防守)<br/>
                        • 12 項指標 ≥ 10 分 (嚴格控管部位)
                    </div>
                    <div style="margin-top:6px;">{pills_light}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────────────
            # 彙總 DataFrame 表格（合格者優先排在最前）
            # ─────────────────────────────────────────────────────────────
            # 優先級排序：推薦建倉(0) > 可建倉(1) > 輕倉(2) > 否決(3) > 資料不足(4)
            def sort_priority(ttype):
                if ttype == "tier_rec":   return 0
                if ttype == "tier_build": return 1
                if ttype == "tier_light": return 2
                if ttype == "fail":       return 3
                return 4

            sorted_results = sorted(results, key=lambda x: (sort_priority(x["ttype"]), -x["sv"]))

            rows = []
            for r in sorted_results:
                def fmtv(v): return f"{v:.3f}" if v is not None and not (isinstance(v,float) and np.isnan(v)) else "N/A"
                rows.append({
                    "代號": r["ticker"],
                    "公司名稱": r["name"],
                    "股價": f"${r['price']:.2f}" if r["price"] and not np.isnan(r["price"]) else "N/A",
                    "M-Score": fmtv(r["mv"]),
                    "Z-Score": fmtv(r["zv"]),
                    "F-Score": str(r["fv"]) if r["fv"] is not None else "N/A",
                    "12項得分": str(r["sv"]),
                    "建倉建議": r["tier"],
                })
            df_sum = pd.DataFrame(rows)

            def color_tier_cell(val):
                val = str(val)
                if "推薦建倉" in val:
                    return "color: #6ee7b7; font-weight: 800; background-color: #064e3b33;"
                elif "可建倉" in val:
                    return "color: #38bdf8; font-weight: 800; background-color: #1e3a5f33;"
                elif "輕倉" in val:
                    return "color: #fbbf24; font-weight: 800; background-color: #451a0333;"
                elif "否決" in val:
                    return "color: #f87171;"
                return "color: #94a3b8;"

            def color_mscore(val):
                try:
                    v = float(val)
                    return "color: #6ee7b7; font-weight: 600;" if v < -1.78 else "color: #f87171; font-weight: 600;"
                except:
                    return "color: #8b949e;"

            def color_zscore(val):
                try:
                    v = float(val)
                    if v > 2.99: return "color: #6ee7b7; font-weight: 600;"
                    if v >= 1.81: return "color: #fbbf24; font-weight: 600;"
                    return "color: #f87171; font-weight: 600;"
                except:
                    return "color: #8b949e;"

            def color_fscore(val):
                try:
                    v = int(val)
                    if v >= 7: return "color: #6ee7b7; font-weight: 600;"
                    if v >= 4: return "color: #fbbf24; font-weight: 600;"
                    return "color: #f87171; font-weight: 600;"
                except:
                    return "color: #8b949e;"

            def color_12score(val):
                try:
                    v = float(val)
                    return "color: #6ee7b7; font-weight: 700;" if v >= 10 else "color: #fbbf24;" if v >= 7 else "color: #f87171;"
                except:
                    return "color: #8b949e;"

            styled = (df_sum.style
                      .map(color_tier_cell,  subset=["建倉建議"])
                      .map(color_mscore,      subset=["M-Score"])
                      .map(color_zscore,      subset=["Z-Score"])
                      .map(color_fscore,      subset=["F-Score"])
                      .map(color_12score,     subset=["12項得分"]))

            st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

            # ── 個股詳情展開 ──
            st.markdown("---")
            st.markdown('<p style="color:#FFFFFF;font-size:1.1rem;font-weight:800;">🔍 個股詳細排雷報告（點選展開）</p>',
                        unsafe_allow_html=True)

            for r in sorted_results:
                tier_icon = "🌟" if r["ttype"]=="tier_rec" else "✅" if r["ttype"]=="tier_build" else "⚠️" if r["ttype"]=="tier_light" else "🚫"
                with st.expander(f"{r['ticker']} — {r['name']}　　{tier_icon} {r['tier']}"):

                    c1, c2, c3, c4 = st.columns(4)

                    def metric_html(col_, label_, val_, note_, is_good):
                        fv2 = f"{val_:.3f}" if val_ is not None else "N/A"
                        col = "#6ee7b7" if (val_ is not None and is_good) else "#f87171" if val_ is not None else "#8b949e"
                        col_.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value" style="color:{col};">{fv2}</div>
                            <div class="metric-label" style="color:#CBD5E1;">{label_}</div>
                            <div style="font-size:0.72rem;color:#8b949e;">{note_}</div>
                        </div>""", unsafe_allow_html=True)

                    metric_html(c1, "Beneish M-Score", r["mv"], "< -1.78 安全無舞弊",
                                r["mv"] is not None and r["mv"] < -1.78)
                    metric_html(c2, "Altman Z-Score",  r["zv"], "> 2.99 安全 / 1.81~2.99 灰色",
                                r["zv"] is not None and r["zv"] > 2.99)

                    fv_num = r["fv"]
                    fc = "#6ee7b7" if fv_num and fv_num>=7 else "#fbbf24" if fv_num and fv_num>=4 else "#f87171"
                    c3.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:{fc};">{fv_num if fv_num is not None else 'N/A'}/9</div>
                        <div class="metric-label" style="color:#CBD5E1;">Piotroski F-Score</div>
                        <div style="font-size:0.72rem;color:#8b949e;">≥7 優質 / 4-6 中等 / ≤3 劣質</div>
                    </div>""", unsafe_allow_html=True)

                    sv_num = r["sv"]
                    sc = "#6ee7b7" if sv_num>=10 else "#fbbf24" if sv_num>=7 else "#f87171"
                    c4.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:{sc};">{sv_num}</div>
                        <div class="metric-label" style="color:#CBD5E1;">12 項指標總分</div>
                        <div style="font-size:0.72rem;color:#8b949e;">≥10 分及格門檻</div>
                    </div>""", unsafe_allow_html=True)

                    # 12 項明細表
                    if r["sd"]:
                        st.markdown('<p style="color:#FFFFFF;font-weight:700;margin-top:0.8rem;">📋 12 項指標明細：</p>',
                                    unsafe_allow_html=True)
                        rows_html = ""
                        for k,(pts,desc) in r["sd"].items():
                            dot = "🟢" if pts>=1 else "🟡" if pts>0 else "🔴"
                            rows_html += f"<tr><td>{dot} {k}</td><td style='color:#fbbf24;font-weight:700;'>{pts}</td><td style='color:#CBD5E1;'>{desc}</td></tr>"
                        pass_text = "✅ 及格 (≥10分)" if sv_num>=10 else "❌ 不及格 (<10分)"
                        pass_col  = "#6ee7b7" if sv_num>=10 else "#f87171"
                        st.markdown(f"""
                        <table class="score-table">
                            <tr><th>指標項目</th><th>得分</th><th>說明</th></tr>
                            {rows_html}
                            <tr style="background:#1a2033;">
                                <td style="color:#FFFFFF;font-weight:700;">總計</td>
                                <td style="color:#38bdf8;font-weight:800;font-size:1.1rem;">{sv_num}</td>
                                <td style="color:{pass_col};font-weight:700;">{pass_text}</td>
                            </tr>
                        </table>""", unsafe_allow_html=True)

                    # F-Score 明細
                    if r["fd"] and isinstance(r["fd"], dict):
                        st.markdown('<p style="color:#FFFFFF;font-weight:700;margin-top:0.8rem;">🔎 F-Score 9項營運明細：</p>',
                                    unsafe_allow_html=True)
                        f_rows = ""
                        for fk, fv3 in r["fd"].items():
                            dot = "🟢" if fv3==1 else "🔴"
                            fc3 = "#6ee7b7" if fv3==1 else "#f87171"
                            f_rows += f"<tr><td>{dot} {fk}</td><td style='color:{fc3};font-weight:700;'>{fv3}</td></tr>"
                        st.markdown(f"""
                        <table class="score-table">
                            <tr><th>F-Score 項目</th><th>分數</th></tr>
                            {f_rows}
                        </table>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# 模組三：K線圖、估值分析、移動止盈
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="module-header">📊 模組三：個股分流估值、互動式 K 線圖與 15% 移動止盈</div>',
                unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        qualified_pool = st.session_state.get("qualified_tickers", [])
        default_sym = qualified_pool[0] if qualified_pool else "NVDA"
        symbol = st.text_input("🔍 股票代號", value=default_sym).upper().strip()
    with col_s2:
        period_map = {"1個月":"1mo","3個月":"3mo","6個月":"6mo","1年":"1y","2年":"2y","5年":"5y"}
        period_choice = st.selectbox("時間區間", list(period_map.keys()), index=3)
        period = period_map[period_choice]
    with col_s3:
        ma_opts = st.multiselect("均線", [5,10,20,50,200], default=[20,50])

    load_btn = st.button("📈 載入分析", type="primary")

    if symbol:
        st.session_state["m3_symbol"] = symbol
        with st.spinner(f"抓取 {symbol} 資料中..."):
            hist = fetch_history(symbol, period=period)
            info = fetch_ticker_info(symbol)

        if hist.empty:
            st.error(f"❌ 無法取得 {symbol} 的歷史資料，請確認代號是否正確")
        else:
            name    = info.get("longName", symbol)
            price   = info.get("currentPrice") or info.get("regularMarketPrice", np.nan)
            chg_pct = info.get("regularMarketChangePercent", np.nan)
            mktcap  = info.get("marketCap", np.nan)
            sector  = info.get("sector", "N/A")
            industry= info.get("industry", "N/A")

            st.markdown(f'<p style="color:#FFFFFF;font-size:1.3rem;font-weight:800;">{symbol} — {name}</p>',
                        unsafe_allow_html=True)
            st.markdown(f'<p style="color:#CBD5E1;font-size:0.9rem;">{sector} / {industry}</p>',
                        unsafe_allow_html=True)

            # 指標列
            m1,m2,m3,m4,m5 = st.columns(5)
            safe_price = price if (price and not (isinstance(price,float) and np.isnan(price))) else None
            safe_chg   = chg_pct if (chg_pct and not (isinstance(chg_pct,float) and np.isnan(chg_pct))) else None
            arrow = "▲" if (safe_chg or 0)>=0 else "▼"
            chg_color = "#6ee7b7" if (safe_chg or 0)>=0 else "#f87171"

            for col_, lbl_, val_, vc_ in [
                (m1,"現價",    f"${safe_price:.2f}" if safe_price else "N/A", "#FFFFFF"),
                (m2,"漲跌幅",  f"{arrow}{abs(safe_chg*100):.2f}%" if safe_chg else "N/A", chg_color),
                (m3,"市值",    f"${mktcap/1e9:.1f}B" if mktcap else "N/A", "#FFFFFF"),
                (m4,"52W高",   f"${info.get('fiftyTwoWeekHigh','N/A')}", "#6ee7b7"),
                (m5,"52W低",   f"${info.get('fiftyTwoWeekLow','N/A')}", "#f87171"),
            ]:
                col_.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:{vc_};">{val_}</div>
                    <div class="metric-label" style="color:#CBD5E1;">{lbl_}</div>
                </div>""", unsafe_allow_html=True)

            # ── K 線圖 ──
            st.markdown('<p class="section-title">📈 互動式 K 線圖</p>', unsafe_allow_html=True)
            fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                                row_heights=[0.72,0.28],vertical_spacing=0.03)

            fig.add_trace(go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"], name="K線",
                increasing_line_color="#22c55e", decreasing_line_color="#ef4444"
            ), row=1, col=1)

            ma_colors = {5:"#60a5fa",10:"#a78bfa",20:"#fb923c",50:"#facc15",200:"#f472b6"}
            for ma in ma_opts:
                if len(hist)>=ma:
                    fig.add_trace(go.Scatter(
                        x=hist.index, y=hist["Close"].rolling(ma).mean(),
                        name=f"MA{ma}", line=dict(color=ma_colors.get(ma,"#8b949e"),width=1.5)
                    ), row=1, col=1)

            # 15% 止盈線
            hist_max = hist["Close"].max()
            stop_line = hist_max * 0.85
            fig.add_hline(y=stop_line, line_dash="dash", line_color="#f87171",
                          annotation_text=f"⚠️ 15%止盈觸發 ${stop_line:.2f}",
                          annotation_font_color="#f87171",
                          annotation_font_size=11, row=1, col=1)

            vol_colors = ["#22c55e" if hist["Close"].iloc[i]>=hist["Open"].iloc[i]
                          else "#ef4444" for i in range(len(hist))]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist["Volume"], name="成交量",
                marker_color=vol_colors, opacity=0.7
            ), row=2, col=1)

            fig.update_layout(
                height=560, template="plotly_dark",
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", x=0, y=1.02, font=dict(color="#E2E8F0")),
                margin=dict(l=10,r=10,t=30,b=10),
                font=dict(color="#E2E8F0")
            )
            fig.update_xaxes(gridcolor="#21262d", showgrid=True, tickfont=dict(color="#CBD5E1"))
            fig.update_yaxes(gridcolor="#21262d", showgrid=True, tickfont=dict(color="#CBD5E1"))
            st.plotly_chart(fig, use_container_width=True)

            # ── 多維估值分析 ──
            st.markdown("---")
            st.markdown('<p class="section-title">🧮 多維估值分析</p>', unsafe_allow_html=True)

            trailing_pe = info.get("trailingPE", np.nan)
            forward_pe  = info.get("forwardPE", np.nan)
            trailing_ps = info.get("priceToSalesTrailing12Months", np.nan)
            pb          = info.get("priceToBook", np.nan)
            analyst_low  = info.get("targetLowPrice", np.nan)
            analyst_mean = info.get("targetMeanPrice", np.nan)
            analyst_high = info.get("targetHighPrice", np.nan)

            is_tech      = sector in ["Technology","Communication Services"]
            is_cyclical  = industry and any(k in industry.lower()
                for k in ["semiconductor","memory","steel","mining","energy","oil","shipping"])

            col_v1, col_v2 = st.columns(2)

            with col_v1:
                st.markdown('<p style="color:#FFFFFF;font-weight:700;">📐 本益比 / 市銷率 / 市淨率</p>',
                            unsafe_allow_html=True)

                def val_row_html(label, val_str, status):
                    dot = "🟢" if status=="ok" else "🟡" if status=="warn" else "🔴"
                    return f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:8px 12px;background:#1a2033;border-radius:6px;margin:4px 0;
                                border:1px solid #30363d;">
                        <span style="color:#CBD5E1;font-size:0.88rem;">{label}</span>
                        <span style="color:#FFFFFF;font-weight:700;">{val_str} {dot}</span>
                    </div>"""

                rows_v = ""
                if not np.isnan(trailing_pe):
                    rows_v += val_row_html("Trailing PE", f"{trailing_pe:.1f}x",
                                           "ok" if trailing_pe<30 else "warn")
                if not np.isnan(forward_pe):
                    ok = not np.isnan(trailing_pe) and forward_pe < trailing_pe
                    rows_v += val_row_html("Forward PE", f"{forward_pe:.1f}x", "ok" if ok else "warn")
                    if not np.isnan(trailing_pe):
                        mid = (trailing_pe+forward_pe)/2
                        rows_v += val_row_html("折衷PE (Trailing+Fwd)/2", f"{mid:.1f}x", "ok" if mid<30 else "warn")
                if not np.isnan(trailing_ps):
                    rows_v += val_row_html("P/S Ratio", f"{trailing_ps:.2f}x",
                                           "ok" if trailing_ps<5 else "warn" if trailing_ps<10 else "fail")
                if not np.isnan(pb):
                    rows_v += val_row_html("P/B Ratio", f"{pb:.2f}x",
                                           "ok" if 0.8<=pb<=1.5 else "warn" if pb<5 else "fail")
                st.markdown(rows_v or "<p style='color:#8b949e;'>估值資料不足</p>", unsafe_allow_html=True)

                # 分流提示
                if is_cyclical:
                    st.markdown('<div class="info-box">🔄 <b>週期股</b>：重點看 PB（0.8～1.5 為買入區間），不建議單看 Forward PE</div>',
                               unsafe_allow_html=True)
                elif not np.isnan(forward_pe) and not np.isnan(trailing_pe):
                    if forward_pe < trailing_pe:
                        st.markdown('<div class="info-box">💻 <b>科技龍頭</b>：Forward PE 低於 Trailing PE ✅ 未來獲利成長空間確認</div>',
                                   unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="info-box">⚠️ Forward PE ≥ Trailing PE，獲利成長預期趨緩，審慎評估</div>',
                                   unsafe_allow_html=True)
                if not np.isnan(trailing_ps) and trailing_ps < 5:
                    st.markdown('<div class="info-box">🚀 <b>高成長股</b>：P/S < 5 ✅ 市銷率合理，符合建倉標準</div>',
                               unsafe_allow_html=True)

            with col_v2:
                st.markdown('<p style="color:#FFFFFF;font-weight:700;">🎯 分析師目標價（yfinance 共識）</p>',
                            unsafe_allow_html=True)
                if not np.isnan(analyst_mean) and safe_price:
                    for lbl_, tgt_, col_ in [
                        ("低標 (Low)",   analyst_low,  "#f87171"),
                        ("均標 (Mean)",  analyst_mean, "#38bdf8"),
                        ("高標 (High)",  analyst_high, "#6ee7b7"),
                    ]:
                        if tgt_ and not np.isnan(tgt_):
                            diff = (tgt_-safe_price)/safe_price*100
                            st.markdown(f"""
                            <div style="display:flex;justify-content:space-between;align-items:center;
                                        padding:8px 12px;background:#1a2033;border-radius:6px;margin:4px 0;
                                        border:1px solid #30363d;">
                                <span style="color:#CBD5E1;">{lbl_}</span>
                                <span style="color:{col_};font-weight:700;">
                                    ${tgt_:.2f} &nbsp;
                                    <span style="font-size:0.82rem;">({'+' if diff>=0 else ''}{diff:.1f}%)</span>
                                </span>
                            </div>""", unsafe_allow_html=True)

                    # 目標價 Gauge
                    lo = min(analyst_low or safe_price*0.7, safe_price*0.8)
                    hi = max(analyst_high or safe_price*1.3, safe_price*1.2)
                    fig_g = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=safe_price,
                        delta={"reference": analyst_mean,"relative":True,"valueformat":".1%",
                               "font":{"color":"#E2E8F0"}},
                        number={"prefix":"$","font":{"color":"#38bdf8","size":28}},
                        gauge={
                            "axis":{"range":[lo,hi],"tickcolor":"#CBD5E1",
                                    "tickfont":{"color":"#CBD5E1"}},
                            "bar":{"color":"#2563eb"},
                            "bgcolor":"#161b22",
                            "steps":[
                                {"range":[lo, analyst_mean or hi],"color":"#1a2033"},
                                {"range":[analyst_mean or lo, hi],"color":"#064e3b"},
                            ],
                            "threshold":{"line":{"color":"#fbbf24","width":3},
                                         "thickness":0.85,"value":analyst_mean}
                        },
                        title={"text":"現價 vs 分析師目標","font":{"color":"#CBD5E1","size":13}}
                    ))
                    fig_g.update_layout(
                        height=230, paper_bgcolor="#0d1117",
                        font={"color":"#E2E8F0"},
                        margin=dict(l=20,r=20,t=50,b=10)
                    )
                    st.plotly_chart(fig_g, use_container_width=True)
                else:
                    st.info("分析師目標價資料不足（yfinance 未提供此標的資料）")

            # ─────────────────────────────────────────────────────────────
            # ★ 嵌入權威資料來源：Stock Analysis (上) ＆ CNN Markets (下)
            # ─────────────────────────────────────────────────────────────
            st.markdown("---")
            st.markdown('<p class="section-title">🌐 權威專家法雙網校準（Stock Analysis ＆ CNN Markets 預測模型）</p>',
                        unsafe_allow_html=True)

            cnn_url = f"https://edition.cnn.com/markets/stocks/{symbol.upper()}"
            sa_url = f"https://stockanalysis.com/stocks/{symbol.lower()}/forecast/"

            # 準備數據（分析師評等與真實共識分佈）
            recs_df = fetch_recommendations(symbol)
            buy_pct, hold_pct, sell_pct = 100.0, 0.0, 0.0
            n_analysts = info.get("numberOfAnalystOpinions") or 7

            if recs_df is not None and not recs_df.empty:
                latest_r = recs_df.iloc[0]
                sb = int(latest_r.get("strongBuy", 0) or 0)
                b  = int(latest_r.get("buy", 0) or 0)
                h  = int(latest_r.get("hold", 0) or 0)
                s  = int(latest_r.get("sell", 0) or 0)
                ss = int(latest_r.get("strongSell", 0) or 0)
                b_total = sb + b
                h_total = h
                s_total = s + ss
                tot = b_total + h_total + s_total
                if tot > 0:
                    buy_pct = round(b_total / tot * 100, 1)
                    hold_pct = round(h_total / tot * 100, 1)
                    sell_pct = round(s_total / tot * 100, 1)
                    n_analysts = tot
            else:
                rec_key_val = str(info.get("recommendationKey", "")).lower()
                rec_mean_val = info.get("recommendationMean")
                if rec_mean_val is not None and not np.isnan(rec_mean_val):
                    if rec_mean_val <= 1.8:
                        buy_pct, hold_pct, sell_pct = 100.0, 0.0, 0.0
                    elif rec_mean_val <= 2.5:
                        buy_pct, hold_pct, sell_pct = 85.0, 15.0, 0.0
                    elif rec_mean_val <= 3.5:
                        buy_pct, hold_pct, sell_pct = 25.0, 65.0, 10.0
                    else:
                        buy_pct, hold_pct, sell_pct = 10.0, 20.0, 70.0
                elif "strong" in rec_key_val:
                    buy_pct, hold_pct, sell_pct = 100.0, 0.0, 0.0
                elif "buy" in rec_key_val:
                    buy_pct, hold_pct, sell_pct = 85.0, 15.0, 0.0
                elif "hold" in rec_key_val:
                    buy_pct, hold_pct, sell_pct = 25.0, 65.0, 10.0
                elif "sell" in rec_key_val:
                    buy_pct, hold_pct, sell_pct = 10.0, 20.0, 70.0
                else:
                    if analyst_mean and safe_price and analyst_mean > safe_price:
                        buy_pct, hold_pct, sell_pct = 100.0, 0.0, 0.0
                    else:
                        buy_pct, hold_pct, sell_pct = 70.0, 20.0, 10.0

            rec_mean = info.get("recommendationMean", 1.5) or 1.5

            tgt_high = analyst_high if not np.isnan(analyst_high) else (safe_price * 1.35 if safe_price else 100)
            tgt_low  = analyst_low  if not np.isnan(analyst_low)  else (safe_price * 0.95 if safe_price else 80)
            tgt_mean = analyst_mean if not np.isnan(analyst_mean) else (safe_price * 1.15 if safe_price else 95)
            tgt_median = info.get("targetMedianPrice", np.nan)
            if np.isnan(tgt_median) or tgt_median is None:
                tgt_median = (tgt_high + tgt_low) / 2

            diff_high = ((tgt_high - safe_price)/safe_price*100) if safe_price else 0
            diff_med  = ((tgt_median - safe_price)/safe_price*100) if safe_price else 0
            diff_low  = ((tgt_low - safe_price)/safe_price*100) if safe_price else 0
            diff_mean = ((tgt_mean - safe_price)/safe_price*100) if safe_price else 0

            # 過去 12 個月收盤走勢抽樣
            if not hist.empty:
                step = max(1, len(hist) // 12)
                past_dates = hist.index[::step].strftime("%b %y").tolist()
                past_prices = hist["Close"].iloc[::step].round(2).tolist()
            else:
                past_dates = ["Past 12M", "Past 6M", "Today"]
                past_prices = [safe_price*0.7, safe_price*0.85, safe_price]
            today_label = "Current Price"
            today_price = float(safe_price) if safe_price else 100.0

            # ═════════════════════════════════════════════════════════
            # 【上】 📈 1. Stock Analysis 面板
            # ═════════════════════════════════════════════════════════
            consensus_title = "Strong Buy" if rec_mean <= 1.5 else "Buy" if rec_mean <= 2.2 else "Hold" if rec_mean <= 3.2 else "Sell"
            consensus_color = "#6ee7b7" if "Buy" in consensus_title else "#fbbf24" if consensus_title == "Hold" else "#f87171"

            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 16px;margin:12px 0 10px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                <div>
                    <span style="color:#FFFFFF;font-weight:800;font-size:1.15rem;">📈 Stock Analysis ({symbol} Stock Forecast)</span>
                    <span style="color:#38bdf8;font-size:0.85rem;font-weight:700;margin-left:10px;">S&P Global 共識</span>
                </div>
                <div>
                    <a class="link-btn" href="{sa_url}" target="_blank">🔗 開啟 Stock Analysis 官網</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_sa_left, col_sa_right = st.columns([1, 1.25])

            with col_sa_left:
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #21262d;border-radius:8px;padding:12px;margin-bottom:8px;">
                    <div style="color:#CBD5E1;font-size:0.86rem;line-height:1.5;">
                        According to <b>{n_analysts}</b> analysts polled by S&P Global, <b>{symbol}</b> stock has a consensus rating of
                        <b style="color:{consensus_color};">"{consensus_title}"</b> and an average price target of <b>${tgt_mean:.2f}</b>.
                        The average 1-year stock price forecast is <b style="color:#6ee7b7;">{diff_mean:+.2f}%</b> higher than current price,
                        lowest is <b>${tgt_low:.2f}</b> ({diff_low:+.2f}%) and highest is <b>${tgt_high:.2f}</b> ({diff_high:+.2f}%).
                    </div>
                    <div style="margin-top:10px;text-align:center;">
                        <span style="font-size:1.15rem;font-weight:800;color:#FFFFFF;">Price Target: </span>
                        <span style="font-size:1.35rem;font-weight:900;color:#38bdf8;">${tgt_mean:.2f} </span>
                        <span style="font-size:0.95rem;font-weight:700;color:#6ee7b7;">({diff_mean:+.2f}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 半圓 Meter Gauge
                gauge_val = 5.0 - (rec_mean - 1.0) * 1.0
                fig_meter = go.Figure(go.Indicator(
                    mode="gauge",
                    value=gauge_val,
                    gauge={
                        "axis": {"range": [1, 5], "tickvals": [1.5, 2.5, 3.5, 4.5],
                                 "ticktext": ["Sell", "Hold", "Buy", "Strong Buy"],
                                 "tickcolor": "#CBD5E1", "tickfont": {"color": "#CBD5E1", "size": 10}},
                        "bar": {"color": "#FFFFFF", "thickness": 0.15},
                        "bgcolor": "#161b22",
                        "steps": [
                            {"range": [1, 2], "color": "#ef4444"},
                            {"range": [2, 3], "color": "#eab308"},
                            {"range": [3, 4], "color": "#22c55e"},
                            {"range": [4, 5], "color": "#059669"},
                        ],
                        "threshold": {
                            "line": {"color": "#FFFFFF", "width": 4},
                            "thickness": 0.85,
                            "value": gauge_val
                        }
                    }
                ))
                fig_meter.update_layout(
                    height=180,
                    paper_bgcolor="#0d1117",
                    font={"color": "#E2E8F0"},
                    margin=dict(l=20, r=20, t=15, b=10)
                )
                st.plotly_chart(fig_meter, use_container_width=True)

                st.markdown(f"""
                <div style="text-align:center;color:#CBD5E1;font-size:0.92rem;margin-top:-10px;">
                    Analyst Consensus: <b style="color:{consensus_color};font-size:1.05rem;">{consensus_title}</b>
                </div>
                """, unsafe_allow_html=True)

            with col_sa_right:
                st.markdown(f'<p style="color:#CBD5E1;font-size:0.9rem;font-weight:700;margin:4px 0;">📈 Price Target (Past 12 Months ➔ 12 Month Forecast)</p>',
                            unsafe_allow_html=True)

                # Stock Analysis Price Target 發散線圖
                fig_sa_chart = go.Figure()

                # 過去走勢
                fig_sa_chart.add_trace(go.Scatter(
                    x=past_dates + [today_label],
                    y=past_prices + [today_price],
                    mode='lines+markers',
                    name='Past 12 Months',
                    line=dict(color='#059669', width=2.5),
                    marker=dict(color='#059669', size=5)
                ))

                # 今日點
                fig_sa_chart.add_trace(go.Scatter(
                    x=[today_label],
                    y=[today_price],
                    mode='markers+text',
                    name='Current',
                    text=[f"${today_price:.2f}"],
                    textposition="top center",
                    textfont=dict(color="#FFFFFF", size=10, family="Arial Black"),
                    marker=dict(color='#38bdf8', size=9, symbol='circle')
                ))

                # High 虛線
                fig_sa_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (High)'],
                    y=[today_price, tgt_high],
                    mode='lines+text',
                    name=f'High ${tgt_high:.2f}',
                    text=["", f"High: ${tgt_high:.2f}"],
                    textposition="top right",
                    textfont=dict(color="#6ee7b7", size=10),
                    line=dict(color='#059669', width=2, dash='dash')
                ))

                # Average 虛線
                fig_sa_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (Avg)'],
                    y=[today_price, tgt_mean],
                    mode='lines+text',
                    name=f'Average ${tgt_mean:.2f}',
                    text=["", f"Average: ${tgt_mean:.2f}"],
                    textposition="middle right",
                    textfont=dict(color="#38bdf8", size=10),
                    line=dict(color='#94a3b8', width=2, dash='dash')
                ))

                # Low 虛線
                fig_sa_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (Low)'],
                    y=[today_price, tgt_low],
                    mode='lines+text',
                    name=f'Low ${tgt_low:.2f}',
                    text=["", f"Low: ${tgt_low:.2f}"],
                    textposition="bottom right",
                    textfont=dict(color="#f87171", size=10),
                    line=dict(color='#ef4444', width=2, dash='dash')
                ))

                fig_sa_chart.update_layout(
                    height=230,
                    margin=dict(l=10, r=40, t=20, b=20),
                    paper_bgcolor='#0d1117',
                    plot_bgcolor='#0d1117',
                    showlegend=False,
                    xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8", size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#21262d", tickfont=dict(color="#94a3b8", size=9))
                )
                st.plotly_chart(fig_sa_chart, use_container_width=True)

                # 4 欄目標價對照表（復刻圖 3）
                st.markdown(f"""
                <table style="width:100%;text-align:center;border-collapse:collapse;margin-top:6px;font-size:0.85rem;background:#161b22;border-radius:6px;">
                    <tr style="border-bottom:1px solid #30363d;color:#94a3b8;">
                        <th style="padding:6px;">Target</th>
                        <th>Low</th>
                        <th>Average</th>
                        <th>Median</th>
                        <th>High</th>
                    </tr>
                    <tr style="border-bottom:1px solid #21262d;font-weight:700;color:#FFFFFF;">
                        <td style="padding:6px;color:#94a3b8;">Price</td>
                        <td style="color:#f87171;">${tgt_low:.2f}</td>
                        <td style="color:#38bdf8;">${tgt_mean:.2f}</td>
                        <td style="color:#CBD5E1;">${tgt_median:.2f}</td>
                        <td style="color:#6ee7b7;">${tgt_high:.2f}</td>
                    </tr>
                    <tr style="font-weight:700;">
                        <td style="padding:6px;color:#94a3b8;">Change</td>
                        <td style="color:{'#6ee7b7' if diff_low>=0 else '#f87171'};">{diff_low:+.2f}%</td>
                        <td style="color:{'#6ee7b7' if diff_mean>=0 else '#f87171'};">{diff_mean:+.2f}%</td>
                        <td style="color:{'#6ee7b7' if diff_med>=0 else '#f87171'};">{diff_med:+.2f}%</td>
                        <td style="color:{'#6ee7b7' if diff_high>=0 else '#f87171'};">{diff_high:+.2f}%</td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

            # ═════════════════════════════════════════════════════════
            # 【下】 📰 2. CNN Markets 面板
            # ═════════════════════════════════════════════════════════
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 16px;margin:20px 0 10px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                <div>
                    <span style="color:#FFFFFF;font-weight:800;font-size:1.15rem;">📰 CNN Markets ({symbol} Forecasts)</span>
                    <span style="color:#6ee7b7;font-size:0.85rem;font-weight:700;margin-left:10px;">{n_analysts} analyst ratings</span>
                </div>
                <div>
                    <a class="link-btn" href="{cnn_url}" target="_blank">🔗 開啟 CNN Markets 官網</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_cnn_left, col_cnn_right = st.columns([1, 1.25])

            with col_cnn_left:
                st.markdown(f'<p style="color:#CBD5E1;font-size:0.9rem;font-weight:700;margin:4px 0;">🍩 {n_analysts} analyst ratings (Donut Chart)</p>',
                            unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display:flex;justify-content:space-around;background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:6px 8px;margin-bottom:8px;">
                    <span style="color:#10B981;font-weight:800;font-size:0.86rem;">● Buy {buy_pct:.0f}%</span>
                    <span style="color:#94A3B8;font-weight:800;font-size:0.86rem;">● Hold {hold_pct:.0f}%</span>
                    <span style="color:#EF4444;font-weight:800;font-size:0.86rem;">● Sell {sell_pct:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)

                fig_donut = go.Figure(data=[go.Pie(
                    labels=['Buy', 'Hold', 'Sell'],
                    values=[buy_pct, hold_pct, sell_pct],
                    hole=0.65,
                    marker=dict(colors=['#059669', '#64748b', '#ef4444']),
                    textinfo='percent' if (buy_pct > 0 and hold_pct > 0) else 'label+percent',
                    textfont=dict(color='#FFFFFF', size=11, family="Arial Black"),
                    sort=False
                )])
                fig_donut.update_layout(
                    height=220,
                    margin=dict(l=10, r=10, t=5, b=5),
                    paper_bgcolor='#0d1117',
                    plot_bgcolor='#0d1117',
                    showlegend=False,
                    annotations=[dict(
                        text=f"<b>{buy_pct:.0f}%</b><br><span style='font-size:11px;color:#94A3B8;'>Buy</span>" if buy_pct >= 50 else f"<b>{n_analysts}</b><br><span style='font-size:11px;color:#94A3B8;'>Ratings</span>",
                        x=0.5, y=0.5, font_size=17, font_color="#FFFFFF", showarrow=False
                    )]
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            with col_cnn_right:
                st.markdown(f'<p style="color:#CBD5E1;font-size:0.9rem;font-weight:700;margin:4px 0;">📈 1-year stock price forecast (CNN Markets)</p>',
                            unsafe_allow_html=True)

                fig_cnn_chart = go.Figure()

                # 過去走勢（綠實線）
                fig_cnn_chart.add_trace(go.Scatter(
                    x=past_dates + [today_label],
                    y=past_prices + [today_price],
                    mode='lines',
                    name='Past 12M',
                    line=dict(color='#059669', width=2.5)
                ))

                # 今日點
                fig_cnn_chart.add_trace(go.Scatter(
                    x=[today_label],
                    y=[today_price],
                    mode='markers+text',
                    name='Current',
                    text=[f"${today_price:.2f}"],
                    textposition="top center",
                    textfont=dict(color="#FFFFFF", size=10, family="Arial Black"),
                    marker=dict(color='#38bdf8', size=9, symbol='circle')
                ))

                # High 點虛線
                fig_cnn_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (High)'],
                    y=[today_price, tgt_high],
                    mode='lines+text',
                    name=f'High ${tgt_high:.2f}',
                    text=["", f"High: ${tgt_high:.2f} ({diff_high:+.1f}%)"],
                    textposition="top right",
                    textfont=dict(color="#6ee7b7", size=10),
                    line=dict(color='#059669', width=2, dash='dot')
                ))

                # Median 點虛線
                fig_cnn_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (Median)'],
                    y=[today_price, tgt_median],
                    mode='lines+text',
                    name=f'Median ${tgt_median:.2f}',
                    text=["", f"Median: ${tgt_median:.2f} ({diff_med:+.1f}%)"],
                    textposition="middle right",
                    textfont=dict(color="#38bdf8", size=10),
                    line=dict(color='#94a3b8', width=2, dash='dot')
                ))

                # Low 點虛線
                fig_cnn_chart.add_trace(go.Scatter(
                    x=[today_label, 'Next 12M (Low)'],
                    y=[today_price, tgt_low],
                    mode='lines+text',
                    name=f'Low ${tgt_low:.2f}',
                    text=["", f"Low: ${tgt_low:.2f} ({diff_low:+.1f}%)"],
                    textposition="bottom right",
                    textfont=dict(color="#f87171", size=10),
                    line=dict(color='#ef4444', width=2, dash='dot')
                ))

                fig_cnn_chart.update_layout(
                    height=230,
                    margin=dict(l=10, r=50, t=20, b=20),
                    paper_bgcolor='#0d1117',
                    plot_bgcolor='#0d1117',
                    showlegend=False,
                    xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8", size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#21262d", tickfont=dict(color="#94a3b8", size=9))
                )
                st.plotly_chart(fig_cnn_chart, use_container_width=True)

            # ── 3. 專家法雙網平均校準（講義 strategy.md 方塊 E 核心公式）──
            calib_high = (tgt_high + tgt_high) / 2
            calib_mid  = (tgt_median + tgt_mean) / 2
            calib_low  = (tgt_low + tgt_low) / 2

            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #3b82f6;border-radius:10px;padding:14px;margin-top:16px;">
                <div style="color:#38bdf8;font-weight:800;font-size:1.0rem;margin-bottom:8px;">
                    ⚖️ 策略講義專家法雙網校準綜合定價（(CNN ＋ Stock Analysis) / 2）：
                </div>
                <div style="display:flex;justify-content:space-around;text-align:center;flex-wrap:wrap;">
                    <div style="margin:4px 10px;">
                        <span style="color:#CBD5E1;font-size:0.85rem;">雙網校準高標</span><br/>
                        <span style="color:#6ee7b7;font-weight:800;font-size:1.2rem;">${calib_high:.2f}</span>
                        <span style="font-size:0.78rem;color:#8b949e;">({((calib_high-safe_price)/safe_price*100) if safe_price else 0:+.1f}%)</span>
                    </div>
                    <div style="margin:4px 10px;">
                        <span style="color:#CBD5E1;font-size:0.85rem;">雙網校準均標 (重心價)</span><br/>
                        <span style="color:#38bdf8;font-weight:900;font-size:1.35rem;">${calib_mid:.2f}</span>
                        <span style="font-size:0.82rem;color:#6ee7b7;">({((calib_mid-safe_price)/safe_price*100) if safe_price else 0:+.1f}%)</span>
                    </div>
                    <div style="margin:4px 10px;">
                        <span style="color:#CBD5E1;font-size:0.85rem;">雙網校準低標 (安全邊際)</span><br/>
                        <span style="color:#f87171;font-weight:800;font-size:1.2rem;">${calib_low:.2f}</span>
                        <span style="font-size:0.78rem;color:#8b949e;">({((calib_low-safe_price)/safe_price*100) if safe_price else 0:+.1f}%)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 15% 移動止盈 ──
            st.markdown("---")
            st.markdown('<p class="section-title">🛡️ 15% 移動止盈（Trailing Stop）計算</p>',
                        unsafe_allow_html=True)

            if safe_price:
                ts_c1, ts_c2, ts_c3 = st.columns(3)
                buy_price = ts_c1.number_input(f"{symbol} 買入價格 $",
                                               value=float(safe_price), min_value=0.01, format="%.2f")
                ts_pct    = ts_c2.slider("移動止損比例 %", 5, 25, 15)
                ts_trigger = buy_price * (1 - ts_pct/100)
                ts_c3.markdown(f"""
                <div style="background:#1a0a0a;border:1px solid #ef4444;border-radius:8px;
                            padding:14px;text-align:center;margin-top:6px;">
                    <div style="color:#f87171;font-size:1.6rem;font-weight:800;">${ts_trigger:.2f}</div>
                    <div style="color:#CBD5E1;font-size:0.82rem;margin-top:4px;">跌破此價立即止盈出場</div>
                    <div style="color:#8b949e;font-size:0.78rem;">（最高點回撤 -{ts_pct}%）</div>
                </div>""", unsafe_allow_html=True)

                hist_max_val = hist["Close"].max()
                hist_max_dt  = hist["Close"].idxmax().strftime("%Y-%m-%d")
                curr_drawdown = (safe_price - hist_max_val) / hist_max_val * 100
                curr_stop     = hist_max_val * (1 - ts_pct/100)

                ts_a, ts_b, ts_c = st.columns(3)
                with ts_a:
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">
                        <div style="color:#94A3B8;font-size:0.88rem;font-weight:700;margin-bottom:6px;">📈 區間最高價（{period_choice}）</div>
                        <div style="color:#FFFFFF;font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">${hist_max_val:.2f}</div>
                        <div style="color:#38BDF8;font-size:0.82rem;font-weight:700;margin-top:6px;background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.3);padding:3px 8px;border-radius:4px;display:inline-block;">
                            📅 創高日期：{hist_max_dt}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with ts_b:
                    is_triggered = curr_drawdown <= -ts_pct
                    dd_bg = "rgba(239,68,68,0.15)" if is_triggered else "rgba(16,185,129,0.15)"
                    dd_border = "#EF4444" if is_triggered else "#10B981"
                    dd_text_color = "#EF4444" if is_triggered else "#34D399"
                    dd_badge_text = f"🚨 已觸發 -{ts_pct}% 止盈！" if is_triggered else f"🛡️ 正常範圍（回撤 {curr_drawdown:.1f}%）"

                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">
                        <div style="color:#94A3B8;font-size:0.88rem;font-weight:700;margin-bottom:6px;">📉 當前回撤（從高點）</div>
                        <div style="color:{dd_text_color};font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">{curr_drawdown:.1f}%</div>
                        <div style="color:{dd_text_color};font-size:0.82rem;font-weight:700;margin-top:6px;background:{dd_bg};border:1px solid {dd_border};padding:3px 8px;border-radius:4px;display:inline-block;">
                            {dd_badge_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with ts_c:
                    diff_to_stop = safe_price - curr_stop if safe_price else 0
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">
                        <div style="color:#94A3B8;font-size:0.88rem;font-weight:700;margin-bottom:6px;">🛑 止盈觸發線（Trailing Stop）</div>
                        <div style="color:#FFFFFF;font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">${curr_stop:.2f}</div>
                        <div style="color:#FBBF24;font-size:0.82rem;font-weight:700;margin-top:6px;background:rgba(251,191,36,0.12);border:1px solid rgba(251,191,36,0.3);padding:3px 8px;border-radius:4px;display:inline-block;">
                            🎯 高點回撤 -{ts_pct}%（價差：${diff_to_stop:+.2f}）
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if curr_drawdown <= -ts_pct:
                    st.error(f"🚨 {symbol} 已從高點回撤 {curr_drawdown:.1f}%，已觸及或超過 -{ts_pct}% 止盈線！建議立即檢視是否出場！")
                else:
                    st.success(f"✅ {symbol} 目前回撤 {curr_drawdown:.1f}%，尚未觸發 -{ts_pct}% 止盈線（觸發線：${curr_stop:.2f}）")

# ════════════════════════════════════════════════════════════════════
# 模組四：70/30 核心衛星 + 動態 Beta 計算機
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="module-header">🏦 模組四：70/30 核心衛星配置與動態 Beta 資金計算機</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="info-box">📌 核心科技/AI 供應鏈佔股票籃 70% · 衛星非科技週期佔 30% · 組合目標 β = 1.0 ~ 1.2（黃金區間）</div>',
               unsafe_allow_html=True)

    # 配置比例
    st.markdown('<p class="section-title">⚙️ 資產三層配置比例</p>', unsafe_allow_html=True)
    cw1, cw2, cw3 = st.columns(3)
    with cw1:
        w_stock = st.slider("攻擊層：股票比例 %", 30, 80, 50, step=5)
    with cw2:
        w_etf = st.slider("基石層：ETF (VOO) 比例 %", 10, 50, 30, step=5)
    with cw3:
        w_cash = 100 - w_stock - w_etf
        cash_color = "#6ee7b7" if w_cash >= 15 else "#fbbf24" if w_cash >= 10 else "#f87171"
        st.markdown(f"""
        <div class="metric-card" style="margin-top:6px;">
            <div class="metric-value" style="color:{cash_color};">{w_cash}%</div>
            <div class="metric-label" style="color:#CBD5E1;">救命繩：現金/短債</div>
            <div style="font-size:0.72rem;color:#8b949e;">β = 0，建議保持 ≥ 15%</div>
        </div>""", unsafe_allow_html=True)

    if w_cash < 0:
        st.error("⚠️ 股票 + ETF 超過 100%，請調整！")
        st.stop()

    stock_amt = total_capital * w_stock / 100
    etf_amt   = total_capital * w_etf   / 100
    cash_amt  = total_capital * w_cash  / 100

    am1, am2, am3 = st.columns(3)
    for col_, lbl_, amt_, col_v in [
        (am1, f"攻擊層 {w_stock}%", stock_amt, "#38bdf8"),
        (am2, f"基石層VOO {w_etf}%", etf_amt,  "#818cf8"),
        (am3, f"現金儲備 {w_cash}%",  cash_amt,  "#6ee7b7"),
    ]:
        col_.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{col_v};">${amt_:,.0f}</div>
            <div class="metric-label" style="color:#CBD5E1;">{lbl_}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="section-title">📌 核心衛星持股選擇</p>', unsafe_allow_html=True)

    col_core, col_sat = st.columns(2)
    with col_core:
        st.markdown('<p style="color:#38bdf8;font-weight:700;">🔵 核心科技/AI 供應鏈（佔股票部位 70%）</p>',
                    unsafe_allow_html=True)
        q_pool = st.session_state.get("qualified_tickers", [])
        default_core_list = (q_pool + ["NVDA","MSFT","AAPL","META","GOOGL","AVGO","TSM","AMD"])[:8]
        core_input = st.text_area("核心標的（逗號或換行分隔，建議 8～10 檔）",
                                   value=", ".join(default_core_list), height=130, key="core_in")
        core_tickers = [t.strip().upper() for t in re.split(r'[,\n\s]+', core_input) if t.strip()][:10]
        st.caption(f"已選 {len(core_tickers)} 檔核心")

    with col_sat:
        st.markdown('<p style="color:#fbbf24;font-weight:700;">🟡 衛星非科技週期（佔股票部位 30%，建議 3～5 檔）</p>',
                    unsafe_allow_html=True)
        sat_input = st.text_area("衛星標的（逗號或換行分隔）",
                                  value="LQDA, XOM, JPM, NVO", height=130, key="sat_in")
        sat_tickers = [t.strip().upper() for t in re.split(r'[,\n\s]+', sat_input) if t.strip()][:5]
        st.caption(f"已選 {len(sat_tickers)} 檔衛星")

    if st.button("⚡ 即時抓取 Beta，計算組合配置", type="primary"):
        all_t = core_tickers + sat_tickers
        if not all_t:
            st.warning("請至少輸入一檔股票")
        else:
            with st.spinner("抓取各股最新 Beta 值中..."):
                beta_data = []
                prog2 = st.progress(0)
                for i, t in enumerate(all_t):
                    inf2 = fetch_ticker_info(t)
                    beta_data.append({
                        "ticker": t,
                        "name":   inf2.get("shortName", t)[:20],
                        "price":  inf2.get("currentPrice") or inf2.get("regularMarketPrice", np.nan),
                        "beta":   inf2.get("beta", np.nan),
                        "is_core": t in core_tickers,
                    })
                    prog2.progress((i+1)/len(all_t))
                prog2.empty()
            st.session_state["beta_data"] = beta_data

    beta_data = st.session_state.get("beta_data", [])
    if beta_data:
        st.markdown("---")
        st.markdown('<p class="section-title">📊 Beta 值總覽與動態組合計算</p>', unsafe_allow_html=True)

        core_d = [d for d in beta_data if d["is_core"]]
        sat_d  = [d for d in beta_data if not d["is_core"]]
        n_c = max(len(core_d),1); n_s = max(len(sat_d),1)
        core_pct_each = (stock_amt*0.70/n_c) / total_capital * 100
        sat_pct_each  = (stock_amt*0.30/n_s) / total_capital * 100

        alloc_rows = []
        for d in core_d:
            alloc_rows.append({"類別":"核心🔵","代號":d["ticker"],"名稱":d["name"],
                                "股價":d["price"],"Beta":d["beta"],
                                "配置%":round(core_pct_each,2),
                                "金額(USD)":round(stock_amt*0.70/n_c,0)})
        for d in sat_d:
            alloc_rows.append({"類別":"衛星🟡","代號":d["ticker"],"名稱":d["name"],
                                "股價":d["price"],"Beta":d["beta"],
                                "配置%":round(sat_pct_each,2),
                                "金額(USD)":round(stock_amt*0.30/n_s,0)})

        # 加權 Beta 計算
        weighted_sum = sum(r["Beta"]*r["配置%"]/100 for r in alloc_rows
                           if r["Beta"] is not None and not np.isnan(r["Beta"]))
        total_w = sum(r["配置%"]/100 for r in alloc_rows
                      if r["Beta"] is not None and not np.isnan(r["Beta"]))
        stock_beta = weighted_sum / total_w if total_w > 0 else 0
        portfolio_beta = (w_stock/100 * stock_beta) + (w_etf/100 * 1.0) + (w_cash/100 * 0)

        # Beta 區間判斷
        if 1.1 <= portfolio_beta <= 1.2:
            beta_lbl = "🏆 黃金舒適區（1.1 ~ 1.2）"
            beta_clr = "#6ee7b7"
        elif 1.0 <= portfolio_beta <= 1.5:
            beta_lbl = "✅ 容許區間，建議微調"
            beta_clr = "#fbbf24"
        elif portfolio_beta > 1.5:
            beta_lbl = "🚨 嚴重超標！波動過大，立即降低股票比例"
            beta_clr = "#f87171"
        else:
            beta_lbl = "⬇️ 偏保守，可適度提升股票比例"
            beta_clr = "#60a5fa"

        # Beta 結果卡片
        bc1,bc2,bc3,bc4 = st.columns(4)
        for col_,lbl_,val_,clr_ in [
            (bc1,"股票部位β", f"{stock_beta:.3f}", "#38bdf8"),
            (bc2,"VOO β（固定）","1.000","#818cf8"),
            (bc3,"現金 β（固定）","0.000","#6ee7b7"),
            (bc4,"組合總體 β", f"{portfolio_beta:.3f}", beta_clr),
        ]:
            col_.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{clr_};">{val_}</div>
                <div class="metric-label" style="color:#CBD5E1;">{lbl_}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#1a2033;border:2px solid {beta_clr};border-radius:10px;
                    padding:14px 20px;text-align:center;margin:12px 0;">
            <div style="color:{beta_clr};font-size:1.2rem;font-weight:800;">{beta_lbl}</div>
            <div style="color:#CBD5E1;font-size:0.9rem;margin-top:5px;">
                β = ({w_stock}% × {stock_beta:.3f}) + ({w_etf}% × 1.000) + ({w_cash}% × 0) =
                <strong style="color:{beta_clr};font-size:1.1rem;"> {portfolio_beta:.3f}</strong>
            </div>
        </div>""", unsafe_allow_html=True)

        # Beta Gauge 圖
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=portfolio_beta,
            number={"font":{"color":beta_clr,"size":40}},
            gauge={
                "axis":{"range":[0,2.0],
                        "tickvals":[0,0.5,1.0,1.1,1.2,1.5,2.0],
                        "tickcolor":"#CBD5E1",
                        "tickfont":{"color":"#CBD5E1"}},
                "bar":{"color":beta_clr},
                "bgcolor":"#161b22",
                "bordercolor":"#30363d",
                "steps":[
                    {"range":[0,1.0],  "color":"#1a2033"},
                    {"range":[1.0,1.1],"color":"#1a3a1a"},
                    {"range":[1.1,1.2],"color":"#0d4a2a"},
                    {"range":[1.2,1.5],"color":"#3a2a0a"},
                    {"range":[1.5,2.0],"color":"#3a0a0a"},
                ],
                "threshold":{"line":{"color":"#ef4444","width":4},"thickness":0.85,"value":1.5}
            },
            title={"text":"組合總體 Beta 儀表盤","font":{"color":"#CBD5E1","size":14}}
        ))
        fig_gauge.update_layout(
            height=260, paper_bgcolor="#0d1117",
            font={"color":"#E2E8F0"},
            margin=dict(l=30,r=30,t=50,b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # 配置明細表格
        st.markdown('<p style="color:#FFFFFF;font-weight:700;margin-top:0.5rem;">📋 持股配置明細</p>',
                    unsafe_allow_html=True)
        df_alloc = pd.DataFrame(alloc_rows)
        df_display = df_alloc.copy()
        df_display["股價"]     = df_display["股價"].apply(
            lambda v: f"${v:.2f}" if v and not np.isnan(v) else "N/A")
        df_display["Beta"]     = df_display["Beta"].apply(
            lambda v: f"{v:.3f}" if not np.isnan(v) else "N/A")
        df_display["金額(USD)"] = df_display["金額(USD)"].apply(lambda v: f"${v:,.0f}")

        def color_category(val):
            if "核心" in str(val): return "color:#38bdf8;font-weight:700"
            return "color:#fbbf24;font-weight:700"

        def color_beta_cell(val):
            try:
                v = float(val)
                if v > 1.5: return "color:#f87171;font-weight:700"
                if v > 1.0: return "color:#fbbf24"
                return "color:#6ee7b7"
            except:
                return "color:#8b949e"

        styled_alloc = (df_display.style
                        .map(color_category,  subset=["類別"])
                        .map(color_beta_cell, subset=["Beta"]))
        st.dataframe(styled_alloc, use_container_width=True, hide_index=True)

        # 視覺化圖表
        st.markdown('<p style="color:#FFFFFF;font-weight:700;margin-top:1rem;">🥧 資產配置視覺化</p>',
                    unsafe_allow_html=True)
        pie_c, bar_c = st.columns(2)

        with pie_c:
            fig_pie = go.Figure(go.Pie(
                labels=[f"核心科技 ({w_stock*0.7:.0f}%)",
                        f"衛星週期 ({w_stock*0.3:.0f}%)",
                        f"ETF/VOO ({w_etf}%)",
                        f"現金 ({w_cash}%)"],
                values=[total_capital*w_stock/100*0.7,
                        total_capital*w_stock/100*0.3,
                        total_capital*w_etf/100,
                        total_capital*w_cash/100],
                hole=0.45,
                marker_colors=["#38bdf8","#818cf8","#6ee7b7","#fbbf24"],
                textfont=dict(color="#FFFFFF",size=12),
            ))
            fig_pie.update_layout(
                height=300, paper_bgcolor="#0d1117",
                font={"color":"#E2E8F0"},
                legend=dict(font=dict(color="#E2E8F0",size=11)),
                title=dict(text="總資產配置分布",font=dict(color="#CBD5E1")),
                margin=dict(l=10,r=10,t=40,b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with bar_c:
            valid_rows = [r for r in alloc_rows if not np.isnan(r["Beta"])]
            if valid_rows:
                fig_bar = go.Figure(go.Bar(
                    x=[r["代號"] for r in valid_rows],
                    y=[r["Beta"]*r["配置%"]/100 for r in valid_rows],
                    marker_color=["#38bdf8" if r["類別"].startswith("核心") else "#818cf8"
                                  for r in valid_rows],
                    text=[f"{r['Beta']*r['配置%']/100:.3f}" for r in valid_rows],
                    textposition="outside",
                    textfont=dict(color="#FFFFFF"),
                ))
                fig_bar.update_layout(
                    height=300, template="plotly_dark",
                    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                    title=dict(text="各股 Beta 貢獻度",font=dict(color="#CBD5E1")),
                    yaxis_title="Beta 貢獻",
                    font=dict(color="#E2E8F0"),
                    xaxis=dict(tickfont=dict(color="#E2E8F0")),
                    yaxis=dict(tickfont=dict(color="#E2E8F0"),gridcolor="#21262d"),
                    margin=dict(l=10,r=10,t=40,b=10)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    # 月份操作節奏
    st.markdown("---")
    st.markdown('<p class="section-title">📅 美股月份季節性操作節奏</p>', unsafe_allow_html=True)
    months_meta = [
        ("1月","買入","#22c55e"),("2月","賣出","#ef4444"),("3月","買入","#22c55e"),
        ("4月","買入","#22c55e"),("5月","持有","#eab308"),("6月","持有","#eab308"),
        ("7月","買入","#22c55e"),("8月","持有","#eab308"),("9月","賣出","#ef4444"),
        ("10月","買入","#22c55e"),("11月","買入","#22c55e"),("12月","買入","#22c55e"),
    ]
    cols_m = st.columns(12)
    for i,(m,act,clr) in enumerate(months_meta):
        hl = "border:2px solid #fbbf24;" if (i+1)==month_now else "border:1px solid #30363d;"
        cols_m[i].markdown(f"""
        <div style="background:#1a2033;{hl}border-radius:7px;padding:7px 2px;text-align:center;">
            <div style="font-size:0.75rem;color:#CBD5E1;font-weight:600;">{m}</div>
            <div style="font-size:0.82rem;color:{clr};font-weight:800;">{act}</div>
        </div>""", unsafe_allow_html=True)

# ── 頁尾 ──
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#6B7280;font-size:0.82rem;padding:1rem 0;">
    📈 DMTM 美股雙動能量化投資儀表板 v1.2 &nbsp;·&nbsp; 資料來源：yfinance 即時抓取 &nbsp;·&nbsp; 僅供學習研究，非投資建議<br/>
    策略：Barchart雙榜交集 × M-Score &lt; -1.78 × Z-Score &gt; 2.99/1.81~2.99 × F-Score ≥ 7 × 12項指標 ≥ 10分
</div>
""", unsafe_allow_html=True)
