#!/usr/bin/env python3
"""Vérifier la plage d'étoiles dans nos données FDJ"""

import pandas as pd
import glob

def check_csv_files():
    print("🔍 Analyse des plages d'étoiles dans tous les CSV")
    print("=" * 50)
    
    csv_files = glob.glob("euromillions*.csv")
    
    all_stars = set()
    
    for csv_file in csv_files:
        print(f"\n📂 Fichier: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            print(f"   📊 {len(df)} lignes")
            
            # Chercher les colonnes d'étoiles
            star_cols = []
            for col in df.columns:
                if 'etoile' in col.lower():
                    star_cols.append(col)
            
            print(f"   🌟 Colonnes étoiles: {star_cols}")
            
            # Analyser les valeurs
            file_stars = set()
            for col in star_cols:
                values = df[col].dropna().unique()
                file_stars.update(values)
                print(f"      {col}: {sorted(values)}")
            
            all_stars.update(file_stars)
            print(f"   📊 Plage dans ce fichier: {min(file_stars)} à {max(file_stars)}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print(f"\n🌟 PLAGE GLOBALE D'ÉTOILES: {min(all_stars)} à {max(all_stars)}")
    print(f"   Étoiles trouvées: {sorted(all_stars)}")
    
    # Vérifier si on a l'étoile 12
    if 12 in all_stars:
        print("   ✅ L'étoile 12 existe dans les données")
    else:
        print("   ⚠️ L'étoile 12 est ABSENTE des données")
        print("   💡 Ceci explique le problème d'entraînement du modèle")

if __name__ == "__main__":
    check_csv_files()