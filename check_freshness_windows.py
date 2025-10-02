#!/usr/bin/env python3
"""
Vérification de l'actualité des tirages EuroMillions
🔍 Version compatible Windows/PowerShell
"""

import sqlite3
from datetime import datetime, timedelta
import requests
from repository import EuromillionsRepository

def check_tirage_freshness():
    """Vérifier si notre base de données est à jour"""
    try:
        print("[INFO] Verification de l'actualite des tirages")
        print("=" * 60)
        
        # Connexion à la base de données
        repo = EuromillionsRepository()
        
        # Statistiques de base
        draws_df = repo.all_draws_df()
        if draws_df.empty:
            print("[ERREUR] Aucun tirage trouvé dans la base")
            return False
            
        total_draws = len(draws_df)
        latest_draw = draws_df.loc[draws_df['draw_date'].idxmax()]
        earliest_draw = draws_df.loc[draws_df['draw_date'].idxmin()]
        
        print(f"[STATS] Total tirages: {total_draws}")
        print(f"[STATS] Premier tirage: {earliest_draw['draw_date'].strftime('%Y-%m-%d')}")
        print(f"[STATS] Dernier tirage: {latest_draw['draw_date'].strftime('%Y-%m-%d')}")
        
        # Analyse de fraîcheur
        latest_date = latest_draw['draw_date'].to_pydatetime()
        current_date = datetime.now()
        days_behind = (current_date - latest_date).days
        
        print(f"[ANALYSE] Date actuelle: {current_date.strftime('%Y-%m-%d')}")
        print(f"[ANALYSE] Retard: {days_behind} jour(s)")
        
        # Statut de fraîcheur
        if days_behind <= 3:
            status = "A JOUR"
            color = "VERT"
        elif days_behind <= 7:
            status = "ACCEPTABLE"
            color = "ORANGE"
        else:
            status = "OBSOLETE"
            color = "ROUGE"
            
        print(f"[STATUT] {status} ({color})")
        
        # Estimations des tirages manquants
        # EuroMillions: Mardi et Vendredi
        def count_euromill_draws_between(start_date, end_date):
            count = 0
            current = start_date + timedelta(days=1)  # Jour suivant le dernier tirage
            while current <= end_date:
                # Mardi = 1, Vendredi = 4 (0=Lundi)
                if current.weekday() in [1, 4]:
                    count += 1
                current += timedelta(days=1)
            return count
        
        estimated_missing = count_euromill_draws_between(latest_date, current_date)
        
        if estimated_missing > 0:
            print(f"[ESTIMATION] Tirages manquants possibles: {estimated_missing}")
        else:
            print("[ESTIMATION] Pas de tirages manquants")
            
        # Test de connectivité FDJ
        print(f"\n[TEST] Verification connectivite FDJ.fr...")
        try:
            response = requests.get("https://www.fdj.fr/jeux/jeux-de-tirage/euromillions", 
                                  timeout=10, 
                                  headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                print("[CONNECTIVITE] FDJ.fr accessible")
            else:
                print(f"[CONNECTIVITE] FDJ.fr status: {response.status_code}")
        except Exception as e:
            print(f"[CONNECTIVITE] Erreur: {str(e)[:100]}")
        
        # Recommandations
        print(f"\n[RECOMMANDATIONS]")
        if days_behind <= 3:
            print("- Base de donnees actuelle, aucune action requise")
        elif days_behind <= 7:
            print("- Mise a jour recommandee sous peu")
        else:
            print("- Mise a jour urgente necessaire")
            print("- Telecharger les derniers CSV depuis FDJ.fr")
            print("- Lancer: python update_tirages.py")
        
        return {
            'status': status,
            'days_behind': days_behind,
            'total_draws': total_draws,
            'latest_date': latest_draw['draw_date'].strftime('%Y-%m-%d'),
            'estimated_missing': estimated_missing
        }
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de la verification: {e}")
        return False

if __name__ == "__main__":
    result = check_tirage_freshness()
    if result and isinstance(result, dict):
        print(f"\n[RESULTAT] {result['status']} - {result['days_behind']} jour(s) de retard")
    else:
        print("[RESULTAT] Verification echouee")