@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo 🚀 UPLOAD AUTOMATIQUE VERS GITHUB - EuroMillions ML Predictor
echo ========================================================================
echo.
echo Ce script va automatiquement uploader votre projet vers GitHub
echo.
echo ⚠️  IMPORTANT: Avant de continuer, assurez-vous d'avoir:
echo    1. Un compte GitHub actif
echo    2. Git installé sur votre ordinateur
echo    3. Accès Internet
echo.
pause

REM Activer l'environnement virtuel si disponible
if exist .venv\Scripts\activate.bat (
    echo 📦 Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Environnement virtuel non trouvé, utilisation de Python global
)

echo.
echo 🐍 Lancement du script Python d'upload...
echo.

REM Lancer le script Python
python auto_upload_github.py

echo.
echo ✅ Script terminé
pause