#!/usr/bin/env python3
"""
Import des données FDJ CSV dans la base EuroMillions
===================================================

Script pour importer les fichiers CSV officiels FDJ dans la base de données.
Supporte le format avec séparateur ';' et toutes les colonnes FDJ.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent))

def parse_fdj_csv(csv_path: str) -> pd.DataFrame:
    """Parse un fichier CSV FDJ et retourne un DataFrame normalisé."""
    print(f"📂 Lecture de {Path(csv_path).name}...")
    
    try:
        # Lire le CSV avec séparateur ';'
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        print(f"   ✅ {len(df)} lignes chargées")
        
        # Afficher les colonnes pour debug
        print(f"   📋 Colonnes: {list(df.columns[:10])}...")  # Première 10 colonnes
        
        # Normaliser les données
        normalized_draws = []
        
        for idx, row in df.iterrows():
            try:
                # Extraire la date (format DD/MM/YYYY)
                date_str = str(row['date_de_tirage'])
                
                # Convertir DD/MM/YYYY vers YYYY-MM-DD
                if '/' in date_str:
                    day, month, year = date_str.split('/')
                    draw_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    print(f"   ⚠️  Format de date non reconnu: {date_str}")
                    continue
                
                # Extraire les numéros
                n1, n2, n3, n4, n5 = int(row['boule_1']), int(row['boule_2']), int(row['boule_3']), int(row['boule_4']), int(row['boule_5'])
                s1, s2 = int(row['etoile_1']), int(row['etoile_2'])
                
                # Trier les numéros (au cas où)
                main_nums = sorted([n1, n2, n3, n4, n5])
                star_nums = sorted([s1, s2])
                
                # Créer l'ID du tirage
                draw_id = f"euromillions-{draw_date}"
                
                # Extraire le jackpot si disponible
                jackpot = None
                if 'rapport_du_rang1' in row and pd.notna(row['rapport_du_rang1']):
                    try:
                        jackpot_str = str(row['rapport_du_rang1']).replace(' ', '')
                        jackpot = float(jackpot_str)
                    except:
                        pass
                
                draw_data = {
                    "draw_id": draw_id,
                    "draw_date": draw_date,
                    "n1": main_nums[0],
                    "n2": main_nums[1], 
                    "n3": main_nums[2],
                    "n4": main_nums[3],
                    "n5": main_nums[4],
                    "s1": star_nums[0],
                    "s2": star_nums[1],
                    "jackpot": jackpot,
                    "source": "FDJ_CSV"
                }
                
                normalized_draws.append(draw_data)
                
            except Exception as e:
                print(f"   ⚠️  Erreur ligne {idx}: {e}")
                continue
        
        print(f"   ✅ {len(normalized_draws)} tirages normalisés")
        return pd.DataFrame(normalized_draws)
        
    except Exception as e:
        print(f"   ❌ Erreur lecture fichier: {e}")
        return pd.DataFrame()

def import_fdj_files():
    """Importer tous les fichiers FDJ CSV."""
    print("🏛️ Import des données officielles FDJ")
    print("=" * 45)
    
    # Chemins des fichiers
    csv_files = [
        r"c:\Users\460nie\Downloads\euromillions\euromillions.csv",
        r"c:\Users\460nie\Downloads\euromillions_2\euromillions_2.csv", 
        r"c:\Users\460nie\Downloads\euromillions_3\euromillions_3.csv"
    ]
    
    all_draws = []
    
    # Traiter chaque fichier
    for csv_file in csv_files:
        csv_path = Path(csv_file)
        if csv_path.exists():
            df = parse_fdj_csv(csv_file)
            if not df.empty:
                all_draws.extend(df.to_dict('records'))
        else:
            print(f"   ❌ Fichier non trouvé: {csv_path}")
    
    print(f"\n📊 Total: {len(all_draws)} tirages à importer")
    
    if not all_draws:
        print("❌ Aucune donnée à importer")
        return False
    
    # Dédupliquer par draw_id
    unique_draws = {}
    for draw in all_draws:
        draw_id = draw['draw_id']
        if draw_id not in unique_draws:
            unique_draws[draw_id] = draw
        # Garder le plus récent en cas de doublon
        elif draw['source'] == 'FDJ_CSV':
            unique_draws[draw_id] = draw
    
    final_draws = list(unique_draws.values())
    print(f"📦 Après dédoublonnage: {len(final_draws)} tirages uniques")
    
    # Trier par date
    final_draws.sort(key=lambda x: x['draw_date'])
    
    # Afficher un échantillon
    print(f"\n🔍 Échantillon des données:")
    for i, draw in enumerate(final_draws[:5]):
        print(f"   {draw['draw_date']}: {draw['n1']}-{draw['n2']}-{draw['n3']}-{draw['n4']}-{draw['n5']} + {draw['s1']}-{draw['s2']}")
    
    if len(final_draws) > 5:
        print(f"   ... et {len(final_draws) - 5} autres")
    
    # Importer dans la base
    print(f"\n💾 Import dans la base de données...")
    
    try:
        from repository import get_repository
        
        repo = get_repository()
        
        # Vider la base actuelle (données de test)
        print("🗑️ Nettoyage des anciennes données...")
        import sqlite3
        from config import get_settings
        
        settings = get_settings()
        db_path = settings.storage_path / 'draws.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM draws')
        conn.commit()
        conn.close()
        print("   ✅ Base nettoyée")
        
        # Insérer les nouvelles données
        result = repo.upsert_draws(final_draws)
        
        print(f"✅ IMPORT TERMINÉ!")
        print(f"   📥 {result.get('inserted', 0)} tirages insérés")
        print(f"   🔄 {result.get('updated', 0)} tirages mis à jour")
        
        if result.get('errors', 0) > 0:
            print(f"   ⚠️ {result['errors']} erreurs")
        
        # Vérifier le résultat
        final_df = repo.all_draws_df()
        print(f"\n📈 Résultat final:")
        print(f"   📊 {len(final_df)} tirages dans la base")
        
        if not final_df.empty:
            print(f"   📅 Période: {final_df['draw_date'].min().date()} à {final_df['draw_date'].max().date()}")
            
            # Afficher les derniers tirages
            print(f"   🔄 Derniers tirages:")
            recent = final_df.sort_values('draw_date', ascending=False).head(3)
            for _, row in recent.iterrows():
                date = row['draw_date'].strftime('%Y-%m-%d')
                balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
                stars = f"{row['s1']:02d}-{row['s2']:02d}"
                print(f"      {date}: {balls} + {stars}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_fdj_files()
    
    if success:
        print(f"\n🎉 SUCCÈS COMPLET!")
        print("   Votre base contient maintenant l'historique officiel FDJ!")
        print("   Vous pouvez maintenant entraîner le modèle avec confiance!")
        
        print(f"\n🚀 Prochaines étapes:")
        print("   1. Re-entraîner le modèle avec ces vraies données")
        print("   2. Générer des prédictions basées sur l'historique réel") 
        print("   3. Profiter des performances améliorées!")
        
    else:
        print(f"\n❌ Échec de l'import")
        print("   Vérifiez les chemins des fichiers CSV")