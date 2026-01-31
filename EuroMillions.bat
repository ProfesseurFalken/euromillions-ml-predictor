@echo off
title EuroMillions ML Predictor
cd /d "E:\Python\_Ai\Ai_Euromillions v3_dev"

echo Fermeture des instances existantes...
taskkill /F /IM streamlit.exe 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

timeout /t 2 /nobreak >nul

call .venv\Scripts\activate.bat
REM Streamlit ouvre le navigateur automatiquement, pas besoin de start
streamlit run ui\streamlit_app.py --server.port 8501
pause
