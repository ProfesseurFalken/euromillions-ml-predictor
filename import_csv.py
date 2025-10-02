#!/usr/bin/env python3
"""
Import manuel des tirages EuroMillions depuis un fichier CSV
"""

import sys
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

def parse_date(date_str: str) -> datetime:
    """Parse différents formats de date."""
    date_str = date_str.strip()
    
    # Formats possibles
    formats = [
        '%d/%m/%Y',     # 27/09/2025
        '%d-%m-%Y',     # 27-09-2025  
        '%Y-%m-%d',     # 2025-09-27
        '%d.%m.%Y',     # 27.09.2025
        '%d %m %Y',     # 27 09 2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Format de date non reconnu: {date_str}")

def detect_csv_format(file_path: str) -> Dict[str, str]:
    """Détecter le format du fichier CSV."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        sample_row = next(reader)
    
    print(f"📋 Header détecté: {header}")
    print(f"📊 Ligne exemple: {sample_row}")
    
    # Mapping des colonnes possibles
    column_mapping = {}
    
    # Détection des colonnes de date
    for i, col in enumerate(header):
        col_lower = col.lower().strip()
        if 'date' in col_lower or 'tirage' in col_lower:
            column_mapping['date'] = i
            break
    
    # Détection des boules principales (5 colonnes)
    ball_cols = []
    for i, col in enumerate(header):
        col_lower = col.lower().strip()
        if any(x in col_lower for x in ['n1', 'n2', 'n3', 'n4', 'n5', 'boule', 'ball']):
            ball_cols.append(i)
    
    if len(ball_cols) >= 5:
        column_mapping['balls'] = ball_cols[:5]
    else:
        # Fallback: prendre les colonnes numériques après la date
        date_col = column_mapping.get('date', 0)
        column_mapping['balls'] = list(range(date_col + 1, date_col + 6))
    
    # Détection des étoiles (2 colonnes)
    star_cols = []
    for i, col in enumerate(header):
        col_lower = col.lower().strip()
        if any(x in col_lower for x in ['e1', 'e2', 'etoile', 'star']):
            star_cols.append(i)
    
    if len(star_cols) >= 2:
        column_mapping['stars'] = star_cols[:2]
    else:
        # Fallback: prendre les 2 colonnes après les boules
        last_ball = column_mapping['balls'][-1]
        column_mapping['stars'] = [last_ball + 1, last_ball + 2]
    
    # Jackpot (optionnel)
    for i, col in enumerate(header):
        col_lower = col.lower().strip()
        if any(x in col_lower for x in ['jackpot', 'gain', 'prix']):
            column_mapping['jackpot'] = i
            break
    
    print(f"🔍 Mapping détecté: {column_mapping}")
    return column_mapping

def import_csv_to_draws(file_path: str) -> List[Dict[str, Any]]:
    """Convertir CSV en format draws."""
    print(f"📁 Import du fichier: {file_path}")
    
    # Détecter le format
    mapping = detect_csv_format(file_path)
    
    draws = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row_num, row in enumerate(reader, 1):
            try:
                # Parse date
                date_col = mapping.get('date', 0)
                draw_date = parse_date(row[date_col])
                
                # Parse boules principales
                ball_indices = mapping['balls']
                balls = [int(row[i]) for i in ball_indices]
                balls.sort()  # Trier comme dans EuroMillions
                
                # Parse étoiles  
                star_indices = mapping['stars']
                stars = [int(row[i]) for i in star_indices]
                stars.sort()  # Trier
                
                # Parse jackpot (optionnel)
                jackpot = None
                if 'jackpot' in mapping and len(row) > mapping['jackpot']:
                    try:
                        jackpot_str = row[mapping['jackpot']].replace(',', '').replace(' ', '')
                        jackpot = float(jackpot_str)
                    except (ValueError, IndexError):
                        pass
                
                # Créer le draw
                draw_id = f"euromillions-{draw_date.strftime('%Y-%m-%d')}"
                
                draw = {
                    "draw_id": draw_id,
                    "draw_date": draw_date,
                    "n1": balls[0],
                    "n2": balls[1], 
                    "n3": balls[2],
                    "n4": balls[3],
                    "n5": balls[4],
                    "s1": stars[0],
                    "s2": stars[1],
                    "jackpot": jackpot,
                    "prize_table": None,
                    "raw_html": f"Imported from CSV: {file_path}"
                }
                
                draws.append(draw)
                
            except Exception as e:
                print(f"⚠️  Erreur ligne {row_num}: {e}")
                continue
    
    print(f"✅ {len(draws)} tirages convertis")
    return draws

def import_and_update_database(csv_file_path: str):
    """Import CSV et mise à jour de la base."""
    print("🔄 Import CSV et mise à jour de la base de données")
    print("=" * 55)
    
    try:
        from repository import get_repository
        
        # Vérifier que le fichier existe
        if not Path(csv_file_path).exists():
            print(f"❌ Fichier non trouvé: {csv_file_path}")
            return False
        
        # Import CSV
        draws = import_csv_to_draws(csv_file_path)
        
        if not draws:
            print("❌ Aucun tirage importé")
            return False
        
        # Afficher aperçu
        print(f"\n📊 Aperçu des {min(3, len(draws))} premiers tirages:")
        for i, draw in enumerate(draws[:3]):
            date = draw['draw_date'].strftime('%Y-%m-%d')
            balls = f"{draw['n1']:02d}-{draw['n2']:02d}-{draw['n3']:02d}-{draw['n4']:02d}-{draw['n5']:02d}"
            stars = f"{draw['s1']:02d}-{draw['s2']:02d}"
            print(f"   {i+1}. {date}: {balls} | ⭐ {stars}")
        
        # Mise à jour base
        print(f"\n💾 Mise à jour de la base de données...")
        repo = get_repository()
        
        # État avant
        before_df = repo.all_draws_df()
        before_count = len(before_df)
        
        # Import
        result = repo.upsert_draws(draws)
        
        # État après
        after_df = repo.all_draws_df()
        after_count = len(after_df)
        
        print(f"✅ Import terminé:")
        print(f"   📥 {result.get('inserted', 0)} nouveaux tirages")
        print(f"   🔄 {result.get('updated', 0)} tirages mis à jour")
        print(f"   📊 Base: {before_count} → {after_count} tirages")
        
        if after_count >= 100:
            print(f"\n🎉 EXCELLENT! {after_count} tirages - assez pour un entraînement robuste!")
        elif after_count >= 50:
            print(f"\n✅ BON! {after_count} tirages - entraînement possible avec paramètres adaptés")
        else:
            print(f"\n⚠️  {after_count} tirages - encore un peu juste pour l'entraînement")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("📁 Import manuel de tirages EuroMillions depuis CSV")
    print("=" * 55)
    
    # Demander le fichier
    csv_file = input("📂 Chemin vers le fichier CSV (ou glissez-le ici): ").strip().strip('"')
    
    if csv_file:
        success = import_and_update_database(csv_file)
        
        if success:
            print("\n🚀 Prêt pour l'entraînement!")
            print("   Utilisez maintenant l'interface Streamlit pour entraîner le modèle")
        else:
            print("\n❌ Import échoué")
    else:
        print("❌ Aucun fichier spécifié")