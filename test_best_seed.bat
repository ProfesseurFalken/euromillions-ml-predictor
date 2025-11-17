@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo 🔬 TEST AUTOMATIQUE - RECHERCHE DE LA MEILLEURE GRAINE
echo ========================================================================
echo.
echo Ce script va tester différentes graines (seeds) pour déterminer
echo lesquelles donnent les meilleurs résultats sur les tirages passés.
echo.
echo ⏱️  Durée estimée: 5-10 minutes
echo.

REM Vérifier l'environnement virtuel
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Environnement virtuel non trouvé
    echo 💡 Lancez d'abord: bootstrap.ps1
    pause
    exit /b 1
)

REM Activer l'environnement
call .venv\Scripts\activate.bat

echo 🚀 Lancement du backtesting...
echo.

REM Lancer le script Python
python test_best_seed.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors du backtesting
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo ✅ BACKTESTING TERMINÉ!
echo ========================================================================
echo.
echo 📊 Résultats disponibles dans: data\backtest_results.csv
echo.
echo 💡 Prochaines étapes:
echo    1. Consultez les résultats ci-dessus
echo    2. Notez la meilleure seed et méthode
echo    3. Utilisez-les dans l'interface Streamlit
echo.

pause
