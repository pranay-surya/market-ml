"""
data.py — All yfinance data fetching with caching.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime


@st.cache_data(ttl=600, show_spinner=False)
def fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    """Download OHLCV data for a ticker. Returns empty DataFrame on failure."""
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Failed to fetch OHLCV for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    """Fetch company metadata from yfinance."""
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(ticker: str, max_items: int = 6) -> list[dict]:
    """Fetch latest news headlines for a ticker."""
    try:
        raw = yf.Ticker(ticker).news or []
        out = []
        for item in raw[:max_items]:
            content = item.get("content", {})
            title = content.get("title") or item.get("title", "")
            provider = content.get("provider", {}).get("displayName", "") or item.get("publisher", "")
            url = (content.get("canonicalUrl", {}) or {}).get("url", "") or item.get("link", "")
            pub_ts = content.get("pubDate") or ""
            if pub_ts:
                try:
                    pub_date = datetime.fromisoformat(pub_ts.replace("Z", "+00:00")).strftime("%b %d, %Y")
                except Exception:
                    pub_date = pub_ts[:10]
            else:
                pub_date = ""
            if title:
                out.append({"title": title, "publisher": provider, "url": url, "date": pub_date})
        return out
    except Exception:
        return []


def fetch_multiple_close(tickers: list[str], period: str) -> dict[str, pd.Series]:
    """
    Fetch closing prices for multiple tickers.
    Returns {ticker: pd.Series}.
    """
    result = {}
    for t in tickers:
        df = fetch_ohlcv(t, period)
        if not df.empty:
            result[t] = df["Close"].squeeze()
    return result
