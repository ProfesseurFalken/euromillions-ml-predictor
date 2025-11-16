@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo 🚀 UPLOAD TO GITHUB - EuroMillions ML Predictor
echo ========================================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git n'est pas installé
    echo 📥 Téléchargez Git : https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git détecté
echo.

REM Show current status
echo 📊 État actuel du repository:
echo ========================================================================
git status --short
echo ========================================================================
echo.

REM Ask for confirmation
set /p confirm="Voulez-vous continuer avec l'upload ? (o/N): "
if /i not "!confirm!"=="o" (
    echo ❌ Upload annulé
    pause
    exit /b 0
)

echo.
echo 📦 Ajout de tous les fichiers...
git add .

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'ajout des fichiers
    pause
    exit /b 1
)

echo ✅ Fichiers ajoutés
echo.

REM Ask for commit message
echo 💬 Message de commit:
echo.
set /p custom_message="Entrez un message personnalisé (ou appuyez sur Entrée pour le message par défaut): "

if "!custom_message!"=="" (
    set "commit_message=Major update: Advanced ML features, improved models, v4 migration, and desktop launcher"
) else (
    set "commit_message=!custom_message!"
)

echo.
echo 💾 Création du commit...
git commit -m "!commit_message!"

if %errorlevel% neq 0 (
    echo ❌ Erreur lors du commit
    pause
    exit /b 1
)

echo ✅ Commit créé
echo.

REM Ask before pushing
echo ⚠️  Prêt à envoyer vers GitHub
set /p push_confirm="Confirmer le push vers origin/main ? (o/N): "
if /i not "!push_confirm!"=="o" (
    echo ℹ️  Push annulé. Les changements sont commités localement.
    echo 💡 Pour pusher plus tard: git push origin main
    pause
    exit /b 0
)

echo.
echo 🚀 Envoi vers GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors du push
    echo.
    echo 💡 Solutions possibles:
    echo    1. Vérifiez votre connexion Internet
    echo    2. Vérifiez vos identifiants GitHub
    echo    3. Essayez: git pull origin main --rebase
    echo    4. Puis: git push origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo ✅ UPLOAD RÉUSSI !
echo ========================================================================
echo.
echo 🌐 Votre projet est maintenant sur GitHub:
echo    https://github.com/ProfesseurFalken/euromillions-ml-predictor
echo.
echo 📋 Prochaines étapes recommandées:
echo    1. Vérifiez que tous les fichiers sont présents
echo    2. Vérifiez que le README.md s'affiche correctement
echo    3. Créez une release si nécessaire (GitHub → Releases)
echo.

pause
