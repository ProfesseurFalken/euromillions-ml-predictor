#!/usr/bin/env python3
"""
Script de mise à jour automatique des tirages EuroMillions
🔄 Mise à jour complète en une commande
"""

import os
import sys
from datetime import datetime
import subprocess

def run_command(cmd, description):
    """Exécuter une commande avec gestion d'erreurs"""
    print(f"▶️ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True, result.stdout
        else:
            print(f"❌ {description} - Erreur:")
            print(f"   {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False, str(e)

def update_tirages():
    """Processus complet de mise à jour"""
    print("🔄 MISE À JOUR AUTOMATIQUE DES TIRAGES EUROMILLIONS")
    print("=" * 60)
    
    # 1. Vérification de l'état actuel
    print("\n📊 ÉTAPE 1/5: Vérification de l'état actuel")
    success, output = run_command("python check_tirage_freshness.py", "Vérification des tirages")
    
    # 2. Tentative de récupération automatique via scraping
    print("\n🌐 ÉTAPE 2/5: Récupération des nouveaux tirages")
    
    # Essayer le scraper hybride
    print("🔍 Tentative via scraper hybride...")
    success_scraper, output_scraper = run_command("python hybrid_scraper.py", "Scraping hybride")
    
    if success_scraper:
        print("✅ Nouveaux tirages récupérés via scraper")
        new_data_found = True
    else:
        print("⚠️ Scraper automatique échoué")
        
        # Vérifier s'il y a des CSV à importer
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'euromillions' in f.lower()]
        
        if csv_files:
            print(f"📄 {len(csv_files)} fichier(s) CSV trouvé(s) - Tentative d'import...")
            success_csv, output_csv = run_command("python import_fdj_special.py", "Import CSV FDJ")
            new_data_found = success_csv
        else:
            print("❌ Aucune nouvelle source de données disponible")
            new_data_found = False
    
    if not new_data_found:
        print("\n⚠️ AUCUNE NOUVELLE DONNÉE TROUVÉE")
        print("💡 Options manuelles :")
        print("   📥 1. Téléchargez des CSV récents depuis FDJ.fr")
        print("   📱 2. Consultez https://www.fdj.fr/jeux/jeux-de-tirage/euromillions")
        return False
    
    # 3. Vérification post-import
    print("\n🔍 ÉTAPE 3/5: Vérification des nouvelles données")
    run_command("python check_tirage_freshness.py", "Vérification post-import")
    
    # 4. Re-entraînement du modèle
    print("\n🤖 ÉTAPE 4/5: Re-entraînement du modèle")
    success_train, output_train = run_command("python cli_train.py train", "Entraînement des modèles")
    
    if success_train:
        print("✅ Modèles re-entraînés avec succès")
    else:
        print("⚠️ Problème lors du re-entraînement")
        print("💡 Les anciens modèles restent utilisables")
    
    # 5. Test des prédictions
    print("\n🎯 ÉTAPE 5/5: Test des nouvelles prédictions")
    success_test, output_test = run_command("python cli_train.py score --top 5", "Test des prédictions")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎉 MISE À JOUR TERMINÉE")
    print("=" * 60)
    
    if success_train:
        print("✅ Système entièrement à jour avec nouveaux modèles")
        print("🎯 Nouvelles prédictions disponibles")
    else:
        print("⚠️ Données mises à jour, modèles à re-entraîner manuellement")
    
    print("\n🚀 Prochaines étapes :")
    print("   📱 Lancer l'interface: python -m streamlit run ui\\streamlit_app.py --server.port 8501")
    print("   🎲 Générer prédictions: python cli_train.py suggest")
    
    return True

def interactive_update():
    """Mode interactif avec choix utilisateur"""
    print("🤔 Mode interactif activé")
    
    response = input("Voulez-vous procéder à la mise à jour automatique ? (o/N): ").lower().strip()
    
    if response in ['o', 'oui', 'y', 'yes']:
        return update_tirages()
    else:
        print("❌ Mise à jour annulée")
        print("💡 Vous pouvez relancer avec: python update_tirages.py")
        return False

if __name__ == "__main__":
    print(f"🕒 Démarrage de la mise à jour - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier si on est en mode interactif
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Mode automatique (sans confirmation)
        update_tirages()
    else:
        # Mode interactif (avec confirmation)
        interactive_update()