#!/usr/bin/env python3
"""
Vérifier les derniers tirages dans la base
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def check_recent_draws():
    """Vérifier les derniers tirages."""
    from repository import get_repository
    
    repo = get_repository()
    df = repo.all_draws_df()
    
    print('🔍 Derniers tirages dans la base:')
    print('=' * 40)
    
    recent = df.sort_values('draw_date', ascending=False).head(5)
    
    for _, row in recent.iterrows():
        date = row['draw_date'].strftime('%Y-%m-%d')
        balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
        stars = f"{row['s1']:02d}-{row['s2']:02d}"
        print(f'{date}: {balls} | ⭐ {stars}')
    
    print('=' * 40)
    
    # Vérifier si on a le tirage du 27/09/2025
    target_date = '2025-09-27'
    has_target = df[df['draw_date'].dt.strftime('%Y-%m-%d') == target_date]
    
    if not has_target.empty:
        print(f'✅ Tirage du {target_date} trouvé:')
        row = has_target.iloc[0]
        balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
        stars = f"{row['s1']:02d}-{row['s2']:02d}"
        print(f'   {balls} | ⭐ {stars}')
    else:
        print(f'❌ Tirage du {target_date} MANQUANT!')
        print('   Le programme utilise des données de test!')

if __name__ == "__main__":
    check_recent_draws()