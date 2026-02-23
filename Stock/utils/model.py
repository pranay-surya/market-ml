"""
model.py — Machine Learning prediction pipeline.

Features used per sample:
  - Lag prices: t-1, t-2, t-3, t-5, t-10
  - Rolling stats: 5d mean, 10d mean, 20d std
  - RSI-14
  - MACD histogram
  - Day-of-week, month (calendar seasonality)

Models available:
  - Random Forest Regressor
  - Linear Regression (with engineered features)

Outputs:
  - ModelResult dataclass with future_dates, future_prices,
    hist_pred, rmse, mae, r2, feature_importances
"""

from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from datetime import timedelta

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

from utils.analysis import compute_rsi, compute_macd


# ─────────────────────────────────────────────
# RESULT DATACLASS
# ─────────────────────────────────────────────
@dataclass
class ModelResult:
    future_dates:        pd.DatetimeIndex
    future_prices:       np.ndarray
    hist_pred:           np.ndarray          # in-sample predictions (same length as close)
    rmse:                float
    mae:                 float
    r2:                  float
    feature_names:       list[str]           = field(default_factory=list)
    feature_importances: np.ndarray | None   = None
    model_name:          str                 = ""
    cv_rmse:             float | None        = None   # cross-val RMSE


# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────
def _build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Build a feature matrix from OHLCV data.
    Returns (feature_df, feature_names).
    Rows with NaN (warm-up period) are dropped.
    """
    close  = df["Close"].squeeze()
    volume = df["Volume"].squeeze() if "Volume" in df.columns else pd.Series(0, index=df.index)

    feat = pd.DataFrame(index=df.index)

    # ── Lagged close prices ──
    for lag in [1, 2, 3, 5, 10]:
        feat[f"lag_{lag}"] = close.shift(lag)

    # ── Rolling statistics ──
    feat["roll_mean_5"]  = close.rolling(5).mean().shift(1)
    feat["roll_mean_10"] = close.rolling(10).mean().shift(1)
    feat["roll_mean_20"] = close.rolling(20).mean().shift(1)
    feat["roll_std_5"]   = close.rolling(5).std().shift(1)
    feat["roll_std_20"]  = close.rolling(20).std().shift(1)

    # ── Price momentum ──
    feat["momentum_5"]   = (close / close.shift(5) - 1).shift(1)
    feat["momentum_10"]  = (close / close.shift(10) - 1).shift(1)
    feat["momentum_20"]  = (close / close.shift(20) - 1).shift(1)

    # ── Volume features ──
    feat["volume_ma5"]   = volume.rolling(5).mean().shift(1)
    feat["volume_ratio"] = (volume / (volume.rolling(20).mean() + 1e-9)).shift(1)

    # ── RSI ──
    rsi = compute_rsi(close, period=14)
    feat["rsi"] = rsi.shift(1)

    # ── MACD histogram ──
    macd = compute_macd(close)
    feat["macd_hist"] = macd["histogram"].shift(1)
    feat["macd_line"] = macd["macd"].shift(1)

    # ── Bollinger Band position ──
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    feat["bb_position"] = ((close - bb_mid) / (2 * bb_std + 1e-9)).shift(1)

    # ── Calendar features ──
    feat["day_of_week"] = pd.to_datetime(df.index).dayofweek
    feat["month"]       = pd.to_datetime(df.index).month

    feature_names = feat.columns.tolist()
    feat.dropna(inplace=True)
    return feat, feature_names


# ─────────────────────────────────────────────
# TRAIN & PREDICT
# ─────────────────────────────────────────────
def train_and_predict(
    df:         pd.DataFrame,
    model_name: str = "Random Forest",
    pred_days:  int = 30,
) -> ModelResult:
    """
    Train on historical data, predict `pred_days` into the future.
    Uses TimeSeriesSplit cross-validation for honest RMSE.
    """
    close = df["Close"].squeeze()

    feat_df, feature_names = _build_features(df)

    # Align target with features (feat_df has NaN rows dropped)
    y_full = close.loc[feat_df.index].values
    X_full = feat_df.values

    # ── Scale ──
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X_full)
    y_scaled = scaler_y.fit_transform(y_full.reshape(-1, 1)).ravel()

    # ── Pick model ──
    if model_name == "Linear Regression":
        model = Ridge(alpha=1.0)
    elif model_name == "Gradient Boosting":
        model = GradientBoostingRegressor(
            n_estimators=300, learning_rate=0.05,
            max_depth=4, random_state=42,
        )
    else:  # default: Random Forest
        model = RandomForestRegressor(
            n_estimators=300, max_depth=10,
            min_samples_leaf=3, random_state=42, n_jobs=-1,
        )

    # ── TimeSeriesSplit CV ──
    tscv = TimeSeriesSplit(n_splits=5)
    cv_errors = []
    for train_idx, val_idx in tscv.split(X_scaled):
        model.fit(X_scaled[train_idx], y_scaled[train_idx])
        val_pred = scaler_y.inverse_transform(
            model.predict(X_scaled[val_idx]).reshape(-1, 1)
        ).ravel()
        val_true = y_full[val_idx]
        cv_errors.append(np.sqrt(mean_squared_error(val_true, val_pred)))
    cv_rmse = float(np.mean(cv_errors))

    # ── Final fit on all data ──
    model.fit(X_scaled, y_scaled)

    # ── In-sample predictions ──
    hist_scaled = model.predict(X_scaled).reshape(-1, 1)
    hist_pred_aligned = scaler_y.inverse_transform(hist_scaled).ravel()

    # Pad back to original length with NaN for the warm-up rows
    n_warmup = len(close) - len(hist_pred_aligned)
    hist_pred = np.concatenate([np.full(n_warmup, np.nan), hist_pred_aligned])

    # ── Metrics on last 20% ──
    split = int(len(y_full) * 0.8)
    test_pred = scaler_y.inverse_transform(
        model.predict(X_scaled[split:]).reshape(-1, 1)
    ).ravel()
    test_true = y_full[split:]
    rmse = float(np.sqrt(mean_squared_error(test_true, test_pred)))
    mae  = float(mean_absolute_error(test_true, test_pred))
    r2   = float(r2_score(test_true, test_pred))

    # ── Future prediction (iterative rollout) ──
    last_row        = X_full[-1].copy()
    last_close      = float(close.iloc[-1])
    future_prices   = []
    close_history   = list(close.values)

    # Column index mapping for feature update
    col = {name: i for i, name in enumerate(feature_names)}

    for step in range(pred_days):
        row_scaled = scaler_X.transform(last_row.reshape(1, -1))
        pred_scaled = model.predict(row_scaled)[0]
        pred_price  = float(
            scaler_y.inverse_transform([[pred_scaled]])[0][0]
        )
        future_prices.append(pred_price)

        # ── Update lag features for next step ──
        new_close = pred_price
        close_history.append(new_close)
        ch = np.array(close_history)

        new_row = last_row.copy()
        if "lag_1"  in col: new_row[col["lag_1"]]  = close_history[-2]
        if "lag_2"  in col: new_row[col["lag_2"]]  = close_history[-3]
        if "lag_3"  in col: new_row[col["lag_3"]]  = close_history[-4]
        if "lag_5"  in col: new_row[col["lag_5"]]  = close_history[-6]  if len(close_history) > 5 else new_close
        if "lag_10" in col: new_row[col["lag_10"]] = close_history[-11] if len(close_history) > 10 else new_close

        if "roll_mean_5"  in col: new_row[col["roll_mean_5"]]  = float(np.mean(ch[-5:]))
        if "roll_mean_10" in col: new_row[col["roll_mean_10"]] = float(np.mean(ch[-10:]))
        if "roll_mean_20" in col: new_row[col["roll_mean_20"]] = float(np.mean(ch[-20:]))
        if "roll_std_5"   in col: new_row[col["roll_std_5"]]   = float(np.std(ch[-5:]))
        if "roll_std_20"  in col: new_row[col["roll_std_20"]]  = float(np.std(ch[-20:]))

        if "momentum_5"  in col: new_row[col["momentum_5"]]  = (ch[-1] / ch[-6]  - 1) if len(ch) > 5  else 0
        if "momentum_10" in col: new_row[col["momentum_10"]] = (ch[-1] / ch[-11] - 1) if len(ch) > 10 else 0
        if "momentum_20" in col: new_row[col["momentum_20"]] = (ch[-1] / ch[-21] - 1) if len(ch) > 20 else 0

        last_row = new_row

    future_prices = np.array(future_prices)

    # ── Future dates (business days) ──
    last_date    = df.index[-1]
    future_dates = pd.bdate_range(
        start=last_date + timedelta(days=1), periods=pred_days
    )

    # ── Feature importances (RF / GB only) ──
    fi = getattr(model, "feature_importances_", None)

    return ModelResult(
        future_dates=future_dates,
        future_prices=future_prices,
        hist_pred=hist_pred,
        rmse=rmse,
        mae=mae,
        r2=r2,
        feature_names=feature_names,
        feature_importances=fi,
        model_name=model_name,
        cv_rmse=cv_rmse,
    )
