"""
Advanced Feature Engineering V2 for EuroMillions Prediction
=============================================================

This module provides sophisticated feature extraction techniques including:
- Pair/Triplet co-occurrence analysis
- Exponential decay hot/cold scoring
- Advanced gap analysis with statistical measures
- Seasonal and cyclical patterns
- Mathematical balance features
- Number spacing and distribution features
- Historical pattern matching

Author: EuroMillions ML Predictor
Version: 2.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import combinations
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


class AdvancedFeatureExtractorV2:
    """
    Advanced feature extractor for EuroMillions lottery prediction.
    
    Implements multiple sophisticated feature engineering techniques
    to capture complex patterns in lottery draw data.
    """
    
    def __init__(self, 
                 window_sizes: List[int] = [10, 30, 50, 100],
                 decay_factor: float = 0.95,
                 n_main_balls: int = 50,
                 n_stars: int = 12):
        """
        Initialize the feature extractor.
        
        Args:
            window_sizes: List of window sizes for multi-scale analysis
            decay_factor: Exponential decay factor for recency weighting (0-1)
            n_main_balls: Number of main balls (default 50 for EuroMillions)
            n_stars: Number of star balls (default 12 for EuroMillions)
        """
        self.window_sizes = sorted(window_sizes)
        self.decay_factor = decay_factor
        self.n_main_balls = n_main_balls
        self.n_stars = n_stars
        
        # Pair/triplet tracking
        self.pair_counts = defaultdict(int)
        self.triplet_counts = defaultdict(int)
        self.star_pair_counts = defaultdict(int)
        
        # Feature names for documentation
        self.feature_names = []
        
        logger.info(f"AdvancedFeatureExtractorV2 initialized with windows: {window_sizes}")
    
    def extract_all_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Extract all advanced features from historical draw data.
        
        Args:
            df: DataFrame with columns [draw_date, n1-n5, s1-s2]
            
        Returns:
            Tuple of (X_main, y_main, X_star, y_star, metadata)
        """
        logger.info(f"Extracting advanced features from {len(df)} draws")
        
        df = df.sort_values('draw_date').reset_index(drop=True)
        n_draws = len(df)
        n_samples = n_draws - 1
        
        # Initialize feature collectors
        all_features_main = []
        all_features_star = []
        
        # Pre-compute pair and triplet frequencies
        self._build_cooccurrence_matrices(df)
        
        for i in range(n_samples):
            historical_df = df.iloc[:i+1]
            current_draw = df.iloc[i]
            
            # Extract per-ball features for main numbers
            main_features = self._extract_main_ball_features(historical_df, i)
            
            # Extract per-ball features for stars
            star_features = self._extract_star_features(historical_df, i)
            
            # Extract global draw features
            global_features = self._extract_global_features(historical_df, current_draw)
            
            # Combine features
            main_with_global = np.concatenate([main_features, global_features])
            star_with_global = np.concatenate([star_features, global_features])
            
            all_features_main.append(main_with_global)
            all_features_star.append(star_with_global)
        
        X_main = np.array(all_features_main)
        X_star = np.array(all_features_star)
        
        # Create labels
        y_main, y_star = self._create_labels(df)
        
        metadata = {
            "n_samples": n_samples,
            "n_main_features": X_main.shape[1],
            "n_star_features": X_star.shape[1],
            "window_sizes": self.window_sizes,
            "decay_factor": self.decay_factor,
            "feature_categories": [
                "multi_window_frequency",
                "exponential_decay_score",
                "gap_statistics",
                "pair_cooccurrence",
                "triplet_cooccurrence", 
                "streak_features",
                "distribution_balance",
                "temporal_patterns"
            ]
        }
        
        logger.info(f"Extracted features: main={X_main.shape}, star={X_star.shape}")
        
        return X_main, y_main, X_star, y_star, metadata
    
    def _build_cooccurrence_matrices(self, df: pd.DataFrame):
        """Build pair and triplet co-occurrence matrices from historical data."""
        
        self.pair_counts = defaultdict(int)
        self.triplet_counts = defaultdict(int)
        self.star_pair_counts = defaultdict(int)
        
        for _, row in df.iterrows():
            balls = sorted([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
            stars = sorted([row['s1'], row['s2']])
            
            # Count pairs
            for pair in combinations(balls, 2):
                self.pair_counts[pair] += 1
            
            # Count triplets
            for triplet in combinations(balls, 3):
                self.triplet_counts[triplet] += 1
            
            # Star pair
            self.star_pair_counts[tuple(stars)] += 1
        
        logger.debug(f"Built co-occurrence: {len(self.pair_counts)} pairs, {len(self.triplet_counts)} triplets")
    
    def _extract_main_ball_features(self, historical_df: pd.DataFrame, current_idx: int) -> np.ndarray:
        """Extract features for each main ball (1-50)."""
        
        features = []
        
        # Get all drawn balls as a list for each draw
        all_balls = []
        for _, row in historical_df.iterrows():
            all_balls.append([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
        
        for ball_num in range(1, self.n_main_balls + 1):
            ball_features = []
            
            # 1. Multi-window frequency (normalized)
            for window in self.window_sizes:
                window_start = max(0, len(historical_df) - window)
                window_data = all_balls[window_start:]
                count = sum(1 for draw in window_data if ball_num in draw)
                freq = count / max(1, len(window_data))
                ball_features.append(freq)
            
            # 2. Exponential decay score (recent appearances weighted more)
            decay_score = 0.0
            for j, draw in enumerate(reversed(all_balls)):
                weight = self.decay_factor ** j
                if ball_num in draw:
                    decay_score += weight
            ball_features.append(decay_score)
            
            # 3. Gap since last appearance
            gap = self._calculate_gap(all_balls, ball_num)
            ball_features.append(gap)
            
            # 4. Gap statistics (mean, std, max gap historically)
            gap_stats = self._calculate_gap_statistics(all_balls, ball_num)
            ball_features.extend(gap_stats)
            
            # 5. Streak features (consecutive appearances/absences)
            streak = self._calculate_streak(all_balls, ball_num)
            ball_features.append(streak)
            
            # 6. Pair strength (average co-occurrence with recent drawn numbers)
            pair_strength = self._calculate_pair_strength(ball_num, all_balls[-10:] if len(all_balls) >= 10 else all_balls)
            ball_features.append(pair_strength)
            
            # 7. Due score (gap vs expected frequency)
            due_score = self._calculate_due_score(gap, len(all_balls))
            ball_features.append(due_score)
            
            features.extend(ball_features)
        
        return np.array(features)
    
    def _extract_star_features(self, historical_df: pd.DataFrame, current_idx: int) -> np.ndarray:
        """Extract features for each star (1-12)."""
        
        features = []
        
        # Get all drawn stars
        all_stars = []
        for _, row in historical_df.iterrows():
            all_stars.append([row['s1'], row['s2']])
        
        for star_num in range(1, self.n_stars + 1):
            star_features = []
            
            # 1. Multi-window frequency
            for window in self.window_sizes:
                window_start = max(0, len(historical_df) - window)
                window_data = all_stars[window_start:]
                count = sum(1 for draw in window_data if star_num in draw)
                freq = count / max(1, len(window_data))
                star_features.append(freq)
            
            # 2. Exponential decay score
            decay_score = 0.0
            for j, draw in enumerate(reversed(all_stars)):
                weight = self.decay_factor ** j
                if star_num in draw:
                    decay_score += weight
            star_features.append(decay_score)
            
            # 3. Gap since last appearance
            gap = self._calculate_gap(all_stars, star_num)
            star_features.append(gap)
            
            # 4. Gap statistics
            gap_stats = self._calculate_gap_statistics(all_stars, star_num)
            star_features.extend(gap_stats)
            
            # 5. Streak
            streak = self._calculate_streak(all_stars, star_num)
            star_features.append(streak)
            
            # 6. Due score
            due_score = self._calculate_star_due_score(gap, len(all_stars))
            star_features.append(due_score)
            
            features.extend(star_features)
        
        return np.array(features)
    
    def _extract_global_features(self, historical_df: pd.DataFrame, current_draw: pd.Series) -> np.ndarray:
        """Extract global/contextual features."""
        
        features = []
        
        # Current draw statistics
        current_balls = sorted([current_draw['n1'], current_draw['n2'], 
                               current_draw['n3'], current_draw['n4'], current_draw['n5']])
        current_stars = sorted([current_draw['s1'], current_draw['s2']])
        
        # 1. Sum statistics
        ball_sum = sum(current_balls)
        star_sum = sum(current_stars)
        features.extend([ball_sum / 175, star_sum / 15])  # Normalized
        
        # 2. Even/Odd balance
        even_count = sum(1 for b in current_balls if b % 2 == 0)
        features.append(even_count / 5)
        
        # 3. Low/High balance (1-25 vs 26-50)
        low_count = sum(1 for b in current_balls if b <= 25)
        features.append(low_count / 5)
        
        # 4. Consecutive number count
        consecutive = sum(1 for i in range(len(current_balls)-1) 
                         if current_balls[i+1] - current_balls[i] == 1)
        features.append(consecutive / 4)
        
        # 5. Number spread (range)
        spread = current_balls[-1] - current_balls[0]
        features.append(spread / 49)
        
        # 6. Gap variance between numbers
        gaps = [current_balls[i+1] - current_balls[i] for i in range(len(current_balls)-1)]
        gap_variance = np.var(gaps) if gaps else 0
        features.append(gap_variance / 100)
        
        # 7. Temporal features
        draw_date = pd.to_datetime(current_draw['draw_date'])
        day_of_week = draw_date.dayofweek / 6
        month = draw_date.month / 12
        day_of_year = draw_date.dayofyear / 365
        
        # Cyclical encoding
        features.extend([
            np.sin(2 * np.pi * day_of_week),
            np.cos(2 * np.pi * day_of_week),
            np.sin(2 * np.pi * month),
            np.cos(2 * np.pi * month),
            np.sin(2 * np.pi * day_of_year),
            np.cos(2 * np.pi * day_of_year)
        ])
        
        # 8. Historical statistics from recent draws
        if len(historical_df) >= 10:
            recent_sums = []
            for _, row in historical_df.tail(10).iterrows():
                recent_sums.append(row['n1'] + row['n2'] + row['n3'] + row['n4'] + row['n5'])
            features.append(np.mean(recent_sums) / 175)
            features.append(np.std(recent_sums) / 50)
        else:
            features.extend([0.5, 0.1])
        
        return np.array(features)
    
    def _calculate_gap(self, draws: List[List[int]], number: int) -> float:
        """Calculate gap since last appearance of a number."""
        for i, draw in enumerate(reversed(draws)):
            if number in draw:
                return i
        return len(draws)  # Never appeared
    
    def _calculate_gap_statistics(self, draws: List[List[int]], number: int) -> List[float]:
        """Calculate gap statistics for a number."""
        gaps = []
        current_gap = 0
        
        for draw in draws:
            if number in draw:
                if current_gap > 0:
                    gaps.append(current_gap)
                current_gap = 0
            else:
                current_gap += 1
        
        if gaps:
            return [float(np.mean(gaps)), float(np.std(gaps)), float(max(gaps))]
        return [float(len(draws)), 0.0, float(len(draws))]
    
    def _calculate_streak(self, draws: List[List[int]], number: int) -> float:
        """Calculate current streak (positive = appearing, negative = absent)."""
        streak = 0
        appearing = None
        
        for draw in reversed(draws):
            if appearing is None:
                appearing = number in draw
                streak = 1 if appearing else -1
            elif (number in draw) == appearing:
                streak += 1 if appearing else -1
            else:
                break
        
        return streak
    
    def _calculate_pair_strength(self, number: int, recent_draws: List[List[int]]) -> float:
        """Calculate average pair strength with recently drawn numbers."""
        recent_numbers = set()
        for draw in recent_draws:
            recent_numbers.update(draw)
        
        if not recent_numbers:
            return 0.0
        
        strengths = []
        for other in recent_numbers:
            if other != number:
                pair = tuple(sorted([number, other]))
                strengths.append(self.pair_counts.get(pair, 0))
        
        return float(np.mean(strengths)) if strengths else 0.0
    
    def _calculate_due_score(self, gap: float, total_draws: int) -> float:
        """Calculate how 'due' a number is based on gap vs expected frequency."""
        # For main balls: 5/50 = 10% chance each draw
        # Expected gap between appearances: ~10 draws
        expected_gap = 10
        if total_draws > 0:
            return (gap - expected_gap) / max(1, expected_gap)
        return 0.0
    
    def _calculate_star_due_score(self, gap: float, total_draws: int) -> float:
        """Calculate how 'due' a star is based on gap vs expected frequency."""
        # For stars: 2/12 = 16.67% chance each draw
        # Expected gap between appearances: ~6 draws
        expected_gap = 6
        if total_draws > 0:
            return (gap - expected_gap) / max(1, expected_gap)
        return 0.0
    
    def _create_labels(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Create binary labels for next draw prediction."""
        n_samples = len(df) - 1
        
        y_main = np.zeros((n_samples, self.n_main_balls), dtype=int)
        y_star = np.zeros((n_samples, self.n_stars), dtype=int)
        
        for i in range(n_samples):
            next_draw = df.iloc[i + 1]
            
            # Main ball labels
            for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
                y_main[i, int(next_draw[col]) - 1] = 1
            
            # Star labels
            for col in ['s1', 's2']:
                y_star[i, int(next_draw[col]) - 1] = 1
        
        return y_main, y_star


class MathematicalBalanceFeatures:
    """
    Mathematical feature extractor focusing on number theory
    and statistical balance properties.
    """
    
    @staticmethod
    def extract_balance_features(numbers: List[int], max_val: int = 50) -> Dict[str, float]:
        """
        Extract mathematical balance features from a set of numbers.
        
        Args:
            numbers: List of drawn numbers
            max_val: Maximum possible value
            
        Returns:
            Dictionary of balance features
        """
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        
        features = {}
        
        # Sum features
        total_sum = sum(sorted_nums)
        expected_sum = n * (max_val + 1) / 2
        features['sum_deviation'] = (total_sum - expected_sum) / expected_sum
        features['sum_normalized'] = total_sum / (n * max_val)
        
        # Range and spread
        features['range'] = sorted_nums[-1] - sorted_nums[0]
        features['range_ratio'] = features['range'] / (max_val - 1)
        
        # Gaps between consecutive numbers
        gaps = [sorted_nums[i+1] - sorted_nums[i] for i in range(n-1)]
        features['avg_gap'] = np.mean(gaps)
        features['gap_variance'] = np.var(gaps)
        features['max_gap'] = max(gaps)
        features['min_gap'] = min(gaps)
        features['gap_uniformity'] = 1 - (np.std(gaps) / np.mean(gaps)) if np.mean(gaps) > 0 else 0
        
        # Distribution in thirds
        third_1 = sum(1 for x in sorted_nums if x <= max_val/3)
        third_2 = sum(1 for x in sorted_nums if max_val/3 < x <= 2*max_val/3)
        third_3 = sum(1 for x in sorted_nums if x > 2*max_val/3)
        features['third_balance'] = 1 - np.std([third_1, third_2, third_3]) / (n/3)
        
        # Even/Odd balance
        even_count = sum(1 for x in sorted_nums if x % 2 == 0)
        features['even_ratio'] = even_count / n
        features['even_odd_balance'] = 1 - abs(even_count - (n - even_count)) / n
        
        # Low/High balance
        low_count = sum(1 for x in sorted_nums if x <= max_val/2)
        features['low_ratio'] = low_count / n
        features['low_high_balance'] = 1 - abs(low_count - (n - low_count)) / n
        
        # Prime numbers
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}
        prime_count = sum(1 for x in sorted_nums if x in primes)
        features['prime_ratio'] = prime_count / n
        
        # Consecutive pairs
        consecutive_count = sum(1 for i in range(n-1) if sorted_nums[i+1] - sorted_nums[i] == 1)
        features['consecutive_ratio'] = consecutive_count / (n - 1)
        
        # Decade distribution (1-10, 11-20, etc.)
        decades = [0] * 5
        for x in sorted_nums:
            decade = min((x - 1) // 10, 4)
            decades[decade] += 1
        features['decade_spread'] = sum(1 for d in decades if d > 0) / 5
        features['decade_variance'] = np.var(decades)
        
        return features
    
    @staticmethod
    def calculate_entropy(numbers: List[int], max_val: int = 50) -> float:
        """Calculate entropy of number distribution."""
        # Bin numbers into groups
        bins = 5
        bin_size = max_val // bins
        counts = [0] * bins
        
        for n in numbers:
            bin_idx = min((n - 1) // bin_size, bins - 1)
            counts[bin_idx] += 1
        
        # Calculate entropy
        total = len(numbers)
        entropy = 0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return entropy / np.log2(bins)  # Normalized


class SequencePatternAnalyzer:
    """
    Analyzes sequential patterns in lottery draws.
    """
    
    def __init__(self, max_pattern_length: int = 5):
        """
        Initialize pattern analyzer.
        
        Args:
            max_pattern_length: Maximum pattern length to search for
        """
        self.max_pattern_length = max_pattern_length
        self.patterns = {}
    
    def find_repeating_patterns(self, draws: List[List[int]]) -> Dict[str, Any]:
        """
        Find repeating patterns across draws.
        
        Args:
            draws: List of draws (each draw is a list of numbers)
            
        Returns:
            Dictionary of found patterns and their frequencies
        """
        patterns = {
            'pair_repeats': defaultdict(int),
            'number_follows': defaultdict(lambda: defaultdict(int)),
            'gap_patterns': [],
        }
        
        # Analyze pair repetitions across consecutive draws
        for i in range(1, len(draws)):
            prev_draw = set(draws[i-1])
            curr_draw = set(draws[i])
            
            # Numbers that repeated
            repeated = prev_draw & curr_draw
            for num in repeated:
                patterns['pair_repeats'][num] += 1
            
            # Numbers that follow other numbers
            for prev_num in prev_draw:
                for curr_num in curr_draw:
                    patterns['number_follows'][prev_num][curr_num] += 1
        
        # Analyze gap patterns
        for num in range(1, 51):
            gaps = []
            current_gap = 0
            for draw in draws:
                if num in draw:
                    if current_gap > 0:
                        gaps.append(current_gap)
                    current_gap = 0
                else:
                    current_gap += 1
            
            if len(gaps) >= 5:
                patterns['gap_patterns'].append({
                    'number': num,
                    'mean_gap': np.mean(gaps),
                    'std_gap': np.std(gaps),
                    'max_gap': max(gaps),
                    'min_gap': min(gaps)
                })
        
        return patterns
    
    def get_follow_probabilities(self, draws: List[List[int]], last_draw: List[int]) -> np.ndarray:
        """
        Get probabilities of each number appearing based on last draw.
        
        Args:
            draws: Historical draws
            last_draw: Most recent draw
            
        Returns:
            Array of probabilities for numbers 1-50
        """
        patterns = self.find_repeating_patterns(draws)
        follow_probs = np.zeros(50)
        
        for prev_num in last_draw:
            if prev_num in patterns['number_follows']:
                follows = patterns['number_follows'][prev_num]
                total = sum(follows.values())
                for next_num, count in follows.items():
                    if 1 <= next_num <= 50:
                        follow_probs[next_num - 1] += count / total
        
        # Normalize
        if follow_probs.sum() > 0:
            follow_probs /= follow_probs.sum()
        
        return follow_probs


class PairTripletAnalyzer:
    """
    Analyzes pair and triplet co-occurrence patterns.
    """
    
    def __init__(self):
        self.pair_matrix = None
        self.triplet_freq = None
        self.star_pair_matrix = None
    
    def build_cooccurrence_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """Build a 50x50 co-occurrence matrix for main balls."""
        
        self.pair_matrix = np.zeros((50, 50), dtype=int)
        
        for _, row in df.iterrows():
            balls = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
            for i, b1 in enumerate(balls):
                for b2 in balls[i+1:]:
                    self.pair_matrix[b1-1, b2-1] += 1
                    self.pair_matrix[b2-1, b1-1] += 1
        
        return self.pair_matrix
    
    def build_star_cooccurrence_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """Build a 12x12 co-occurrence matrix for stars."""
        
        self.star_pair_matrix = np.zeros((12, 12), dtype=int)
        
        for _, row in df.iterrows():
            s1, s2 = row['s1'], row['s2']
            self.star_pair_matrix[s1-1, s2-1] += 1
            self.star_pair_matrix[s2-1, s1-1] += 1
        
        return self.star_pair_matrix
    
    def get_best_pairs(self, number: int, top_k: int = 5) -> List[Tuple[int, int]]:
        """Get the numbers that most frequently appear with a given number."""
        
        if self.pair_matrix is None:
            return []
        
        row = self.pair_matrix[number - 1].copy()
        top_indices = np.argsort(row)[-top_k:][::-1]
        
        return [(idx + 1, row[idx]) for idx in top_indices if row[idx] > 0]
    
    def get_pair_score(self, numbers: List[int]) -> float:
        """Calculate the average pair score for a combination."""
        
        if self.pair_matrix is None:
            return 0.0
        
        total_score = 0
        pair_count = 0
        
        for i, n1 in enumerate(numbers):
            for n2 in numbers[i+1:]:
                total_score += self.pair_matrix[n1-1, n2-1]
                pair_count += 1
        
        return total_score / pair_count if pair_count > 0 else 0.0


def build_advanced_datasets_v2(df: pd.DataFrame, 
                               window_sizes: List[int] = [10, 30, 50, 100],
                               decay_factor: float = 0.95) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict]:
    """
    Build datasets using advanced feature extraction V2.
    
    This is the main entry point for the advanced feature engineering module.
    
    Args:
        df: DataFrame with draw data
        window_sizes: List of rolling window sizes
        decay_factor: Exponential decay factor
        
    Returns:
        Tuple of (X_main, y_main, X_star, y_star, metadata)
    """
    extractor = AdvancedFeatureExtractorV2(
        window_sizes=window_sizes,
        decay_factor=decay_factor
    )
    
    return extractor.extract_all_features(df)


# Convenience function for integration
def get_advanced_feature_names_v2(n_main: int = 50, n_star: int = 12, 
                                   window_sizes: List[int] = [10, 30, 50, 100]) -> Dict[str, List[str]]:
    """Get feature names for documentation."""
    
    # Per-ball features (for each of 50 main balls)
    per_ball_features = [
        *[f'freq_w{w}' for w in window_sizes],
        'decay_score',
        'gap_current',
        'gap_mean',
        'gap_std', 
        'gap_max',
        'streak',
        'pair_strength',
        'due_score'
    ]
    
    # Global features
    global_features = [
        'sum_normalized',
        'star_sum_normalized',
        'even_ratio',
        'low_ratio',
        'consecutive_ratio',
        'spread_normalized',
        'gap_variance',
        'day_sin', 'day_cos',
        'month_sin', 'month_cos',
        'year_sin', 'year_cos',
        'recent_sum_mean',
        'recent_sum_std'
    ]
    
    main_features = [f'ball_{i}_{feat}' for i in range(1, n_main+1) for feat in per_ball_features]
    main_features.extend(global_features)
    
    star_per_ball = [
        *[f'freq_w{w}' for w in window_sizes],
        'decay_score',
        'gap_current',
        'gap_mean',
        'gap_std',
        'gap_max', 
        'streak',
        'due_score'
    ]
    
    star_features = [f'star_{i}_{feat}' for i in range(1, n_star+1) for feat in star_per_ball]
    star_features.extend(global_features)
    
    return {
        'main': main_features,
        'star': star_features,
        'global': global_features
    }


if __name__ == "__main__":
    # Test the module
    from repository import get_repository
    
    print("Testing Advanced Feature Extraction V2...")
    repo = get_repository()
    df = repo.all_draws_df()
    
    if len(df) > 100:
        print(f"Using {len(df)} draws for testing")
        X_main, y_main, X_star, y_star, meta = build_advanced_datasets_v2(df.tail(200))
        
        print(f"\nFeature shapes:")
        print(f"  X_main: {X_main.shape}")
        print(f"  y_main: {y_main.shape}")
        print(f"  X_star: {X_star.shape}")
        print(f"  y_star: {y_star.shape}")
        print(f"\nMetadata: {meta}")
    else:
        print("Not enough data for testing")
