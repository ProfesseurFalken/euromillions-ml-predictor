#!/usr/bin/env python3
"""
Script d'upload automatique complet vers GitHub
Exécutez simplement : python auto_upload_github.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run_cmd(cmd, show_output=True):
    """Exécuter une commande et afficher le résultat"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if show_output and result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Erreur: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur d'exécution: {e}")
        return False

def check_git():
    """Vérifier que Git est installé"""
    print("🔍 Vérification de Git...")
    if run_cmd("git --version", show_output=False):
        print("✅ Git est installé")
        return True
    else:
        print("❌ Git n'est pas installé")
        print("📥 Téléchargez Git : https://git-scm.com/download/win")
        return False

def check_git_status():
    """Vérifier l'état du repository Git"""
    print("\n📊 État du repository Git...")
    
    # Vérifier s'il y a des changements
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        print("📝 Changements détectés, ajout des fichiers...")
        run_cmd("git add .")
        
        # Créer un commit
        commit_msg = """🚀 Update: EuroMillions ML Prediction System

✨ Mise à jour complète du système de prédiction EuroMillions

📊 Fonctionnalités:
- Interface web Streamlit complète en français
- Modèles ML LightGBM optimisés
- Import CSV FDJ avec détection automatique d'encodage
- Ajout manuel de tirages via interface web
- 2,063+ tirages historiques (2011-2025)
- Pipeline de validation croisée temporelle
- 3 méthodes de prédiction intelligentes
- Scripts de maintenance Windows
- Documentation exhaustive

🔧 Améliorations:
- Performance optimisée des modèles
- Interface utilisateur améliorée
- Gestion robuste des données
- Scripts d'automatisation
- Support multi-encodage CSV"""
        
        success = run_cmd(f'git commit -m "{commit_msg}"')
        if success:
            print("✅ Nouveau commit créé")
        else:
            print("ℹ️ Aucun changement à commiter ou commit existant")
    else:
        print("✅ Repository à jour")

def setup_github_remote():
    """Configurer le remote GitHub"""
    print("\n🌐 Configuration du repository GitHub distant...")
    print()
    print("=" * 70)
    print("📋 INSTRUCTIONS IMPORTANTES:")
    print("=" * 70)
    print()
    print("1. Ouvrez votre navigateur et allez sur: https://github.com")
    print("2. Cliquez sur le bouton '+' en haut à droite")
    print("3. Sélectionnez 'New repository'")
    print()
    print("4. Configurez le repository:")
    print("   📝 Nom: euromillions-ml-predictor")
    print("   📄 Description: 🎰 EuroMillions ML - Système de prédiction IA")
    print("   🔒 IMPORTANT: Cochez 'Private' (repository privé)")
    print("   ❌ NE COCHEZ PAS 'Add a README file'")
    print("   ❌ NE COCHEZ PAS 'Add .gitignore'")
    print("   ❌ NE COCHEZ PAS 'Choose a license'")
    print()
    print("5. Cliquez sur 'Create repository'")
    print()
    print("=" * 70)
    print()
    
    username = input("Entrez votre nom d'utilisateur GitHub: ").strip()
    
    if not username:
        print("❌ Nom d'utilisateur requis")
        return False, None
    
    remote_url = f"https://github.com/{username}/euromillions-ml-predictor.git"
    
    # Vérifier si le remote existe déjà
    result = subprocess.run(
        "git remote get-url origin",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("ℹ️ Remote 'origin' existe déjà, mise à jour...")
        run_cmd("git remote remove origin", show_output=False)
    
    print(f"\n🔗 Ajout du remote: {remote_url}")
    success = run_cmd(f"git remote add origin {remote_url}")
    
    return success, username

def push_to_github():
    """Pousser vers GitHub"""
    print("\n📤 Upload vers GitHub...")
    print("⏳ Cela peut prendre quelques secondes...")
    
    # Renommer la branche en 'main' si nécessaire
    run_cmd("git branch -M main", show_output=False)
    
    # Push
    print("\n🚀 Push en cours...")
    success = run_cmd("git push -u origin main")
    
    if not success:
        print("\n⚠️ Le push a échoué. Vérifiez que:")
        print("1. Le repository existe sur GitHub")
        print("2. Il est bien configuré comme 'Private'")
        print("3. Vous êtes connecté à GitHub")
        print()
        print("💡 Si c'est votre première utilisation de Git:")
        print("   Configurez vos identifiants:")
        print("   git config --global user.name 'Votre Nom'")
        print("   git config --global user.email 'votre@email.com'")
        return False
    
    return True

def create_tag():
    """Créer un tag pour la version"""
    print("\n🏷️ Création du tag v1.0.0...")
    
    # Supprimer le tag s'il existe déjà
    run_cmd("git tag -d v1.0.0", show_output=False)
    run_cmd("git push origin --delete v1.0.0", show_output=False)
    
    tag_success = run_cmd('git tag -a v1.0.0 -m "Version 1.0.0: Systeme complet EuroMillions ML"')
    
    if tag_success:
        print("📤 Push du tag...")
        run_cmd("git push origin v1.0.0")
        return True
    
    return False

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 UPLOAD AUTOMATIQUE VERS GITHUB - EuroMillions ML Predictor")
    print("=" * 70)
    print()
    
    # Vérifications préliminaires
    if not check_git():
        input("\nAppuyez sur Entrée pour quitter...")
        return False
    
    # Vérifier l'état Git et faire un commit si nécessaire
    check_git_status()
    
    # Configuration GitHub
    success, username = setup_github_remote()
    if not success:
        input("\nAppuyez sur Entrée pour quitter...")
        return False
    
    # Push vers GitHub
    if not push_to_github():
        input("\nAppuyez sur Entrée pour quitter...")
        return False
    
    # Créer le tag
    create_tag()
    
    # Succès !
    print()
    print("=" * 70)
    print("✅ UPLOAD TERMINÉ AVEC SUCCÈS!")
    print("=" * 70)
    print()
    print(f"🔗 Votre repository: https://github.com/{username}/euromillions-ml-predictor")
    print(f"🔒 Status: PRIVÉ")
    print(f"📊 Tous les fichiers du projet ont été uploadés")
    print(f"🏷️ Version: v1.0.0")
    print()
    print("🎉 Votre EuroMillions ML Predictor est maintenant sauvegardé sur GitHub!")
    print()
    
    input("Appuyez sur Entrée pour quitter...")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Upload annulé par l'utilisateur")
        input("\nAppuyez sur Entrée pour quitter...")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")