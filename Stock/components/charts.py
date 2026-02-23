"""
charts.py — All Plotly chart builders.

Each function returns a go.Figure ready for st.plotly_chart().
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.config import PLOTLY_THEME, COLORS


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _apply_theme(fig: go.Figure, height: int = 480) -> go.Figure:
    fig.update_layout(**PLOTLY_THEME, height=height)
    return fig


# ─────────────────────────────────────────────
# OVERVIEW: CANDLESTICK + VOLUME + RSI + MACD
# ─────────────────────────────────────────────
def build_overview_chart(
    df:      pd.DataFrame,
    signals: dict,
    show_bb: bool = True,
) -> go.Figure:
    close  = df["Close"].squeeze()
    ma20   = signals.get("ma20")
    ma50   = signals.get("ma50")
    ma200  = signals.get("ma200")
    rsi    = signals.get("rsi")
    macd_d = signals.get("macd", {})
    bb     = signals.get("bb", {})

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.03,
        subplot_titles=("", "RSI (14)", "MACD"),
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"].squeeze(),
        high=df["High"].squeeze(),
        low=df["Low"].squeeze(),
        close=close,
        name="OHLC",
        increasing_line_color="#00d4aa",
        decreasing_line_color="#f43f5e",
        increasing_fillcolor="rgba(0,212,170,0.25)",
        decreasing_fillcolor="rgba(244,63,94,0.25)",
    ), row=1, col=1)

    # ── Bollinger Bands ──
    if show_bb and bb:
        fig.add_trace(go.Scatter(
            x=df.index, y=bb["upper"],
            name="BB Upper", line=dict(color="rgba(139,92,246,0.4)", width=1, dash="dot"),
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=bb["lower"],
            name="BB Lower", line=dict(color="rgba(139,92,246,0.4)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(139,92,246,0.05)",
            showlegend=False,
        ), row=1, col=1)

    # ── Moving Averages ──
    if ma20 is not None:
        fig.add_trace(go.Scatter(x=ma20.index, y=ma20, name="MA20",
            line=dict(color="#3b82f6", width=1.5, dash="dot")), row=1, col=1)
    if ma50 is not None:
        fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name="MA50",
            line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
    if ma200 is not None and len(df) >= 200:
        fig.add_trace(go.Scatter(x=ma200.index, y=ma200, name="MA200",
            line=dict(color="#8b5cf6", width=1.5, dash="dash")), row=1, col=1)

    # ── RSI ──
    if rsi is not None:
        fig.add_trace(go.Scatter(
            x=rsi.index, y=rsi, name="RSI",
            line=dict(color="#00d4aa", width=1.5),
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#f43f5e", opacity=0.6, row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#00d4aa", opacity=0.6, row=2, col=1)

    # ── MACD ──
    if macd_d:
        macd_line = macd_d.get("macd")
        sig_line  = macd_d.get("signal")
        hist      = macd_d.get("histogram")
        if hist is not None:
            hist_colors = ["#00d4aa" if v >= 0 else "#f43f5e" for v in hist.fillna(0)]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist,
                name="MACD Hist", marker_color=hist_colors, opacity=0.6,
            ), row=3, col=1)
        if macd_line is not None:
            fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, name="MACD",
                line=dict(color="#3b82f6", width=1.5)), row=3, col=1)
        if sig_line is not None:
            fig.add_trace(go.Scatter(x=sig_line.index, y=sig_line, name="Signal",
                line=dict(color="#f59e0b", width=1.5)), row=3, col=1)

    fig.update_layout(
        **PLOTLY_THEME,
        height=640,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="RSI",         row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD",        row=3, col=1)

    return fig


# ─────────────────────────────────────────────
# VOLUME BAR CHART (standalone)
# ─────────────────────────────────────────────
def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    close  = df["Close"].squeeze()
    open_  = df["Open"].squeeze()
    colors = ["#00d4aa" if c >= o else "#f43f5e" for c, o in zip(close, open_)]
    fig = go.Figure(go.Bar(
        x=df.index, y=df["Volume"].squeeze(),
        marker_color=colors, opacity=0.7, name="Volume",
    ))
    _apply_theme(fig, height=200)
    fig.update_yaxes(title_text="Volume")
    return fig


# ─────────────────────────────────────────────
# COMPARISON: RELATIVE RETURN LINE CHART
# ─────────────────────────────────────────────
def build_comparison_chart(
    all_data:     dict[str, pd.Series],
    period_label: str,
) -> go.Figure:
    fig = go.Figure()
    for i, (ticker, series) in enumerate(all_data.items()):
        rel = (series / series.iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=rel.index, y=rel,
            name=ticker,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            hovertemplate=f"<b>{ticker}</b><br>%{{x|%b %d, %Y}}<br>Return: %{{y:.1f}}<extra></extra>",
        ))
    fig.add_hline(y=100, line_dash="dot", line_color="#475569",
                  opacity=0.6, annotation_text="Baseline (100)")
    fig.update_layout(
        **PLOTLY_THEME,
        height=460,
        yaxis_title=f"Relative Return (Base=100) · {period_label}",
        xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────
# COMPARISON: TOTAL RETURN BAR
# ─────────────────────────────────────────────
def build_return_bar(all_data: dict[str, pd.Series]) -> go.Figure:
    returns = {t: float((s.iloc[-1] / s.iloc[0] - 1) * 100) for t, s in all_data.items()}
    sorted_r = dict(sorted(returns.items(), key=lambda x: x[1], reverse=True))
    colors   = ["#00d4aa" if v >= 0 else "#f43f5e" for v in sorted_r.values()]
    fig = go.Figure(go.Bar(
        x=list(sorted_r.keys()),
        y=list(sorted_r.values()),
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in sorted_r.values()],
        textposition="outside",
        textfont=dict(color="#e2e8f0"),
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        height=300,
        yaxis_title="Total Return (%)",
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# COMPARISON: CORRELATION HEATMAP
# ─────────────────────────────────────────────
def build_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        corr_df,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
    )
    fig.update_layout(
        **PLOTLY_THEME,
        height=400,
        coloraxis_colorbar=dict(title="ρ", tickfont=dict(color="#94a3b8")),
    )
    fig.update_traces(textfont=dict(size=12, color="white"))
    return fig


# ─────────────────────────────────────────────
# AI PREDICTION CHART
# ─────────────────────────────────────────────
def build_prediction_chart(
    hist_df:       pd.DataFrame,
    hist_pred:     np.ndarray,
    future_dates:  pd.DatetimeIndex,
    future_prices: np.ndarray,
    model_name:    str,
) -> go.Figure:
    hist_close = hist_df["Close"].squeeze()
    last_date  = hist_df.index[-1]

    upper = future_prices * 1.05
    lower = future_prices * 0.95

    fig = go.Figure()

    # ── Historical actual ──
    fig.add_trace(go.Scatter(
        x=hist_df.index, y=hist_close,
        name="Actual Price",
        line=dict(color="#3b82f6", width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.05)",
    ))

    # ── In-sample model fit ──
    valid_mask = ~np.isnan(hist_pred[-len(hist_df):])
    hist_pred_slice = hist_pred[-len(hist_df):]
    if valid_mask.any():
        fig.add_trace(go.Scatter(
            x=hist_df.index[valid_mask],
            y=hist_pred_slice[valid_mask],
            name=f"{model_name} Fit",
            line=dict(color="#f59e0b", width=1.5, dash="dot"),
            opacity=0.75,
        ))

    # ── Confidence band ──
    fig.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself", fillcolor="rgba(0,212,170,0.08)",
        line=dict(color="rgba(0,212,170,0)"),
        name="±5% Band",
    ))

    # ── Forecast line (bridged from last actual) ──
    bridge_x = [last_date] + list(future_dates)
    bridge_y = [float(hist_close.iloc[-1])] + list(future_prices)
    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_y,
        name="Forecast",
        line=dict(color="#00d4aa", width=2.5, dash="dash"),
        mode="lines+markers",
        marker=dict(size=4, color="#00d4aa"),
    ))

    # ── "Today" vertical line as Scatter ──
    y_min = float(min(float(hist_close.min()), float(future_prices.min())) * 0.97)
    y_max = float(max(float(hist_close.max()), float(future_prices.max())) * 1.03)
    fig.add_trace(go.Scatter(
        x=[last_date, last_date],
        y=[y_min, y_max],
        mode="lines+text",
        line=dict(color="#475569", width=1.5, dash="dot"),
        text=["", "Today"],
        textposition="top center",
        textfont=dict(color="#94a3b8", size=11),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        **PLOTLY_THEME,
        height=500,
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────
# FEATURE IMPORTANCE BAR
# ─────────────────────────────────────────────
def build_feature_importance_chart(
    names:        list[str],
    importances:  np.ndarray,
    top_n:        int = 15,
) -> go.Figure:
    idx   = np.argsort(importances)[-top_n:]
    fig = go.Figure(go.Bar(
        x=importances[idx],
        y=[names[i] for i in idx],
        orientation="h",
        marker=dict(
            color=importances[idx],
            colorscale=[[0, "#1e2d45"], [1, "#00d4aa"]],
        ),
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        height=420,
        xaxis_title="Importance",
        yaxis_title="",
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# RSI GAUGE (mini chart)
# ─────────────────────────────────────────────
def build_rsi_gauge(rsi_val: float) -> go.Figure:
    color = "#f43f5e" if rsi_val > 70 else ("#00d4aa" if rsi_val < 30 else "#f59e0b")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rsi_val,
        number={"suffix": "", "font": {"color": color, "size": 28, "family": "Space Mono"}},
        gauge={
            "axis":       {"range": [0, 100], "tickcolor": "#64748b"},
            "bar":        {"color": color, "thickness": 0.3},
            "bgcolor":    "#111827",
            "bordercolor":"#1e2d45",
            "steps": [
                {"range": [0,  30], "color": "rgba(0,212,170,0.1)"},
                {"range": [30, 70], "color": "rgba(234,179,8,0.08)"},
                {"range": [70,100], "color": "rgba(244,63,94,0.1)"},
            ],
            "threshold": {
                "line":  {"color": color, "width": 3},
                "value": rsi_val,
            },
        },
        title={"text": "RSI (14)", "font": {"color": "#94a3b8", "size": 13}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(l=20, r=20, t=30, b=10),
    )
    return fig
