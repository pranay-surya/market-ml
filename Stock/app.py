"""
app.py — MarketLens: AI Stock Market Analysis Dashboard
Entry point — assembles sidebar, tabs, and all components.

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ── Local modules ──────────────────────────────
from utils.config import CUSTOM_CSS
from utils.data import fetch_ohlcv, fetch_info, fetch_news, fetch_multiple_close
from utils.analysis import (
    compute_signals,
    compute_performance_table,
    compute_correlation,
    compute_returns,
)
from utils.model import train_and_predict

from components.charts import (
    build_overview_chart,
    build_comparison_chart,
    build_return_bar,
    build_correlation_heatmap,
    build_prediction_chart,
    build_feature_importance_chart,
    build_rsi_gauge,
)
from components.ui import (
    render_sidebar,
    render_kpi_row,
    render_signal_panel,
    render_forecast_table,
    render_header,
    icon,
)


# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MarketLens | AI Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS and Google Material Icons
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR CONFIGURATION
# ─────────────────────────────────────────────
cfg = render_sidebar()

primary_ticker = cfg["primary_ticker"]
selected_tickers = cfg["selected_tickers"]
period = cfg["period"]
period_label = cfg["period_label"]
show_bb = cfg["show_bb"]
model_type = "Random Forest"
pred_days = 30


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
render_header(datetime.now().strftime("%B %d, %Y | %H:%M"))


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
with st.spinner(f"Loading data for {primary_ticker}..."):
    primary_df = fetch_ohlcv(primary_ticker, period)
    info = fetch_info(primary_ticker)
    news = fetch_news(primary_ticker)

if primary_df.empty:
    st.error("Unable to fetch data. Please check your connection or try a different ticker.")
    st.stop()

signals = compute_signals(primary_df)

if not signals:
    st.error("Insufficient historical data to compute signals. Minimum 50 bars required.")
    st.stop()


# ─────────────────────────────────────────────
# KEY PERFORMANCE INDICATORS
# ─────────────────────────────────────────────
render_kpi_row(primary_ticker, signals, info)

st.divider()


# ─────────────────────────────────────────────
# MAIN CONTENT TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Comparison",
    "AI Predictions",
])


# ═════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═════════════════════════════════════════════
with tab1:
    col_chart, col_panel = st.columns([2, 1], gap="medium")

    with col_chart:
        st.markdown(f"""
        <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            {icon('candlestick_chart', '24px', '#e2e8f0')}
            {primary_ticker} — Price Action & Indicators
        </h3>
        """, unsafe_allow_html=True)
        
        fig_overview = build_overview_chart(primary_df, signals, show_bb=show_bb)
        st.plotly_chart(fig_overview, use_container_width=True)

        # RSI Gauge and MACD Summary
        gauge_col, macd_col = st.columns([1, 3])
        
        with gauge_col:
            rsi_val = signals.get("rsi_val", 50)
            st.plotly_chart(build_rsi_gauge(rsi_val), use_container_width=True)
        
        with macd_col:
            macd_data = signals.get("macd", {})
            macd_val = float(macd_data["macd"].iloc[-1]) if macd_data.get("macd") is not None else 0
            signal_val = float(macd_data["signal"].iloc[-1]) if macd_data.get("signal") is not None else 0
            hist_val = float(macd_data["histogram"].iloc[-1]) if macd_data.get("histogram") is not None else 0
            
            with st.container(border=True):
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
                    {icon('analytics', '20px', '#94a3b8')}
                    <span style="font-weight:600;color:#e2e8f0">MACD Analysis</span>
                </div>
                """, unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                
                with m1:
                    st.metric("MACD Line", f"{macd_val:.3f}")
                
                with m2:
                    st.metric("Signal Line", f"{signal_val:.3f}")
                
                with m3:
                    momentum_label = "Bullish" if hist_val >= 0 else "Bearish"
                    st.metric("Histogram", f"{hist_val:+.3f}", momentum_label)

    with col_panel:
        st.markdown(f"""
        <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            {icon('radar', '24px', '#e2e8f0')}
            Signals & Information
        </h3>
        """, unsafe_allow_html=True)
        
        render_signal_panel(signals, info, news)


# ═════════════════════════════════════════════
# TAB 2: COMPARISON
# ═════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        {icon('compare_arrows', '24px', '#e2e8f0')}
        Relative Performance | {period_label}
    </h3>
    """, unsafe_allow_html=True)
    
    st.caption("All securities normalized to 100 at the start of the selected period.")

    with st.spinner("Loading comparison data..."):
        all_data = fetch_multiple_close(selected_tickers, period)

    if not all_data:
        st.warning("No data available for the selected securities.")
    else:
        # Relative Performance Chart
        st.plotly_chart(
            build_comparison_chart(all_data, period_label),
            use_container_width=True,
        )

        # Performance Summary
        st.markdown(f"""
        <h4 style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
            {icon('table_chart', '20px', '#94a3b8')}
            Performance Summary
        </h4>
        """, unsafe_allow_html=True)
        
        perf_df = compute_performance_table(all_data, period_label)
        st.dataframe(perf_df, use_container_width=True)

        st.markdown(f"""
        <h4 style="display:flex;align-items:center;gap:8px;margin:24px 0 12px">
            {icon('leaderboard', '20px', '#94a3b8')}
            Return Ranking
        </h4>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(
            build_return_bar(all_data),
            use_container_width=True,
        )

        # Correlation Matrix
        if len(all_data) >= 2:
            st.markdown(f"""
            <h4 style="display:flex;align-items:center;gap:8px;margin:24px 0 8px">
                {icon('hub', '20px', '#94a3b8')}
                Return Correlation Matrix
            </h4>
            """, unsafe_allow_html=True)
            
            st.caption("Pearson correlation of daily returns. Values range from -1 (inverse) to +1 (identical movement).")
            
            corr_df = compute_correlation(all_data)
            st.plotly_chart(
                build_correlation_heatmap(corr_df),
                use_container_width=True,
            )

        # Export Button
        csv_data = compute_performance_table(all_data, period_label).to_csv()
        
        st.download_button(
            label="Export Performance Data",
            data=csv_data,
            file_name=f"marketlens_performance_{period}.csv",
            mime="text/csv",
            type="secondary",
        )


# ═════════════════════════════════════════════
# TAB 3: AI PREDICTIONS
# ═════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        {icon('psychology', '24px', '#e2e8f0')}
        AI Price Forecast
        <span style="background:#3b82f6;color:#fff;font-size:0.65rem;padding:2px 8px;
                     border-radius:4px;font-weight:600;margin-left:8px">BETA</span>
    </h3>
    """, unsafe_allow_html=True)
    
    st.caption(
        f"Forecasting the next {pred_days} trading days for {primary_ticker} "
        f"using {model_type} with engineered technical features."
    )

    with st.spinner(f"Training {model_type} model..."):
        result = train_and_predict(primary_df, model_name=model_type, pred_days=pred_days)

    current_price = float(primary_df["Close"].squeeze().iloc[-1])
    final_prediction = float(result.future_prices[-1])
    predicted_change = (final_prediction - current_price) / current_price * 100

    # Model Performance Metrics
    st.markdown(f"""
    <h4 style="display:flex;align-items:center;gap:8px;margin:16px 0 12px">
        {icon('monitoring', '20px', '#94a3b8')}
        Model Performance
    </h4>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.metric("Current Price", f"${current_price:,.2f}")
    
    with m2:
        st.metric(
            f"Forecast ({pred_days}D)",
            f"${final_prediction:,.2f}",
            f"{predicted_change:+.2f}%",
        )
    
    with m3:
        st.metric("Test RMSE", f"${result.rmse:.2f}", "20% holdout")
    
    with m4:
        st.metric("Test MAE", f"${result.mae:.2f}")
    
    with m5:
        cv_display = f"${result.cv_rmse:.2f}" if result.cv_rmse else "N/A"
        st.metric("CV RMSE", cv_display, "5-fold TS CV")

    # Forecast Visualization
    display_days = min(365, len(primary_df))
    hist_df = primary_df.iloc[-display_days:]

    st.plotly_chart(
        build_prediction_chart(
            hist_df,
            result.hist_pred,
            result.future_dates,
            result.future_prices,
            model_type,
        ),
        use_container_width=True,
    )

    # Feature Importance and Forecast Schedule
    importance_col, schedule_col = st.columns([1, 1], gap="large")

    with importance_col:
        if result.feature_importances is not None:
            st.markdown(f"""
            <h4 style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                {icon('neurology', '20px', '#94a3b8')}
                Feature Importance
            </h4>
            """, unsafe_allow_html=True)
            
            st.caption("Relative importance of input features in the model.")
            
            st.plotly_chart(
                build_feature_importance_chart(
                    result.feature_names,
                    result.feature_importances,
                ),
                use_container_width=True,
            )
        else:
            st.info("Feature importance analysis is not available for Linear Regression models.")

    with schedule_col:
        st.markdown(f"""
        <h4 style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            {icon('event_note', '20px', '#94a3b8')}
            Forecast Schedule
        </h4>
        """, unsafe_allow_html=True)
        
        render_forecast_table(
            result.future_dates,
            result.future_prices,
            current_price,
            every_n=5,
        )

        # Export Forecast
        forecast_df = pd.DataFrame({
            "Date": result.future_dates.strftime("%Y-%m-%d"),
            "Predicted_Close": [f"{p:.4f}" for p in result.future_prices],
            "Change_Pct": [
                f"{(p - current_price) / current_price * 100:.2f}"
                for p in result.future_prices
            ],
        })
        
        st.download_button(
            label="Export Forecast Data",
            data=forecast_df.to_csv(index=False),
            file_name=f"{primary_ticker}_forecast_{pred_days}d.csv",
            mime="text/csv",
            type="secondary",
        )

    # Risk Disclaimer
    st.warning(
        """
        **Risk Disclaimer**
        
        These forecasts are generated by machine learning models trained exclusively on 
        historical price data. They do not incorporate earnings reports, news events, 
        macroeconomic factors, or market sentiment. This tool is intended for 
        **educational and research purposes only** and should not be construed as 
        financial advice or used as the basis for investment decisions.
        """
    )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()

st.markdown(f"""
<div style="text-align:center;padding:8px 0">
    <p style="color:#64748b;font-size:0.75rem;font-family:'Space Mono',monospace;margin:0">
        MarketLens | Built with Streamlit, yfinance & scikit-learn | Data delayed ~15 minutes | Not financial advice
    </p>
</div>
""", unsafe_allow_html=True)