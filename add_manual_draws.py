#!/usr/bin/env python3
"""
Interface simple pour ajouter des tirages manuellement
Permet d'ajouter un ou plusieurs tirages directement dans la base
"""

from repository import EuromillionsRepository
from datetime import datetime
import sys

def add_manual_draw():
    """Ajouter un tirage manuellement"""
    print("[AJOUT MANUEL] Nouveau tirage EuroMillions")
    print("=" * 50)
    
    try:
        # Demander les informations du tirage
        print("Entrez les informations du tirage :")
        
        # Date
        date_str = input("Date (format YYYY-MM-DD, ex: 2025-09-30): ").strip()
        try:
            draw_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            print("[ERREUR] Format de date invalide")
            return False
        
        # Numéros principaux
        print("Numéros principaux (1-50) :")
        main_numbers = []
        for i in range(1, 6):
            while True:
                try:
                    num = int(input(f"  Numéro {i}: "))
                    if 1 <= num <= 50 and num not in main_numbers:
                        main_numbers.append(num)
                        break
                    else:
                        print("    Numéro invalide ou déjà saisi (1-50)")
                except ValueError:
                    print("    Veuillez entrer un nombre")
        
        # Étoiles
        print("Étoiles (1-12) :")
        stars = []
        for i in range(1, 3):
            while True:
                try:
                    star = int(input(f"  Étoile {i}: "))
                    if 1 <= star <= 12 and star not in stars:
                        stars.append(star)
                        break
                    else:
                        print("    Étoile invalide ou déjà saisie (1-12)")
                except ValueError:
                    print("    Veuillez entrer un nombre")
        
        # Trier les numéros
        main_numbers.sort()
        stars.sort()
        
        # Créer l'ID du tirage
        draw_id = f"EM-{date_str}"
        
        # Affichage de confirmation
        print(f"\n[CONFIRMATION]")
        print(f"Date: {draw_date}")
        print(f"Numéros: {' - '.join(map(str, main_numbers))}")
        print(f"Étoiles: {' - '.join(map(str, stars))}")
        print(f"ID: {draw_id}")
        
        confirm = input("\nConfirmer l'ajout ? (o/N): ").lower().strip()
        
        if confirm in ['o', 'oui', 'y', 'yes']:
            # Préparer les données
            draw_data = {
                'draw_id': draw_id,
                'draw_date': draw_date,
                'n1': main_numbers[0],
                'n2': main_numbers[1], 
                'n3': main_numbers[2],
                'n4': main_numbers[3],
                'n5': main_numbers[4],
                's1': stars[0],
                's2': stars[1],
                'jackpot': None,
                'prize_table': None,
                'raw_html': None
            }
            
            # Sauvegarder
            repo = EuromillionsRepository()
            result = repo.upsert_draws([draw_data])
            
            if result['inserted'] > 0:
                print(f"[SUCCES] Tirage ajouté avec succès !")
                print(f"[INFO] {result['inserted']} nouveau tirage")
            elif result['updated'] > 0:
                print(f"[INFO] Tirage existant mis à jour")
                print(f"[INFO] {result['updated']} tirage modifié")
            else:
                print(f"[ERREUR] Échec de l'ajout")
                return False
            
            # Recommandation de re-entraînement
            print(f"\n[CONSEIL] Après l'ajout de nouveaux tirages :")
            print(f"  1. Vérifiez: python status.py")
            print(f"  2. Re-entraînez: python cli_train.py train")
            
            return True
        else:
            print("[ANNULE] Tirage non ajouté")
            return False
            
    except KeyboardInterrupt:
        print("\n[ANNULE] Opération interrompue")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout: {e}")
        return False

def add_multiple_draws():
    """Ajouter plusieurs tirages en série"""
    print("[AJOUT MULTIPLE] Plusieurs tirages")
    print("=" * 50)
    
    count = 0
    while True:
        print(f"\n--- Tirage #{count + 1} ---")
        if add_manual_draw():
            count += 1
            
        continue_adding = input(f"\nAjouter un autre tirage ? (o/N): ").lower().strip()
        if continue_adding not in ['o', 'oui', 'y', 'yes']:
            break
    
    print(f"\n[TERMINE] {count} tirage(s) ajouté(s)")
    return count > 0

def main():
    """Menu principal"""
    print("AJOUT MANUEL DE TIRAGES EUROMILLIONS")
    print("=" * 50)
    print("1. Ajouter un tirage")
    print("2. Ajouter plusieurs tirages") 
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        add_manual_draw()
    elif choice == "2":
        add_multiple_draws()
    elif choice == "3":
        print("Au revoir !")
    else:
        print("Choix invalide")

if __name__ == "__main__":
    main()