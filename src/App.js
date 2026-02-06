import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [year, setYear] = useState(2030);
  const [inflation, setInflation] = useState(6.5);
  const [predictions, setPredictions] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetch('/api/historical')
      .then(res => res.json())
      .then(data => {
        setHistoricalData(data);
        setChartData(data);
      });
  }, []);

  useEffect(() => {
    if (predictions) {
      const combined = [...historicalData];
      const lastYear = historicalData.length > 0 ? historicalData[historicalData.length - 1].Year : 2024;
      const lastGDP = historicalData[historicalData.length - 1]['GDP Growth'];
      
      combined[combined.length - 1] = {
        ...combined[combined.length - 1],
        'Predicted GDP Growth': lastGDP
      };
      
      for (let y = lastYear + 1; y <= year; y++) {
        combined.push({
          Year: y,
          'Predicted GDP Growth': predictions.avg_prediction
        });
      }
      setChartData(combined);
    } else {
      setChartData(historicalData);
    }
  }, [predictions, historicalData, year]);

  const handlePredict = async () => {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year, inflation })
    });
    const data = await response.json();
    setPredictions(data);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🇱🇰 Sri Lanka Economy Predictor</h1>
          <p>Predict GDP Growth using Machine Learning</p>
        </header>

        <div className="input-section">
          <h3>Economic Indicators</h3>
          <div className="inputs">
            <label>
              Year:
              <input 
                type="number" 
                value={year} 
                onChange={(e) => setYear(e.target.value)}
                min="2025" 
                max="2050"
              />
            </label>
            <label>
              Inflation Rate (%):
              <input 
                type="number" 
                value={inflation} 
                onChange={(e) => setInflation(e.target.value)}
                step="0.1"
                min="0"
                max="50"
              />
            </label>
            <button onClick={handlePredict}>🔮 Predict GDP Growth</button>
          </div>
        </div>

        {predictions && (
          <div className="predictions">
            <div className="prediction-cards">
              <div className="card">
                <h3>📊 Linear Regression</h3>
                <div className="value">{predictions.lr_prediction}%</div>
                <p>GDP Growth Rate</p>
              </div>
              <div className="card">
                <h3>🌲 Random Forest</h3>
                <div className="value">{predictions.rf_prediction}%</div>
                <p>GDP Growth Rate</p>
              </div>
              <div className="card final">
                <h3>🏆 Average</h3>
                <div className="value">{predictions.avg_prediction}%</div>
                <p>Final Prediction</p>
              </div>
            </div>
            
            <div className={`interpretation ${predictions.avg_prediction > 5 ? 'success' : predictions.avg_prediction > 0 ? 'info' : 'warning'}`}>
              {predictions.avg_prediction > 5 ? '🚀 Strong economic growth expected!' :
               predictions.avg_prediction > 0 ? '📈 Moderate economic growth expected.' :
               '⚠️ Economic challenges predicted.'}
            </div>
          </div>
        )}

        <div className="chart-section">
          <h3>📊 Historical & Predicted GDP Growth</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Year" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="GDP Growth" stroke="#FF6B35" strokeWidth={3} name="Historical" />
                <Line type="monotone" dataKey="Predicted GDP Growth" stroke="#4CAF50" strokeWidth={3} name="Predicted" connectNulls={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>Loading chart...</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;