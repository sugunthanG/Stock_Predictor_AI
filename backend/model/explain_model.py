# backend/model/explain_model.py
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance

def train_and_predict(stock_df: pd.DataFrame):
    """
    Trains a small logistic regression model on daily returns to predict whether next-day return > 0.
    Returns a dict with:
      - prediction: "UP 📈" or "DOWN 📉"
      - suggestion: "Buy ✅" or "Avoid ❌"
      - raw_prediction_value: probability for UP (float)
      - feature_importance: {feature_name: importance_value}
      - explanation: small summary dict
    """

    # Defensive copy
    df = stock_df.copy()

    # Ensure Close column exists
    if "Close" not in df.columns:
        raise ValueError("Input DataFrame must contain 'Close' column")

    # Create return feature
    df["Return"] = df["Close"].pct_change()
    df = df.dropna().copy()
    if df.shape[0] < 5:
        # Not enough data to train
        return {
            "prediction": "N/A",
            "suggestion": "N/A",
            "raw_prediction_value": None,
            "feature_importance": {},
            "explanation": {"reason": "Not enough data"}
        }

    # X: current return; y: whether next day's return > 0
    X = df[["Return"]].iloc[:-1].values  # all but last row
    y = (df["Return"].shift(-1) > 0).astype(int).iloc[:-1].values  # label for next day

    # Standard scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, shuffle=False)

    model = LogisticRegression(max_iter=500)
    model.fit(X_train, y_train)

    # Predict on latest available X (last known return)
    latest_return = df["Return"].iloc[-1]
    latest_X = scaler.transform(np.array([[latest_return]]))
    prob_up = float(model.predict_proba(latest_X)[0][1])
    pred_label = "UP 📈" if prob_up >= 0.5 else "DOWN 📉"
    suggestion = "Buy ✅" if prob_up >= 0.5 else "Avoid ❌"

    # Permutation importance on test set to get feature importance
    try:
        r = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
        importances = r.importances_mean
        feature_names = ["Return"]
        feature_importance = {name: float(val) for name, val in zip(feature_names, importances)}
    except Exception as e:
        print("Permutation importance error:", e)
        feature_importance = {"Return": None}

    explanation = {
        "latest_return": float(latest_return),
        "probability_up": prob_up,
        "model_type": "LogisticRegression (returns-based)",
    }

    return {
        "prediction": pred_label,
        "suggestion": suggestion,
        "raw_prediction_value": prob_up,
        "feature_importance": feature_importance,
        "explanation": explanation
    }
