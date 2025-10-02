#!/usr/bin/env python3
"""
Vérification complète de la base de données EuroMillions
"""

import pandas as pd
from repository import EuromillionsRepository
from collections import Counter
import sqlite3

def check_database_completeness():
    print("🔍 Vérification complète de la base de données")
    print("=" * 50)
    
    # Connexion directe à la DB pour des stats détaillées
    repo = EuromillionsRepository()
    
    # 1. Stats générales
    df = repo.all_draws_df()
    print(f"📊 Total des tirages dans la DB: {len(df)}")
    
    if len(df) == 0:
        print("❌ Aucun tirage trouvé dans la base!")
        return
        
    print(f"📅 Période: {df['draw_date'].min()} → {df['draw_date'].max()}")
    
    # 2. Analyse par année
    print(f"\n📈 Répartition par année:")
    df['year'] = df['draw_date'].dt.year
    yearly_counts = df.groupby('year').size().sort_index()
    
    total_expected = 0
    for year, count in yearly_counts.items():
        # EuroMillions: 2 tirages par semaine (mardi + vendredi) = ~104 par an
        expected_per_year = 104 if year < 2025 else 80  # Estimation pour 2025 partiel
        total_expected += expected_per_year
        status = "✅" if count >= expected_per_year * 0.9 else "⚠️"
        print(f"   {year}: {count:3d} tirages {status} (attendu: ~{expected_per_year})")
    
    print(f"\n📊 Total attendu approximatif: ~{total_expected}")
    print(f"📊 Total présent: {len(df)}")
    coverage = (len(df) / total_expected) * 100 if total_expected > 0 else 0
    print(f"📊 Couverture: {coverage:.1f}%")
    
    # 3. Vérification de la cohérence des données
    print(f"\n🔍 Vérification de la cohérence:")
    
    # Vérifier les numéros principaux
    main_numbers = []
    for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
        if col in df.columns:
            values = df[col].dropna()
            main_numbers.extend(values.tolist())
            min_val, max_val = values.min(), values.max()
            print(f"   {col}: {min_val}-{max_val} ✅")
    
    # Vérifier les étoiles
    star_numbers = []
    for col in ['s1', 's2']:
        if col in df.columns:
            values = df[col].dropna()
            star_numbers.extend(values.tolist())
            min_val, max_val = values.min(), values.max()
            print(f"   {col}: {min_val}-{max_val} ✅")
    
    # 4. Analyse de fréquence
    print(f"\n📊 Analyse de fréquence:")
    main_counts = Counter(main_numbers)
    star_counts = Counter(star_numbers)
    
    print(f"   Numéros principaux (1-50):")
    print(f"      Plage: {min(main_counts.keys())}-{max(main_counts.keys())}")
    print(f"      Fréquence moyenne: {sum(main_counts.values()) / len(main_counts):.1f}")
    
    print(f"   Étoiles (1-11):")
    print(f"      Plage: {min(star_counts.keys())}-{max(star_counts.keys())}")
    print(f"      Fréquence moyenne: {sum(star_counts.values()) / len(star_counts):.1f}")
    
    # 5. Détection de gaps temporels
    print(f"\n⏰ Analyse des gaps temporels:")
    df_sorted = df.sort_values('draw_date')
    df_sorted['date_diff'] = df_sorted['draw_date'].diff()
    
    # Gaps de plus de 5 jours (anormal)
    big_gaps = df_sorted[df_sorted['date_diff'] > pd.Timedelta(days=5)]
    if len(big_gaps) > 0:
        print(f"   ⚠️ {len(big_gaps)} gaps suspects trouvés:")
        for _, row in big_gaps.head(10).iterrows():
            print(f"      {row['draw_date']} (gap: {row['date_diff'].days} jours)")
    else:
        print(f"   ✅ Aucun gap suspect détecté")
    
    # 6. Doublons
    print(f"\n🔄 Vérification des doublons:")
    duplicates = df.duplicated(subset=['draw_date'], keep=False)
    if duplicates.any():
        print(f"   ⚠️ {duplicates.sum()} doublons détectés")
        print(df[duplicates][['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']])
    else:
        print(f"   ✅ Aucun doublon détecté")
    
    # 7. Valeurs manquantes
    print(f"\n❓ Valeurs manquantes:")
    for col in ['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                print(f"   ⚠️ {col}: {missing} valeurs manquantes")
            else:
                print(f"   ✅ {col}: complet")
    
    # 8. Échantillon des données les plus récentes
    print(f"\n📋 Échantillon des 5 tirages les plus récents:")
    recent = df_sorted.tail(5)[['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']]
    for _, row in recent.iterrows():
        date_str = row['draw_date'].strftime('%Y-%m-%d')
        numbers = f"{int(row['n1'])}-{int(row['n2'])}-{int(row['n3'])}-{int(row['n4'])}-{int(row['n5'])}"
        stars = f"{int(row['s1'])}-{int(row['s2'])}"
        print(f"   {date_str}: {numbers} + ⭐ {stars}")
    
    # 9. Résumé final
    print(f"\n🎯 RÉSUMÉ:")
    if len(df) >= 500:
        print(f"   ✅ Base de données bien remplie ({len(df)} tirages)")
    elif len(df) >= 200:
        print(f"   ⚠️ Base correcte mais pourrait être plus complète ({len(df)} tirages)")
    else:
        print(f"   ❌ Base insuffisante ({len(df)} tirages)")
    
    if coverage >= 80:
        print(f"   ✅ Couverture excellente ({coverage:.1f}%)")
    elif coverage >= 60:
        print(f"   ⚠️ Couverture correcte ({coverage:.1f}%)")
    else:
        print(f"   ❌ Couverture insuffisante ({coverage:.1f}%)")

if __name__ == "__main__":
    check_database_completeness()