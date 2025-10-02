#!/usr/bin/env python3
"""
Script d'import avancé pour les nouveaux CSV FDJ 
Détecte automatiquement le format et gère les différentes périodes
"""

import pandas as pd
import glob
import os
from datetime import datetime
from repository import EuromillionsRepository

def detect_csv_format(filepath):
    """Analyse un CSV pour détecter son format"""
    print(f"🔍 Analyse de {os.path.basename(filepath)}...")
    
    try:
        # Essayer différents encodages et séparateurs
        sample = None
        for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
            for sep in [',', ';', '\t']:
                try:
                    sample = pd.read_csv(filepath, nrows=5, encoding=encoding, sep=sep)
                    print(f"   ✅ Encodage: {encoding}, Séparateur: '{sep}'")
                    break
                except:
                    continue
            if sample is not None:
                break
        
        if sample is None:
            raise Exception("Impossible de lire le fichier avec les encodages testés")
        
        print(f"   📋 Colonnes: {list(sample.columns)}")
        print(f"   📊 {len(pd.read_csv(filepath))} lignes totales")
        
        # Détecter les colonnes de date
        date_cols = [col for col in sample.columns if any(keyword in col.lower() 
                    for keyword in ['date', 'tirage', 'jour'])]
        print(f"   📅 Colonnes de date: {date_cols}")
        
        # Détecter les colonnes de numéros
        number_cols = [col for col in sample.columns if any(keyword in col.lower() 
                      for keyword in ['boule', 'numero', 'n1', 'n2', 'n3', 'n4', 'n5'])]
        print(f"   🎱 Colonnes numéros: {number_cols}")
        
        # Détecter les colonnes d'étoiles  
        star_cols = [col for col in sample.columns if any(keyword in col.lower() 
                    for keyword in ['etoile', 'star', 'lucky'])]
        print(f"   ⭐ Colonnes étoiles: {star_cols}")
        
        # Analyser les valeurs des étoiles pour détecter la plage
        if star_cols:
            all_stars = []
            df_full = pd.read_csv(filepath)
            for col in star_cols:
                stars = df_full[col].dropna().unique()
                all_stars.extend(stars)
            
            if all_stars:
                star_range = f"{min(all_stars)}-{max(all_stars)}"
                print(f"   📊 Plage étoiles: {star_range}")
                
                # Déterminer la période des règles
                if max(all_stars) == 11:
                    print(f"   ⚡ Format: Ancien (étoiles 1-11)")
                elif max(all_stars) == 12:
                    print(f"   ⚡ Format: Nouveau (étoiles 1-12)")
        
        return {
            'columns': list(sample.columns),
            'rows': len(pd.read_csv(filepath)),
            'date_cols': date_cols,
            'number_cols': number_cols,
            'star_cols': star_cols
        }
        
    except Exception as e:
        print(f"   ❌ Erreur d'analyse: {e}")
        return None

def import_new_csv_files():
    """Import tous les nouveaux CSV trouvés"""
    print("🎯 Import des nouveaux CSV FDJ")
    print("=" * 40)
    
    # Chercher tous les CSV
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ Aucun fichier CSV trouvé dans le répertoire")
        print("💡 Placez vos fichiers CSV FDJ dans ce dossier et relancez")
        return
    
    print(f"📂 {len(csv_files)} fichier(s) CSV trouvé(s):")
    for f in csv_files:
        print(f"   • {f}")
    
    # Analyser chaque fichier
    all_data = []
    for csv_file in csv_files:
        print(f"\n" + "="*50)
        format_info = detect_csv_format(csv_file)
        
        if format_info is None:
            print(f"⚠️ Fichier {csv_file} ignoré (erreur d'analyse)")
            continue
            
        # Demander confirmation pour chaque fichier
        print(f"\n❓ Importer {csv_file} ? (o/n)")
        # Pour l'automatisation, on assume 'oui'
        response = 'o'  # input().lower().strip()
        
        if response == 'o':
            try:
                # Utiliser les mêmes paramètres que pour l'analyse
                df = None
                for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
                    for sep in [',', ';', '\t']:
                        try:
                            df = pd.read_csv(csv_file, encoding=encoding, sep=sep)
                            break
                        except:
                            continue
                    if df is not None:
                        break
                        
                if df is not None:
                    all_data.append((csv_file, df, format_info))
                    print(f"✅ {csv_file} chargé ({len(df)} lignes)")
                else:
                    print(f"❌ Impossible de lire {csv_file}")
            except Exception as e:
                print(f"❌ Erreur de lecture de {csv_file}: {e}")
    
    if not all_data:
        print("\n❌ Aucun fichier valide à importer")
        return
    
    # Consolider et normaliser toutes les données
    print(f"\n🔄 Consolidation de {len(all_data)} fichier(s)...")
    
    normalized_draws = []
    
    for filename, df, format_info in all_data:
        print(f"\n📊 Traitement de {filename}...")
        
        # Normaliser chaque fichier selon son format
        draws = normalize_csv_data(df, format_info, filename)
        normalized_draws.extend(draws)
        print(f"   ✅ {len(draws)} tirages normalisés")
    
    # Supprimer les doublons par date
    draws_df = pd.DataFrame(normalized_draws)
    if not draws_df.empty:
        initial_count = len(draws_df)
        draws_df = draws_df.drop_duplicates(subset=['draw_date'], keep='last')
        final_count = len(draws_df)
        
        print(f"\n📦 Consolidation finale:")
        print(f"   📊 Total avant dédoublonnage: {initial_count}")
        print(f"   📊 Total après dédoublonnage: {final_count}")
        
        if final_count > 0:
            # Import en base
            repo = EuromillionsRepository()
            
            print(f"\n💾 Import en base de données...")
            print(f"🗑️ Suppression des données existantes récentes...")
            
            # Supprimer les données après 2016 pour éviter les conflits
            import sqlite3
            conn = sqlite3.connect('data/draws.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM draws WHERE draw_date > '2016-12-31'")
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"   ✅ {deleted_count} anciennes données récentes supprimées")
            
            # Insérer les nouvelles données
            inserted = 0
            conn = sqlite3.connect('data/draws.db')
            cursor = conn.cursor()
            
            for _, row in draws_df.iterrows():
                try:
                    cursor.execute(
                        "INSERT OR REPLACE INTO draws (draw_date, n1, n2, n3, n4, n5, s1, s2, jackpot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            row['draw_date'].strftime('%Y-%m-%d'),
                            row['numbers'][0], row['numbers'][1], row['numbers'][2], row['numbers'][3], row['numbers'][4],
                            row['stars'][0], row['stars'][1],
                            row.get('jackpot', 0)
                        )
                    )
                    inserted += 1
                except Exception as e:
                    print(f"   ⚠️ Erreur d'insertion: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"\n🎉 IMPORT TERMINÉ!")
            print(f"   📥 {inserted} nouveaux tirages importés")
            
            # Vérifier le résultat final
            final_df = repo.all_draws_df()
            print(f"   📊 Total en base: {len(final_df)} tirages")
            print(f"   📅 Nouvelle période: {final_df['draw_date'].min()} → {final_df['draw_date'].max()}")
            
        else:
            print("❌ Aucune donnée valide à importer")

def normalize_csv_data(df, format_info, filename):
    """Normalise un DataFrame selon le format détecté"""
    draws = []
    
    # Identifier les bonnes colonnes
    date_col = format_info['date_cols'][0] if format_info['date_cols'] else None
    star_cols = format_info['star_cols']
    
    if not date_col:
        print(f"   ⚠️ Aucune colonne de date trouvée dans {filename}")
        return draws
    
    for _, row in df.iterrows():
        try:
            # Parser la date
            date_str = str(row[date_col])
            
            # Essayer différents formats de date
            date_obj = None
            for fmt in ['%Y%m%d', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if date_obj is None:
                continue
            
            # Extraire les numéros principaux
            numbers = []
            for i in range(1, 6):  # boule_1 à boule_5
                col_names = [f'boule_{i}', f'n{i}', f'numero_{i}']
                for col_name in col_names:
                    if col_name in row.index:
                        numbers.append(int(row[col_name]))
                        break
            
            # Extraire les étoiles
            stars = []
            for i in range(1, 3):  # etoile_1 à etoile_2
                col_names = [f'etoile_{i}', f'star_{i}', f'lucky_star_{i}']
                for col_name in col_names:
                    if col_name in row.index:
                        stars.append(int(row[col_name]))
                        break
            
            # Vérifier la validité
            if len(numbers) == 5 and len(stars) == 2:
                if all(1 <= n <= 50 for n in numbers) and all(1 <= s <= 12 for s in stars):
                    draws.append({
                        'draw_date': date_obj,
                        'numbers': numbers,
                        'stars': stars,
                        'jackpot': 0
                    })
            
        except Exception as e:
            # Ignorer les lignes problématiques
            continue
    
    return draws

if __name__ == "__main__":
    import_new_csv_files()