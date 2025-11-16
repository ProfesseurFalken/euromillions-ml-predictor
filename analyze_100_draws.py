"""
Analyse des 100 derniers tirages avec enrichissement et corrélations.
"""

from correlation_engine import build_and_analyze_enriched_dataset
from repository import get_repository
import json
from datetime import datetime

print("="*70)
print("ANALYSE DES 100 DERNIERS TIRAGES")
print("="*70)

# Charger les 100 derniers tirages
print("\n📊 Chargement des données...")
repo = get_repository()
all_draws = repo.all_draws_df()
draws_df = all_draws.tail(100)

print(f"✅ {len(draws_df)} tirages sélectionnés")
print(f"   Période: {draws_df['draw_date'].min()} à {draws_df['draw_date'].max()}")
print(f"\n⏱️  Temps estimé: ~{len(draws_df) * 6 / 60:.0f} minutes")
print("   (avec système de cache pour accélérer)")

# Lancer l'enrichissement et l'analyse
print("\n🔄 Enrichissement en cours...")
print("   Collecte: Astronomie + Météo + Géophysique")
print("   Analyse: Mathématiques + Corrélations")
print("   Les données en cache seront réutilisées\n")

start_time = datetime.now()

enriched_df, correlations = build_and_analyze_enriched_dataset(draws_df)

elapsed = (datetime.now() - start_time).total_seconds()

print("\n" + "="*70)
print("✅ ANALYSE TERMINÉE")
print("="*70)

print(f"\n⏱️  Temps écoulé: {elapsed/60:.1f} minutes")
print(f"📊 Dataset enrichi: {len(enriched_df)} lignes × {len(enriched_df.columns)} colonnes")

# Afficher les statistiques
print("\n📈 STATISTIQUES DES CORRÉLATIONS")
print("-" * 70)
print(f"Total de tests: {correlations['total_tests']}")
print(f"Corrélations significatives (p < 0.05): {correlations['significant_count']}")

if correlations['significant_count'] > 0:
    print(f"\n🎯 TOP 10 CORRÉLATIONS DÉCOUVERTES:")
    print("-" * 70)
    
    for i, corr in enumerate(correlations['significant_correlations'][:10], 1):
        ext_factor = corr['external_factor']
        draw_var = corr['draw_variable']
        pearson = corr['pearson_r']
        spearman = corr['spearman_r']
        n = corr['sample_size']
        
        # Déterminer la force de la corrélation
        max_r = max(abs(pearson), abs(spearman))
        if max_r >= 0.5:
            strength = "🔥 FORTE"
        elif max_r >= 0.3:
            strength = "⚡ MODÉRÉE"
        else:
            strength = "✨ FAIBLE"
        
        print(f"\n{i}. {strength}")
        print(f"   {ext_factor} ↔ {draw_var}")
        print(f"   Pearson: {pearson:+.3f} | Spearman: {spearman:+.3f}")
        print(f"   Échantillon: {n} tirages")
else:
    print("\n⚠️  Aucune corrélation significative trouvée (p < 0.05)")
    print("   Cela suggère que les facteurs externes testés")
    print("   n'ont pas d'influence détectable sur les tirages.")

# Afficher quelques statistiques du dataset enrichi
print("\n📊 APERÇU DES DONNÉES ENRICHIES")
print("-" * 70)

# Statistiques des variables externes
if 'moon_phase_pct' in enriched_df.columns:
    moon_valid = enriched_df['moon_phase_pct'].notna().sum()
    if moon_valid > 0:
        print(f"🌙 Phase lunaire: {moon_valid}/{len(enriched_df)} données valides")
        print(f"   Moyenne: {enriched_df['moon_phase_pct'].mean():.1f}%")

if 'temperature_c' in enriched_df.columns:
    temp_valid = enriched_df['temperature_c'].notna().sum()
    if temp_valid > 0:
        print(f"🌡️  Température: {temp_valid}/{len(enriched_df)} données valides")
        print(f"   Moyenne: {enriched_df['temperature_c'].mean():.1f}°C")
        print(f"   Min/Max: {enriched_df['temperature_c'].min():.1f}°C / {enriched_df['temperature_c'].max():.1f}°C")

if 'pressure_hpa' in enriched_df.columns:
    press_valid = enriched_df['pressure_hpa'].notna().sum()
    if press_valid > 0:
        print(f"💨 Pression: {press_valid}/{len(enriched_df)} données valides")
        print(f"   Moyenne: {enriched_df['pressure_hpa'].mean():.1f} hPa")

if 'kp_index' in enriched_df.columns:
    kp_valid = enriched_df['kp_index'].notna().sum()
    print(f"⚡ Indice Kp: {kp_valid}/{len(enriched_df)} données valides")
    if kp_valid > 0:
        print(f"   Moyenne: {enriched_df['kp_index'].mean():.2f}")

# Statistiques mathématiques
print(f"\n🔢 Propriétés mathématiques:")
print(f"   Somme moyenne: {enriched_df['sum_numbers'].mean():.1f}")
print(f"   Nombres premiers moyens: {enriched_df['prime_count'].mean():.2f}/5")
print(f"   Fibonacci moyens: {enriched_df['fibonacci_count'].mean():.2f}/5")

print("\n📁 FICHIERS GÉNÉRÉS")
print("-" * 70)
print("✅ data/correlations/enriched_draws.csv")
print("   → Dataset complet avec toutes les variables")
print("✅ data/correlations/correlations.json")
print("   → Résultats détaillés des corrélations")

print("\n💡 PROCHAINES ÉTAPES")
print("-" * 70)
print("1. Examiner les corrélations dans correlations.json")
print("2. Ouvrir enriched_draws.csv dans Excel/LibreOffice")
print("3. Créer des visualisations des patterns découverts")
print("4. Si des corrélations intéressantes: analyser l'historique complet")

print("\n" + "="*70)
print("🎓 INTERPRÉTATION SCIENTIFIQUE")
print("="*70)
print("""
Rappel important:
- Une corrélation significative (p < 0.05) ne signifie pas causalité
- Avec ~40 tests, ~2 seront significatifs par hasard (5%)
- Les tirages EuroMillions sont conçus pour être aléatoires
- Ce système est à but éducatif et de recherche

Si aucune corrélation forte n'est trouvée:
✅ C'est le résultat attendu scientifiquement
✅ Cela confirme la qualité du système de tirage
✅ Le projet reste excellent pour apprendre la data science
""")

print("="*70)
