@echo off
setlocal enabledelayedexpansion
title EuroMillions ML - Lancement Simple

echo.
echo ================================================
echo     EUROMILLIONS ML - LANCEMENT AUTOMATIQUE
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

echo [INFO] Arret des anciens processus Streamlit...
taskkill /F /IM python.exe /T >nul 2>&1

echo [INFO] Attente de liberation des ports...
timeout /t 2 /nobreak >nul

echo [INFO] Activation de l'environnement Python...
call .venv\Scripts\activate.bat

echo [INFO] Demarrage de Streamlit...

REM Essayer plusieurs ports
for %%P in (8501 8502 8503 8504) do (
    echo [TEST] Tentative port %%P...
    netstat -ano | findstr :%%P >nul 2>&1
    if !errorlevel! neq 0 (
        echo [INFO] Port %%P disponible - Lancement en cours...
        echo [INFO] Interface: http://localhost:%%P
        echo [INFO] Appuyez sur Ctrl+C pour arreter
        echo.
        
        REM Ouvrir le navigateur apres 3 secondes
        start /B powershell -Command "Start-Sleep 3; Start-Process 'http://localhost:%%P'"
        
        REM Lancer Streamlit
        python -m streamlit run ui\streamlit_app.py --server.port %%P --server.headless true
        goto END
    ) else (
        echo [INFO] Port %%P occupe
    )
)

echo [ERREUR] Aucun port disponible
pause
exit /b 1

:END
echo.
echo [INFO] Streamlit arrete
pause