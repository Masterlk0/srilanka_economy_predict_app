@echo off
echo Starting Sri Lanka Economy Predictor...
echo.

echo Starting backend server...
start python backend.py

timeout /t 3 /nobreak

echo Backend started on http://localhost:5000
echo Starting React app...
echo.

npm start