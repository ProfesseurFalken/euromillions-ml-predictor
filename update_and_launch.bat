@echo off
echo.
echo =====================================================
echo 🔄 MISE A JOUR EUROMILLIONS - INTERFACE WINDOWS
echo =====================================================
echo.

REM Vérifier si le venv existe
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Environnement virtuel non trouvé
    echo 💡 Lancez d'abord: bootstrap.ps1
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

echo 📊 État actuel des tirages:
echo.
python check_tirage_freshness.py
echo.

echo =====================================================
set /p choice="Voulez-vous mettre à jour les tirages ? (O/N): "

if /i "%choice%"=="O" (
    echo.
    echo 🔄 Lancement de la mise à jour...
    python update_tirages.py --auto
    echo.
    echo =====================================================
    echo 🎯 Mise à jour terminée !
    echo.
    set /p launch="Voulez-vous lancer l'interface Streamlit ? (O/N): "
    if /i "!launch!"=="O" (
        echo 🚀 Lancement de l'interface...
        start /B streamlit run ui\streamlit_app.py --server.port 8501
        echo 📱 Interface disponible sur: http://localhost:8501
        timeout /t 3 > nul
        start http://localhost:8501
    )
) else (
    echo ❌ Mise à jour annulée
)

echo.
pause