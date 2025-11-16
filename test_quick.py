"""
Script de test rapide pour vérifier les données et tester le système avancé.
"""

from repository import get_repository
from correlation_engine import MultiSourceCorrelator
from analyzers.number_theory import analyze_draw_number_theory
from collectors import get_astronomical_data, get_weather_data, get_geophysical_data
from datetime import datetime
import pandas as pd

print("="*70)
print("TEST COMPLET DU SYSTÈME AVANCÉ")
print("="*70)

# 1. Vérifier les données disponibles
print("\n1️⃣ Vérification des données...")
repo = get_repository()
draws_df = repo.all_draws_df()

if len(draws_df) == 0:
    print("❌ Aucun tirage dans la base de données")
    print("   Lancez d'abord: python build_datasets.py")
    exit(1)

print(f"✅ {len(draws_df)} tirages disponibles")
print(f"   Période: {draws_df['draw_date'].min()} à {draws_df['draw_date'].max()}")

# 2. Tester les collecteurs avec un tirage récent
print("\n2️⃣ Test des collecteurs avec un tirage récent...")
recent_draw = draws_df.iloc[-1]
test_date = pd.to_datetime(recent_draw['draw_date'])
if test_date.hour == 0:
    test_date = test_date.replace(hour=21, minute=5)

print(f"   Date: {test_date.strftime('%d/%m/%Y %H:%M')}")
print(f"   Numéros: {int(recent_draw['n1'])}, {int(recent_draw['n2'])}, {int(recent_draw['n3'])}, {int(recent_draw['n4'])}, {int(recent_draw['n5'])}")
print(f"   Étoiles: {int(recent_draw['s1'])}, {int(recent_draw['s2'])}")

# Test astronomie
print("\n   🌙 Astronomie...")
try:
    astro = get_astronomical_data(test_date)
    print(f"      ✅ Phase: {astro['moon']['phase_name']}, {astro['moon']['illumination']:.1f}%")
except Exception as e:
    print(f"      ⚠️ Erreur: {e}")

# Test météo
print("   🌡️ Météo...")
try:
    weather = get_weather_data(test_date)
    w = weather['weather']
    print(f"      ✅ {w.get('temperature_celsius', 'N/A')}°C, {w.get('humidity_percent', 'N/A')}%, {w.get('pressure_hpa', 'N/A')} hPa")
except Exception as e:
    print(f"      ⚠️ Erreur: {e}")

# Test géophysique
print("   🌍 Géophysique...")
try:
    geo = get_geophysical_data(test_date)
    print(f"      ✅ Kp: {geo['geomagnetic'].get('kp_average', 'N/A')}")
except Exception as e:
    print(f"      ⚠️ Erreur: {e}")

# 3. Analyse mathématique
print("\n3️⃣ Analyse mathématique du tirage...")
numbers = [int(recent_draw['n1']), int(recent_draw['n2']), int(recent_draw['n3']), 
           int(recent_draw['n4']), int(recent_draw['n5'])]
stars = [int(recent_draw['s1']), int(recent_draw['s2'])]

try:
    math_analysis = analyze_draw_number_theory(numbers, stars)
    print(f"   🔢 Nombres premiers: {math_analysis['primes']['count']}/5")
    print(f"   🔢 Fibonacci: {math_analysis['fibonacci']['count']}/5")
    print(f"   🔢 Somme: {math_analysis['sums_products']['sum_numbers']}")
    print(f"   🔢 Parité: {math_analysis['parity']['even_count']} pairs, {math_analysis['parity']['odd_count']} impairs")
except Exception as e:
    print(f"   ⚠️ Erreur: {e}")

# 4. Test enrichissement (petit échantillon)
print("\n4️⃣ Test d'enrichissement (5 derniers tirages)...")
sample_df = draws_df.tail(5).copy()

try:
    correlator = MultiSourceCorrelator()
    enriched_df = correlator.build_enriched_dataset(sample_df)
    print(f"   ✅ Dataset enrichi: {len(enriched_df)} lignes, {len(enriched_df.columns)} colonnes")
    
    # Afficher un aperçu
    print("\n   📊 Aperçu des données enrichies:")
    print(f"      Colonnes: {', '.join(enriched_df.columns[:10])}...")
    
except Exception as e:
    print(f"   ⚠️ Erreur: {e}")
    import traceback
    traceback.print_exc()

# 5. Proposer l'analyse complète
print("\n" + "="*70)
print("✅ TESTS TERMINÉS")
print("="*70)

print(f"\n💡 Vous avez {len(draws_df)} tirages dans votre base.")
print("   Pour une analyse complète avec corrélations:")
print("   1. Cela prendra environ 5-7 secondes par tirage")
print(f"   2. Temps estimé: ~{len(draws_df) * 6 / 60:.0f} minutes")
print("   3. Les résultats seront sauvegardés dans data/correlations/")
print("\n   Commande:")
print("   python -c \"from correlation_engine import build_and_analyze_enriched_dataset; from repository import get_repository; repo = get_repository(); df = repo.all_draws_df(); build_and_analyze_enriched_dataset(df)\"")

print("\n" + "="*70)
