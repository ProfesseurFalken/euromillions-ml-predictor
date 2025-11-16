"""
Analyseur temporel avancé: Transformée de Fourier, analyse de chaos, ondelettes.
Recherche de cycles cachés et patterns non-linéaires dans les tirages.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from loguru import logger
from pathlib import Path
import json

# Import optionnel de scipy pour analyses avancées
try:
    from scipy import signal
    from scipy.fft import fft, fftfreq
    from scipy.stats import entropy
    SCIPY_AVAILABLE = True
except ImportError:
    logger.warning("scipy non disponible, certaines analyses seront limitées")
    SCIPY_AVAILABLE = False

try:
    import pywt  # PyWavelets pour analyse en ondelettes
    PYWT_AVAILABLE = True
except ImportError:
    logger.warning("pywt non disponible, analyse en ondelettes non disponible")
    PYWT_AVAILABLE = False


class TemporalAnalyzer:
    """
    Analyse temporelle avancée des séries de tirages.
    
    Méthodes:
    - Transformée de Fourier (détection de cycles)
    - Analyse en ondelettes (patterns multi-échelle)
    - Théorie du chaos (exposant de Lyapunov, entropie)
    - Autocorrélation (mémoire temporelle)
    """
    
    def __init__(self, cache_dir: str = "./data/temporal_analysis"):
        """Initialise l'analyseur avec cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fourier_analysis(self, series: np.ndarray) -> Dict[str, Any]:
        """
        Analyse de Fourier pour détecter des cycles cachés dans une série temporelle.
        
        Args:
            series: Série temporelle (ex: fréquence d'un numéro au fil du temps)
            
        Returns:
            Dict avec fréquences dominantes, périodes, puissance spectrale
        """
        if not SCIPY_AVAILABLE:
            return {'error': 'scipy requis pour analyse de Fourier'}
        
        n = len(series)
        if n < 4:
            return {'error': 'Série trop courte pour analyse de Fourier'}
        
        try:
            # Centrer la série (retirer la moyenne)
            series_centered = series - np.mean(series)
            
            # Transformée de Fourier
            yf = fft(series_centered)
            xf = fftfreq(n, 1)  # Fréquences (1 = par tirage)
            
            # Puissance spectrale (ne garder que les fréquences positives)
            power = np.abs(yf[:n//2])**2
            freqs = xf[:n//2]
            
            # Trouver les 5 fréquences dominantes (exclure DC component à 0)
            if len(power) > 1:
                sorted_indices = np.argsort(power[1:])[::-1][:5] + 1
                dominant_freqs = freqs[sorted_indices]
                dominant_powers = power[sorted_indices]
                
                # Convertir en périodes (nombre de tirages)
                dominant_periods = []
                for f in dominant_freqs:
                    if f != 0:
                        period = 1 / abs(f)
                        dominant_periods.append(round(period, 2))
                    else:
                        dominant_periods.append(np.inf)
                
                return {
                    'dominant_frequencies': [round(f, 4) for f in dominant_freqs],
                    'dominant_periods': dominant_periods,
                    'dominant_powers': [round(p, 2) for p in dominant_powers],
                    'total_power': round(float(np.sum(power)), 2),
                    'has_strong_periodicity': float(max(dominant_powers)) > np.mean(power) * 5
                }
            else:
                return {'error': 'Données insuffisantes'}
                
        except Exception as e:
            logger.error(f"Erreur analyse de Fourier: {e}")
            return {'error': str(e)}
    
    def wavelet_analysis(self, series: np.ndarray, wavelet: str = 'db4') -> Dict[str, Any]:
        """
        Analyse en ondelettes pour détection de patterns à différentes échelles.
        
        Args:
            series: Série temporelle
            wavelet: Type d'ondelette (db4, haar, sym4, etc.)
            
        Returns:
            Dict avec coefficients et énergies par niveau
        """
        if not PYWT_AVAILABLE:
            return {'error': 'pywt requis pour analyse en ondelettes'}
        
        if len(series) < 4:
            return {'error': 'Série trop courte pour analyse en ondelettes'}
        
        try:
            # Décomposition en ondelettes (jusqu'à niveau 4)
            max_level = min(4, pywt.dwt_max_level(len(series), wavelet))
            coeffs = pywt.wavedec(series, wavelet, level=max_level)
            
            # Calculer l'énergie à chaque niveau
            energies = [float(np.sum(c**2)) for c in coeffs]
            total_energy = sum(energies)
            
            # Pourcentage d'énergie par niveau
            energy_percentages = [e / total_energy * 100 for e in energies]
            
            return {
                'wavelet_type': wavelet,
                'decomposition_levels': max_level,
                'energies_by_level': [round(e, 2) for e in energies],
                'energy_percentages': [round(p, 2) for p in energy_percentages],
                'dominant_level': int(np.argmax(energies)),
                'total_energy': round(total_energy, 2)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse en ondelettes: {e}")
            return {'error': str(e)}
    
    def chaos_analysis(self, series: np.ndarray) -> Dict[str, Any]:
        """
        Analyse de la théorie du chaos: entropie, complexité, prévisibilité.
        
        Args:
            series: Série temporelle
            
        Returns:
            Dict avec métriques de chaos
        """
        if len(series) < 10:
            return {'error': 'Série trop courte pour analyse du chaos'}
        
        try:
            results = {}
            
            # 1. Entropie de Shannon
            hist, _ = np.histogram(series, bins=10, density=True)
            hist = hist[hist > 0]  # Retirer les bins vides
            shannon_entropy = float(-np.sum(hist * np.log2(hist + 1e-10)))
            results['shannon_entropy'] = round(shannon_entropy, 4)
            
            # 2. Approximate Entropy (ApEn) - mesure de régularité
            apen = self._approximate_entropy(series, m=2, r=0.2*np.std(series))
            results['approximate_entropy'] = round(apen, 4)
            
            # 3. Exposant de Hurst (mesure de persistence)
            hurst = self._hurst_exponent(series)
            results['hurst_exponent'] = round(hurst, 4)
            results['hurst_interpretation'] = self._interpret_hurst(hurst)
            
            # 4. Dimension de corrélation (approximation)
            # Note: Calcul simplifié, pour une véritable analyse il faut plus de points
            results['correlation_dimension'] = 'N/A (nécessite plus de données)'
            
            # 5. Exposant de Lyapunov (version simplifiée)
            # Note: Calcul exact très complexe, on fait une approximation
            lyap_approx = self._lyapunov_approximation(series)
            results['lyapunov_approx'] = round(lyap_approx, 4)
            results['is_chaotic'] = lyap_approx > 0
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur analyse du chaos: {e}")
            return {'error': str(e)}
    
    def _approximate_entropy(self, series: np.ndarray, m: int, r: float) -> float:
        """
        Calcule l'Approximate Entropy (ApEn).
        
        ApEn mesure la régularité d'une série temporelle.
        Valeurs basses = régulière, valeurs hautes = irrégulière.
        """
        def _maxdist(x_i, x_j):
            return max([abs(ua - va) for ua, va in zip(x_i, x_j)])
        
        def _phi(m):
            x = [[series[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
            C = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0) for x_i in x]
            return (N - m + 1.0)**(-1) * sum(np.log(C))
        
        N = len(series)
        return abs(_phi(m + 1) - _phi(m))
    
    def _hurst_exponent(self, series: np.ndarray) -> float:
        """
        Calcule l'exposant de Hurst par méthode R/S (Rescaled Range).
        
        H < 0.5: Anti-persistant (mean-reverting)
        H = 0.5: Marche aléatoire
        H > 0.5: Persistant (trending)
        """
        # Créer des sous-séries de tailles croissantes
        lags = range(2, min(100, len(series)//2))
        tau = []
        
        for lag in lags:
            # Diviser en sous-séries
            subseries = [series[i:i+lag] for i in range(0, len(series), lag)]
            
            # Calculer R/S pour chaque sous-série
            rs = []
            for s in subseries:
                if len(s) < lag:
                    continue
                mean_s = np.mean(s)
                y = np.cumsum(s - mean_s)
                R = np.max(y) - np.min(y)
                S = np.std(s)
                if S > 0:
                    rs.append(R / S)
            
            if rs:
                tau.append(np.mean(rs))
        
        if len(tau) < 2:
            return 0.5  # Valeur par défaut (marche aléatoire)
        
        # Régression log-log pour estimer H
        lags_log = np.log(list(lags[:len(tau)]))
        tau_log = np.log(tau)
        
        # Régression linéaire
        coeffs = np.polyfit(lags_log, tau_log, 1)
        hurst = coeffs[0]
        
        return float(hurst)
    
    def _interpret_hurst(self, h: float) -> str:
        """Interprète la valeur de l'exposant de Hurst."""
        if h < 0.4:
            return 'fortement anti-persistant (mean-reverting)'
        elif h < 0.5:
            return 'anti-persistant'
        elif h < 0.6:
            return 'marche aléatoire'
        elif h < 0.7:
            return 'persistant'
        else:
            return 'fortement persistant (trending)'
    
    def _lyapunov_approximation(self, series: np.ndarray) -> float:
        """
        Approximation de l'exposant de Lyapunov.
        
        Positif = chaotique, Négatif = stable.
        """
        # Approximation très simplifiée basée sur divergence locale
        diffs = np.diff(series)
        if len(diffs) == 0:
            return 0.0
        
        # Calculer la variation logarithmique moyenne
        log_diffs = np.log(np.abs(diffs) + 1e-10)
        lyap = float(np.mean(log_diffs))
        
        return lyap
    
    def autocorrelation_analysis(self, series: np.ndarray, max_lag: int = 50) -> Dict[str, Any]:
        """
        Analyse de l'autocorrélation pour détecter la mémoire temporelle.
        
        Args:
            series: Série temporelle
            max_lag: Nombre maximum de lags à tester
            
        Returns:
            Dict avec autocorrélations et lags significatifs
        """
        if len(series) < max_lag:
            max_lag = len(series) - 1
        
        try:
            # Calculer l'autocorrélation pour chaque lag
            acf = []
            for lag in range(max_lag + 1):
                if lag == 0:
                    acf.append(1.0)
                else:
                    # Autocorrélation de Pearson
                    corr = np.corrcoef(series[:-lag], series[lag:])[0, 1]
                    acf.append(float(corr) if not np.isnan(corr) else 0.0)
            
            # Trouver les lags avec autocorrélation significative (|r| > 0.2)
            significant_lags = []
            for i, r in enumerate(acf):
                if i > 0 and abs(r) > 0.2:
                    significant_lags.append({'lag': i, 'correlation': round(r, 4)})
            
            return {
                'autocorrelations': [round(r, 4) for r in acf],
                'significant_lags': significant_lags,
                'has_memory': len(significant_lags) > 0,
                'strongest_lag': int(np.argmax(np.abs(acf[1:])) + 1) if len(acf) > 1 else 0,
                'strongest_correlation': round(float(max(acf[1:], key=abs)), 4) if len(acf) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse autocorrélation: {e}")
            return {'error': str(e)}
    
    def analyze_number_frequency_series(self, draws_df: pd.DataFrame, number: int) -> Dict[str, Any]:
        """
        Analyse temporelle complète pour un numéro spécifique.
        
        Args:
            draws_df: DataFrame des tirages
            number: Numéro à analyser (1-50)
            
        Returns:
            Dict avec toutes les analyses temporelles
        """
        # Créer une série binaire: 1 si le numéro est sorti, 0 sinon
        series = []
        for _, row in draws_df.iterrows():
            numbers = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
            series.append(1 if number in numbers else 0)
        
        series = np.array(series)
        
        logger.info(f"Analyse temporelle du numéro {number} sur {len(series)} tirages")
        
        results = {
            'number': number,
            'total_draws': len(series),
            'appearances': int(np.sum(series)),
            'frequency': float(np.mean(series))
        }
        
        # Analyses
        results['fourier'] = self.fourier_analysis(series)
        results['wavelet'] = self.wavelet_analysis(series)
        results['chaos'] = self.chaos_analysis(series)
        results['autocorrelation'] = self.autocorrelation_analysis(series)
        
        return results


def analyze_temporal_patterns(draws_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Fonction utilitaire pour analyser les patterns temporels de tous les numéros.
    
    Args:
        draws_df: DataFrame des tirages
        
    Returns:
        Dict avec analyses pour numéros clés (1, 7, 13, 21, 42, 49, 50)
    """
    analyzer = TemporalAnalyzer()
    
    # Analyser quelques numéros représentatifs
    key_numbers = [1, 7, 13, 21, 42, 49, 50]
    
    results = {}
    for num in key_numbers:
        results[f'number_{num}'] = analyzer.analyze_number_frequency_series(draws_df, num)
    
    return results


if __name__ == "__main__":
    # Test de l'analyseur
    analyzer = TemporalAnalyzer()
    
    # Créer une série de test avec un cycle caché
    t = np.arange(0, 100)
    test_series = np.sin(2 * np.pi * t / 10) + 0.5 * np.sin(2 * np.pi * t / 5) + np.random.normal(0, 0.1, 100)
    
    print("\n=== ANALYSE TEMPORELLE (série de test avec cycles) ===")
    
    fourier = analyzer.fourier_analysis(test_series)
    print("\n1. Analyse de Fourier:")
    print(json.dumps(fourier, indent=2))
    
    wavelet = analyzer.wavelet_analysis(test_series)
    print("\n2. Analyse en ondelettes:")
    print(json.dumps(wavelet, indent=2))
    
    chaos = analyzer.chaos_analysis(test_series)
    print("\n3. Analyse du chaos:")
    print(json.dumps(chaos, indent=2))
    
    autocorr = analyzer.autocorrelation_analysis(test_series, max_lag=20)
    print("\n4. Autocorrélation:")
    print(json.dumps(autocorr, indent=2))
