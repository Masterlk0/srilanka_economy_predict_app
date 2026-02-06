@echo off
echo ========================================
echo Sri Lanka Economy Predictor
echo ========================================
echo.
echo Starting backend server...
start /B python backend.py
timeout /t 3 /nobreak >nul 2>&1

echo Backend: http://localhost:5000
echo Starting frontend...
echo.

npm start
