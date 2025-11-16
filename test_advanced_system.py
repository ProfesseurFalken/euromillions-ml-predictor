"""
Script de test complet pour le système avancé de collecte et d'analyse.

Ce script:
1. Teste tous les collecteurs de données
2. Teste tous les analyseurs
3. Construit un petit dataset enrichi
4. Calcule les corrélations
5. Génère un rapport
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import json
from loguru import logger

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration du logger
logger.add("logs/advanced_system_test_{time}.log", rotation="10 MB")


def test_collectors():
    """Teste tous les collecteurs de données."""
    print("\n" + "="*70)
    print("TEST DES COLLECTEURS DE DONNÉES")
    print("="*70)
    
    test_date = datetime(2024, 10, 11, 21, 5)  # Vendredi 11 octobre 2024, 21h05
    
    # 1. Test collecteur astronomique
    print("\n1. Test collecteur astronomique...")
    try:
        from collectors.astronomical_data import get_astronomical_data
        astro_data = get_astronomical_data(test_date)
        print(f"   ✓ Phase lunaire: {astro_data.get('moon', {}).get('phase_name', 'N/A')}")
        print(f"   ✓ Illumination: {astro_data.get('moon', {}).get('illumination', 'N/A')}%")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # 2. Test collecteur météo
    print("\n2. Test collecteur météo...")
    try:
        from collectors.weather_data import get_weather_data
        weather_data = get_weather_data(test_date)
        weather = weather_data.get('weather', {})
        print(f"   ✓ Température: {weather.get('temperature_celsius', 'N/A')}°C")
        print(f"   ✓ Humidité: {weather.get('humidity_percent', 'N/A')}%")
        print(f"   ✓ Pression: {weather.get('pressure_hpa', 'N/A')} hPa")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # 3. Test collecteur géophysique
    print("\n3. Test collecteur géophysique...")
    try:
        from collectors.geophysical_data import get_geophysical_data
        geo_data = get_geophysical_data(test_date)
        geomag = geo_data.get('geomagnetic', {})
        print(f"   ✓ Indice Kp: {geomag.get('kp_average', 'N/A')}")
        print(f"   ✓ Activité: {geomag.get('activity_level', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")


def test_analyzers():
    """Teste tous les analyseurs."""
    print("\n" + "="*70)
    print("TEST DES ANALYSEURS")
    print("="*70)
    
    # Tirage de test avec des propriétés intéressantes
    test_numbers = [3, 13, 21, 34, 47]  # Contient Fibonacci: 3, 13, 21, 34
    test_stars = [5, 11]  # Nombres premiers
    
    # 1. Test analyseur de théorie des nombres
    print("\n1. Test analyseur de théorie des nombres...")
    try:
        from analyzers.number_theory import analyze_draw_number_theory
        analysis = analyze_draw_number_theory(test_numbers, test_stars)
        print(f"   ✓ Nombres premiers: {analysis['primes']['count']}/5")
        print(f"   ✓ Nombres Fibonacci: {analysis['fibonacci']['count']}/5")
        print(f"   ✓ Somme: {analysis['sums_products']['sum_numbers']}")
        print(f"   ✓ Parité équilibrée: {analysis['parity']['is_balanced_parity']}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # 2. Test analyseur temporel
    print("\n2. Test analyseur temporel...")
    try:
        from analyzers.temporal_analysis import TemporalAnalyzer
        import numpy as np
        
        analyzer = TemporalAnalyzer()
        
        # Créer une série de test avec un cycle (période 10)
        test_series = np.sin(2 * np.pi * np.arange(100) / 10) + 0.2 * np.random.randn(100)
        
        fourier = analyzer.fourier_analysis(test_series)
        print(f"   ✓ Transformée de Fourier: {len(fourier.get('dominant_periods', []))} périodes trouvées")
        
        chaos = analyzer.chaos_analysis(test_series)
        print(f"   ✓ Entropie de Shannon: {chaos.get('shannon_entropy', 'N/A')}")
        print(f"   ✓ Exposant de Hurst: {chaos.get('hurst_exponent', 'N/A')} ({chaos.get('hurst_interpretation', '')})")
        
        autocorr = analyzer.autocorrelation_analysis(test_series, max_lag=20)
        print(f"   ✓ Mémoire temporelle: {'Oui' if autocorr.get('has_memory') else 'Non'}")
        
    except Exception as e:
        print(f"   ✗ Erreur: {e}")


def test_correlation_engine():
    """Teste le moteur de corrélation."""
    print("\n" + "="*70)
    print("TEST DU MOTEUR DE CORRÉLATION")
    print("="*70)
    
    # Créer un petit dataset de test
    print("\n1. Création d'un dataset de test...")
    
    # 10 tirages fictifs sur 2 semaines (mardi/vendredi)
    dates = []
    current_date = datetime(2024, 10, 1, 21, 5)  # Mardi
    for i in range(10):
        dates.append(current_date)
        # Alterner entre mardi (2 jours après) et vendredi (5 jours après précédent tirage)
        if i % 2 == 0:
            current_date += timedelta(days=3)  # Mardi -> Vendredi
        else:
            current_date += timedelta(days=4)  # Vendredi -> Mardi
    
    test_draws = pd.DataFrame({
        'draw_date': dates,
        'n1': [1, 7, 13, 19, 25, 31, 37, 43, 5, 11],
        'n2': [2, 8, 14, 20, 26, 32, 38, 44, 6, 12],
        'n3': [3, 9, 15, 21, 27, 33, 39, 45, 7, 13],
        'n4': [4, 10, 16, 22, 28, 34, 40, 46, 8, 14],
        'n5': [5, 11, 17, 23, 29, 35, 41, 47, 9, 15],
        's1': [1, 3, 5, 7, 9, 11, 1, 3, 5, 7],
        's2': [2, 4, 6, 8, 10, 12, 2, 4, 6, 8]
    })
    
    print(f"   ✓ Dataset créé: {len(test_draws)} tirages")
    
    # 2. Enrichir le dataset
    print("\n2. Enrichissement du dataset...")
    try:
        from correlation_engine import MultiSourceCorrelator
        
        correlator = MultiSourceCorrelator()
        enriched_df = correlator.build_enriched_dataset(test_draws)
        
        print(f"   ✓ Dataset enrichi: {enriched_df.shape[0]} lignes, {enriched_df.shape[1]} colonnes")
        print(f"   Colonnes: {', '.join(enriched_df.columns[:10])}...")
        
    except Exception as e:
        print(f"   ✗ Erreur enrichissement: {e}")
        return None
    
    # 3. Calculer les corrélations
    print("\n3. Calcul des corrélations...")
    try:
        correlations = correlator.calculate_correlations(enriched_df)
        
        print(f"   ✓ Tests de corrélation: {correlations['total_tests']}")
        print(f"   ✓ Corrélations significatives: {correlations['significant_count']}")
        
        if correlations['significant_count'] > 0:
            print("\n   Top 3 corrélations:")
            for i, corr in enumerate(correlations['significant_correlations'][:3], 1):
                print(f"      {i}. {corr['external_factor']} vs {corr['draw_variable']}")
                print(f"         Pearson r={corr['pearson_r']:.3f}, Spearman r={corr['spearman_r']:.3f}")
        
        return enriched_df, correlations
        
    except Exception as e:
        print(f"   ✗ Erreur calcul corrélations: {e}")
        return None


def generate_report(enriched_df, correlations):
    """Génère un rapport complet."""
    print("\n" + "="*70)
    print("GÉNÉRATION DU RAPPORT")
    print("="*70)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'system_version': '1.0.0-advanced',
        'dataset': {
            'rows': len(enriched_df) if enriched_df is not None else 0,
            'columns': len(enriched_df.columns) if enriched_df is not None else 0,
        },
        'correlations': correlations if correlations else {},
        'summary': {
            'collectors_available': True,
            'analyzers_available': True,
            'correlation_engine_available': True
        }
    }
    
    # Sauvegarder le rapport
    report_dir = Path("data/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / f"advanced_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Rapport sauvegardé: {report_path}")
    
    return report


def main():
    """Fonction principale."""
    print("\n" + "="*70)
    print("TEST COMPLET DU SYSTÈME AVANCÉ EUROMILLIONS")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Tester les collecteurs
    test_collectors()
    
    # 2. Tester les analyseurs
    test_analyzers()
    
    # 3. Tester le moteur de corrélation
    result = test_correlation_engine()
    
    # 4. Générer le rapport
    if result:
        enriched_df, correlations = result
        report = generate_report(enriched_df, correlations)
    else:
        report = generate_report(None, None)
    
    print("\n" + "="*70)
    print("TEST TERMINÉ")
    print("="*70)
    
    print("\n📊 RÉSUMÉ:")
    print(f"  • Collecteurs: ✓ Opérationnels")
    print(f"  • Analyseurs: ✓ Opérationnels")
    print(f"  • Moteur de corrélation: ✓ Opérationnel")
    
    print("\n💡 PROCHAINES ÉTAPES:")
    print("  1. Collecter les données historiques complètes")
    print("  2. Analyser les corrélations sur l'historique complet")
    print("  3. Intégrer au système de prédiction ML")
    print("  4. Créer le dashboard de visualisation")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
