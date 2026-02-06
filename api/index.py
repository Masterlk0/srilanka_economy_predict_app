from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)

lr_model = None
rf_model = None
scaler = None
historical_data = []

def train_models():
    global lr_model, rf_model, scaler, historical_data
    
    csv_path = os.path.join(os.path.dirname(__file__), "..", "ml.csv")
    df = pd.read_csv(csv_path)
    
    gdp_row = df[df['Series Name'] == 'GDP growth (annual %)'].iloc[0]
    inflation_row = df[df['Series Name'] == 'Inflation, GDP deflator (annual %)'].iloc[0]
    
    years, gdp_values, inflation_values = [], [], []
    
    for col in df.columns:
        if '[YR' in col and ']' in col:
            year = int(col.split('[YR')[1].split(']')[0])
            gdp_val = gdp_row[col]
            inf_val = inflation_row[col]
            
            if pd.notna(gdp_val) and pd.notna(inf_val) and gdp_val != '..' and inf_val != '..':
                years.append(year)
                gdp_values.append(float(gdp_val))
                inflation_values.append(float(inf_val))
    
    X = np.array(inflation_values).reshape(-1, 1)
    y = np.array(gdp_values)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    lr_model = LinearRegression()
    lr_model.fit(X_scaled, y)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    historical_data = [{'Year': y, 'GDP Growth': g} for y, g in zip(years, gdp_values)]

@app.route('/api/historical')
def get_historical():
    if not historical_data:
        train_models()
    return jsonify(historical_data)

@app.route('/api/predict', methods=['POST'])
def predict():
    if lr_model is None:
        train_models()
    
    data = request.json
    inflation = float(data['inflation'])
    year = int(data['year'])
    
    input_data = np.array([[inflation]])
    input_scaled = scaler.transform(input_data)
    
    lr_pred = lr_model.predict(input_scaled)[0]
    rf_pred = rf_model.predict(input_data)[0]
    avg_pred = (lr_pred + rf_pred) / 2
    
    return jsonify({
        'lr_prediction': round(lr_pred, 2),
        'rf_prediction': round(rf_pred, 2),
        'avg_prediction': round(avg_pred, 2),
        'year': year
    })

# Vercel handler
handler = app
