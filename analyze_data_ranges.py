#!/usr/bin/env python3
"""
Analyser et adapter le système pour la plage d'étoiles détectée dans les données
"""

import pandas as pd
import numpy as np
from repository import EuromillionsRepository

def analyze_data_ranges():
    """Analyser les plages de numéros et étoiles dans les données"""
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    print("🔍 Analyse des plages de données")
    print("=" * 40)
    
    # Analyser les numéros principaux
    main_numbers = []
    for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
        if col in df.columns:
            main_numbers.extend(df[col].dropna().tolist())
    
    # Analyser les étoiles
    stars = []
    for col in ['s1', 's2']:
        if col in df.columns:
            stars.extend(df[col].dropna().tolist())
    
    main_min, main_max = min(main_numbers), max(main_numbers)
    star_min, star_max = min(stars), max(stars)
    
    print(f"📊 Numéros principaux: {main_min} à {main_max}")
    print(f"🌟 Étoiles: {star_min} à {star_max}")
    print(f"📅 Période des données: {df['draw_date'].min()} à {df['draw_date'].max()}")
    
    # Vérifier les changements de règles au fil du temps
    print("\n📈 Analyse chronologique des étoiles:")
    df_sorted = df.sort_values('draw_date')
    
    yearly_stats = []
    for year in range(2011, 2024):
        year_data = df_sorted[df_sorted['draw_date'].dt.year == year]
        if len(year_data) > 0:
            year_stars = []
            for col in ['s1', 's2']:
                year_stars.extend(year_data[col].dropna().tolist())
            
            if year_stars:
                year_min, year_max = min(year_stars), max(year_stars)
                yearly_stats.append((year, year_min, year_max, len(year_data)))
                print(f"   {year}: étoiles {year_min}-{year_max} ({len(year_data)} tirages)")
    
    # Recommandation
    print(f"\n💡 Recommandations:")
    print(f"   📊 Configurer le modèle pour {star_max} étoiles (au lieu de 12)")
    print(f"   🔧 Adapter build_datasets.py pour cette plage")
    
    return {
        'main_range': (main_min, main_max),
        'star_range': (star_min, star_max),
        'yearly_stats': yearly_stats
    }

def create_adaptive_config():
    """Créer une configuration adaptative"""
    stats = analyze_data_ranges()
    star_min, star_max = stats['star_range']
    
    config_content = f'''
# Configuration adaptative générée automatiquement
MAIN_NUMBERS_MIN = 1
MAIN_NUMBERS_MAX = 50
STARS_MIN = {star_min}
STARS_MAX = {star_max}

# Calculé à partir des données réelles:
# - Numéros: {stats['main_range'][0]}-{stats['main_range'][1]}
# - Étoiles: {star_min}-{star_max}
'''
    
    print(f"\n📝 Configuration suggérée:")
    print(config_content)
    
    return stats

if __name__ == "__main__":
    create_adaptive_config()