#!/usr/bin/env python3
"""
Script de mise à jour automatique des tirages EuroMillions
Version compatible Windows/PowerShell (sans émojis Unicode)
"""

import os
import sys
from datetime import datetime
import subprocess

def run_command(cmd, description):
    """Exécuter une commande avec gestion d'erreurs"""
    print(f"[ACTION] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"[SUCCES] {description} - OK")
            return True, result.stdout
        else:
            print(f"[ERREUR] {description} - Echec:")
            print(f"   {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"[ERREUR] {description} - Exception: {e}")
        return False, str(e)

def update_tirages():
    """Processus complet de mise à jour"""
    print("[INFO] MISE A JOUR AUTOMATIQUE DES TIRAGES EUROMILLIONS")
    print("=" * 60)
    
    # 1. Vérification de l'état actuel
    print("\n[ETAPE 1/5] Verification de l'etat actuel")
    success, output = run_command("python check_freshness_windows.py", "Verification des tirages")
    
    # 2. Tentative de récupération automatique via scraping
    print("\n[ETAPE 2/5] Recuperation des nouveaux tirages")
    
    # Essayer le scraper hybride
    print("[INFO] Tentative via scraper hybride...")
    success_scraper, output_scraper = run_command("python hybrid_scraper.py", "Scraping hybride")
    
    if success_scraper:
        print("[SUCCES] Nouveaux tirages recuperes via scraper")
        new_data_found = True
    else:
        print("[ATTENTION] Scraper automatique echoue")
        
        # Vérifier s'il y a des CSV à importer
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'euromillions' in f.lower()]
        
        if csv_files:
            print(f"[INFO] {len(csv_files)} fichier(s) CSV trouve(s) - Tentative d'import...")
            success_csv, output_csv = run_command("python import_fdj_special.py", "Import CSV FDJ")
            new_data_found = success_csv
        else:
            print("[ERREUR] Aucune nouvelle source de donnees disponible")
            new_data_found = False
    
    if not new_data_found:
        print("\n[ATTENTION] AUCUNE NOUVELLE DONNEE TROUVEE")
        print("[CONSEILS] Options manuelles :")
        print("   1. Telechargez des CSV recents depuis FDJ.fr")
        print("   2. Consultez https://www.fdj.fr/jeux/jeux-de-tirage/euromillions")
        return False
    
    # 3. Vérification post-import
    print("\n[ETAPE 3/5] Verification des nouvelles donnees")
    run_command("python check_freshness_windows.py", "Verification post-import")
    
    # 4. Re-entraînement du modèle
    print("\n[ETAPE 4/5] Re-entrainement du modele")
    success_train, output_train = run_command("python cli_train.py train", "Entrainement des modeles")
    
    if success_train:
        print("[SUCCES] Modeles re-entraines avec succes")
    else:
        print("[ATTENTION] Probleme lors du re-entrainement")
        print("[INFO] Les anciens modeles restent utilisables")
    
    # 5. Test des prédictions
    print("\n[ETAPE 5/5] Test des nouvelles predictions")
    success_test, output_test = run_command("python cli_train.py score --top 5", "Test des predictions")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("[RESULTAT] MISE A JOUR TERMINEE")
    print("=" * 60)
    
    if success_train:
        print("[SUCCES] Systeme entierement a jour avec nouveaux modeles")
        print("[INFO] Nouvelles predictions disponibles")
    else:
        print("[ATTENTION] Donnees mises a jour, modeles a re-entrainer manuellement")
    
    print("\n[PROCHAINES ETAPES]")
    print("   Interface: python -m streamlit run ui\\streamlit_app.py --server.port 8501")
    print("   Predictions: python cli_train.py suggest")
    
    return True

def interactive_update():
    """Mode interactif avec choix utilisateur"""
    print("[INFO] Mode interactif active")
    
    response = input("Voulez-vous proceder a la mise a jour automatique ? (o/N): ").lower().strip()
    
    if response in ['o', 'oui', 'y', 'yes']:
        return update_tirages()
    else:
        print("[INFO] Mise a jour annulee")
        print("[CONSEIL] Vous pouvez relancer avec: python update_tirages_windows.py")
        return False

if __name__ == "__main__":
    print(f"[DEBUT] Demarrage de la mise a jour - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier si on est en mode interactif
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Mode automatique (sans confirmation)
        update_tirages()
    else:
        # Mode interactif (avec confirmation)
        interactive_update()