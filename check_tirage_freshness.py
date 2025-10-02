#!/usr/bin/env python3
"""
Vérification de l'actualité des tirages EuroMillions
"""

from repository import EuromillionsRepository
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def check_tirage_freshness():
    print("🔍 Vérification de l'actualité des tirages")
    print("=" * 50)
    
    # Charger nos données actuelles
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    if len(df) == 0:
        print("❌ Aucun tirage en base")
        return
    
    # Analyser nos données
    latest_date = df['draw_date'].max()
    total_draws = len(df)
    
    print(f"📊 État de notre base :")
    print(f"   📅 Dernier tirage: {latest_date.strftime('%Y-%m-%d')} ({latest_date.strftime('%A')})")
    print(f"   📊 Total tirages: {total_draws}")
    print(f"   📈 Période: {df['draw_date'].min().strftime('%Y-%m-%d')} → {latest_date.strftime('%Y-%m-%d')}")
    
    # Calculer le décalage par rapport à aujourd'hui
    today = datetime.now().date()
    latest_date_only = latest_date.date()
    days_behind = (today - latest_date_only).days
    
    print(f"\n⏰ Analyse temporelle :")
    print(f"   📅 Aujourd'hui: {today.strftime('%Y-%m-%d')} ({today.strftime('%A')})")
    print(f"   📉 Retard: {days_behind} jours")
    
    # Estimation des tirages manqués
    # EuroMillions: mardi et vendredi = 2 par semaine
    estimated_missing = (days_behind // 7) * 2
    if days_behind % 7 >= 2:  # Si on a dépassé mardi
        estimated_missing += 1
    if days_behind % 7 >= 5:  # Si on a dépassé vendredi
        estimated_missing += 1
    
    print(f"   🎯 Tirages probablement manqués: ~{estimated_missing}")
    
    # Évaluation
    if days_behind <= 3:
        status = "✅ À JOUR"
        color = "🟢"
    elif days_behind <= 7:
        status = "⚠️ LÉGÈREMENT EN RETARD"
        color = "🟡"
    elif days_behind <= 14:
        status = "⚠️ EN RETARD"
        color = "🟠"
    else:
        status = "❌ TRÈS EN RETARD"
        color = "🔴"
    
    print(f"\n{color} STATUT: {status}")
    
    # Recommandations
    print(f"\n💡 Recommandations :")
    if days_behind <= 3:
        print(f"   ✅ Vos données sont à jour !")
    elif days_behind <= 7:
        print(f"   📥 Mise à jour recommandée sous peu")
    else:
        print(f"   🚨 Mise à jour urgente recommandée")
        print(f"   📊 Il manque probablement {estimated_missing} tirages récents")
    
    # Vérifier les derniers tirages
    print(f"\n📋 Derniers tirages en base :")
    recent = df.tail(3).sort_values('draw_date', ascending=False)
    for _, row in recent.iterrows():
        date_str = row['draw_date'].strftime('%Y-%m-%d')
        day_str = row['draw_date'].strftime('%A')
        numbers = f"{int(row['n1'])}-{int(row['n2'])}-{int(row['n3'])}-{int(row['n4'])}-{int(row['n5'])}"
        stars = f"{int(row['s1'])}-{int(row['s2'])}"
        print(f"   {date_str} ({day_str}): {numbers} + ⭐ {stars}")
    
    return {
        'latest_date': latest_date,
        'days_behind': days_behind,
        'estimated_missing': estimated_missing,
        'status': status,
        'total_draws': total_draws
    }

def check_official_source():
    """Essayer de vérifier contre une source officielle"""
    print(f"\n🌐 Vérification contre source officielle :")
    
    try:
        # Tenter de récupérer le dernier tirage depuis FDJ
        url = "https://www.fdj.fr/jeux/jeux-de-tirage/euromillions"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"   🔍 Vérification sur FDJ.fr...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Connexion réussie à FDJ.fr")
            print(f"   💡 Pour une vérification précise, consultez manuellement:")
            print(f"      📱 https://www.fdj.fr/jeux/jeux-de-tirage/euromillions")
            print(f"      📱 https://www.euro-millions.com/fr/resultats")
        else:
            print(f"   ⚠️ Impossible de se connecter à FDJ.fr ({response.status_code})")
            
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {str(e)[:100]}...")
    
    print(f"\n🔍 Sources officielles à vérifier manuellement :")
    print(f"   🇫🇷 FDJ: https://www.fdj.fr/jeux/jeux-de-tirage/euromillions")
    print(f"   🇪🇺 Euro-Millions: https://www.euro-millions.com/fr/resultats")
    print(f"   🇬🇧 UK National Lottery: https://www.national-lottery.co.uk/results/euromillions")

if __name__ == "__main__":
    result = check_tirage_freshness()
    check_official_source()