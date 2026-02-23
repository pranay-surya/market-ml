# MarketLens — AI Stock Analysis Platform

A professional, dark-themed stock market dashboard built with Streamlit. MarketLens combines real-time market data, technical analysis, multi-stock comparison, and machine learning price forecasting in a single unified interface.

---

## Features

**Overview Tab**
- Interactive candlestick chart with OHLCV data
- Bollinger Bands, MA20, MA50, MA200 overlays
- RSI (14) gauge and signal classification
- MACD line, signal line, and histogram breakdown
- Live trading signals: BUY / SELL / HOLD based on MA crossover
- Market strength indicator, 52-week range tracker, and company profile

**Comparison Tab**
- Relative performance chart normalized to a base of 100
- Performance summary table with total return, 1-month, 1-week, annualized volatility, and Sharpe ratio
- Return ranking bar chart sorted by performance
- Pearson correlation heatmap of daily returns
- CSV export of performance data

**AI Predictions Tab**
- Price forecasting using Random Forest, Gradient Boosting, or Linear Regression
- 10–60 trading day configurable forecast horizon
- Confidence band (±5%) around predictions
- In-sample model fit visualization bridged to forecast
- Feature importance chart (RF and GB models)
- Model evaluation metrics: RMSE, MAE, R², and 5-fold time-series cross-validation RMSE
- Forecast schedule table with per-day predicted close and percentage change
- CSV export of forecast data

---

## Tech Stack

| Layer | Library |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io) |
| Market Data | [yfinance](https://pypi.org/project/yfinance/) |
| Charting | [Plotly](https://plotly.com/python/) |
| Machine Learning | [scikit-learn](https://scikit-learn.org/) |
| Data Processing | [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Icons | [Google Material Symbols](https://fonts.google.com/icons) |

---

## Project Structure

```
marketlens/
├── app.py                  # Entry point — assembles tabs and layout
├── components/
│   ├── ui.py               # Sidebar, KPI row, signal panel, forecast table
│   └── charts.py           # All Plotly chart builders
└── utils/
    ├── config.py           # Stock universe, period map, CSS, Plotly theme
    ├── data.py             # yfinance data fetching with Streamlit caching
    ├── analysis.py         # Technical indicators and signal logic
    └── model.py            # ML feature engineering and prediction pipeline
```

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/marketlens.git
cd marketlens
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Requirements

```
streamlit>=1.35.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.20.0
scikit-learn>=1.4.0
```

---

## Configuration

**Stock Universe** — edit `utils/config.py` to add or remove tickers from the `STOCKS` dictionary.

**Time Periods** — the `PERIOD_MAP` dictionary in `utils/config.py` controls the available historical data windows.

**ML Defaults** — forecast horizon and model type are set in `app.py` (`pred_days = 30`, `model_type = "Random Forest"`). These can be exposed as sidebar controls if needed.

---

## Technical Indicators

| Indicator | Parameters | Usage |
|---|---|---|
| Simple Moving Average | 20, 50, 200 periods | Trend direction and crossover signals |
| RSI | 14 periods | Overbought (>70) / Oversold (<30) detection |
| MACD | 12 / 26 / 9 EMA | Momentum and crossover confirmation |
| Bollinger Bands | 20 periods, 2σ | Volatility and price channel |

---

## ML Feature Engineering

The prediction model is trained on the following engineered features:

- **Lagged prices** — close at t-1, t-2, t-3, t-5, t-10
- **Rolling statistics** — 5, 10, 20-day mean and standard deviation
- **Momentum** — 5, 10, 20-day price momentum
- **Volume** — 5-day volume MA and 20-day volume ratio
- **RSI** — 14-period RSI
- **MACD** — histogram and MACD line values
- **Bollinger Band position** — normalized price position within the band
- **Calendar features** — day of week, month

All features are shifted by one period to prevent data leakage. Scaling is applied via `MinMaxScaler`. Future predictions use an iterative rollout strategy where each predicted price is fed back as a lag feature for the next step.

---

## Data

Market data is sourced from Yahoo Finance via the `yfinance` library. Prices are auto-adjusted for splits and dividends. Data is cached for 10 minutes using Streamlit's `@st.cache_data` decorator to reduce API calls during active sessions.

> **Note:** Data is typically delayed by approximately 15 minutes. This tool is intended for educational and research purposes only and should not be used as the basis for investment decisions.

---

## License

MIT License. See `LICENSE` for details.
