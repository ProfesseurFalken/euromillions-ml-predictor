"""
Backtesting System for EuroMillions Prediction
==============================================

This module implements comprehensive backtesting including:
- Walk-forward validation
- Hit rate tracking (2/5, 3/5, 4/5, 5/5 matches)
- Expected value calculation
- Performance metrics over time
- Statistical significance testing
- Comparison with random baseline

Author: EuroMillions ML Predictor
Version: 2.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss, roc_auc_score

# Local imports
from repository import get_repository
from build_datasets import build_enhanced_datasets


class BacktestEngine:
    """
    Comprehensive backtesting engine for lottery prediction models.
    """
    
    def __init__(self, 
                 train_size: int = 500,
                 test_size: int = 50,
                 step_size: int = 25):
        """
        Initialize backtesting engine.
        
        Args:
            train_size: Number of draws for training in each window
            test_size: Number of draws to test in each window
            step_size: Number of draws to move forward each iteration
        """
        self.train_size = train_size
        self.test_size = test_size
        self.step_size = step_size
        
        self.results = []
        self.hit_rates = defaultdict(list)
        self.metrics_history = []
        
        logger.info(f"BacktestEngine initialized: train={train_size}, test={test_size}, step={step_size}")
    
    def run_walk_forward(self, 
                        model_class,
                        df: pd.DataFrame,
                        model_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run walk-forward backtesting.
        
        Args:
            model_class: Class of model to test (must have fit/predict_proba methods)
            df: DataFrame with draw data
            model_params: Parameters to pass to model constructor
            
        Returns:
            Backtesting results
        """
        model_params = model_params or {}
        df = df.sort_values('draw_date').reset_index(drop=True)
        n_draws = len(df)
        
        logger.info(f"Starting walk-forward backtest with {n_draws} draws")
        
        results = []
        current_pos = self.train_size
        
        while current_pos + self.test_size <= n_draws:
            # Define train/test split
            train_df = df.iloc[current_pos - self.train_size:current_pos]
            test_df = df.iloc[current_pos:current_pos + self.test_size]
            
            # Build features
            X_train, y_train, _, _, _ = build_enhanced_datasets(train_df, window_size=50)
            
            # Train model
            model = model_class(**model_params)
            from sklearn.multioutput import MultiOutputClassifier
            multi_model = MultiOutputClassifier(model)
            multi_model.fit(X_train, y_train)
            
            # Test on each draw
            for i in range(len(test_df)):
                test_idx = current_pos + i
                
                # Build features for prediction
                pred_df = df.iloc[test_idx - 50:test_idx + 1]
                X_pred, _, _, _, _ = build_enhanced_datasets(pred_df, window_size=50)
                
                if len(X_pred) == 0:
                    continue
                
                # Get predictions
                proba = multi_model.predict_proba(X_pred[-1:])
                main_proba = np.array([p[0, 1] if len(p.shape) > 1 else p[0] for p in proba])
                
                # Get top 5 predicted numbers
                predicted_main = np.argsort(main_proba)[-5:][::-1] + 1
                
                # Get actual numbers
                actual_row = df.iloc[test_idx]
                actual_main = set([actual_row['n1'], actual_row['n2'], 
                                  actual_row['n3'], actual_row['n4'], actual_row['n5']])
                
                # Calculate hits
                hits = len(set(predicted_main) & actual_main)
                
                results.append({
                    'date': actual_row['draw_date'],
                    'predicted': list(predicted_main),
                    'actual': list(actual_main),
                    'hits': hits,
                    'position': current_pos + i
                })
            
            current_pos += self.step_size
            logger.debug(f"Progress: {current_pos}/{n_draws}")
        
        self.results = results
        return self._calculate_metrics(results)
    
    def _calculate_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results."""
        
        if not results:
            return {'error': 'No results'}
        
        hits = [r['hits'] for r in results]
        
        metrics = {
            'total_draws_tested': len(results),
            'hit_distribution': {
                f'{i}_hits': sum(1 for h in hits if h == i) for i in range(6)
            },
            'hit_rates': {
                f'{i}+_hits_rate': sum(1 for h in hits if h >= i) / len(hits) for i in range(1, 6)
            },
            'average_hits': np.mean(hits),
            'std_hits': np.std(hits),
            'max_hits': max(hits),
            'min_hits': min(hits),
        }
        
        # Calculate expected value
        metrics['expected_random'] = 5 * 5 / 50  # Random baseline
        metrics['improvement_vs_random'] = (metrics['average_hits'] - metrics['expected_random']) / metrics['expected_random'] * 100
        
        return metrics
    
    def run_model_comparison(self,
                            models: Dict[str, Any],
                            df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare multiple models using walk-forward validation.
        
        Args:
            models: Dictionary of model_name -> (model_class, params)
            df: DataFrame with draw data
            
        Returns:
            Comparison results
        """
        comparison = {}
        
        for name, (model_class, params) in models.items():
            logger.info(f"Testing model: {name}")
            metrics = self.run_walk_forward(model_class, df, params)
            comparison[name] = metrics
        
        return comparison


class HitRateTracker:
    """
    Tracks hit rates over time for model monitoring.
    """
    
    def __init__(self):
        """Initialize hit rate tracker."""
        self.history = []
        self.rolling_window = 50
    
    def record(self, 
               draw_date: datetime,
               predicted_main: List[int],
               predicted_stars: List[int],
               actual_main: List[int],
               actual_stars: List[int]):
        """
        Record a prediction result.
        
        Args:
            draw_date: Date of draw
            predicted_main: Predicted main numbers
            predicted_stars: Predicted stars
            actual_main: Actual main numbers
            actual_stars: Actual stars
        """
        main_hits = len(set(predicted_main) & set(actual_main))
        star_hits = len(set(predicted_stars) & set(actual_stars))
        
        self.history.append({
            'date': draw_date,
            'predicted_main': predicted_main,
            'predicted_stars': predicted_stars,
            'actual_main': actual_main,
            'actual_stars': actual_stars,
            'main_hits': main_hits,
            'star_hits': star_hits,
            'total_score': main_hits + star_hits * 0.5  # Weighted score
        })
    
    def get_rolling_metrics(self) -> Dict[str, float]:
        """Get rolling average metrics."""
        
        if len(self.history) < self.rolling_window:
            recent = self.history
        else:
            recent = self.history[-self.rolling_window:]
        
        if not recent:
            return {}
        
        main_hits = [r['main_hits'] for r in recent]
        star_hits = [r['star_hits'] for r in recent]
        
        return {
            'rolling_main_avg': float(np.mean(main_hits)),
            'rolling_star_avg': float(np.mean(star_hits)),
            'rolling_main_2plus_rate': sum(1 for h in main_hits if h >= 2) / len(main_hits),
            'rolling_main_3plus_rate': sum(1 for h in main_hits if h >= 3) / len(main_hits),
            'rolling_total_avg': float(np.mean([r['total_score'] for r in recent]))
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        
        if not self.history:
            return {'error': 'No history'}
        
        main_hits = [r['main_hits'] for r in self.history]
        star_hits = [r['star_hits'] for r in self.history]
        
        return {
            'total_predictions': len(self.history),
            'date_range': {
                'from': str(self.history[0]['date']),
                'to': str(self.history[-1]['date'])
            },
            'main_hit_distribution': {
                f'{i}_hits': sum(1 for h in main_hits if h == i) for i in range(6)
            },
            'star_hit_distribution': {
                f'{i}_hits': sum(1 for h in star_hits if h == i) for i in range(3)
            },
            'average_main_hits': np.mean(main_hits),
            'average_star_hits': np.mean(star_hits),
            'best_main_hits': max(main_hits),
            'any_jackpot': any(h == 5 and self.history[i]['star_hits'] == 2 
                              for i, h in enumerate(main_hits))
        }
    
    def save(self, path: Path):
        """Save history to file."""
        path = Path(path)
        with open(path, 'w') as f:
            json.dump(self.history, f, default=str, indent=2)
    
    def load(self, path: Path):
        """Load history from file."""
        path = Path(path)
        if path.exists():
            with open(path, 'r') as f:
                self.history = json.load(f)


class ExpectedValueCalculator:
    """
    Calculate expected value of predictions vs random selection.
    """
    
    # EuroMillions prize structure (approximate, varies by draw)
    PRIZE_STRUCTURE = {
        (5, 2): 50000000,  # Jackpot (average)
        (5, 1): 300000,
        (5, 0): 50000,
        (4, 2): 3000,
        (4, 1): 200,
        (4, 0): 100,
        (3, 2): 100,
        (3, 1): 15,
        (3, 0): 13,
        (2, 2): 18,
        (2, 1): 8,
        (1, 2): 10,
        (2, 0): 4,
    }
    
    # Ticket cost
    TICKET_COST = 2.50
    
    @classmethod
    def calculate_ev(cls, hit_rates: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate expected value from hit rates.
        
        Args:
            hit_rates: Dictionary with hit rate statistics
            
        Returns:
            Expected value metrics
        """
        # Simplified calculation based on main ball hits
        # (Full calculation would need star hit rates too)
        
        # Estimated EV based on main hits
        main_ev = 0
        
        # Using simplified prize estimates for main balls only
        simplified_prizes = {
            5: 50000,  # 5 main (avg with stars)
            4: 150,    # 4 main (avg with stars)
            3: 20,     # 3 main (avg with stars)
            2: 5,      # 2 main (avg with stars)
            1: 0,      # No prize for 1 hit
            0: 0
        }
        
        hit_dist = hit_rates.get('hit_distribution', {})
        for hits in range(6):
            rate_key = f'{hits}_hits'
            if isinstance(hit_dist, dict) and rate_key in hit_dist:
                rate = hit_dist[rate_key] / hit_rates.get('total_draws_tested', 1)  # type: ignore[operator]
                main_ev += rate * simplified_prizes.get(hits, 0)
        
        return {
            'expected_return_per_ticket': main_ev,
            'ticket_cost': cls.TICKET_COST,
            'expected_profit_per_ticket': main_ev - cls.TICKET_COST,
            'roi_percentage': (main_ev - cls.TICKET_COST) / cls.TICKET_COST * 100,
            'breakeven_jackpot_probability': cls.TICKET_COST / 50000000
        }
    
    @classmethod
    def calculate_random_ev(cls) -> Dict[str, float]:
        """Calculate expected value for random selection."""
        
        # Probability of each outcome for random selection
        # Main balls: 5 from 50, Stars: 2 from 12
        
        from math import comb
        
        total_main_combos = comb(50, 5)  # ~2.1 million
        total_star_combos = comb(12, 2)  # 66
        total_combos = total_main_combos * total_star_combos
        
        # Expected value calculation
        ev = 0
        
        for (main_hits, star_hits), prize in cls.PRIZE_STRUCTURE.items():
            # Probability of getting exactly this many hits
            main_prob = (comb(5, main_hits) * comb(45, 5 - main_hits)) / total_main_combos
            star_prob = (comb(2, star_hits) * comb(10, 2 - star_hits)) / total_star_combos
            prob = main_prob * star_prob
            ev += prob * prize
        
        return {
            'random_ev': ev,
            'random_roi': (ev - cls.TICKET_COST) / cls.TICKET_COST * 100,
            'jackpot_probability': 1 / total_combos,
            'any_prize_probability': sum(
                (comb(5, m) * comb(45, 5-m)) / total_main_combos *
                (comb(2, s) * comb(10, 2-s)) / total_star_combos
                for (m, s) in cls.PRIZE_STRUCTURE.keys()
            )
        }


class StatisticalValidator:
    """
    Statistical validation of prediction performance.
    """
    
    @staticmethod
    def binomial_test(successes: int, trials: int, expected_prob: float) -> Dict[str, float]:
        """
        Perform binomial test to check if success rate is significantly better than expected.
        
        Args:
            successes: Number of successes (e.g., draws with 2+ hits)
            trials: Total number of trials
            expected_prob: Expected probability under null hypothesis
            
        Returns:
            Test results
        """
        try:
            from scipy.stats import binomtest, binom  # type: ignore[import-not-found]
            result = binomtest(successes, trials, expected_prob, alternative='greater')
            p_value = result.pvalue
            
            return {
                'observed_rate': successes / trials,
                'expected_rate': expected_prob,
                'p_value': p_value,
                'significant_at_05': p_value < 0.05,
                'significant_at_01': p_value < 0.01,
                'confidence_interval': tuple(binom.interval(0.95, trials, successes / trials))  # type: ignore[arg-type]
            }
        except ImportError:
            # Fallback without scipy
            observed = successes / trials
            se = np.sqrt(expected_prob * (1 - expected_prob) / trials)
            z_score = (observed - expected_prob) / se
            
            return {
                'observed_rate': observed,
                'expected_rate': expected_prob,
                'z_score': z_score,
                'significant_at_05': z_score > 1.645,
                'significant_at_01': z_score > 2.326
            }
    
    @staticmethod
    def calculate_random_baseline() -> Dict[str, float]:
        """Calculate random selection baseline probabilities."""
        
        from math import comb
        
        total_combos = comb(50, 5)
        
        # Probability of exactly k hits when selecting 5 from 50
        # Hypergeometric distribution
        probs = {}
        for k in range(6):
            # P(exactly k hits) = C(5,k) * C(45, 5-k) / C(50, 5)
            prob = (comb(5, k) * comb(45, 5 - k)) / total_combos
            probs[f'{k}_hits_prob'] = prob
        
        # Cumulative probabilities
        probs['2plus_hits_prob'] = sum(probs[f'{k}_hits_prob'] for k in range(2, 6))
        probs['3plus_hits_prob'] = sum(probs[f'{k}_hits_prob'] for k in range(3, 6))
        probs['expected_hits'] = sum(k * probs[f'{k}_hits_prob'] for k in range(6))
        
        return probs


def run_full_backtest(model_type: str = 'lightgbm',
                     train_size: int = 500,
                     test_size: int = 100) -> Dict[str, Any]:
    """
    Run full backtest with statistical validation.
    
    Args:
        model_type: Type of model to test
        train_size: Training window size
        test_size: Test window size
        
    Returns:
        Complete backtest results
    """
    logger.info("Running full backtest...")
    
    # Load data
    repo = get_repository()
    df = repo.all_draws_df()
    
    if len(df) < train_size + test_size:
        return {'error': f'Not enough data: {len(df)} draws'}
    
    # Initialize engine
    engine = BacktestEngine(train_size=train_size, test_size=test_size)
    
    # Select model
    if model_type == 'lightgbm':
        import lightgbm as lgb
        model_class = lgb.LGBMClassifier
        model_params = {'n_estimators': 100, 'max_depth': 8, 'random_state': 42, 'verbose': -1}
    elif model_type == 'xgboost':
        import xgboost as xgb
        model_class = xgb.XGBClassifier
        model_params = {'n_estimators': 100, 'max_depth': 6, 'random_state': 42, 'verbosity': 0}
    else:
        import lightgbm as lgb
        model_class = lgb.LGBMClassifier
        model_params = {'n_estimators': 100, 'random_state': 42, 'verbose': -1}
    
    # Run backtest
    metrics = engine.run_walk_forward(model_class, df, model_params)
    
    # Calculate random baseline
    baseline = StatisticalValidator.calculate_random_baseline()
    
    # Statistical tests
    total_tests = metrics.get('total_draws_tested', 0)
    hits_2plus = sum(1 for r in engine.results if r['hits'] >= 2)
    
    significance = StatisticalValidator.binomial_test(
        hits_2plus, total_tests, baseline['2plus_hits_prob']
    )
    
    # Expected value
    ev_model = ExpectedValueCalculator.calculate_ev(metrics)
    ev_random = ExpectedValueCalculator.calculate_random_ev()
    
    return {
        'model_type': model_type,
        'metrics': metrics,
        'baseline': baseline,
        'statistical_significance': significance,
        'expected_value': {
            'model': ev_model,
            'random': ev_random
        },
        'conclusion': {
            'beats_random': metrics.get('average_hits', 0) > baseline.get('expected_hits', 0),
            'statistically_significant': significance.get('significant_at_05', False),
            'improvement_percentage': metrics.get('improvement_vs_random', 0)
        }
    }


def save_backtest_report(results: Dict[str, Any], path: Path):
    """Save backtest results to file."""
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Backtest report saved to {path}")


if __name__ == "__main__":
    # Test module
    print("Testing Backtesting System...")
    
    results = run_full_backtest(model_type='lightgbm', train_size=300, test_size=50)
    
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    
    print(f"\nModel: {results.get('model_type')}")
    print(f"Draws tested: {results.get('metrics', {}).get('total_draws_tested')}")
    
    print("\nHit Distribution:")
    for k, v in results.get('metrics', {}).get('hit_distribution', {}).items():
        print(f"  {k}: {v}")
    
    print(f"\nAverage hits: {results.get('metrics', {}).get('average_hits', 0):.3f}")
    print(f"Random baseline: {results.get('baseline', {}).get('expected_hits', 0):.3f}")
    print(f"Improvement: {results.get('metrics', {}).get('improvement_vs_random', 0):.1f}%")
    
    print("\nStatistical Significance:")
    sig = results.get('statistical_significance', {})
    print(f"  P-value: {sig.get('p_value', 'N/A')}")
    print(f"  Significant at 5%: {sig.get('significant_at_05', False)}")
    
    print("\nConclusion:")
    conclusion = results.get('conclusion', {})
    print(f"  Beats random: {conclusion.get('beats_random', False)}")
    print(f"  Statistically significant: {conclusion.get('statistically_significant', False)}")
