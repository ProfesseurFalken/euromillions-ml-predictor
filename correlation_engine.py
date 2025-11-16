"""
Module de corrélation multi-sources: combine toutes les données externes et analyse les corrélations.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple
from loguru import logger
from pathlib import Path
import json

try:
    from scipy.stats import pearsonr, spearmanr
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy non disponible, corrélations limitées")

# Import des collecteurs
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from collectors.astronomical_data import get_astronomical_data
    from collectors.weather_data import get_weather_data
    from collectors.geophysical_data import get_geophysical_data
    from analyzers.number_theory import analyze_draw_number_theory
    COLLECTORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Collecteurs non disponibles: {e}")
    COLLECTORS_AVAILABLE = False


class MultiSourceCorrelator:
    """
    Corrèle les données de tirages avec les facteurs externes.
    
    Cherche des corrélations entre:
    - Numéros sortis et phases lunaires
    - Numéros sortis et météo
    - Numéros sortis et activité géomagnétique
    - Propriétés mathématiques et facteurs externes
    """
    
    def __init__(self, cache_dir: str = "./data/correlations"):
        """Initialise le corrélateur avec cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_enriched_draw_data(self, draw_date: datetime, numbers: List[int], 
                                   stars: List[int]) -> Dict[str, Any]:
        """
        Collecte toutes les données pour un tirage donné.
        
        Args:
            draw_date: Date et heure du tirage
            numbers: 5 numéros principaux
            stars: 2 étoiles
            
        Returns:
            Dict avec toutes les données enrichies
        """
        logger.info(f"Collecte des données enrichies pour le tirage du {draw_date}")
        
        enriched_data = {
            'draw_date': draw_date.isoformat(),
            'numbers': numbers,
            'stars': stars,
            'sum_numbers': sum(numbers),
            'sum_stars': sum(stars)
        }
        
        if not COLLECTORS_AVAILABLE:
            logger.warning("Collecteurs non disponibles, données limitées")
            return enriched_data
        
        # 1. Données astronomiques
        try:
            astro_data = get_astronomical_data(draw_date)
            enriched_data['astronomical'] = astro_data
            
            # Extraire les métriques clés
            moon = astro_data.get('moon', {})
            enriched_data['moon_phase_pct'] = moon.get('phase_percentage', None)
            enriched_data['moon_illumination'] = moon.get('illumination', None)
            enriched_data['moon_age_days'] = moon.get('age_days', None)
            
        except Exception as e:
            logger.error(f"Erreur collecte données astronomiques: {e}")
            enriched_data['astronomical'] = {}
        
        # 2. Données météorologiques
        try:
            weather_data = get_weather_data(draw_date)
            enriched_data['weather'] = weather_data
            
            # Extraire les métriques clés
            weather = weather_data.get('weather', {})
            enriched_data['temperature_c'] = weather.get('temperature_celsius', None)
            enriched_data['humidity_pct'] = weather.get('humidity_percent', None)
            enriched_data['pressure_hpa'] = weather.get('pressure_hpa', None)
            enriched_data['wind_speed_kmh'] = weather.get('wind_speed_kmh', None)
            
        except Exception as e:
            logger.error(f"Erreur collecte données météo: {e}")
            enriched_data['weather'] = {}
        
        # 3. Données géophysiques
        try:
            geo_data = get_geophysical_data(draw_date)
            enriched_data['geophysical'] = geo_data
            
            # Extraire les métriques clés
            geomag = geo_data.get('geomagnetic', {})
            enriched_data['kp_index'] = geomag.get('kp_average', None)
            
            seismic = geo_data.get('seismic', {})
            enriched_data['earthquake_count'] = seismic.get('earthquake_count', None)
            
        except Exception as e:
            logger.error(f"Erreur collecte données géophysiques: {e}")
            enriched_data['geophysical'] = {}
        
        # 4. Analyse mathématique du tirage
        try:
            math_analysis = analyze_draw_number_theory(numbers, stars)
            enriched_data['mathematics'] = math_analysis
            
            # Extraire métriques clés
            enriched_data['prime_count'] = math_analysis.get('primes', {}).get('count', 0)
            enriched_data['fibonacci_count'] = math_analysis.get('fibonacci', {}).get('count', 0)
            enriched_data['even_count'] = math_analysis.get('parity', {}).get('even_count', 0)
            
        except Exception as e:
            logger.error(f"Erreur analyse mathématique: {e}")
            enriched_data['mathematics'] = {}
        
        logger.info("✓ Données enrichies collectées")
        
        return enriched_data
    
    def build_enriched_dataset(self, draws_df: pd.DataFrame) -> pd.DataFrame:
        """
        Construit un dataset enrichi avec toutes les données externes.
        
        Args:
            draws_df: DataFrame avec les tirages (draw_date, n1-n5, s1-s2)
            
        Returns:
            DataFrame enrichi avec colonnes supplémentaires
        """
        logger.info(f"Construction du dataset enrichi pour {len(draws_df)} tirages")
        
        enriched_rows = []
        
        for idx, row in draws_df.iterrows():
            try:
                # Convertir la date en datetime
                if isinstance(row['draw_date'], str):
                    draw_date = pd.to_datetime(row['draw_date'])
                else:
                    draw_date = row['draw_date']
                
                # Assumer 21h05 si pas d'heure
                if draw_date.hour == 0 and draw_date.minute == 0:
                    draw_date = draw_date.replace(hour=21, minute=5)
                
                # Collecter les données enrichies
                numbers = [int(row['n1']), int(row['n2']), int(row['n3']), 
                          int(row['n4']), int(row['n5'])]
                stars = [int(row['s1']), int(row['s2'])]
                
                enriched = self.collect_enriched_draw_data(draw_date, numbers, stars)
                
                # Créer une ligne plate pour le DataFrame
                flat_row = {
                    'draw_date': draw_date,
                    'n1': row['n1'], 'n2': row['n2'], 'n3': row['n3'],
                    'n4': row['n4'], 'n5': row['n5'],
                    's1': row['s1'], 's2': row['s2'],
                    'sum_numbers': enriched.get('sum_numbers'),
                    'sum_stars': enriched.get('sum_stars'),
                    'moon_phase_pct': enriched.get('moon_phase_pct'),
                    'moon_illumination': enriched.get('moon_illumination'),
                    'moon_age_days': enriched.get('moon_age_days'),
                    'temperature_c': enriched.get('temperature_c'),
                    'humidity_pct': enriched.get('humidity_pct'),
                    'pressure_hpa': enriched.get('pressure_hpa'),
                    'wind_speed_kmh': enriched.get('wind_speed_kmh'),
                    'kp_index': enriched.get('kp_index'),
                    'earthquake_count': enriched.get('earthquake_count'),
                    'prime_count': enriched.get('prime_count'),
                    'fibonacci_count': enriched.get('fibonacci_count'),
                    'even_count': enriched.get('even_count')
                }
                
                enriched_rows.append(flat_row)
                
                # Log progression
                if (idx + 1) % 10 == 0:
                    logger.info(f"Progression: {idx + 1}/{len(draws_df)} tirages traités")
                
            except Exception as e:
                logger.error(f"Erreur traitement tirage {idx}: {e}")
                continue
        
        enriched_df = pd.DataFrame(enriched_rows)
        logger.info(f"✓ Dataset enrichi créé: {len(enriched_df)} lignes, {len(enriched_df.columns)} colonnes")
        
        # Sauvegarder
        output_path = self.cache_dir / "enriched_draws.csv"
        enriched_df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"✓ Dataset sauvegardé: {output_path}")
        
        return enriched_df
    
    def calculate_correlations(self, enriched_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les corrélations entre les numéros sortis et les facteurs externes.
        
        Args:
            enriched_df: DataFrame enrichi
            
        Returns:
            Dict avec toutes les corrélations découvertes
        """
        if not SCIPY_AVAILABLE:
            logger.warning("scipy non disponible, corrélations limitées")
            return {}
        
        logger.info("Calcul des corrélations multi-sources")
        
        correlations = {}
        
        # Variables externes à tester
        external_vars = [
            'moon_phase_pct', 'moon_illumination', 'moon_age_days',
            'temperature_c', 'humidity_pct', 'pressure_hpa', 'wind_speed_kmh',
            'kp_index', 'earthquake_count'
        ]
        
        # Variables de tirages à tester
        draw_vars = [
            'sum_numbers', 'sum_stars', 
            'prime_count', 'fibonacci_count', 'even_count'
        ]
        
        # Calculer corrélations Pearson et Spearman
        for ext_var in external_vars:
            if ext_var not in enriched_df.columns:
                continue
            
            correlations[ext_var] = {}
            
            for draw_var in draw_vars:
                if draw_var not in enriched_df.columns:
                    continue
                
                # Filtrer les valeurs non-nulles
                valid_mask = enriched_df[ext_var].notna() & enriched_df[draw_var].notna()
                
                if valid_mask.sum() < 10:  # Minimum 10 points pour corréler
                    continue
                
                ext_values = enriched_df.loc[valid_mask, ext_var].values
                draw_values = enriched_df.loc[valid_mask, draw_var].values
                
                try:
                    # Corrélation de Pearson (linéaire)
                    pearson_r, pearson_p = pearsonr(ext_values, draw_values)
                    
                    # Corrélation de Spearman (monotone, non-linéaire)
                    spearman_r, spearman_p = spearmanr(ext_values, draw_values)
                    
                    correlations[ext_var][draw_var] = {
                        'pearson_r': round(float(pearson_r), 4),
                        'pearson_p_value': round(float(pearson_p), 4),
                        'spearman_r': round(float(spearman_r), 4),
                        'spearman_p_value': round(float(spearman_p), 4),
                        'sample_size': int(valid_mask.sum()),
                        'is_significant': bool(pearson_p < 0.05 or spearman_p < 0.05)
                    }
                    
                except Exception as e:
                    logger.debug(f"Erreur corrélation {ext_var} vs {draw_var}: {e}")
                    continue
        
        # Trouver les corrélations significatives
        significant_correlations = []
        for ext_var, draw_corrs in correlations.items():
            for draw_var, corr_data in draw_corrs.items():
                if corr_data.get('is_significant', False):
                    significant_correlations.append({
                        'external_factor': ext_var,
                        'draw_variable': draw_var,
                        'pearson_r': corr_data['pearson_r'],
                        'spearman_r': corr_data['spearman_r'],
                        'sample_size': corr_data['sample_size']
                    })
        
        # Trier par force de corrélation
        significant_correlations.sort(
            key=lambda x: max(abs(x['pearson_r']), abs(x['spearman_r'])),
            reverse=True
        )
        
        result = {
            'all_correlations': correlations,
            'significant_correlations': significant_correlations,
            'total_tests': sum(len(v) for v in correlations.values()),
            'significant_count': len(significant_correlations)
        }
        
        logger.info(f"✓ {result['total_tests']} corrélations testées, "
                   f"{result['significant_count']} significatives trouvées")
        
        # Sauvegarder
        output_path = self.cache_dir / "correlations.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Corrélations sauvegardées: {output_path}")
        
        return result


def build_and_analyze_enriched_dataset(draws_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fonction utilitaire complète: construit le dataset enrichi et calcule les corrélations.
    
    Args:
        draws_df: DataFrame des tirages
        
    Returns:
        Tuple (DataFrame enrichi, Dict des corrélations)
    """
    correlator = MultiSourceCorrelator()
    
    # Construire le dataset enrichi
    enriched_df = correlator.build_enriched_dataset(draws_df)
    
    # Calculer les corrélations
    correlations = correlator.calculate_correlations(enriched_df)
    
    return enriched_df, correlations


if __name__ == "__main__":
    # Test avec des données fictives
    test_draws = pd.DataFrame({
        'draw_date': pd.date_range('2024-01-01', periods=10, freq='3D'),
        'n1': [1, 5, 10, 15, 20, 25, 30, 35, 40, 45],
        'n2': [2, 6, 11, 16, 21, 26, 31, 36, 41, 46],
        'n3': [3, 7, 12, 17, 22, 27, 32, 37, 42, 47],
        'n4': [4, 8, 13, 18, 23, 28, 33, 38, 43, 48],
        'n5': [5, 9, 14, 19, 24, 29, 34, 39, 44, 49],
        's1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        's2': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    })
    
    correlator = MultiSourceCorrelator()
    
    print("\n=== TEST COLLECTEUR MULTI-SOURCES ===")
    enriched_df, correlations = build_and_analyze_enriched_dataset(test_draws)
    
    print(f"\nDataset enrichi: {enriched_df.shape}")
    print(f"Colonnes: {list(enriched_df.columns)}")
    
    print(f"\nCorrélations significatives: {correlations['significant_count']}")
    for corr in correlations['significant_correlations'][:5]:
        print(f"  - {corr['external_factor']} vs {corr['draw_variable']}: r={corr['pearson_r']}")
