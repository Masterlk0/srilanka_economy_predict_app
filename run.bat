@echo off
echo Installing backend dependencies...
pip install flask flask-cors pandas numpy scikit-learn

echo Installing frontend dependencies...
call npm install

echo Starting backend server...
start python backend.py

timeout /t 3

echo Starting React app...
npm start