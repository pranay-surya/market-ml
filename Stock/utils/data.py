"""
data.py — All yfinance data fetching with caching.

Uses curl_cffi to impersonate a real browser at the TLS/HTTP2 level,
which is required to bypass Yahoo Finance's bot detection on shared
cloud IPs like Streamlit Cloud.
"""

import time
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

try:
    from curl_cffi import requests as curl_requests
    _SESSION = curl_requests.Session(impersonate="chrome110")
    _CURL_AVAILABLE = True
except ImportError:
    import requests
    _SESSION = requests.Session()
    _SESSION.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    _CURL_AVAILABLE = False


def _ticker(symbol: str) -> yf.Ticker:
    """Return a yf.Ticker using the best available session."""
    return yf.Ticker(symbol, session=_SESSION)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner=False)
def fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    """Download OHLCV data for a ticker. Returns empty DataFrame on failure."""
    for attempt in range(3):
        try:
            df = yf.download(
                ticker,
                period=period,
                auto_adjust=True,
                progress=False,
                timeout=15,
                session=_SESSION,
            )
            if df is None or df.empty:
                time.sleep(2 ** attempt)
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df.dropna(inplace=True)
            if not df.empty:
                return df
        except Exception as e:
            st.error(f"[Attempt {attempt + 1}] OHLCV fetch failed for {ticker}: {e}")
            time.sleep(2 ** attempt)
    return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    """Fetch company metadata from yfinance."""
    for attempt in range(3):
        try:
            info = _ticker(ticker).info
            if info and len(info) > 5:
                return info
        except Exception as e:
            st.warning(f"[Attempt {attempt + 1}] Info fetch failed for {ticker}: {e}")
        time.sleep(2 ** attempt)
    return {}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(ticker: str, max_items: int = 6) -> list[dict]:
    """Fetch latest news headlines for a ticker."""
    try:
        raw = _ticker(ticker).news or []
        out = []
        for item in raw[:max_items]:
            content = item.get("content", {})
            title = content.get("title") or item.get("title", "")
            provider = (
                content.get("provider", {}).get("displayName", "")
                or item.get("publisher", "")
            )
            url = (
                (content.get("canonicalUrl", {}) or {}).get("url", "")
                or item.get("link", "")
            )
            pub_ts = content.get("pubDate") or ""
            if pub_ts:
                try:
                    pub_date = datetime.fromisoformat(
                        pub_ts.replace("Z", "+00:00")
                    ).strftime("%b %d, %Y")
                except Exception:
                    pub_date = pub_ts[:10]
            else:
                pub_date = ""
            if title:
                out.append({
                    "title": title,
                    "publisher": provider,
                    "url": url,
                    "date": pub_date,
                })
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
        if not df.empty and "Close" in df.columns:
            result[t] = df["Close"].squeeze()
    return result
