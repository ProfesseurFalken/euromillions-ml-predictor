"""
Advanced Feature Engineering for EuroMillions Prediction
========================================================

This module implements sophisticated features to improve prediction accuracy:
1. Multi-scale temporal patterns
2. Number interaction patterns
3. Position-aware features
4. Statistical distribution features
5. Momentum indicators
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from loguru import logger


def build_advanced_features(df: pd.DataFrame, window_sizes: list = [10, 30, 100]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build advanced prediction features with multiple improvements.
    
    Key improvements:
    1. Multi-window frequency analysis (short/medium/long term)
    2. Position-specific patterns (some numbers appear more in certain positions)
    3. Number pairing analysis (numbers that often appear together)
    4. Hot/cold indicators (momentum)
    5. Statistical distribution features (variance, entropy)
    6. Cyclical patterns (day of week, month effects)
    
    Args:
        df: DataFrame with historical draws
        window_sizes: List of window sizes for multi-scale analysis
        
    Returns:
        X_main, y_main, X_star, y_star, metadata
    """
    logger.info("Building advanced features with improved prediction capabilities")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    df = df.sort_values('draw_date').reset_index(drop=True)
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    
    n_draws = len(df)
    n_samples = n_draws - 1
    
    # Feature dimensions per number:
    # - 3 frequencies (short/medium/long windows)
    # - gap since last
    # - streak
    # - position frequency (how often in each position 1-5)
    # - hot/cold indicator
    # - pair frequency (appears with high-frequency numbers)
    # - variance of gaps
    # - cyclical (day of week, month)
    n_base_features = 15  # Increased from 4
    
    X_main = np.zeros((n_samples, 50 * n_base_features))
    X_star = np.zeros((n_samples, 12 * 8))  # Stars have simpler features
    y_main = np.zeros((n_samples, 50), dtype=int)
    y_star = np.zeros((n_samples, 12), dtype=int)
    
    # Tracking structures
    main_counts = {w: np.zeros(50) for w in window_sizes}
    star_counts = {w: np.zeros(12) for w in window_sizes}
    main_last_seen = np.full(50, -1)
    star_last_seen = np.full(12, -1)
    main_position_counts = np.zeros((50, 5))  # 50 numbers × 5 positions
    main_gaps_history = {i: [] for i in range(50)}  # Track gap history
    star_gaps_history = {i: [] for i in range(12)}
    main_streaks = np.zeros(50)
    star_streaks = np.zeros(12)
    main_pair_counts = np.zeros((50, 50))  # Co-occurrence matrix
    
    logger.info(f"Processing {n_samples} samples with {n_base_features} features per number")
    
    for i in range(n_samples):
        current_draw = df.iloc[i]
        next_draw = df.iloc[i + 1]
        
        # Extract numbers (0-based)
        current_main = [current_draw[f'n{j}'] - 1 for j in range(1, 6)]
        current_stars = [current_draw['s1'] - 1, current_draw['s2'] - 1]
        next_main = [next_draw[f'n{j}'] - 1 for j in range(1, 6)]
        next_stars = [next_draw['s1'] - 1, next_draw['s2'] - 1]
        
        # Extract temporal features
        day_of_week = current_draw['draw_date'].dayofweek / 6.0  # Normalize 0-1
        month = current_draw['draw_date'].month / 12.0  # Normalize 0-1
        
        # Update position-specific counts
        for pos, ball in enumerate(current_main):
            main_position_counts[ball, pos] += 1
        
        # Update pair co-occurrence
        for b1 in current_main:
            for b2 in current_main:
                if b1 != b2:
                    main_pair_counts[b1, b2] += 1
        
        # Update all window frequencies
        for window in window_sizes:
            for ball in current_main:
                main_counts[window][ball] += 1
            for star in current_stars:
                star_counts[window][star] += 1
            
            # Remove old counts outside window
            if i >= window:
                old_draw = df.iloc[i - window]
                old_main = [old_draw[f'n{j}'] - 1 for j in range(1, 6)]
                old_stars = [old_draw['s1'] - 1, old_draw['s2'] - 1]
                for ball in old_main:
                    main_counts[window][ball] = max(0, main_counts[window][ball] - 1)
                for star in old_stars:
                    star_counts[window][star] = max(0, star_counts[window][star] - 1)
        
        # Update gaps and streaks
        for ball in range(50):
            if ball in current_main:
                if main_last_seen[ball] >= 0:
                    gap = i - main_last_seen[ball]
                    main_gaps_history[ball].append(gap)
                    if len(main_gaps_history[ball]) > 20:  # Keep last 20 gaps
                        main_gaps_history[ball].pop(0)
                main_last_seen[ball] = i
                main_streaks[ball] = max(1, main_streaks[ball] + 1) if main_streaks[ball] >= 0 else 1
            else:
                main_streaks[ball] = min(-1, main_streaks[ball] - 1) if main_streaks[ball] <= 0 else -1
        
        for star in range(12):
            if star in current_stars:
                if star_last_seen[star] >= 0:
                    gap = i - star_last_seen[star]
                    star_gaps_history[star].append(gap)
                    if len(star_gaps_history[star]) > 20:
                        star_gaps_history[star].pop(0)
                star_last_seen[star] = i
                star_streaks[star] = max(1, star_streaks[star] + 1) if star_streaks[star] >= 0 else 1
            else:
                star_streaks[star] = min(-1, star_streaks[star] - 1) if star_streaks[star] <= 0 else -1
        
        # Build features for each main ball
        feature_idx = 0
        for ball in range(50):
            features = []
            
            # Multi-scale frequencies
            for window in window_sizes:
                eff_window = min(window, i + 1)
                freq = main_counts[window][ball] / eff_window if eff_window > 0 else 0
                features.append(freq)
            
            # Gap features
            current_gap = (i - main_last_seen[ball]) if main_last_seen[ball] >= 0 else i + 1
            features.append(min(current_gap / 100.0, 1.0))  # Normalize gap
            
            # Streak
            features.append(np.tanh(main_streaks[ball] / 5.0))  # Normalized streak
            
            # Position preferences (5 features)
            total_appearances = main_position_counts[ball].sum()
            if total_appearances > 0:
                position_prefs = main_position_counts[ball] / total_appearances
            else:
                position_prefs = np.ones(5) * 0.2  # Uniform if never seen
            features.extend(position_prefs)
            
            # Hot/cold indicator based on recent vs long-term frequency
            if i > window_sizes[0]:
                recent_freq = main_counts[window_sizes[0]][ball] / window_sizes[0]
                long_freq = main_counts[window_sizes[-1]][ball] / min(window_sizes[-1], i + 1)
                momentum = recent_freq - long_freq  # Positive = getting hotter
                features.append(momentum)
            else:
                features.append(0.0)
            
            # Pair frequency (appears with popular numbers)
            if i > 10:
                # Find top 10 most frequent numbers in long window
                top_numbers = np.argsort(main_counts[window_sizes[-1]])[-10:]
                pair_score = sum(main_pair_counts[ball, n] for n in top_numbers if n != ball)
                pair_score = pair_score / (i + 1) if i > 0 else 0
                features.append(pair_score)
            else:
                features.append(0.0)
            
            # Gap variance (consistency indicator)
            if len(main_gaps_history[ball]) > 2:
                gap_var = np.var(main_gaps_history[ball])
                features.append(min(gap_var / 100.0, 1.0))  # Normalized
            else:
                features.append(0.0)
            
            # Temporal features
            features.append(day_of_week)
            features.append(month)
            
            # Add features to matrix
            X_main[i, feature_idx:feature_idx + n_base_features] = features
            feature_idx += n_base_features
        
        # Build simpler features for stars (8 features per star)
        feature_idx = 0
        for star in range(12):
            features = []
            
            # Multi-scale frequencies
            for window in window_sizes:
                eff_window = min(window, i + 1)
                freq = star_counts[window][star] / eff_window if eff_window > 0 else 0
                features.append(freq)
            
            # Gap
            current_gap = (i - star_last_seen[star]) if star_last_seen[star] >= 0 else i + 1
            features.append(min(current_gap / 100.0, 1.0))
            
            # Streak
            features.append(np.tanh(star_streaks[star] / 5.0))
            
            # Hot/cold
            if i > window_sizes[0]:
                recent_freq = star_counts[window_sizes[0]][star] / window_sizes[0]
                long_freq = star_counts[window_sizes[-1]][star] / min(window_sizes[-1], i + 1)
                momentum = recent_freq - long_freq
                features.append(momentum)
            else:
                features.append(0.0)
            
            # Gap variance
            if len(star_gaps_history[star]) > 2:
                gap_var = np.var(star_gaps_history[star])
                features.append(min(gap_var / 100.0, 1.0))
            else:
                features.append(0.0)
            
            # Temporal
            features.append(day_of_week)
            
            X_star[i, feature_idx:feature_idx + 8] = features
            feature_idx += 8
        
        # Build labels
        for ball in next_main:
            y_main[i, ball] = 1
        for star in next_stars:
            y_star[i, star] = 1
    
    meta = {
        "data_from": df.iloc[0]['draw_date'],
        "data_to": df.iloc[-1]['draw_date'],
        "n_draws": n_draws,
        "n_samples": n_samples,
        "window_sizes": window_sizes,
        "features_per_number": n_base_features,
        "features_per_star": 8,
        "feature_types": [
            "multi_scale_frequency", 
            "gap_based", 
            "position_preference",
            "momentum_indicators",
            "pair_frequency",
            "gap_variance",
            "temporal_cyclical"
        ],
        "X_main_shape": X_main.shape,
        "X_star_shape": X_star.shape,
        "advanced": True,
        "version": "2.0"
    }
    
    logger.info(f"Advanced features built: X_main{X_main.shape}, X_star{X_star.shape}")
    logger.info(f"Feature improvements: {len(meta['feature_types'])} feature categories")
    
    return X_main, y_main, X_star, y_star, meta
