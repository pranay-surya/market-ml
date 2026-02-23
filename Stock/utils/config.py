"""
config.py — Central configuration: stock universe, time periods, theme, and styling.
"""

# ─────────────────────────────────────────────
# STOCK UNIVERSE
# ─────────────────────────────────────────────
STOCKS = {
    # Technology
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Alphabet (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Tesla (TSLA)": "TSLA",
    # Finance & Healthcare
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Visa (V)": "V",
    "UnitedHealth (UNH)": "UNH",
    "JPMorgan Chase (JPM)": "JPM",
    "Johnson & Johnson (JNJ)": "JNJ",
    # Additional
    "Walmart (WMT)": "WMT",
    "Procter & Gamble (PG)": "PG",
    "Mastercard (MA)": "MA",
}

# ─────────────────────────────────────────────
# TIME PERIODS
# ─────────────────────────────────────────────
PERIOD_MAP = {
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
COLORS = [
    "#00d4aa",  # Primary accent (teal)
    "#3b82f6",  # Secondary accent (blue)
    "#f59e0b",  # Warning (amber)
    "#8b5cf6",  # Purple
    "#f43f5e",  # Danger (rose)
    "#10b981",  # Success (emerald)
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#84cc16",  # Lime
    "#fb923c",  # Orange
]

# ─────────────────────────────────────────────
# PLOTLY THEME CONFIGURATION
# ─────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(10,14,26,0)",
    plot_bgcolor="rgba(17,24,39,0.6)",
    font=dict(
        family="DM Sans, sans-serif",
        color="#94a3b8",
        size=12,
    ),
    xaxis=dict(
        gridcolor="#1e2d45",
        showgrid=True,
        zeroline=False,
        linecolor="#1e2d45",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="#1e2d45",
        showgrid=True,
        zeroline=False,
        linecolor="#1e2d45",
        tickfont=dict(size=11),
    ),
    margin=dict(l=20, r=20, t=40, b=20),
    hoverlabel=dict(
        bgcolor="#1a2235",
        bordercolor="#1e2d45",
        font=dict(family="DM Sans", color="#e2e8f0"),
    ),
)


def get_plotly_layout(**overrides):
    """
    Returns a copy of PLOTLY_THEME merged with any overrides.
    Use this to avoid conflicts when charts need custom settings.
    """
    layout = PLOTLY_THEME.copy()
    layout.update(overrides)
    return layout


# ─────────────────────────────────────────────
# CUSTOM CSS STYLES
# ─────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ══════════════════════════════════════════════
   FONT IMPORTS
   ══════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ══════════════════════════════════════════════
   CSS VARIABLES
   ══════════════════════════════════════════════ */
:root {
    /* Background colors */
    --bg-primary:    #0a0e1a;
    --bg-surface:    #111827;
    --bg-surface-2:  #1a2235;
    --bg-elevated:   #1e293b;
    
    /* Border colors */
    --border-primary: #1e2d45;
    --border-subtle:  #334155;
    
    /* Accent colors */
    --accent-primary:   #00d4aa;
    --accent-secondary: #3b82f6;
    --accent-tertiary:  #8b5cf6;
    
    /* Semantic colors */
    --color-bull:    #00d4aa;
    --color-bear:    #f43f5e;
    --color-warning: #f59e0b;
    --color-info:    #3b82f6;
    
    /* Text colors */
    --text-primary:   #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted:     #64748b;
    
    /* Spacing */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    
    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-normal: 0.25s ease;
}

/* ══════════════════════════════════════════════
   BASE STYLES
   ══════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Material Icons base styling */
.material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    vertical-align: middle;
    line-height: 1;
}

/* ══════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-primary);
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] h4 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ══════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface-2);
    border-radius: var(--radius-lg);
    padding: 6px;
    gap: 6px;
    border: 1px solid var(--border-primary);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-muted) !important;
    border-radius: var(--radius-md);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 10px 24px;
    transition: var(--transition-fast);
    border: none;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(59, 130, 246, 0.1);
    color: var(--text-secondary) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--accent-secondary) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* ══════════════════════════════════════════════
   METRIC CARDS
   ══════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 18px 22px;
    transition: var(--transition-fast);
}

[data-testid="stMetric"]:hover {
    border-color: var(--border-subtle);
    background: var(--bg-surface-2);
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

[data-testid="stMetricDelta"] svg {
    width: 12px;
    height: 12px;
}

/* ══════════════════════════════════════════════
   CONTAINERS & CARDS
   ══════════════════════════════════════════════ */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
}

/* Info card styling */
.info-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin: 10px 0;
    transition: var(--transition-fast);
}

.info-card:hover {
    border-color: var(--border-subtle);
}

.info-card h4 {
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.info-card p {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.6;
    margin: 6px 0;
}

/* ══════════════════════════════════════════════
   SIGNAL BADGES
   ══════════════════════════════════════════════ */
.signal-bull {
    background: rgba(0, 212, 170, 0.12);
    color: var(--color-bull);
    border: 1px solid rgba(0, 212, 170, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.02em;
}

.signal-bear {
    background: rgba(244, 63, 94, 0.12);
    color: var(--color-bear);
    border: 1px solid rgba(244, 63, 94, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.02em;
}

.signal-hold {
    background: rgba(234, 179, 8, 0.12);
    color: var(--color-warning);
    border: 1px solid rgba(234, 179, 8, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.02em;
}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════ */
h1, h2, h3 {
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
}

h1 { font-size: 1.75rem !important; }
h2 { font-size: 1.4rem !important; }
h3 { font-size: 1.15rem !important; }

h4 {
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* ══════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════ */
.stButton > button {
    background: var(--bg-surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    transition: var(--transition-fast) !important;
}

.stButton > button:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--border-subtle) !important;
}

.stButton > button[kind="primary"] {
    background: var(--accent-secondary) !important;
    border-color: var(--accent-secondary) !important;
}

.stButton > button[kind="primary"]:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
}

.stDownloadButton > button {
    background: var(--bg-surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: var(--transition-fast) !important;
}

.stDownloadButton > button:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--accent-secondary) !important;
    color: var(--accent-secondary) !important;
}

/* ══════════════════════════════════════════════
   INPUTS & SELECTS
   ══════════════════════════════════════════════ */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-surface-2) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
}

.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: var(--accent-secondary) !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* ══════════════════════════════════════════════
   DATAFRAMES & TABLES
   ══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-surface-2) !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.7rem !important;
    letter-spacing: 0.05em;
}

[data-testid="stDataFrame"] td {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ══════════════════════════════════════════════
   DIVIDERS
   ══════════════════════════════════════════════ */
hr, [data-testid="stDivider"] {
    border: none !important;
    border-top: 1px solid var(--border-primary) !important;
    margin: 24px 0 !important;
}

/* ══════════════════════════════════════════════
   ALERTS & NOTIFICATIONS
   ══════════════════════════════════════════════ */
.stAlert {
    border-radius: var(--radius-lg) !important;
    border: 1px solid !important;
}

[data-testid="stAlert"][data-baseweb="notification"] {
    background: var(--bg-surface) !important;
}

/* ══════════════════════════════════════════════
   SPINNER
   ══════════════════════════════════════════════ */
.stSpinner > div {
    border-color: var(--accent-secondary) !important;
    border-top-color: transparent !important;
}

/* ══════════════════════════════════════════════
   CAPTIONS
   ══════════════════════════════════════════════ */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════
   NEWS ITEMS
   ══════════════════════════════════════════════ */
.news-item {
    background: var(--bg-surface-2);
    border-left: 3px solid var(--accent-secondary);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 12px 16px;
    margin: 8px 0;
    transition: var(--transition-fast);
}

.news-item:hover {
    background: var(--bg-elevated);
}

.news-item a {
    color: var(--text-primary);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.875rem;
    line-height: 1.4;
    display: block;
}

.news-item a:hover {
    color: var(--accent-secondary);
}

.news-item span {
    color: var(--text-muted);
    font-size: 0.75rem;
    display: block;
    margin-top: 6px;
}

/* ══════════════════════════════════════════════
   BADGE STYLES
   ══════════════════════════════════════════════ */
.badge-beta {
    background: linear-gradient(135deg, var(--accent-secondary), var(--accent-tertiary));
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    display: inline-block;
    vertical-align: middle;
    margin-left: 10px;
}

/* ══════════════════════════════════════════════
   SCROLLBAR STYLING
   ══════════════════════════════════════════════ */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-subtle);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* ══════════════════════════════════════════════
   TOGGLE SWITCH
   ══════════════════════════════════════════════ */
[data-testid="stToggle"] label span {
    color: var(--text-secondary) !important;
}

/* ══════════════════════════════════════════════
   SLIDER
   ══════════════════════════════════════════════ */
.stSlider > div > div > div {
    background: var(--accent-secondary) !important;
}

.stSlider > div > div > div > div {
    background: white !important;
    border: 2px solid var(--accent-secondary) !important;
}

/* ══════════════════════════════════════════════
   EXPANDER
   ══════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-primary) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

.streamlit-expanderContent {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-primary) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
}

/* ══════════════════════════════════════════════
   CHART CONTAINERS
   ══════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] {
    border-radius: var(--radius-lg);
    overflow: hidden;
}

/* ══════════════════════════════════════════════
   RESPONSIVE ADJUSTMENTS
   ══════════════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-size: 0.85rem;
    }
}
</style>
"""