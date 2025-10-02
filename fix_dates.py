#!/usr/bin/env python3
"""
Correction des dates et réimport des données
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def fix_dates_and_reimport():
    """Corriger les dates et réimporter les données."""
    print('🔧 Correction des dates et réimport des données')
    print('=' * 50)
    
    try:
        from repository import get_repository
        from hybrid_scraper import hybrid_scrape_latest
        import sqlite3
        from config import get_settings
        
        # 1. Vider la base (pour recommencer proprement)
        print('🗑️ Nettoyage de la base...')
        settings = get_settings()
        db_path = settings.storage_path / 'draws.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM draws')
        conn.commit()
        conn.close()
        
        print('   ✅ Base nettoyée')
        
        # 2. Récupérer les données avec le nouveau système
        print('🕷️ Récupération des données avec gestion des dates corrigée...')
        repo = get_repository()
        
        # Récupérer un nombre raisonnable de tirages
        real_draws = hybrid_scrape_latest(limit=50)
        
        if real_draws:
            print(f'   ✅ {len(real_draws)} tirages récupérés')
            
            # Afficher quelques exemples pour vérifier les formats
            print('🔍 Vérification des formats de dates:')
            for i, draw in enumerate(real_draws[:3]):
                draw_date = draw.get('draw_date', 'N/A')
                print(f'   Draw {i+1}: date="{draw_date}" (type: {type(draw_date).__name__})')
            
            # 3. Insérer avec le repository corrigé
            print('💾 Insertion avec repository corrigé...')
            result = repo.upsert_draws(real_draws)
            
            print(f'   ✅ {result["inserted"]} tirages insérés')
            print(f'   ✅ {result["updated"]} tirages mis à jour')
            
            if result.get("errors", 0) > 0:
                print(f'   ⚠️ {result["errors"]} erreurs')
            
            # 4. Vérifier le résultat final
            print('🔍 Vérification finale:')
            df = repo.all_draws_df()
            
            if not df.empty:
                print(f'   📊 {len(df)} tirages dans la base')
                print(f'   📅 Dates: {df["draw_date"].min().date()} à {df["draw_date"].max().date()}')
                
                print('   🔄 Derniers tirages:')
                recent = df.sort_values('draw_date', ascending=False).head(3)
                
                for _, row in recent.iterrows():
                    date = row['draw_date'].strftime('%Y-%m-%d')
                    balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
                    stars = f"{row['s1']:02d}-{row['s2']:02d}"
                    print(f'      {date}: {balls} | ⭐ {stars}')
                
                print('\n🎉 SUCCÈS! Les dates sont maintenant correctement gérées!')
            else:
                print('   ❌ Aucune donnée dans la base après import')
                
        else:
            print('❌ Impossible de récupérer les données')
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_dates_and_reimport()