"""
Analyseur basé sur la théorie des nombres: Fibonacci, nombres premiers, golden ratio, etc.
Recherche de patterns mathématiques dans les tirages EuroMillions.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from loguru import logger
from pathlib import Path
import json


class NumberTheoryAnalyzer:
    """
    Analyse les tirages sous l'angle de la théorie des nombres.
    
    Recherche:
    - Séquences de Fibonacci
    - Nombres premiers
    - Golden ratio (φ = 1.618...)
    - Patterns modulo N
    - Suites arithmétiques/géométriques
    """
    
    def __init__(self):
        """Initialise l'analyseur avec des constantes mathématiques."""
        # Nombres premiers jusqu'à 50 (pour les numéros EuroMillions)
        self.primes_up_to_50 = self._generate_primes(50)
        
        # Nombres de Fibonacci jusqu'à 50
        self.fibonacci_up_to_50 = self._generate_fibonacci(50)
        
        # Golden ratio
        self.phi = (1 + np.sqrt(5)) / 2  # φ ≈ 1.618033988749895
        
        # Cache des analyses
        self.cache_dir = Path("./data/number_theory")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_primes(self, max_n: int) -> List[int]:
        """
        Génère tous les nombres premiers jusqu'à max_n (crible d'Ératosthène).
        
        Args:
            max_n: Nombre maximum
            
        Returns:
            Liste des nombres premiers
        """
        if max_n < 2:
            return []
        
        # Crible d'Ératosthène
        sieve = [True] * (max_n + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(np.sqrt(max_n)) + 1):
            if sieve[i]:
                for j in range(i*i, max_n + 1, i):
                    sieve[j] = False
        
        return [i for i in range(max_n + 1) if sieve[i]]
    
    def _generate_fibonacci(self, max_n: int) -> List[int]:
        """
        Génère la séquence de Fibonacci jusqu'à max_n.
        
        Args:
            max_n: Nombre maximum
            
        Returns:
            Liste des nombres de Fibonacci
        """
        fib = [1, 1]
        while True:
            next_fib = fib[-1] + fib[-2]
            if next_fib > max_n:
                break
            fib.append(next_fib)
        return fib
    
    def analyze_draw(self, numbers: List[int], stars: List[int]) -> Dict[str, Any]:
        """
        Analyse un tirage individuel selon la théorie des nombres.
        
        Args:
            numbers: Liste des 5 numéros principaux
            stars: Liste des 2 étoiles
            
        Returns:
            Dict avec toutes les analyses
        """
        analysis = {
            'numbers': numbers,
            'stars': stars
        }
        
        # 1. Analyse des nombres premiers
        analysis['primes'] = self._analyze_primes(numbers)
        analysis['primes_stars'] = self._analyze_primes(stars)
        
        # 2. Analyse Fibonacci
        analysis['fibonacci'] = self._analyze_fibonacci(numbers)
        analysis['fibonacci_stars'] = self._analyze_fibonacci(stars)
        
        # 3. Analyse Golden Ratio
        analysis['golden_ratio'] = self._analyze_golden_ratio(numbers)
        
        # 4. Analyse modulo
        analysis['modulo'] = self._analyze_modulo_patterns(numbers)
        
        # 5. Suites arithmétiques/géométriques
        analysis['sequences'] = self._analyze_sequences(numbers)
        
        # 6. Parité et divisibilité
        analysis['parity'] = self._analyze_parity(numbers)
        
        # 7. Sommes et produits
        analysis['sums_products'] = self._analyze_sums_products(numbers, stars)
        
        return analysis
    
    def _analyze_primes(self, numbers: List[int]) -> Dict[str, Any]:
        """Analyse la présence de nombres premiers."""
        primes_in_draw = [n for n in numbers if n in self.primes_up_to_50]
        
        return {
            'count': len(primes_in_draw),
            'numbers': primes_in_draw,
            'percentage': len(primes_in_draw) / len(numbers) * 100,
            'is_all_primes': len(primes_in_draw) == len(numbers),
            'is_no_primes': len(primes_in_draw) == 0
        }
    
    def _analyze_fibonacci(self, numbers: List[int]) -> Dict[str, Any]:
        """Analyse la présence de nombres de Fibonacci."""
        fib_in_draw = [n for n in numbers if n in self.fibonacci_up_to_50]
        
        return {
            'count': len(fib_in_draw),
            'numbers': fib_in_draw,
            'percentage': len(fib_in_draw) / len(numbers) * 100,
            'is_all_fibonacci': len(fib_in_draw) == len(numbers),
            'is_no_fibonacci': len(fib_in_draw) == 0
        }
    
    def _analyze_golden_ratio(self, numbers: List[int]) -> Dict[str, Any]:
        """
        Analyse les ratios entre numéros consécutifs pour détecter le nombre d'or.
        
        Le golden ratio φ apparaît souvent dans la nature.
        """
        sorted_nums = sorted(numbers)
        ratios = []
        golden_ratio_matches = 0
        
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i] != 0:
                ratio = sorted_nums[i + 1] / sorted_nums[i]
                ratios.append(ratio)
                
                # Vérifier si proche du golden ratio (tolérance ±0.1)
                if abs(ratio - self.phi) < 0.1:
                    golden_ratio_matches += 1
        
        avg_ratio = np.mean(ratios) if ratios else 0
        
        return {
            'ratios': [round(r, 3) for r in ratios],
            'average_ratio': round(avg_ratio, 3),
            'golden_ratio_matches': golden_ratio_matches,
            'phi_deviation': round(abs(avg_ratio - self.phi), 3),
            'is_near_golden': abs(avg_ratio - self.phi) < 0.2
        }
    
    def _analyze_modulo_patterns(self, numbers: List[int]) -> Dict[str, Any]:
        """
        Analyse les patterns modulo N (N = 2, 3, 5, 7, 11, 13).
        
        Recherche de cycles cachés dans les tirages.
        """
        modulos = [2, 3, 5, 7, 11, 13]
        patterns = {}
        
        for mod in modulos:
            remainders = [n % mod for n in numbers]
            patterns[f'mod_{mod}'] = {
                'remainders': remainders,
                'unique_count': len(set(remainders)),
                'distribution': {i: remainders.count(i) for i in range(mod)}
            }
        
        return patterns
    
    def _analyze_sequences(self, numbers: List[int]) -> Dict[str, Any]:
        """
        Détecte les suites arithmétiques et géométriques.
        
        Suite arithmétique: a, a+d, a+2d, ...
        Suite géométrique: a, a*r, a*r², ...
        """
        sorted_nums = sorted(numbers)
        
        # Suite arithmétique
        differences = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
        is_arithmetic = len(set(differences)) == 1
        
        # Suite géométrique (approximative car on a des entiers)
        ratios = []
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i] != 0:
                ratios.append(sorted_nums[i + 1] / sorted_nums[i])
        is_geometric = len(set([round(r, 1) for r in ratios])) == 1 if ratios else False
        
        return {
            'is_arithmetic_sequence': is_arithmetic,
            'differences': differences,
            'is_geometric_sequence': is_geometric,
            'ratios': [round(r, 2) for r in ratios]
        }
    
    def _analyze_parity(self, numbers: List[int]) -> Dict[str, Any]:
        """
        Analyse la parité (pair/impair) et divisibilité.
        """
        even_count = sum(1 for n in numbers if n % 2 == 0)
        odd_count = len(numbers) - even_count
        
        # Divisibilité par 3, 5, 7
        div_by_3 = sum(1 for n in numbers if n % 3 == 0)
        div_by_5 = sum(1 for n in numbers if n % 5 == 0)
        div_by_7 = sum(1 for n in numbers if n % 7 == 0)
        
        return {
            'even_count': even_count,
            'odd_count': odd_count,
            'even_odd_ratio': even_count / len(numbers),
            'divisible_by_3': div_by_3,
            'divisible_by_5': div_by_5,
            'divisible_by_7': div_by_7,
            'is_balanced_parity': abs(even_count - odd_count) <= 1
        }
    
    def _analyze_sums_products(self, numbers: List[int], stars: List[int]) -> Dict[str, Any]:
        """
        Analyse les sommes, produits et propriétés algébriques.
        """
        sum_numbers = sum(numbers)
        product_numbers = np.prod(numbers)
        
        sum_stars = sum(stars)
        product_stars = np.prod(stars)
        
        # Vérifier si la somme est un nombre remarquable
        is_sum_prime = sum_numbers in self.primes_up_to_50 or self._is_prime(sum_numbers)
        is_sum_fibonacci = sum_numbers in self.fibonacci_up_to_50
        
        # Moyenne et écart-type
        mean_numbers = np.mean(numbers)
        std_numbers = np.std(numbers)
        
        return {
            'sum_numbers': sum_numbers,
            'product_numbers': int(product_numbers),
            'mean_numbers': round(mean_numbers, 2),
            'std_numbers': round(std_numbers, 2),
            'sum_stars': sum_stars,
            'product_stars': int(product_stars),
            'is_sum_prime': is_sum_prime,
            'is_sum_fibonacci': is_sum_fibonacci,
            'sum_mod_10': sum_numbers % 10,  # Dernier chiffre de la somme
            'sum_digital_root': self._digital_root(sum_numbers)
        }
    
    def _is_prime(self, n: int) -> bool:
        """Vérifie si un nombre est premier."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(np.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _digital_root(self, n: int) -> int:
        """
        Calcule la racine numérique (somme itérative des chiffres).
        
        Ex: 38 → 3+8=11 → 1+1=2
        """
        while n >= 10:
            n = sum(int(digit) for digit in str(n))
        return n
    
    def analyze_historical_patterns(self, draws_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les patterns sur l'historique complet des tirages.
        
        Args:
            draws_df: DataFrame avec colonnes n1, n2, n3, n4, n5, s1, s2
            
        Returns:
            Dict avec analyses statistiques sur tous les tirages
        """
        logger.info(f"Analyse de {len(draws_df)} tirages historiques")
        
        analyses = []
        for _, row in draws_df.iterrows():
            numbers = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
            stars = [row['s1'], row['s2']]
            analysis = self.analyze_draw(numbers, stars)
            analyses.append(analysis)
        
        # Statistiques agrégées
        stats = {
            'total_draws': len(analyses),
            'primes': {
                'avg_count': np.mean([a['primes']['count'] for a in analyses]),
                'max_count': max([a['primes']['count'] for a in analyses]),
                'all_primes_draws': sum([a['primes']['is_all_primes'] for a in analyses])
            },
            'fibonacci': {
                'avg_count': np.mean([a['fibonacci']['count'] for a in analyses]),
                'max_count': max([a['fibonacci']['count'] for a in analyses]),
                'all_fibonacci_draws': sum([a['fibonacci']['is_all_fibonacci'] for a in analyses])
            },
            'golden_ratio': {
                'avg_deviation': np.mean([a['golden_ratio']['phi_deviation'] for a in analyses]),
                'near_golden_draws': sum([a['golden_ratio']['is_near_golden'] for a in analyses])
            },
            'parity': {
                'avg_even_count': np.mean([a['parity']['even_count'] for a in analyses]),
                'balanced_draws': sum([a['parity']['is_balanced_parity'] for a in analyses])
            },
            'sums': {
                'avg_sum': np.mean([a['sums_products']['sum_numbers'] for a in analyses]),
                'std_sum': np.std([a['sums_products']['sum_numbers'] for a in analyses]),
                'prime_sum_draws': sum([a['sums_products']['is_sum_prime'] for a in analyses])
            }
        }
        
        logger.info("✓ Analyse théorie des nombres terminée")
        
        return stats


def analyze_draw_number_theory(numbers: List[int], stars: List[int]) -> Dict[str, Any]:
    """
    Fonction utilitaire pour analyser un tirage.
    
    Args:
        numbers: 5 numéros principaux
        stars: 2 étoiles
        
    Returns:
        Dict avec toutes les analyses mathématiques
    """
    analyzer = NumberTheoryAnalyzer()
    return analyzer.analyze_draw(numbers, stars)


if __name__ == "__main__":
    # Test de l'analyseur
    analyzer = NumberTheoryAnalyzer()
    
    # Exemple de tirage
    test_numbers = [3, 13, 21, 34, 42]  # Contient des Fibonacci!
    test_stars = [5, 11]  # Nombres premiers!
    
    analysis = analyzer.analyze_draw(test_numbers, test_stars)
    
    print("\n=== ANALYSE THÉORIE DES NOMBRES ===")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
