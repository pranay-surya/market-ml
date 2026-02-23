"""
analysis.py — All technical indicators and signal logic.

Functions:
  compute_moving_averages   → MA20, MA50, MA200
  compute_rsi               → 14-period RSI
  compute_macd              → MACD line, signal, histogram
  compute_bollinger_bands   → Upper, middle, lower bands
  compute_signals           → Consolidated dict with strength + crossover signal
  compute_returns           → Relative return series (base=100)
  compute_performance_table → Summary stats for comparison tab
  compute_correlation       → Pairwise correlation matrix
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# MOVING AVERAGES
# ─────────────────────────────────────────────
def compute_moving_averages(close: pd.Series) -> dict[str, pd.Series]:
    return {
        "MA20":  close.rolling(20).mean(),
        "MA50":  close.rolling(50).mean(),
        "MA200": close.rolling(200).mean(),
    }


# ─────────────────────────────────────────────
# RSI
# ─────────────────────────────────────────────
def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


# ─────────────────────────────────────────────
# MACD
# ─────────────────────────────────────────────
def compute_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> dict[str, pd.Series]:
    ema_fast   = close.ewm(span=fast,   adjust=False).mean()
    ema_slow   = close.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal     = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram  = macd_line - signal
    return {"macd": macd_line, "signal": signal, "histogram": histogram}


# ─────────────────────────────────────────────
# BOLLINGER BANDS
# ─────────────────────────────────────────────
def compute_bollinger_bands(
    close: pd.Series,
    period: int = 20,
    num_std: float = 2.0,
) -> dict[str, pd.Series]:
    middle = close.rolling(period).mean()
    std    = close.rolling(period).std()
    return {
        "upper":  middle + num_std * std,
        "middle": middle,
        "lower":  middle - num_std * std,
    }


# ─────────────────────────────────────────────
# CONSOLIDATED SIGNALS
# ─────────────────────────────────────────────
def compute_signals(df: pd.DataFrame) -> dict:
    """
    Returns a dict with:
      last, prev, change_1d, change_1w,
      ma20, ma50, ma200, ma20_val, ma50_val, ma200_val,
      rsi, rsi_val,
      macd (dict),
      bb (dict),
      strength, signal, rsi_signal
    """
    if df.empty or len(df) < 50:
        return {}

    close = df["Close"].squeeze()
    mas   = compute_moving_averages(close)
    rsi   = compute_rsi(close)
    macd  = compute_macd(close)
    bb    = compute_bollinger_bands(close)

    last  = float(close.iloc[-1])
    prev  = float(close.iloc[-2])
    week_ago = float(close.iloc[-6]) if len(close) >= 6 else prev

    ma20_val  = float(mas["MA20"].iloc[-1])
    ma50_val  = float(mas["MA50"].iloc[-1])
    ma200_val = float(mas["MA200"].iloc[-1]) if len(df) >= 200 else None
    rsi_val   = float(rsi.iloc[-1])

    change_1d = (last - prev) / prev * 100
    change_1w = (last - week_ago) / week_ago * 100

    # Market strength (price vs MA50)
    strength = "Bullish 🟢" if last > ma50_val else "Bearish 🔴"

    # MA Crossover signal (MA20 vs MA50)
    ma20_prev = float(mas["MA20"].iloc[-2])
    ma50_prev = float(mas["MA50"].iloc[-2])
    if   ma20_val > ma50_val and ma20_prev <= ma50_prev:
        signal = "BUY"
    elif ma20_val < ma50_val and ma20_prev >= ma50_prev:
        signal = "SELL"
    else:
        signal = "HOLD"

    # RSI signal
    if   rsi_val < 30:  rsi_signal = "Oversold 🟢"
    elif rsi_val > 70:  rsi_signal = "Overbought 🔴"
    else:               rsi_signal = "Neutral ⚪"

    return {
        "last": last, "prev": prev,
        "change_1d": change_1d, "change_1w": change_1w,
        "ma20": mas["MA20"], "ma50": mas["MA50"], "ma200": mas["MA200"],
        "ma20_val": ma20_val, "ma50_val": ma50_val, "ma200_val": ma200_val,
        "rsi": rsi, "rsi_val": rsi_val, "rsi_signal": rsi_signal,
        "macd": macd, "bb": bb,
        "strength": strength, "signal": signal,
    }


# ─────────────────────────────────────────────
# COMPARISON HELPERS
# ─────────────────────────────────────────────
def compute_returns(series: pd.Series) -> pd.Series:
    """Normalize to base-100 relative return series."""
    return (series / series.iloc[0]) * 100


def compute_performance_table(
    all_data: dict[str, pd.Series],
    period_label: str,
) -> pd.DataFrame:
    rows = []
    for ticker, series in all_data.items():
        total_ret  = (series.iloc[-1] / series.iloc[0] - 1) * 100
        month_ret  = (series.iloc[-1] / series.iloc[-min(30, len(series))] - 1) * 100
        week_ret   = (series.iloc[-1] / series.iloc[-min(5,  len(series))] - 1) * 100
        ann_vol    = series.pct_change().std() * np.sqrt(252) * 100
        sharpe     = (series.pct_change().mean() * 252) / (series.pct_change().std() * np.sqrt(252) + 1e-9)
        rows.append({
            "Ticker":                        ticker,
            f"Total ({period_label})":       f"{total_ret:+.2f}%",
            "1-Month":                       f"{month_ret:+.2f}%",
            "1-Week":                        f"{week_ret:+.2f}%",
            "Ann. Volatility":               f"{ann_vol:.1f}%",
            "Sharpe (approx)":               f"{sharpe:.2f}",
            "Current Price":                 f"${float(series.iloc[-1]):.2f}",
        })
    return pd.DataFrame(rows).set_index("Ticker")


def compute_correlation(all_data: dict[str, pd.Series]) -> pd.DataFrame:
    """Pairwise Pearson correlation of daily returns."""
    returns = pd.DataFrame({t: s.pct_change() for t, s in all_data.items()}).dropna()
    return returns.corr()
