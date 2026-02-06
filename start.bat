@echo off
echo Starting Sri Lanka Economy Predictor...
echo.

start /B python backend.py
timeout /t 2 /nobreak >nul 2>&1

echo Backend started on http://localhost:5000
echo Starting frontend...
echo.

npm start
