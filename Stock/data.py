"""
data.py — All yfinance data fetching with caching.
Uses a custom requests session with browser-like headers to avoid
Yahoo Finance rate limiting on shared cloud IPs (e.g. Streamlit Cloud).
"""

import time
import requests
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime


# ---------------------------------------------------------------------------
# Shared session that mimics a real browser — avoids 429 rate-limit errors
# on shared cloud hosting where Yahoo blocks the default yfinance user-agent.
# ---------------------------------------------------------------------------
def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    )
    return session


_SESSION = _make_session()


def _ticker(symbol: str) -> yf.Ticker:
    """Return a yf.Ticker that uses our browser-spoofed session."""
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
            # yfinance returns a near-empty dict on silent failure
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
                out.append(
                    {
                        "title": title,
                        "publisher": provider,
                        "url": url,
                        "date": pub_date,
                    }
                )
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