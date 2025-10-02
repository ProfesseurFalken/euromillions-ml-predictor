#!/usr/bin/env python3
"""
Nettoyage automatique des dates futures
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def auto_clean():
    """Nettoyage automatique."""
    from repository import get_repository
    import sqlite3
    from config import get_settings
    from datetime import datetime

    print("🧹 Nettoyage automatique des dates futures...")

    # Supprimer les dates futures
    repo = get_repository()
    settings = get_settings()
    db_path = settings.storage_path / 'draws.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    today = datetime.now().date().isoformat()
    cursor.execute('DELETE FROM draws WHERE DATE(draw_date) > DATE(?)', (today,))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(f'✅ {deleted} tirages avec dates futures supprimés')

    # Vérifier le résultat
    df = repo.all_draws_df()
    print(f'📊 Tirages restants: {len(df)}')
    if not df.empty:
        min_date = df['draw_date'].min().date()
        max_date = df['draw_date'].max().date()
        print(f'📅 Plage de dates: {min_date} à {max_date}')

if __name__ == "__main__":
    auto_clean()