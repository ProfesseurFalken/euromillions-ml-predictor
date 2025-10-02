#!/usr/bin/env python3
"""
Script pour nettoyer les dates futures incorrectes dans la base de données
"""

import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

def clean_future_dates():
    """Supprimer les tirages avec des dates futures."""
    print("🧹 Nettoyage des dates futures dans la base de données")
    print("=" * 60)
    
    try:
        from repository import get_repository
        
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            print("❌ Aucune donnée trouvée dans la base")
            return
        
        print(f"📊 Nombre total de tirages: {len(df)}")
        
        # Date limite (aujourd'hui)
        today = datetime.now().date()
        print(f"📅 Date limite: {today}")
        
        # Convertir draw_date en date pour comparaison
        df['draw_date_only'] = df['draw_date'].dt.date
        
        # Identifier les dates futures
        future_mask = df['draw_date_only'] > today
        future_draws = df[future_mask]
        valid_draws = df[~future_mask]
        
        print(f"⚠️  Tirages avec dates futures: {len(future_draws)}")
        print(f"✅ Tirages avec dates valides: {len(valid_draws)}")
        
        if len(future_draws) > 0:
            print(f"\n🗑️  Dates futures à supprimer:")
            for idx, row in future_draws.head(10).iterrows():
                date_str = row['draw_date'].strftime('%Y-%m-%d')
                print(f"   - {date_str}")
            
            if len(future_draws) > 10:
                print(f"   ... et {len(future_draws) - 10} autres")
            
            # Confirmer la suppression
            response = input(f"\n❓ Supprimer {len(future_draws)} tirages avec dates futures? (y/N): ")
            
            if response.lower() in ['y', 'yes', 'oui']:
                # Supprimer de la base de données
                import sqlite3
                from config import get_settings
                
                settings = get_settings()
                db_path = settings.storage_path / "draws.db"
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Supprimer les tirages futurs
                future_dates = [row['draw_date'].strftime('%Y-%m-%d') for _, row in future_draws.iterrows()]
                placeholders = ','.join(['?' for _ in future_dates])
                
                query = f"DELETE FROM draws WHERE DATE(draw_date) > DATE(?)"
                cursor.execute(query, (today.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                print(f"✅ {deleted_count} tirages supprimés avec succès!")
                
                # Vérification après nettoyage
                df_cleaned = repo.all_draws_df()
                print(f"📊 Tirages restants: {len(df_cleaned)}")
                
                if not df_cleaned.empty:
                    print(f"📅 Nouvelle plage de dates: {df_cleaned['draw_date'].min().date()} à {df_cleaned['draw_date'].max().date()}")
                
            else:
                print("❌ Suppression annulée")
        else:
            print("✅ Aucune date future trouvée - base de données propre!")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_future_dates()