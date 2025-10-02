#!/usr/bin/env python3
"""Vérifier la distribution des étoiles 12 par période"""

from repository import EuromillionsRepository
import pandas as pd

repo = EuromillionsRepository()
df = repo.all_draws_df()

print("🔍 Analyse de la distribution des étoiles 12")
print("=" * 50)

# Compter les étoiles 12
s1_12 = (df['s1'] == 12).sum()
s2_12 = (df['s2'] == 12).sum()
total_12 = s1_12 + s2_12

print(f"📊 Étoiles 12 trouvées:")
print(f"   s1 = 12: {s1_12} fois")
print(f"   s2 = 12: {s2_12} fois") 
print(f"   Total: {total_12} fois")
print(f"   Sur {len(df)} tirages = {total_12/len(df)*100:.1f}%")

# Analyser par année
print(f"\n📅 Distribution par année:")
df['year'] = df['draw_date'].dt.year

for year in sorted(df['year'].unique()):
    year_data = df[df['year'] == year]
    year_s1_12 = (year_data['s1'] == 12).sum()
    year_s2_12 = (year_data['s2'] == 12).sum()
    year_total_12 = year_s1_12 + year_s2_12
    
    print(f"   {year}: {year_total_12:2d} étoiles 12 sur {len(year_data):3d} tirages ({year_total_12/len(year_data)*100:.1f}%)")

# Analyser quand l'étoile 12 est apparue pour la première fois
twelve_dates = df[(df['s1'] == 12) | (df['s2'] == 12)]['draw_date']
if len(twelve_dates) > 0:
    first_12 = twelve_dates.min()
    print(f"\n⭐ Première étoile 12: {first_12}")
    print(f"   Changement de règles EuroMillions: septembre 2016")
else:
    print(f"\n❌ Aucune étoile 12 trouvée!")