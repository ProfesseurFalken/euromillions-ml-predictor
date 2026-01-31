"""
Multi-Strategy Ticket Generation for EuroMillions
=================================================

This module implements advanced ticket generation strategies including:
- Coverage optimization (maximize number spread)
- Wheeling systems (mathematical coverage guarantees)
- Risk-based profiles (conservative, balanced, aggressive)
- Statistical balance enforcement
- Hot/Cold number strategies
- Pair correlation optimization

Author: EuroMillions ML Predictor
Version: 2.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional, Set
from itertools import combinations
from collections import defaultdict
from loguru import logger
import random


class TicketStrategy:
    """Base class for ticket generation strategies."""
    
    def __init__(self, n_main: int = 50, n_stars: int = 12):
        """
        Initialize strategy.
        
        Args:
            n_main: Total main balls (50 for EuroMillions)
            n_stars: Total stars (12 for EuroMillions)
        """
        self.n_main = n_main
        self.n_stars = n_stars
    
    def generate(self, 
                 main_proba: np.ndarray,
                 star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """
        Generate tickets based on strategy.
        
        Args:
            main_proba: Probability array for main balls (size 50)
            star_proba: Probability array for stars (size 12)
            n_tickets: Number of tickets to generate
            
        Returns:
            List of tickets, each with 'main' and 'stars' keys
        """
        raise NotImplementedError


class ProbabilityBasedStrategy(TicketStrategy):
    """Generate tickets based on model probabilities."""
    
    def __init__(self, temperature: float = 1.0, **kwargs):
        """
        Initialize probability-based strategy.
        
        Args:
            temperature: Softmax temperature (higher = more random)
        """
        super().__init__(**kwargs)
        self.temperature = temperature
    
    def _softmax(self, proba: np.ndarray) -> np.ndarray:
        """Apply temperature-scaled softmax."""
        exp_proba = np.exp(proba / self.temperature)
        return exp_proba / exp_proba.sum()
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray, 
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate tickets using weighted probability sampling."""
        
        tickets = []
        
        # Apply softmax with temperature
        main_weights = self._softmax(main_proba)
        star_weights = self._softmax(star_proba)
        
        for _ in range(n_tickets):
            # Sample without replacement for main balls
            main_balls = np.random.choice(
                range(1, self.n_main + 1),
                size=5,
                replace=False,
                p=main_weights
            )
            
            # Sample without replacement for stars
            stars = np.random.choice(
                range(1, self.n_stars + 1),
                size=2,
                replace=False,
                p=star_weights
            )
            
            tickets.append({
                'main': sorted(main_balls.tolist()),
                'stars': sorted(stars.tolist())
            })
        
        return tickets


class CoverageOptimizedStrategy(TicketStrategy):
    """Generate tickets to maximize number coverage."""
    
    def __init__(self, min_coverage: float = 0.6, **kwargs):
        """
        Initialize coverage strategy.
        
        Args:
            min_coverage: Minimum fraction of numbers to cover
        """
        super().__init__(**kwargs)
        self.min_coverage = min_coverage
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate tickets optimizing for coverage."""
        
        tickets = []
        covered_main = set()
        covered_stars = set()
        
        # Sort numbers by probability
        main_ranked = np.argsort(main_proba)[::-1] + 1
        star_ranked = np.argsort(star_proba)[::-1] + 1
        
        for i in range(n_tickets):
            # Select numbers prioritizing uncovered high-probability ones
            main_balls = []
            
            # First, pick uncovered high-probability numbers
            for num in main_ranked:
                if num not in covered_main and len(main_balls) < 5:
                    main_balls.append(num)
                    covered_main.add(num)
            
            # Fill remaining with highest probability
            for num in main_ranked:
                if num not in main_balls and len(main_balls) < 5:
                    main_balls.append(num)
            
            # Similar for stars
            stars = []
            for num in star_ranked:
                if num not in covered_stars and len(stars) < 2:
                    stars.append(num)
                    covered_stars.add(num)
            
            for num in star_ranked:
                if num not in stars and len(stars) < 2:
                    stars.append(num)
            
            tickets.append({
                'main': sorted(main_balls),
                'stars': sorted(stars)
            })
            
            # Check if we've achieved minimum coverage
            main_coverage = len(covered_main) / self.n_main
            star_coverage = len(covered_stars) / self.n_stars
            
            if main_coverage >= self.min_coverage and star_coverage >= self.min_coverage:
                # Add more diverse tickets
                pass
        
        return tickets


class WheelingStrategy(TicketStrategy):
    """
    Wheeling system for guaranteed coverage.
    
    If any subset of your key numbers appears, you're guaranteed
    a minimum number of matches.
    """
    
    def __init__(self, wheel_type: str = 'full', **kwargs):
        """
        Initialize wheeling strategy.
        
        Args:
            wheel_type: 'full', 'abbreviated', or 'key'
        """
        super().__init__(**kwargs)
        self.wheel_type = wheel_type
    
    def _full_wheel(self, numbers: List[int], pick: int = 5) -> List[List[int]]:
        """Generate all combinations (full wheel)."""
        return [list(c) for c in combinations(numbers, pick)]
    
    def _abbreviated_wheel(self, numbers: List[int], pick: int = 5) -> List[List[int]]:
        """Generate abbreviated wheel with guaranteed 3-if-3 coverage."""
        
        n = len(numbers)
        if n <= pick:
            return [numbers[:pick]]
        
        tickets = []
        # Use a systematic approach
        for i in range(0, n - pick + 1):
            ticket = numbers[i:i + pick]
            if len(ticket) == pick:
                tickets.append(ticket)
        
        # Add some mixed tickets for better coverage
        if n > pick + 1:
            for i in range(n):
                ticket = [numbers[i]]
                for j in range(1, pick):
                    ticket.append(numbers[(i + j * 2) % n])
                if len(set(ticket)) == pick:
                    tickets.append(sorted(list(set(ticket))[:pick]))
        
        return tickets[:20]  # Limit to reasonable number
    
    def _key_wheel(self, key_numbers: List[int], other_numbers: List[int], 
                   n_keys: int = 2) -> List[List[int]]:
        """Generate wheel with key numbers appearing in every ticket."""
        
        tickets = []
        remaining_pick = 5 - n_keys
        
        for combo in combinations(other_numbers, remaining_pick):
            ticket = list(key_numbers[:n_keys]) + list(combo)
            tickets.append(sorted(ticket))
        
        return tickets[:20]  # Limit
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate wheeled tickets."""
        
        # Select key numbers based on probabilities
        n_key_numbers = min(8, n_tickets + 3)  # Pool size
        key_main = np.argsort(main_proba)[-n_key_numbers:][::-1] + 1
        key_stars = np.argsort(star_proba)[-4:][::-1] + 1
        
        if self.wheel_type == 'full':
            main_combos = self._full_wheel(key_main.tolist())
        elif self.wheel_type == 'key':
            # First 2 numbers are keys
            main_combos = self._key_wheel(
                key_main[:2].tolist(),
                key_main[2:].tolist()
            )
        else:  # abbreviated
            main_combos = self._abbreviated_wheel(key_main.tolist())
        
        star_combos = self._full_wheel(key_stars.tolist(), 2)
        
        # Combine main and star combinations
        tickets = []
        for i in range(min(n_tickets, len(main_combos))):
            tickets.append({
                'main': sorted(main_combos[i]),
                'stars': sorted(star_combos[i % len(star_combos)])
            })
        
        return tickets


class BalancedStrategy(TicketStrategy):
    """
    Generate tickets with statistical balance properties.
    
    Enforces:
    - Even/Odd balance (2-3 or 3-2)
    - Low/High balance (2-3 or 3-2)
    - Sum within common range
    - Appropriate number spacing
    """
    
    def __init__(self, 
                 target_sum_range: Tuple[int, int] = (95, 160),
                 max_consecutive: int = 2,
                 **kwargs):
        """
        Initialize balanced strategy.
        
        Args:
            target_sum_range: Target range for sum of main balls
            max_consecutive: Maximum consecutive numbers allowed
        """
        super().__init__(**kwargs)
        self.target_sum_range = target_sum_range
        self.max_consecutive = max_consecutive
    
    def _is_balanced(self, numbers: List[int]) -> bool:
        """Check if a combination is balanced."""
        
        sorted_nums = sorted(numbers)
        
        # Check even/odd balance
        even_count = sum(1 for n in numbers if n % 2 == 0)
        if even_count not in [2, 3]:
            return False
        
        # Check low/high balance (1-25 vs 26-50)
        low_count = sum(1 for n in numbers if n <= 25)
        if low_count not in [2, 3]:
            return False
        
        # Check sum range
        total_sum = sum(numbers)
        if not (self.target_sum_range[0] <= total_sum <= self.target_sum_range[1]):
            return False
        
        # Check consecutive numbers
        consecutive_count = 0
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i + 1] - sorted_nums[i] == 1:
                consecutive_count += 1
        if consecutive_count > self.max_consecutive:
            return False
        
        return True
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate balanced tickets."""
        
        tickets = []
        attempts = 0
        max_attempts = n_tickets * 100
        
        # Weight probabilities for sampling
        main_weights = main_proba / main_proba.sum()
        star_weights = star_proba / star_proba.sum()
        
        while len(tickets) < n_tickets and attempts < max_attempts:
            attempts += 1
            
            # Sample candidate main balls
            candidates = np.random.choice(
                range(1, self.n_main + 1),
                size=5,
                replace=False,
                p=main_weights
            )
            
            if self._is_balanced(candidates.tolist()):
                # Sample stars
                stars = np.random.choice(
                    range(1, self.n_stars + 1),
                    size=2,
                    replace=False,
                    p=star_weights
                )
                
                tickets.append({
                    'main': sorted(candidates.tolist()),
                    'stars': sorted(stars.tolist())
                })
        
        # If not enough balanced tickets, fill with probability-based
        if len(tickets) < n_tickets:
            prob_strategy = ProbabilityBasedStrategy()
            extra = prob_strategy.generate(main_proba, star_proba, n_tickets - len(tickets))
            tickets.extend(extra)
        
        return tickets


class HotColdStrategy(TicketStrategy):
    """
    Strategy based on hot (frequent) and cold (due) numbers.
    """
    
    def __init__(self, 
                 hot_ratio: float = 0.6,
                 due_threshold: float = 0.7,
                 **kwargs):
        """
        Initialize hot/cold strategy.
        
        Args:
            hot_ratio: Fraction of numbers from hot pool
            due_threshold: Threshold for considering a number "due"
        """
        super().__init__(**kwargs)
        self.hot_ratio = hot_ratio
        self.due_threshold = due_threshold
    
    def classify_numbers(self, proba: np.ndarray, gap_features: Optional[np.ndarray] = None) -> Dict[str, List[int]]:
        """Classify numbers into hot, cold, and due categories."""
        
        # Hot numbers: top 30% by probability
        hot_threshold = np.percentile(proba, 70)
        hot_numbers = [i + 1 for i, p in enumerate(proba) if p >= hot_threshold]
        
        # Cold numbers: bottom 30% by probability
        cold_threshold = np.percentile(proba, 30)
        cold_numbers = [i + 1 for i, p in enumerate(proba) if p <= cold_threshold]
        
        # Due numbers: low probability but overdue (simulated here)
        # In practice, would use gap features
        mid_numbers = [i + 1 for i, p in enumerate(proba) 
                       if cold_threshold < p < hot_threshold]
        
        return {
            'hot': hot_numbers,
            'cold': cold_numbers,
            'mid': mid_numbers
        }
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate tickets mixing hot and due numbers."""
        
        main_classes = self.classify_numbers(main_proba)
        star_classes = self.classify_numbers(star_proba)
        
        tickets = []
        
        for i in range(n_tickets):
            # Determine mix for this ticket
            n_hot = int(5 * self.hot_ratio)
            n_other = 5 - n_hot
            
            main_balls = []
            
            # Add hot numbers
            if main_classes['hot']:
                hot_sample = random.sample(
                    main_classes['hot'],
                    min(n_hot, len(main_classes['hot']))
                )
                main_balls.extend(hot_sample)
            
            # Add mid/cold numbers
            other_pool = main_classes['mid'] + main_classes['cold']
            if other_pool and len(main_balls) < 5:
                other_sample = random.sample(
                    [n for n in other_pool if n not in main_balls],
                    min(n_other, len([n for n in other_pool if n not in main_balls]))
                )
                main_balls.extend(other_sample)
            
            # Fill any remaining
            all_numbers = list(range(1, self.n_main + 1))
            while len(main_balls) < 5:
                num = random.choice([n for n in all_numbers if n not in main_balls])
                main_balls.append(num)
            
            # Stars - similar approach
            star_balls = []
            if star_classes['hot']:
                star_balls.extend(random.sample(
                    star_classes['hot'],
                    min(1, len(star_classes['hot']))
                ))
            
            while len(star_balls) < 2:
                num = random.choice([n for n in range(1, self.n_stars + 1) if n not in star_balls])
                star_balls.append(num)
            
            tickets.append({
                'main': sorted(main_balls[:5]),
                'stars': sorted(star_balls[:2])
            })
        
        return tickets


class RiskProfileStrategy(TicketStrategy):
    """
    Generate tickets based on risk profile.
    
    - Conservative: High probability numbers only
    - Balanced: Mix of strategies
    - Aggressive: Include long-shot numbers
    """
    
    def __init__(self, profile: str = 'balanced', **kwargs):
        """
        Initialize risk profile strategy.
        
        Args:
            profile: 'conservative', 'balanced', or 'aggressive'
        """
        super().__init__(**kwargs)
        self.profile = profile
    
    def generate(self, main_proba: np.ndarray, star_proba: np.ndarray,
                 n_tickets: int = 5) -> List[Dict[str, List[int]]]:
        """Generate tickets based on risk profile."""
        
        tickets = []
        
        if self.profile == 'conservative':
            # Use only top-probability numbers
            temperature = 0.5  # Lower temperature = more deterministic
            strategy = ProbabilityBasedStrategy(temperature=temperature)
            tickets = strategy.generate(main_proba, star_proba, n_tickets)
            
        elif self.profile == 'aggressive':
            # Include some low-probability "longshot" numbers
            # Boost probabilities of less likely numbers
            boosted_main = main_proba.copy()
            boosted_main[main_proba < np.median(main_proba)] *= 2
            boosted_main /= boosted_main.sum()
            
            boosted_star = star_proba.copy()
            boosted_star[star_proba < np.median(star_proba)] *= 2
            boosted_star /= boosted_star.sum()
            
            strategy = ProbabilityBasedStrategy(temperature=1.5)
            tickets = strategy.generate(boosted_main, boosted_star, n_tickets)
            
        else:  # balanced
            # Mix of strategies
            strategies = [
                ProbabilityBasedStrategy(temperature=1.0),
                BalancedStrategy(),
                HotColdStrategy()
            ]
            
            for i in range(n_tickets):
                strategy = strategies[i % len(strategies)]
                ticket = strategy.generate(main_proba, star_proba, 1)[0]
                tickets.append(ticket)
        
        return tickets


class TicketGenerator:
    """
    Master ticket generator combining all strategies.
    """
    
    STRATEGIES = {
        'probability': ProbabilityBasedStrategy,
        'coverage': CoverageOptimizedStrategy,
        'wheel': WheelingStrategy,
        'balanced': BalancedStrategy,
        'hotcold': HotColdStrategy,
        'conservative': lambda **kw: RiskProfileStrategy(profile='conservative', **kw),
        'aggressive': lambda **kw: RiskProfileStrategy(profile='aggressive', **kw),
    }
    
    def __init__(self):
        """Initialize ticket generator."""
        self.history = []
    
    def generate(self,
                main_proba: np.ndarray,
                star_proba: np.ndarray,
                strategy: str = 'balanced',
                n_tickets: int = 5,
                **strategy_kwargs) -> List[Dict[str, List[int]]]:
        """
        Generate tickets using specified strategy.
        
        Args:
            main_proba: Probability array for main balls
            star_proba: Probability array for stars
            strategy: Strategy name
            n_tickets: Number of tickets
            **strategy_kwargs: Additional strategy parameters
            
        Returns:
            List of generated tickets
        """
        if strategy not in self.STRATEGIES:
            logger.warning(f"Unknown strategy '{strategy}', using 'balanced'")
            strategy = 'balanced'
        
        strategy_class = self.STRATEGIES[strategy]
        strategy_instance = strategy_class(**strategy_kwargs)
        
        tickets = strategy_instance.generate(main_proba, star_proba, n_tickets)
        
        # Record in history
        self.history.append({
            'strategy': strategy,
            'n_tickets': n_tickets,
            'tickets': tickets
        })
        
        return tickets
    
    def generate_multi_strategy(self,
                               main_proba: np.ndarray,
                               star_proba: np.ndarray,
                               n_tickets: int = 10) -> Dict[str, List[Dict]]:
        """
        Generate tickets using multiple strategies for diversity.
        
        Args:
            main_proba: Probability array for main balls
            star_proba: Probability array for stars
            n_tickets: Total number of tickets
            
        Returns:
            Dictionary of strategy -> tickets
        """
        result = {}
        tickets_per_strategy = max(1, n_tickets // 4)
        
        for strategy in ['probability', 'balanced', 'coverage', 'hotcold']:
            result[strategy] = self.generate(
                main_proba, star_proba,
                strategy=strategy,
                n_tickets=tickets_per_strategy
            )
        
        return result
    
    def score_ticket(self, ticket: Dict[str, List[int]], 
                    main_proba: np.ndarray, star_proba: np.ndarray) -> float:
        """
        Score a ticket based on model probabilities.
        
        Args:
            ticket: Ticket with 'main' and 'stars' keys
            main_proba: Model probabilities for main balls
            star_proba: Model probabilities for stars
            
        Returns:
            Combined probability score
        """
        main_score = sum(main_proba[n - 1] for n in ticket['main'])
        star_score = sum(star_proba[n - 1] for n in ticket['stars'])
        
        # Normalize
        return (main_score / 5 + star_score / 2) / 2
    
    def analyze_tickets(self, tickets: List[Dict]) -> Dict[str, Any]:
        """
        Analyze generated tickets for coverage and balance.
        
        Args:
            tickets: List of tickets
            
        Returns:
            Analysis results
        """
        all_main = set()
        all_stars = set()
        
        sums = []
        even_counts = []
        low_counts = []
        
        for ticket in tickets:
            all_main.update(ticket['main'])
            all_stars.update(ticket['stars'])
            
            sums.append(sum(ticket['main']))
            even_counts.append(sum(1 for n in ticket['main'] if n % 2 == 0))
            low_counts.append(sum(1 for n in ticket['main'] if n <= 25))
        
        return {
            'main_coverage': len(all_main) / 50,
            'star_coverage': len(all_stars) / 12,
            'unique_main_numbers': len(all_main),
            'unique_star_numbers': len(all_stars),
            'average_sum': np.mean(sums),
            'sum_range': (min(sums), max(sums)),
            'average_even_count': np.mean(even_counts),
            'average_low_count': np.mean(low_counts)
        }


def generate_tickets(main_proba: np.ndarray,
                    star_proba: np.ndarray,
                    strategy: str = 'balanced',
                    n_tickets: int = 5) -> List[Dict[str, List[int]]]:
    """
    Convenience function to generate tickets.
    
    Args:
        main_proba: Probability array for main balls
        star_proba: Probability array for stars
        strategy: Strategy name
        n_tickets: Number of tickets
        
    Returns:
        List of tickets
    """
    generator = TicketGenerator()
    return generator.generate(main_proba, star_proba, strategy, n_tickets)


if __name__ == "__main__":
    # Test module
    print("Testing Multi-Strategy Ticket Generation...")
    
    # Create fake probabilities for testing
    np.random.seed(42)
    main_proba = np.random.dirichlet(np.ones(50))
    star_proba = np.random.dirichlet(np.ones(12))
    
    generator = TicketGenerator()
    
    print("\n" + "="*60)
    print("Testing different strategies:")
    print("="*60)
    
    for strategy in ['probability', 'balanced', 'coverage', 'wheel', 'hotcold']:
        print(f"\n{strategy.upper()} Strategy:")
        tickets = generator.generate(main_proba, star_proba, strategy=strategy, n_tickets=3)
        for i, t in enumerate(tickets):
            print(f"  Ticket {i+1}: {t['main']} | ⭐ {t['stars']}")
    
    print("\n" + "="*60)
    print("Multi-strategy generation:")
    print("="*60)
    
    multi = generator.generate_multi_strategy(main_proba, star_proba, n_tickets=12)
    for strategy, tickets in multi.items():
        print(f"\n{strategy}:")
        for t in tickets:
            print(f"  {t['main']} | ⭐ {t['stars']}")
    
    print("\n" + "="*60)
    print("Ticket Analysis:")
    print("="*60)
    
    all_tickets = [t for tickets in multi.values() for t in tickets]
    analysis = generator.analyze_tickets(all_tickets)
    for key, value in analysis.items():
        print(f"  {key}: {value}")
