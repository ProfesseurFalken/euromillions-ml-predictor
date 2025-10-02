@echo off
setlocal enabledelayedexpansion
title EuroMillions ML - Statut et Mise a Jour

echo.
echo ================================================
echo     EUROMILLIONS ML - PANNEAU DE CONTROLE
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

:MENU
echo.
echo ================================================
echo              MENU PRINCIPAL
echo ================================================
echo.
echo 1. Afficher le statut actuel
echo 2. Mettre a jour les tirages
echo 3. Lancer l'interface Streamlit
echo 4. Generer des predictions
echo 5. Quitter
echo.
set /p choice="Votre choix (1-5): "

if "%choice%"=="1" goto STATUS
if "%choice%"=="2" goto UPDATE
if "%choice%"=="3" goto LAUNCH_UI
if "%choice%"=="4" goto PREDICT
if "%choice%"=="5" goto EXIT
echo [ERREUR] Choix invalide
goto MENU

:STATUS
echo.
echo [ACTION] Verification du statut...
python status.py
echo.
pause
goto MENU

:UPDATE
echo.
echo [ACTION] Mise a jour des tirages...
python update_tirages_windows.py
echo.
pause
goto MENU

:LAUNCH_UI
echo.
echo [ACTION] Lancement de l'interface Streamlit...
echo [INFO] Verification du port 8501...

REM Verifier si le port 8501 est libre
netstat -ano | findstr :8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo [ATTENTION] Port 8501 deja utilise, tentative sur port 8502...
    set STREAMLIT_PORT=8502
) else (
    echo [INFO] Port 8501 disponible
    set STREAMLIT_PORT=8501
)

echo [INFO] Interface disponible sur: http://localhost:!STREAMLIT_PORT!
echo [INFO] Appuyez sur Ctrl+C dans cette fenetre pour arreter
echo.

REM Lancer Streamlit avec le port determine
python -m streamlit run ui\streamlit_app.py --server.port !STREAMLIT_PORT!

REM Si echec, essayer port alternatif
if %errorlevel% neq 0 (
    echo [ERREUR] Echec sur port !STREAMLIT_PORT!, tentative port 8503...
    python -m streamlit run ui\streamlit_app.py --server.port 8503
)

echo.
pause
goto MENU

:PREDICT
echo.
echo [ACTION] Generation de predictions...
python cli_train.py suggest
echo.
pause
goto MENU

:EXIT
echo.
echo [INFO] Au revoir !
exit /b 0