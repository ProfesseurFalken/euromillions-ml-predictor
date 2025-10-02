#!/usr/bin/env python3
"""
Réinitialisation complète avec les vraies données EuroMillions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def reset_with_real_data():
    """Vider la base et la remplir avec les vraies données."""
    print('🔄 Réinitialisation complète avec les vraies données')
    print('=' * 55)
    
    try:
        from repository import get_repository
        from hybrid_scraper import hybrid_scrape_latest
        import sqlite3
        from config import get_settings
        
        # 1. Vider complètement la base
        print('🗑️ Suppression des anciennes données...')
        settings = get_settings()
        db_path = settings.storage_path / 'draws.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM draws')
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f'   ✅ {deleted} anciennes entrées supprimées')
        
        # 2. Récupérer les vraies données
        print('🕷️ Récupération des vraies données...')
        repo = get_repository()
        
        # Récupérer les 100 derniers tirages réels
        real_draws = hybrid_scrape_latest(limit=100)
        
        if real_draws:
            print(f'   ✅ {len(real_draws)} vrais tirages récupérés')
            
            # 3. Insérer dans la base
            print('💾 Insertion dans la base de données...')
            result = repo.upsert_draws(real_draws)
            
            print(f'   ✅ {result["inserted"]} tirages insérés')
            print(f'   ✅ {result["updated"]} tirages mis à jour')
            print(f'   ⚠️ {result["skipped"]} tirages ignorés')
            
            # 4. Vérifier les derniers tirages
            print('🔍 Vérification des derniers tirages:')
            df = repo.all_draws_df()
            recent = df.sort_values('draw_date', ascending=False).head(5)
            
            for _, row in recent.iterrows():
                date = row['draw_date'].strftime('%Y-%m-%d')
                balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
                stars = f"{row['s1']:02d}-{row['s2']:02d}"
                print(f'   {date}: {balls} | ⭐ {stars}')
            
            print('\n🎉 SUCCÈS! La base contient maintenant les vraies données!')
            print('   Vous pouvez maintenant utiliser le programme normalement.')
            
        else:
            print('❌ Impossible de récupérer les vraies données')
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_with_real_data()