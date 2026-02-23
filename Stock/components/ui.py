"""
ui.py — Reusable Streamlit UI components with Google Material Icons integration.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from utils.config import STOCKS, PERIOD_MAP


# ─────────────────────────────────────────────
# MATERIAL ICON HELPER
# ─────────────────────────────────────────────
def icon(name: str, size: str = "18px", color: str = "inherit") -> str:
    """Returns HTML span for Material Symbols icon."""
    return f'<span class="material-symbols-outlined" style="font-size:{size};color:{color};vertical-align:middle">{name}</span>'


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar() -> dict:
    """Render sidebar with stock selection and settings."""
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0 12px">
            <span style="font-family:'Space Mono',monospace;font-size:1.5rem;
                         font-weight:700;color:#00d4aa;display:flex;align-items:center;justify-content:center;gap:8px">
                {icon('show_chart', '28px', '#00d4aa')} MarketLens
            </span>
            <span style="color:#64748b;font-size:0.75rem;letter-spacing:0.5px">AI Stock Analysis Platform</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        # Stock Selection Section
        st.markdown(f'#### {icon("search", "20px", "#94a3b8")} Stock Selection', unsafe_allow_html=True)
        
        selected_labels = st.multiselect(
            "Select up to 10 stocks",
            options=list(STOCKS.keys()),
            default=["Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)"],
            max_selections=10,
        )
        
        if not selected_labels:
            st.warning("Please select at least one stock to continue.")
            st.stop()

        selected_tickers = [STOCKS[label] for label in selected_labels]

        st.markdown("")
        
        # Time Period Section
        st.markdown(f'#### {icon("calendar_month", "20px", "#94a3b8")} Time Period', unsafe_allow_html=True)
        
        period_label = st.selectbox(
            "Historical data window",
            list(PERIOD_MAP.keys()),
            index=0,
        )
        period = PERIOD_MAP[period_label]

        st.markdown("")
        
        # Primary Stock Section
        st.markdown(f'#### {icon("target", "20px", "#94a3b8")} Primary Analysis', unsafe_allow_html=True)
        
        primary_label = st.selectbox(
            "Select stock for detailed analysis",
            selected_labels,
            index=0,
        )
        primary_ticker = STOCKS[primary_label]

        st.markdown("")
        
        # Chart Options Section
        st.markdown(f'#### {icon("tune", "20px", "#94a3b8")} Chart Options', unsafe_allow_html=True)
        
        show_bb = st.toggle("Show Bollinger Bands", value=True)

        st.markdown("---")
        
        if st.button("Refresh Data", use_container_width=True, type="secondary"):
            st.cache_data.clear()
            st.rerun()

    return {
        "selected_labels": selected_labels,
        "selected_tickers": selected_tickers,
        "period_label": period_label,
        "period": period,
        "primary_label": primary_label,
        "primary_ticker": primary_ticker,
        "show_bb": show_bb,
    }


# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
def render_kpi_row(ticker: str, signals: dict, info: dict) -> None:
    """Render key performance indicators row."""
    price = signals.get("last", 0)
    chg_1d = signals.get("change_1d", 0)
    chg_1w = signals.get("change_1w", 0)
    rsi_val = signals.get("rsi_val", None)
    pe = info.get("trailingPE", None)
    fwd_pe = info.get("forwardPE", None)
    mktcap = info.get("marketCap", None)
    vol = info.get("volume", None)
    beta = info.get("beta", None)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    with k1:
        st.metric(
            label=f"{ticker} Price",
            value=f"${price:,.2f}",
            delta=f"{chg_1d:+.2f}% 1D",
        )
    
    with k2:
        st.metric(
            label="Weekly Change",
            value=f"{chg_1w:+.2f}%",
            delta=f"vs {chg_1d:+.2f}% daily",
        )
    
    with k3:
        rsi_label = "Neutral"
        if rsi_val:
            if rsi_val > 70:
                rsi_label = "Overbought"
            elif rsi_val < 30:
                rsi_label = "Oversold"
        st.metric(
            label="RSI (14)",
            value=f"{rsi_val:.1f}" if rsi_val else "N/A",
            delta=rsi_label,
        )
    
    with k4:
        st.metric(
            label="P/E Ratio (TTM)",
            value=f"{pe:.1f}x" if pe else "N/A",
            delta=f"Fwd: {fwd_pe:.1f}x" if fwd_pe else None,
        )
    
    with k5:
        st.metric(
            label="Market Cap",
            value=_format_market_cap(mktcap),
        )
    
    with k6:
        vol_str = f"{vol/1e6:.1f}M" if vol else "N/A"
        beta_str = f"Beta: {beta:.2f}" if beta else None
        st.metric(
            label="Volume",
            value=vol_str,
            delta=beta_str,
        )


def _format_market_cap(mktcap) -> str:
    """Format market cap to human-readable string."""
    if not mktcap:
        return "N/A"
    if mktcap >= 1e12:
        return f"${mktcap/1e12:.2f}T"
    if mktcap >= 1e9:
        return f"${mktcap/1e9:.1f}B"
    return f"${mktcap/1e6:.0f}M"


# ─────────────────────────────────────────────
# SIGNAL PANEL
# ─────────────────────────────────────────────
def render_signal_panel(signals: dict, info: dict, news: list) -> None:
    """Render signal panel with technical indicators and company info."""
    strength = signals.get("strength", "N/A")
    sig = signals.get("signal", "HOLD")
    rsi_val = signals.get("rsi_val", 0)
    rsi_signal = signals.get("rsi_signal", "")
    ma50_val = signals.get("ma50_val", 0)
    ma200_val = signals.get("ma200_val")
    last = signals.get("last", 0)

    # Market Strength Card
    is_bullish = "Bull" in strength
    strength_color = "#00d4aa" if is_bullish else "#f43f5e"
    strength_icon = "trending_up" if is_bullish else "trending_down"
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            {icon('sensors', '20px', '#94a3b8')}
            <span style="font-weight:600;color:#e2e8f0">Market Strength</span>
        </div>
        <p style="font-size:1.1rem;color:{strength_color};font-weight:600;margin:4px 0;display:flex;align-items:center;gap:6px">
            {icon(strength_icon, '20px', strength_color)} {strength}
        </p>
        <p style="color:#94a3b8;font-size:0.85rem;margin:0">
            Price <b style="color:#e2e8f0">${last:.2f}</b> vs MA50 <b style="color:#e2e8f0">${ma50_val:.2f}</b>
        </p>
        """, unsafe_allow_html=True)

    # MA Crossover Signal Card
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            {icon('compare_arrows', '20px', '#94a3b8')}
            <span style="font-weight:600;color:#e2e8f0">MA Crossover Signal</span>
        </div>
        <p style="color:#94a3b8;font-size:0.85rem;margin:4px 0">MA20 vs MA50:</p>
        <div style="margin:8px 0">{_render_signal_badge(sig)}</div>
        """, unsafe_allow_html=True)

    # RSI Signal Card
    if rsi_val > 70:
        rsi_color = "#f43f5e"
    elif rsi_val < 30:
        rsi_color = "#00d4aa"
    else:
        rsi_color = "#f59e0b"
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            {icon('speed', '20px', '#94a3b8')}
            <span style="font-weight:600;color:#e2e8f0">RSI Signal</span>
        </div>
        <p style="font-size:1.1rem;color:{rsi_color};font-weight:600;margin:4px 0">{rsi_signal}</p>
        <p style="color:#94a3b8;font-size:0.85rem;margin:0">
            RSI(14) = <b style="color:{rsi_color}">{rsi_val:.1f}</b>
        </p>
        """, unsafe_allow_html=True)

    # 52-Week Range Card
    low52 = info.get("fiftyTwoWeekLow")
    high52 = info.get("fiftyTwoWeekHigh")
    
    if low52 and high52:
        pct = min(100, max(0, (last - low52) / (high52 - low52) * 100))
        
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                {icon('straighten', '20px', '#94a3b8')}
                <span style="font-weight:600;color:#e2e8f0">52-Week Range</span>
            </div>
            <div style="background:#1e293b;border-radius:6px;height:8px;margin:12px 0;overflow:hidden">
                <div style="background:linear-gradient(90deg,#3b82f6,#00d4aa);width:{pct:.1f}%;height:100%;border-radius:6px"></div>
            </div>
            <p style="color:#94a3b8;font-size:0.8rem;margin:0">{pct:.1f}% from 52-week low</p>
            """, unsafe_allow_html=True)

    # Company Profile Card
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            {icon('business', '20px', '#94a3b8')}
            <span style="font-weight:600;color:#e2e8f0">Company Profile</span>
        </div>
        <p style="color:#94a3b8;font-size:0.85rem;margin:4px 0">
            <b style="color:#e2e8f0">Sector:</b> {info.get('sector', 'N/A')}
        </p>
        <p style="color:#64748b;font-size:0.82rem;margin:4px 0;line-height:1.4">
            {info.get('longBusinessSummary', '')[:180]}...
        </p>
        """, unsafe_allow_html=True)

    # News Section
    if news:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
                {icon('article', '20px', '#94a3b8')}
                <span style="font-weight:600;color:#e2e8f0">Latest News</span>
            </div>
            """, unsafe_allow_html=True)
            
            for item in news[:3]:
                title = item.get('title', '')
                url = item.get('url', '#')
                st.markdown(f"""
                <div style="padding:8px 0;border-bottom:1px solid #1e293b">
                    <a href="{url}" target="_blank" style="color:#60a5fa;text-decoration:none;font-size:0.85rem;line-height:1.4">
                        {title}
                    </a>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def _render_signal_badge(signal: str) -> str:
    """Return HTML badge for trading signal."""
    if signal == "BUY":
        return f'''
        <span style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;
                     background:rgba(0,212,170,0.15);color:#00d4aa;border-radius:6px;
                     font-weight:600;font-size:0.9rem">
            {icon('arrow_upward', '16px', '#00d4aa')} BUY
        </span>'''
    elif signal == "SELL":
        return f'''
        <span style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;
                     background:rgba(244,63,94,0.15);color:#f43f5e;border-radius:6px;
                     font-weight:600;font-size:0.9rem">
            {icon('arrow_downward', '16px', '#f43f5e')} SELL
        </span>'''
    return f'''
    <span style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;
                 background:rgba(148,163,184,0.15);color:#94a3b8;border-radius:6px;
                 font-weight:600;font-size:0.9rem">
        {icon('remove', '16px', '#94a3b8')} HOLD
    </span>'''


def render_header(date_str: str) -> None:
    """Render main application header."""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:24px 0 16px;
                border-bottom:1px solid #1e293b;margin-bottom:24px">
        <div>
            <p style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;
                      color:#00d4aa;margin:0;display:flex;align-items:center;gap:10px">
                {icon('show_chart', '32px', '#00d4aa')} MarketLens
            </p>
            <p style="color:#64748b;font-size:0.85rem;margin:4px 0 0;letter-spacing:0.3px">
                AI-Powered Stock Analysis Platform &nbsp;|&nbsp; {date_str}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_forecast_table(
    future_dates,
    future_prices,
    current_price: float,
    every_n: int = 5,
) -> None:
    """Render forecast schedule table."""
    rows = []
    
    for i, (date, price) in enumerate(zip(future_dates, future_prices)):
        if i % every_n == 0 or i == len(future_prices) - 1:
            change = (price - current_price) / current_price * 100
            trend = "+" if change >= 0 else "-"
            
            rows.append({
                "Day": i + 1,
                "Date": date.strftime("%b %d, %Y"),
                "Predicted Close": f"${price:.2f}",
                "Change": f"{change:+.2f}%",
                "Trend": trend,
            })
    
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Trend": st.column_config.TextColumn(
                "Trend",
                width="small",
            ),
        },
    )