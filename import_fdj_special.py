#!/usr/bin/env python3
"""
Script spécialisé pour les CSV FDJ avec format complexe
Traite les fichiers FDJ avec structure particulière 
"""

import pandas as pd
import glob
import os
from datetime import datetime
import sqlite3

def parse_fdj_csv_special_format(filepath):
    """Parse spécial pour les CSV FDJ avec format complexe"""
    print(f"🔧 Parsing spécialisé de {os.path.basename(filepath)}...")
    
    try:
        # Lire le fichier brut
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Séparer les lignes
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            print("   ⚠️ Fichier trop court")
            return []
            
        # La première ligne contient les noms de colonnes
        header_line = lines[0]
        columns = header_line.split(';')
        
        print(f"   📋 {len(columns)} colonnes détectées")
        
        # Identifier les colonnes importantes
        date_col_idx = None
        ball_cols_idx = []
        star_cols_idx = []
        
        for i, col in enumerate(columns):
            col_lower = col.lower()
            if 'date_de_tirage' in col_lower:
                date_col_idx = i
            elif col_lower.startswith('boule_'):
                ball_cols_idx.append(i)
            elif col_lower.startswith('etoile_'):
                star_cols_idx.append(i)
        
        print(f"   📅 Colonne date: {date_col_idx}")
        print(f"   🎱 Colonnes boules: {ball_cols_idx}")
        print(f"   ⭐ Colonnes étoiles: {star_cols_idx}")
        
        if date_col_idx is None or len(ball_cols_idx) != 5 or len(star_cols_idx) != 2:
            print("   ⚠️ Structure de colonnes incorrecte")
            return []
        
        # Parser les données
        draws = []
        for line_num, line in enumerate(lines[1:], 2):
            if not line.strip():
                continue
                
            values = line.split(';')
            
            # S'assurer qu'on a assez de valeurs
            if len(values) <= max(date_col_idx, max(ball_cols_idx), max(star_cols_idx)):
                continue
                
            try:
                # Parser la date
                date_str = values[date_col_idx].strip()
                
                # Format FDJ: DD/MM/YYYY
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                else:
                    continue
                
                # Parser les numéros
                balls = []
                for idx in ball_cols_idx:
                    try:
                        ball = int(values[idx].strip())
                        if 1 <= ball <= 50:
                            balls.append(ball)
                    except (ValueError, IndexError):
                        break
                
                # Parser les étoiles
                stars = []
                for idx in star_cols_idx:
                    try:
                        star = int(values[idx].strip())
                        if 1 <= star <= 12:
                            stars.append(star)
                    except (ValueError, IndexError):
                        break
                
                # Vérifier la validité
                if len(balls) == 5 and len(stars) == 2:
                    draws.append({
                        'draw_date': date_obj,
                        'numbers': balls,
                        'stars': stars
                    })
                    
            except Exception as e:
                # Ignorer les lignes problématiques
                continue
        
        print(f"   ✅ {len(draws)} tirages extraits")
        return draws
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []

def import_fdj_special_format():
    """Import avec le parsing spécialisé FDJ"""
    print("🎯 Import FDJ - Format Spécialisé")
    print("=" * 40)
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ Aucun fichier CSV trouvé")
        return
        
    print(f"📂 {len(csv_files)} fichier(s) trouvé(s)")
    
    all_draws = []
    
    for csv_file in csv_files:
        print(f"\n📁 Traitement de {csv_file}...")
        draws = parse_fdj_csv_special_format(csv_file)
        all_draws.extend(draws)
    
    if not all_draws:
        print("\n❌ Aucune donnée valide trouvée")
        return
    
    # Convertir en DataFrame et dédoublonner
    print(f"\n🔄 Consolidation de {len(all_draws)} tirages...")
    draws_df = pd.DataFrame(all_draws)
    
    # Supprimer les doublons par date
    initial_count = len(draws_df)
    draws_df = draws_df.drop_duplicates(subset=['draw_date'], keep='last')
    final_count = len(draws_df)
    
    print(f"   📊 Avant dédoublonnage: {initial_count}")
    print(f"   📊 Après dédoublonnage: {final_count}")
    
    if final_count == 0:
        print("❌ Aucune donnée unique à importer")
        return
    
    # Trier par date
    draws_df = draws_df.sort_values('draw_date')
    
    print(f"   📅 Période: {draws_df['draw_date'].min()} → {draws_df['draw_date'].max()}")
    
    # Import en base de données
    print(f"\n💾 Import en base de données...")
    
    # Supprimer les données après 2016
    conn = sqlite3.connect('data/draws.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM draws WHERE draw_date > '2016-12-31'")
    deleted_count = cursor.rowcount
    print(f"   🗑️ {deleted_count} anciennes données récentes supprimées")
    
    # Insérer les nouvelles données
    inserted = 0
    for _, row in draws_df.iterrows():
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO draws (draw_date, n1, n2, n3, n4, n5, s1, s2, jackpot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row['draw_date'].strftime('%Y-%m-%d'),
                    row['numbers'][0], row['numbers'][1], row['numbers'][2], row['numbers'][3], row['numbers'][4],
                    row['stars'][0], row['stars'][1],
                    0  # jackpot par défaut
                )
            )
            inserted += 1
        except Exception as e:
            print(f"   ⚠️ Erreur insertion: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 IMPORT TERMINÉ!")
    print(f"   📥 {inserted} nouveaux tirages importés")
    
    # Vérification finale
    from repository import EuromillionsRepository
    repo = EuromillionsRepository()
    final_df = repo.all_draws_df()
    print(f"   📊 Total en base: {len(final_df)} tirages")
    print(f"   📅 Nouvelle période complète: {final_df['draw_date'].min()} → {final_df['draw_date'].max()}")
    
    # Échantillon des nouvelles données
    print(f"\n📋 Échantillon des nouveaux tirages:")
    new_data = draws_df.tail(5)
    for _, row in new_data.iterrows():
        date_str = row['draw_date'].strftime('%Y-%m-%d')
        numbers_str = '-'.join(map(str, sorted(row['numbers'])))
        stars_str = '-'.join(map(str, sorted(row['stars'])))
        print(f"   {date_str}: {numbers_str} + ⭐ {stars_str}")

if __name__ == "__main__":
    import_fdj_special_format()