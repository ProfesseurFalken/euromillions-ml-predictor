REM ===================================================
REM    EUROMILLIONS ML - LANCEUR PRINCIPAL
REM ===================================================
REM 
REM Choisissez votre mode de lancement :
REM
REM 1. UTILISATION NORMALE (recommandé)
REM    Double-cliquez sur: start_euromillions.bat
REM
REM 2. GESTION COMPLETE
REM    Double-cliquez sur: menu.bat
REM
REM ===================================================

@echo off
echo.
echo ====================================================
echo     EUROMILLIONS ML - QUEL MODE VOULEZ-VOUS ?
echo ====================================================
echo.
echo 1. Interface Web (utilisation normale)
echo 2. Menu complet (gestion + maintenance)
echo 3. Statut rapide seulement
echo 4. Quitter
echo.
set /p choice="Votre choix (1-4): "

if "%choice%"=="1" goto LAUNCH_WEB
if "%choice%"=="2" goto LAUNCH_MENU
if "%choice%"=="3" goto STATUS_ONLY
if "%choice%"=="4" goto EXIT

echo Choix invalide
pause
exit /b 1

:LAUNCH_WEB
echo.
echo [ACTION] Lancement de l'interface web...
start_euromillions.bat
goto EXIT

:LAUNCH_MENU
echo.
echo [ACTION] Lancement du menu complet...
menu.bat
goto EXIT

:STATUS_ONLY
echo.
echo [ACTION] Verification du statut...
call .venv\Scripts\activate.bat
python status.py
pause
goto EXIT

:EXIT
exit /b 0