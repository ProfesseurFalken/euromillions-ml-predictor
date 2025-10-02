#!/usr/bin/env python3
"""
Script de statut rapide EuroMillions
Affiche l'état actuel sans modifications
"""

from check_freshness_windows import check_tirage_freshness
import sys

def quick_status():
    """Affichage rapide du statut"""
    print("[STATUT RAPIDE] EuroMillions ML System")
    print("=" * 50)
    
    result = check_tirage_freshness()
    
    if result and isinstance(result, dict):
        status = result['status']
        days_behind = result['days_behind']
        total_draws = result['total_draws']
        
        print(f"\n[RESUME]")
        print(f"  Statut: {status}")
        print(f"  Retard: {days_behind} jour(s)")
        print(f"  Total tirages: {total_draws}")
        
        if days_behind <= 3:
            print("  Action requise: Aucune")
            print("  Conseil: Systeme operationnel")
        elif days_behind <= 7:
            print("  Action requise: Mise a jour recommandee")
            print("  Conseil: python update_tirages_windows.py")
        else:
            print("  Action requise: Mise a jour urgente")
            print("  Conseil: Telecharger nouveaux CSV + update")
            
        return True
    else:
        print("[ERREUR] Impossible de determiner le statut")
        return False

if __name__ == "__main__":
    success = quick_status()
    sys.exit(0 if success else 1)