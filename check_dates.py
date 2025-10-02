#!/usr/bin/env python3
"""
Script pour vérifier les dates dans la base de données
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

def check_database_dates():
    """Vérifier les dates stockées dans la base."""
    print("🔍 Vérification des dates dans la base de données")
    print("=" * 55)
    
    try:
        from repository import get_repository
        
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            print("❌ Aucune donnée trouvée dans la base")
            return
        
        print(f"📊 Nombre de tirages: {len(df)}")
        print(f"📅 Date min: {df['draw_date'].min()}")
        print(f"📅 Date max: {df['draw_date'].max()}")
        
        print(f"\n📋 Échantillon des 10 derniers tirages:")
        print("-" * 70)
        
        # Trier par date décroissante et prendre les 10 derniers
        recent = df.sort_values('draw_date', ascending=False).head(10)
        
        for idx, row in recent.iterrows():
            date_str = row['draw_date'].strftime('%Y-%m-%d')
            balls = f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}"
            stars = f"{row['s1']:02d}-{row['s2']:02d}"
            print(f"{date_str}  |  {balls}  |  {stars}")
        
        print("-" * 70)
        
        # Vérifier s'il y a des dates futures
        from datetime import datetime
        today = datetime.now().date()
        future_dates = df[df['draw_date'] > today]
        
        if not future_dates.empty:
            print(f"\n⚠️  PROBLÈME DÉTECTÉ: {len(future_dates)} tirages avec des dates futures!")
            print("📅 Dates futures trouvées:")
            for idx, row in future_dates.head(5).iterrows():
                print(f"   - {row['draw_date'].strftime('%Y-%m-%d')}")
        else:
            print(f"\n✅ Toutes les dates sont cohérentes (≤ {today})")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_dates()