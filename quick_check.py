#!/usr/bin/env python3
"""
Vérification simple des tirages
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def quick_check():
    """Vérification rapide."""
    from repository import get_repository
    
    repo = get_repository()
    df = repo.all_draws_df()
    
    print(f'📊 Total tirages: {len(df)}')
    
    if not df.empty:
        print('🔍 Derniers tirages:')
        recent = df.sort_values('draw_date', ascending=False).head(5)
        
        for idx, row in recent.iterrows():
            # Vérification des dates nulles
            if pd.isna(row['draw_date']):
                print(f'   Date manquante: n={row["n1"]}-{row["n2"]}-{row["n3"]}-{row["n4"]}-{row["n5"]} | s={row["s1"]}-{row["s2"]}')
            else:
                date_str = row['draw_date'].strftime('%Y-%m-%d')
                print(f'   {date_str}: {row["n1"]:02d}-{row["n2"]:02d}-{row["n3"]:02d}-{row["n4"]:02d}-{row["n5"]:02d} | ⭐ {row["s1"]:02d}-{row["s2"]:02d}')

if __name__ == "__main__":
    import pandas as pd
    quick_check()