#!/usr/bin/env python3
"""
Système de backtesting automatique pour trouver la meilleure graine aléatoire.

Ce script teste différentes graines (seeds) et méthodes de génération
pour déterminer lesquelles auraient donné les meilleurs résultats
sur les tirages passés.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
from loguru import logger

from repository import get_repository
from streamlit_adapters import EuromillionsUIAdapter

# Configuration du logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


class SeedBacktester:
    """Teste différentes graines pour trouver les meilleures performances."""
    
    def __init__(self, seeds_to_test: List[int] = None, methods_to_test: List[str] = None):
        """
        Args:
            seeds_to_test: Liste de graines à tester (défaut: 1-100)
            methods_to_test: Méthodes à tester (défaut: toutes)
        """
        self.seeds = seeds_to_test or list(range(1, 101))  # Test 100 graines par défaut
        self.methods = methods_to_test or ["topk", "random", "hybrid", "ensemble"]
        self.repo = get_repository()
        self.adapter = EuromillionsUIAdapter()
        
    def calculate_match_score(self, predicted: List[int], actual: List[int]) -> int:
        """
        Calcule le score de correspondance entre prédiction et résultat réel.
        
        Returns:
            Score: nombre de numéros correspondants
        """
        return len(set(predicted) & set(actual))
    
    def calculate_ticket_score(self, ticket: Dict[str, Any], actual_draw: pd.Series) -> Dict[str, int]:
        """
        Calcule le score d'un ticket par rapport au tirage réel.
        
        Returns:
            Dict avec 'main_matches' (0-5) et 'star_matches' (0-2)
        """
        main_matches = self.calculate_match_score(ticket['main'], actual_draw['main'])
        star_matches = self.calculate_match_score(ticket['stars'], actual_draw['stars'])
        
        return {
            'main_matches': main_matches,
            'star_matches': star_matches,
            'total_score': main_matches * 10 + star_matches * 5  # Pondération
        }
    
    def get_euromillions_gain(self, main_matches: int, star_matches: int) -> str:
        """
        Retourne le rang de gain EuroMillions.
        
        Returns:
            Rang du gain (ex: "Rang 1", "Rang 5", "Rien")
        """
        if main_matches == 5 and star_matches == 2:
            return "Rang 1 - JACKPOT! 🎰💰"
        elif main_matches == 5 and star_matches == 1:
            return "Rang 2 - ~100K€ 💎"
        elif main_matches == 5 and star_matches == 0:
            return "Rang 3 - ~10K€ 💰"
        elif main_matches == 4 and star_matches == 2:
            return "Rang 4 - ~1K€ 🎁"
        elif main_matches == 4 and star_matches == 1:
            return "Rang 5 - ~100€ 🎫"
        elif main_matches == 3 and star_matches == 2:
            return "Rang 6 - ~50€ 🎫"
        elif main_matches == 4 and star_matches == 0:
            return "Rang 7 - ~30€ 🎫"
        elif main_matches == 2 and star_matches == 2:
            return "Rang 8 - ~20€ 🎫"
        elif main_matches == 3 and star_matches == 1:
            return "Rang 9 - ~15€ 🎫"
        elif main_matches == 3 and star_matches == 0:
            return "Rang 10 - ~10€ 🎫"
        elif main_matches == 1 and star_matches == 2:
            return "Rang 11 - ~8€ 🎫"
        elif main_matches == 2 and star_matches == 1:
            return "Rang 12 - ~5€ 🎫"
        else:
            return "Rien gagné ❌"
    
    def backtest_single_config(self, seed: int, method: str, 
                              test_draws: pd.DataFrame, 
                              n_tickets: int = 10) -> Dict[str, Any]:
        """
        Teste une configuration (seed + méthode) sur des tirages historiques.
        
        Args:
            seed: Graine aléatoire
            method: Méthode de génération
            test_draws: DataFrame des tirages à tester
            n_tickets: Nombre de tickets à générer
            
        Returns:
            Statistiques de performance
        """
        total_main_matches = 0
        total_star_matches = 0
        total_score = 0
        best_result = {'main': 0, 'stars': 0}
        wins_by_rank = {f"Rang {i}": 0 for i in range(1, 13)}
        wins_by_rank["Rien gagné"] = 0
        
        for idx, actual_draw in test_draws.iterrows():
            try:
                # Générer les tickets avec cette config
                tickets = self.adapter.suggest_tickets_ui(
                    n=n_tickets,
                    method=method,
                    seed=seed,
                    use_ensemble=(method == "ensemble")
                )
                
                # Évaluer chaque ticket
                for ticket in tickets:
                    score = self.calculate_ticket_score(ticket, actual_draw)
                    total_main_matches += score['main_matches']
                    total_star_matches += score['star_matches']
                    total_score += score['total_score']
                    
                    # Meilleur résultat
                    if (score['main_matches'] > best_result['main'] or 
                        (score['main_matches'] == best_result['main'] and 
                         score['star_matches'] > best_result['stars'])):
                        best_result = {
                            'main': score['main_matches'],
                            'stars': score['star_matches']
                        }
                    
                    # Compter les gains
                    rank = self.get_euromillions_gain(score['main_matches'], score['star_matches'])
                    wins_by_rank[rank] = wins_by_rank.get(rank, 0) + 1
                    
            except Exception as e:
                logger.warning(f"Erreur pour seed={seed}, method={method}: {e}")
                continue
        
        n_draws_tested = len(test_draws)
        n_total_tickets = n_draws_tested * n_tickets
        
        return {
            'seed': seed,
            'method': method,
            'n_draws_tested': n_draws_tested,
            'n_tickets_generated': n_total_tickets,
            'total_main_matches': total_main_matches,
            'total_star_matches': total_star_matches,
            'total_score': total_score,
            'avg_main_matches': total_main_matches / n_total_tickets if n_total_tickets > 0 else 0,
            'avg_star_matches': total_star_matches / n_total_tickets if n_total_tickets > 0 else 0,
            'avg_score': total_score / n_total_tickets if n_total_tickets > 0 else 0,
            'best_result': best_result,
            'wins_by_rank': wins_by_rank
        }
    
    def run_comprehensive_test(self, n_recent_draws: int = 50, 
                              n_tickets_per_draw: int = 10) -> pd.DataFrame:
        """
        Lance un test complet sur toutes les combinaisons seed/méthode.
        
        Args:
            n_recent_draws: Nombre de tirages récents à utiliser pour le test
            n_tickets_per_draw: Nombre de tickets à générer par tirage
            
        Returns:
            DataFrame avec les résultats de tous les tests
        """
        logger.info(f"🚀 Démarrage du backtest complet")
        logger.info(f"   Seeds à tester: {len(self.seeds)}")
        logger.info(f"   Méthodes: {', '.join(self.methods)}")
        logger.info(f"   Tirages de test: {n_recent_draws} derniers")
        logger.info(f"   Tickets par tirage: {n_tickets_per_draw}")
        
        # Récupérer les tirages récents
        all_draws = self.repo.all_draws_df()
        test_draws = all_draws.tail(n_recent_draws)
        
        logger.info(f"   Date de début: {test_draws.iloc[0]['draw_date']}")
        logger.info(f"   Date de fin: {test_draws.iloc[-1]['draw_date']}")
        logger.info("")
        
        results = []
        total_tests = len(self.seeds) * len(self.methods)
        current_test = 0
        
        for seed in self.seeds:
            for method in self.methods:
                current_test += 1
                logger.info(f"[{current_test}/{total_tests}] Test seed={seed}, method={method}...")
                
                result = self.backtest_single_config(
                    seed=seed,
                    method=method,
                    test_draws=test_draws,
                    n_tickets=n_tickets_per_draw
                )
                results.append(result)
        
        # Convertir en DataFrame
        df_results = pd.DataFrame(results)
        
        # Trier par score moyen décroissant
        df_results = df_results.sort_values('avg_score', ascending=False)
        
        return df_results
    
    def display_top_results(self, df_results: pd.DataFrame, top_n: int = 10):
        """Affiche les meilleurs résultats."""
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🏆 TOP {top_n} MEILLEURES CONFIGURATIONS")
        logger.info("=" * 80)
        
        for idx, row in df_results.head(top_n).iterrows():
            logger.info("")
            logger.info(f"Rang #{idx + 1}")
            logger.info(f"  • Seed: {row['seed']}")
            logger.info(f"  • Méthode: {row['method']}")
            logger.info(f"  • Score moyen: {row['avg_score']:.2f}")
            logger.info(f"  • Numéros principaux (moy): {row['avg_main_matches']:.2f}/5")
            logger.info(f"  • Étoiles (moy): {row['avg_star_matches']:.2f}/2")
            logger.info(f"  • Meilleur résultat: {row['best_result']['main']} numéros + {row['best_result']['stars']} étoiles")
            
            # Afficher les gains
            wins = row['wins_by_rank']
            logger.info(f"  • Gains simulés:")
            for rank, count in wins.items():
                if count > 0 and "Rang" in rank:
                    logger.info(f"     - {rank}: {count} fois")
        
        logger.info("")
        logger.info("=" * 80)
    
    def export_results(self, df_results: pd.DataFrame, filename: str = "backtest_results.csv"):
        """Exporte les résultats en CSV."""
        output_path = Path("data") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir wins_by_rank en colonnes séparées
        df_export = df_results.copy()
        for rank in ["Rang 1 - JACKPOT! 🎰💰", "Rang 2 - ~100K€ 💎", "Rang 3 - ~10K€ 💰"]:
            df_export[rank] = df_export['wins_by_rank'].apply(lambda x: x.get(rank, 0))
        
        df_export.drop(columns=['wins_by_rank', 'best_result'], inplace=True)
        df_export.to_csv(output_path, index=False)
        
        logger.info(f"📊 Résultats exportés vers: {output_path}")


def main():
    """Fonction principale."""
    logger.info("=" * 80)
    logger.info("🔬 SYSTÈME DE BACKTESTING - RECHERCHE DE LA MEILLEURE GRAINE")
    logger.info("=" * 80)
    logger.info("")
    
    # Configuration
    seeds_to_test = list(range(1, 51))  # Tester seeds 1 à 50
    methods_to_test = ["topk", "random", "hybrid"]  # Les principales méthodes
    
    # Créer le backtester
    backtester = SeedBacktester(
        seeds_to_test=seeds_to_test,
        methods_to_test=methods_to_test
    )
    
    # Lancer le test complet
    df_results = backtester.run_comprehensive_test(
        n_recent_draws=30,  # Tester sur les 30 derniers tirages
        n_tickets_per_draw=10  # 10 tickets par tirage
    )
    
    # Afficher les meilleurs résultats
    backtester.display_top_results(df_results, top_n=10)
    
    # Exporter
    backtester.export_results(df_results)
    
    logger.info("")
    logger.info("✅ Backtesting terminé!")
    logger.info("")
    logger.info("💡 Recommandation: Utilisez la seed et la méthode du top 1 pour vos prochaines générations!")


if __name__ == "__main__":
    main()
