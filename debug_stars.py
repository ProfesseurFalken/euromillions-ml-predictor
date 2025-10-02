#!/usr/bin/env python3
"""Debug script pour analyser les problèmes d'entraînement des étoiles"""

import sys
import pandas as pd
from repository import EuromillionsRepository
from build_datasets import build_enhanced_datasets
from collections import Counter

def main():
    print("🔍 Debug des données d'étoiles")
    print("=" * 40)
    
    # Charger les données
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    print(f"📊 Total des tirages: {len(df)}")
    print(f"📅 Période: {df['draw_date'].min()} à {df['draw_date'].max()}")
    print(f"📋 Colonnes disponibles: {list(df.columns)}")
    
    # Analyser les étoiles
    print("\n🌟 Analyse des étoiles:")
    # Les étoiles sont dans s1 et s2
    if 's1' in df.columns and 's2' in df.columns:
        stars_1 = df['s1'].tolist()
        stars_2 = df['s2'].tolist()
        print(f"   ✅ Étoiles trouvées dans s1 et s2")
    else:
        print("   ❌ Colonnes s1 et s2 non trouvées")
        return
    all_stars = stars_1 + stars_2
    
    star_counts = Counter(all_stars)
    print(f"   Étoiles uniques: {sorted(star_counts.keys())}")
    print(f"   Plage: {min(star_counts.keys())} à {max(star_counts.keys())}")
    
    # Compter par étoile
    print("\n📊 Fréquence par étoile:")
    for star in sorted(star_counts.keys()):
        print(f"   ⭐ {star:2d}: {star_counts[star]:3d} fois")
    
    # Vérifier les données d'entraînement
    print("\n🏗️ Construction des datasets...")
    try:
        X_main, y_main, X_star, y_star = build_enhanced_datasets(df)
        print(f"   ✅ X_main: {X_main.shape}")
        print(f"   ✅ y_main: {y_main.shape}")
        print(f"   ✅ X_star: {X_star.shape}")
        print(f"   ✅ y_star: {y_star.shape}")
        
        # Analyser y_star
        print("\n🌟 Analyse y_star:")
        print(f"   Colonnes: {y_star.columns.tolist()}")
        
        # Vérifier chaque colonne
        for col in y_star.columns:
            unique_values = y_star[col].unique()
            print(f"   {col}: {len(unique_values)} valeurs uniques -> {sorted(unique_values)}")
            
        # Vérifier s'il y a des colonnes avec seulement des 0
        only_zeros = []
        for col in y_star.columns:
            if y_star[col].sum() == 0:
                only_zeros.append(col)
        
        if only_zeros:
            print(f"\n⚠️ Colonnes avec que des 0: {only_zeros}")
        else:
            print(f"\n✅ Toutes les colonnes ont au moins un 1")
            
    except Exception as e:
        print(f"❌ Erreur lors de la construction: {e}")

if __name__ == "__main__":
    main()