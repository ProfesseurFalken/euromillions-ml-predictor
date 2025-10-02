@echo off
setlocal enabledelayedexpansion
title EuroMillions ML - Lancement Rapide

echo.
echo ================================================
echo     EUROMILLIONS ML - LANCEMENT RAPIDE
echo ================================================
echo.

REM Verifier si le venv existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve
    echo [CONSEIL] Lancez d'abord: bootstrap.ps1
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

echo [INFO] Recherche d'un port disponible...

REM Fonction pour tester les ports
set "PORT_FOUND=0"
for %%P in (8501 8502 8503 8504 8505) do (
    if !PORT_FOUND! equ 0 (
        netstat -ano | findstr :%%P >nul 2>&1
        if !errorlevel! neq 0 (
            echo [INFO] Port %%P disponible
            set "STREAMLIT_PORT=%%P"
            set "PORT_FOUND=1"
        ) else (
            echo [INFO] Port %%P occupe
        )
    )
)

if !PORT_FOUND! equ 0 (
    echo [ERREUR] Aucun port disponible trouve
    pause
    exit /b 1
)

echo.
echo [ACTION] Lancement sur le port !STREAMLIT_PORT!...
echo [INFO] Interface: http://localhost:!STREAMLIT_PORT!
echo [INFO] Ctrl+C pour arreter
echo.

REM Ouvrir automatiquement le navigateur apres 3 secondes
start /B timeout /t 3 /nobreak >nul && start http://localhost:!STREAMLIT_PORT!

REM Lancer Streamlit
python -m streamlit run ui\streamlit_app.py --server.port !STREAMLIT_PORT! --server.headless true

echo.
echo [INFO] Streamlit arrete
pause