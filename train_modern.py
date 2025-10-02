#!/usr/bin/env python3
"""Entraîner uniquement sur les données post-2016 avec 12 étoiles"""

import sys
import pandas as pd
from repository import EuromillionsRepository
from train_models import ModelTrainer

def train_modern_rules():
    print("🤖 Entraînement sur données modernes (post-2016)")
    print("=" * 50)
    
    # Charger les données
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    print(f"📊 Total des tirages: {len(df)}")
    print(f"📅 Période complète: {df['draw_date'].min()} → {df['draw_date'].max()}")
    
    # Filtrer pour ne garder que les données post-2016 (règles modernes)
    cutoff_date = '2016-09-27'  # Date du changement de règles
    modern_df = df[df['draw_date'] >= cutoff_date].copy()
    
    print(f"\n🔄 Données modernes (après {cutoff_date}):")
    print(f"   📊 {len(modern_df)} tirages")
    print(f"   📅 Période: {modern_df['draw_date'].min()} → {modern_df['draw_date'].max()}")
    
    # Vérifier les étoiles
    all_stars = []
    for col in ['s1', 's2']:
        all_stars.extend(modern_df[col].tolist())
    
    star_min, star_max = min(all_stars), max(all_stars)
    print(f"   ⭐ Étoiles: {star_min} à {star_max}")
    
    if len(modern_df) < 300:
        print(f"\n❌ Pas assez de données modernes ({len(modern_df)} < 300)")
        print("💡 Continuons avec toutes les données mais adaptons le modèle")
        return train_adaptive_model()
    
    # Créer un fichier temporaire avec les données modernes
    temp_db_path = 'data/draws_modern.db'
    
    import sqlite3
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    # Créer la table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draws (
            draw_id INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            n1 INTEGER NOT NULL,
            n2 INTEGER NOT NULL,
            n3 INTEGER NOT NULL,
            n4 INTEGER NOT NULL,
            n5 INTEGER NOT NULL,
            s1 INTEGER NOT NULL,
            s2 INTEGER NOT NULL,
            jackpot REAL DEFAULT 0,
            prize_table_json TEXT,
            raw_html TEXT,
            prize_table TEXT
        )
    ''')
    
    # Insérer les données modernes
    for _, row in modern_df.iterrows():
        cursor.execute(
            "INSERT OR REPLACE INTO draws (draw_date, n1, n2, n3, n4, n5, s1, s2, jackpot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row['draw_date'].strftime('%Y-%m-%d'),
                int(row['n1']), int(row['n2']), int(row['n3']), int(row['n4']), int(row['n5']),
                int(row['s1']), int(row['s2']),
                0
            )
        )
    
    conn.commit()
    conn.close()
    
    print(f"\n🤖 Entraînement avec {len(modern_df)} tirages modernes...")
    
    # Utiliser le trainer avec la base temporaire
    from train_models import train_latest
    
    # Sauvegarder la config actuelle
    import config
    original_db = config.get_settings().db_url
    
    try:
        # Changer temporairement vers la DB moderne
        config.get_settings().db_url = f"sqlite:///{temp_db_path}"
        
        # Entraîner
        result = train_latest(min_rows=200)  # Réduire le minimum pour les données modernes
        
        print(f"\n🎉 Entraînement terminé!")
        print(f"   🎱 Modèle numéros: {result.get('main_log_loss', 'N/A')}")
        print(f"   ⭐ Modèle étoiles: {result.get('star_log_loss', 'N/A')}")
        
    finally:
        # Restaurer la config originale
        config.get_settings().db_url = original_db
        
        # Nettoyer
        import os
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    
    return result

def train_adaptive_model():
    """Modèle adaptatif qui gère les deux périodes"""
    print("\n🔄 Mode adaptatif: données mixtes 11/12 étoiles")
    
    # Pour l'instant, utilisons seulement les données post-2016
    # On peut améliorer plus tard pour combiner les deux périodes
    
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    # Prendre seulement post-2016 pour éviter les problèmes
    modern_df = df[df['draw_date'] >= '2016-09-27'].copy()
    
    print(f"📊 Utilisation de {len(modern_df)} tirages modernes")
    
    if len(modern_df) >= 300:
        return train_modern_rules()
    else:
        print("❌ Pas assez de données pour un entraînement fiable")
        return None

if __name__ == "__main__":
    train_modern_rules()