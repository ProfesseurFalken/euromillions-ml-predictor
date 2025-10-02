@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo 🚀 INSTALLATION AUTOMATIQUE - EuroMillions ML Predictor
echo ========================================================================
echo.
echo Ce script va automatiquement installer le projet depuis GitHub
echo.

REM Vérifier si Git est installé
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git n'est pas installé
    echo 📥 Téléchargez Git : https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git détecté

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé
    echo 📥 Téléchargez Python : https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Vérifier si le dossier existe déjà
if exist "euromillions-ml-predictor" (
    echo 📁 Dossier euromillions-ml-predictor existe déjà
    set /p overwrite="Voulez-vous le supprimer et réinstaller ? (o/N): "
    if /i "!overwrite!"=="o" (
        echo 🗑️ Suppression du dossier existant...
        rmdir /s /q "euromillions-ml-predictor"
    ) else (
        echo ❌ Installation annulée
        pause
        exit /b 1
    )
)

echo.
echo 📥 Clonage du repository depuis GitHub...
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git

if %errorlevel% neq 0 (
    echo ❌ Échec du clonage
    echo 💡 Vérifiez votre connexion Internet et vos droits d'accès
    pause
    exit /b 1
)

echo ✅ Clonage réussi

echo.
echo 📁 Entrée dans le dossier du projet...
cd euromillions-ml-predictor

echo.
echo 🐍 Création de l'environnement virtuel Python...
python -m venv .venv

if %errorlevel% neq 0 (
    echo ❌ Échec de la création de l'environnement virtuel
    pause
    exit /b 1
)

echo ✅ Environnement virtuel créé

echo.
echo 📦 Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo.
echo 📋 Installation des dépendances Python...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Échec de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances installées

echo.
echo ⚙️ Configuration du projet...
if not exist .env (
    copy .env.example .env >nul 2>&1
    echo ✅ Fichier de configuration créé
)

echo.
echo ========================================================================
echo ✅ INSTALLATION TERMINÉE AVEC SUCCÈS !
echo ========================================================================
echo.
echo 🎯 Prochaines étapes recommandées :
echo.
echo 1. 📊 Importer vos données :
echo    python import_fdj_special.py  (si vous avez des CSV FDJ)
echo    OU
echo    python scraper.py  (pour télécharger automatiquement)
echo.
echo 2. 🤖 Entraîner les modèles :
echo    python cli_train.py train
echo.
echo 3. 🚀 Lancer l'interface :
echo    start_euromillions.bat
echo    OU
echo    streamlit run ui/streamlit_app.py
echo.
echo 🌐 L'interface sera disponible sur : http://localhost:8501
echo.
echo 📚 Documentation complète dans README.md
echo.

set /p launch="Voulez-vous lancer l'interface maintenant ? (o/N): "
if /i "!launch!"=="o" (
    echo.
    echo 🚀 Lancement de l'interface...
    start_euromillions.bat
) else (
    echo.
    echo 💡 Pour lancer plus tard : double-cliquez sur start_euromillions.bat
)

pause