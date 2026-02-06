import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
CORS(app)

lr_model = None
rf_model = None
scaler = None
historical_data = []

def train_models():
    global lr_model, rf_model, scaler, historical_data

    # CSV path (works locally + on deploy)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "ml.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"ml.csv not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate needed column
    if "Series Name" not in df.columns:
        raise ValueError("CSV must contain a 'Series Name' column.")

    # Pick rows
    gdp_df = df[df["Series Name"] == "GDP growth (annual %)"]
    inf_df = df[df["Series Name"] == "Inflation, GDP deflator (annual %)"]

    if gdp_df.empty or inf_df.empty:
        raise ValueError("Required series rows not found in CSV. Check 'Series Name' values.")

    gdp_row = gdp_df.iloc[0]
    inflation_row = inf_df.iloc[0]

    years, gdp_values, inflation_values = [], [], []

    for col in df.columns:
        if "[YR" in col and "]" in col:
            try:
                year = int(col.split("[YR")[1].split("]")[0])
            except Exception:
                continue

            gdp_val = gdp_row[col]
            inf_val = inflation_row[col]

            # Skip missing/invalid
            if pd.isna(gdp_val) or pd.isna(inf_val) or gdp_val == ".." or inf_val == "..":
                continue

            try:
                years.append(year)
                gdp_values.append(float(gdp_val))
                inflation_values.append(float(inf_val))
            except Exception:
                continue

    if len(years) < 3:
        raise ValueError("Not enough valid data points to train models.")

    X = np.array(inflation_values).reshape(-1, 1)
    y = np.array(gdp_values)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    lr_model = LinearRegression()
    lr_model.fit(X_scaled, y)

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X, y)

    historical_data = [
        {"Year": int(yy), "GDP Growth": float(g)}
        for yy, g in zip(years, gdp_values)
    ]


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "lr_loaded": lr_model is not None,
        "rf_loaded": rf_model is not None,
        "scaler_loaded": scaler is not None,
        "historical_count": len(historical_data)
    })


@app.route("/api/historical")
def get_historical():
    return jsonify(historical_data)


@app.route("/api/predict", methods=["POST"])
def predict():
    if lr_model is None or rf_model is None or scaler is None:
        return jsonify({"error": "Models not loaded. Server not ready."}), 503

    data = request.get_json(silent=True) or {}

    if "inflation" not in data or "year" not in data:
        return jsonify({"error": "Send JSON with keys: inflation, year"}), 400

    try:
        inflation = float(data["inflation"])
        year = int(data["year"])
    except Exception:
        return jsonify({"error": "inflation must be number, year must be integer"}), 400

    input_data = np.array([[inflation]])
    input_scaled = scaler.transform(input_data)

    lr_pred = float(lr_model.predict(input_scaled)[0])
    rf_pred = float(rf_model.predict(input_data)[0])
    avg_pred = (lr_pred + rf_pred) / 2.0

    return jsonify({
        "lr_prediction": round(lr_pred, 2),
        "rf_prediction": round(rf_pred, 2),
        "avg_prediction": round(avg_pred, 2),
        "year": year,
        "inflation": inflation
    })


# ✅ Train on import so gunicorn deploy works
try:
    train_models()
except Exception as e:
    # Don't crash completely; health endpoint will show not-ready
    print("Model training failed:", str(e))


if __name__ == "__main__":
    # Deploy-friendly run
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
