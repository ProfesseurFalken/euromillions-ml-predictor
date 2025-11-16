"""
Dataset builder for Euromillions machine learning features.
Creates features based on historical patterns and frequencies.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from datetime import datetime, timedelta
from loguru import logger


def build_datasets(df: pd.DataFrame, window_size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build machine learning datasets from historical draw data.
    
    Args:
        df: DataFrame from repository.all_draws_df() with columns:
            draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2, ...
        window_size: Rolling window size for frequency calculations (default: 100)
    
    Returns:
        Tuple containing:
        - X_main: Features for main balls (n_samples, 50 * n_features)
        - y_main: Labels for main balls (n_samples, 50) - binary whether ball appears
        - X_star: Features for star balls (n_samples, 12 * n_features) 
        - y_star: Labels for star balls (n_samples, 12) - binary whether star appears
        - meta: Dictionary with metadata about the dataset
    """
    logger.info(f"Building datasets from {len(df)} draws with window size {window_size}")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Ensure DataFrame is sorted by date
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    # Prepare data structures
    n_draws = len(df)
    n_samples = n_draws - 1  # We predict the next draw, so last draw has no target
    
    # Feature dimensions: frequency + gap_since_last for each ball/star
    n_main_features = 2  # frequency, gap_since_last
    n_star_features = 2  # frequency, gap_since_last
    
    # Initialize feature matrices
    X_main = np.zeros((n_samples, 50, n_main_features))  # 50 main balls
    X_star = np.zeros((n_samples, 12, n_star_features))  # 12 stars
    
    # Initialize label matrices (binary: does ball/star appear in next draw?)
    y_main = np.zeros((n_samples, 50), dtype=int)
    y_star = np.zeros((n_samples, 12), dtype=int)
    
    # Track last seen positions for gap calculation
    main_last_seen = np.full(50, -1)  # Index of last draw where each ball appeared
    star_last_seen = np.full(12, -1)  # Index of last draw where each star appeared
    
    # Track frequency counts for rolling window
    main_counts = np.zeros(50)  # Running count for each main ball
    star_counts = np.zeros(12)  # Running count for each star
    
    logger.info("Processing draws and building features...")
    
    for i in range(n_samples):
        current_draw = df.iloc[i]
        next_draw = df.iloc[i + 1]
        
        # Extract current draw numbers (convert to 0-based indexing)
        current_main = [
            current_draw['n1'] - 1, current_draw['n2'] - 1, current_draw['n3'] - 1,
            current_draw['n4'] - 1, current_draw['n5'] - 1
        ]
        current_stars = [current_draw['s1'] - 1, current_draw['s2'] - 1]
        
        # Extract next draw numbers for labels (convert to 0-based indexing)
        next_main = [
            next_draw['n1'] - 1, next_draw['n2'] - 1, next_draw['n3'] - 1,
            next_draw['n4'] - 1, next_draw['n5'] - 1
        ]
        next_stars = [next_draw['s1'] - 1, next_draw['s2'] - 1]
        
        # Update counts and last seen for current draw
        for ball in current_main:
            main_counts[ball] += 1
            main_last_seen[ball] = i
        
        for star in current_stars:
            star_counts[star] += 1
            star_last_seen[star] = i
        
        # Calculate effective window size (smaller at beginning)
        effective_window = min(window_size, i + 1)
        
        # Remove old counts if window is full
        if i >= window_size:
            old_draw = df.iloc[i - window_size]
            old_main = [
                old_draw['n1'] - 1, old_draw['n2'] - 1, old_draw['n3'] - 1,
                old_draw['n4'] - 1, old_draw['n5'] - 1
            ]
            old_stars = [old_draw['s1'] - 1, old_draw['s2'] - 1]
            
            for ball in old_main:
                main_counts[ball] = max(0, main_counts[ball] - 1)
            
            for star in old_stars:
                star_counts[star] = max(0, star_counts[star] - 1)
        
        # Build features for each main ball (1-50)
        for ball_idx in range(50):
            # Feature 1: Rolling frequency (normalized by effective window)
            frequency = main_counts[ball_idx] / effective_window
            
            # Feature 2: Gap since last seen
            if main_last_seen[ball_idx] == -1:
                gap_since_last = i + 1  # Never seen before
            else:
                gap_since_last = i - main_last_seen[ball_idx]
            
            X_main[i, ball_idx, 0] = frequency
            X_main[i, ball_idx, 1] = gap_since_last
        
        # Build features for each star (1-12)
        for star_idx in range(12):
            # Feature 1: Rolling frequency (normalized by effective window)
            frequency = star_counts[star_idx] / effective_window
            
            # Feature 2: Gap since last seen
            if star_last_seen[star_idx] == -1:
                gap_since_last = i + 1  # Never seen before
            else:
                gap_since_last = i - star_last_seen[star_idx]
            
            X_star[i, star_idx, 0] = frequency
            X_star[i, star_idx, 1] = gap_since_last
        
        # Build labels (binary: does ball/star appear in next draw?)
        for ball in next_main:
            y_main[i, ball] = 1
        
        for star in next_stars:
            y_star[i, star] = 1
    
    # Reshape feature matrices for ML algorithms
    # From (n_samples, n_balls, n_features) to (n_samples, n_balls * n_features)
    X_main_flat = X_main.reshape(n_samples, -1)  # Shape: (n_samples, 50 * 2)
    X_star_flat = X_star.reshape(n_samples, -1)  # Shape: (n_samples, 12 * 2)
    
    # Create metadata
    meta = {
        "data_from": df.iloc[0]['draw_date'],
        "data_to": df.iloc[-1]['draw_date'],
        "n_draws": n_draws,
        "n_samples": n_samples,
        "window_size": window_size,
        "main_balls_range": "1-50",
        "stars_range": "1-12",
        "features": ["rolling_frequency", "gap_since_last"],
        "X_main_shape": X_main_flat.shape,
        "X_star_shape": X_star_flat.shape,
        "y_main_shape": y_main.shape,
        "y_star_shape": y_star.shape,
        "feature_names_main": [f"ball_{b+1}_{feat}" for b in range(50) for feat in ["freq", "gap"]],
        "feature_names_star": [f"star_{s+1}_{feat}" for s in range(12) for feat in ["freq", "gap"]]
    }
    
    logger.info(f"Dataset built successfully:")
    logger.info(f"  - X_main shape: {X_main_flat.shape}")
    logger.info(f"  - y_main shape: {y_main.shape}")
    logger.info(f"  - X_star shape: {X_star_flat.shape}")
    logger.info(f"  - y_star shape: {y_star.shape}")
    logger.info(f"  - Date range: {meta['data_from']} to {meta['data_to']}")
    
    return X_main_flat, y_main, X_star_flat, y_star, meta


def get_feature_statistics(X: np.ndarray, feature_names: list) -> pd.DataFrame:
    """
    Get descriptive statistics for features.
    
    Args:
        X: Feature matrix
        feature_names: List of feature names
    
    Returns:
        DataFrame with feature statistics
    """
    stats_df = pd.DataFrame({
        'feature': feature_names,
        'mean': X.mean(axis=0),
        'std': X.std(axis=0),
        'min': X.min(axis=0),
        'max': X.max(axis=0),
        'median': np.median(X, axis=0)
    })
    
    return stats_df


def analyze_label_distribution(y: np.ndarray, ball_type: str = "main") -> pd.DataFrame:
    """
    Analyze the distribution of labels (how often each ball/star appears).
    
    Args:
        y: Label matrix (n_samples, n_balls)
        ball_type: "main" or "star"
    
    Returns:
        DataFrame with appearance statistics
    """
    n_samples, n_balls = y.shape
    
    stats = []
    for i in range(n_balls):
        ball_num = i + 1
        appearances = y[:, i].sum()
        frequency = appearances / n_samples
        
        stats.append({
            f'{ball_type}_number': ball_num,
            'appearances': appearances,
            'frequency': frequency,
            'never_appeared': appearances == 0,
            'always_appeared': appearances == n_samples
        })
    
    return pd.DataFrame(stats)


def split_datasets(X_main: np.ndarray, y_main: np.ndarray, 
                  X_star: np.ndarray, y_star: np.ndarray,
                  train_ratio: float = 0.8) -> Tuple[np.ndarray, ...]:
    """
    Split datasets into train/test sets chronologically.
    
    Args:
        X_main, y_main: Main ball features and labels
        X_star, y_star: Star features and labels
        train_ratio: Ratio of data to use for training
    
    Returns:
        Tuple of (X_main_train, X_main_test, y_main_train, y_main_test,
                 X_star_train, X_star_test, y_star_train, y_star_test)
    """
    n_samples = X_main.shape[0]
    split_idx = int(n_samples * train_ratio)
    
    X_main_train, X_main_test = X_main[:split_idx], X_main[split_idx:]
    y_main_train, y_main_test = y_main[:split_idx], y_main[split_idx:]
    X_star_train, X_star_test = X_star[:split_idx], X_star[split_idx:]
    y_star_train, y_star_test = y_star[:split_idx], y_star[split_idx:]
    
    logger.info(f"Dataset split: {split_idx} training samples, {n_samples - split_idx} test samples")
    
    return (X_main_train, X_main_test, y_main_train, y_main_test,
            X_star_train, X_star_test, y_star_train, y_star_test)


def build_enhanced_datasets(df: pd.DataFrame, window_size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build enhanced datasets with additional features.
    
    Enhanced features include:
    - Rolling frequency over different windows
    - Gap since last seen
    - Streak counts (consecutive appearances/absences)
    - Relative position features
    
    Args:
        df: DataFrame from repository.all_draws_df()
        window_size: Base window size for calculations
    
    Returns:
        Same structure as build_datasets but with more features
    """
    logger.info(f"Building enhanced datasets with additional features")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Ensure DataFrame is sorted by date
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    n_draws = len(df)
    n_samples = n_draws - 1
    
    # Enhanced features: frequency, gap, short_freq, streak
    n_main_features = 4
    n_star_features = 4
    
    X_main = np.zeros((n_samples, 50, n_main_features))
    X_star = np.zeros((n_samples, 12, n_star_features))
    y_main = np.zeros((n_samples, 50), dtype=int)
    y_star = np.zeros((n_samples, 12), dtype=int)
    
    # Tracking arrays
    main_last_seen = np.full(50, -1)
    star_last_seen = np.full(12, -1)
    main_counts = np.zeros(50)
    star_counts = np.zeros(12)
    main_short_counts = np.zeros(50)  # Shorter window counts
    star_short_counts = np.zeros(12)
    main_streaks = np.zeros(50)  # Current streak (positive=appearing, negative=absent)
    star_streaks = np.zeros(12)
    
    short_window = window_size // 3  # Shorter window for recent trends
    
    for i in range(n_samples):
        current_draw = df.iloc[i]
        next_draw = df.iloc[i + 1]
        
        # Current and next draw numbers (0-based)
        current_main = [current_draw[f'n{j}'] - 1 for j in range(1, 6)]
        current_stars = [current_draw['s1'] - 1, current_draw['s2'] - 1]
        next_main = [next_draw[f'n{j}'] - 1 for j in range(1, 6)]
        next_stars = [next_draw['s1'] - 1, next_draw['s2'] - 1]
        
        # Update counts and streaks
        for ball in range(50):
            if ball in current_main:
                main_counts[ball] += 1
                main_short_counts[ball] += 1
                main_last_seen[ball] = i
                main_streaks[ball] = max(1, main_streaks[ball] + 1) if main_streaks[ball] >= 0 else 1
            else:
                main_streaks[ball] = min(-1, main_streaks[ball] - 1) if main_streaks[ball] <= 0 else -1
        
        for star in range(12):
            if star in current_stars:
                star_counts[star] += 1
                star_short_counts[star] += 1
                star_last_seen[star] = i
                star_streaks[star] = max(1, star_streaks[star] + 1) if star_streaks[star] >= 0 else 1
            else:
                star_streaks[star] = min(-1, star_streaks[star] - 1) if star_streaks[star] <= 0 else -1
        
        # Handle window overflow
        effective_window = min(window_size, i + 1)
        effective_short_window = min(short_window, i + 1)
        
        if i >= window_size:
            old_draw = df.iloc[i - window_size]
            old_main = [old_draw[f'n{j}'] - 1 for j in range(1, 6)]
            old_stars = [old_draw['s1'] - 1, old_draw['s2'] - 1]
            for ball in old_main:
                main_counts[ball] = max(0, main_counts[ball] - 1)
            for star in old_stars:
                star_counts[star] = max(0, star_counts[star] - 1)
        
        if i >= short_window:
            old_short_draw = df.iloc[i - short_window]
            old_short_main = [old_short_draw[f'n{j}'] - 1 for j in range(1, 6)]
            old_short_stars = [old_short_draw['s1'] - 1, old_short_draw['s2'] - 1]
            for ball in old_short_main:
                main_short_counts[ball] = max(0, main_short_counts[ball] - 1)
            for star in old_short_stars:
                star_short_counts[star] = max(0, star_short_counts[star] - 1)
        
        # Build enhanced features
        for ball in range(50):
            X_main[i, ball, 0] = main_counts[ball] / effective_window  # Long-term frequency
            X_main[i, ball, 1] = (i - main_last_seen[ball]) if main_last_seen[ball] >= 0 else i + 1  # Gap
            X_main[i, ball, 2] = main_short_counts[ball] / effective_short_window  # Short-term frequency
            X_main[i, ball, 3] = main_streaks[ball]  # Streak
        
        for star in range(12):
            X_star[i, star, 0] = star_counts[star] / effective_window
            X_star[i, star, 1] = (i - star_last_seen[star]) if star_last_seen[star] >= 0 else i + 1
            X_star[i, star, 2] = star_short_counts[star] / effective_short_window
            X_star[i, star, 3] = star_streaks[star]
        
        # Build labels
        for ball in next_main:
            y_main[i, ball] = 1
        for star in next_stars:
            y_star[i, star] = 1
    
    # Reshape for ML
    X_main_flat = X_main.reshape(n_samples, -1)
    X_star_flat = X_star.reshape(n_samples, -1)
    
    meta = {
        "data_from": df.iloc[0]['draw_date'],
        "data_to": df.iloc[-1]['draw_date'],
        "n_draws": n_draws,
        "n_samples": n_samples,
        "window_size": window_size,
        "short_window_size": short_window,
        "features": ["long_frequency", "gap_since_last", "short_frequency", "streak"],
        "X_main_shape": X_main_flat.shape,
        "X_star_shape": X_star_flat.shape,
        "enhanced": True
    }
    
    return X_main_flat, y_main, X_star_flat, y_star, meta


def build_enhanced_datasets_v2(df: pd.DataFrame, window_size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build enhanced datasets with advanced temporal features.
    
    Args:
        df: DataFrame from repository.all_draws_df()
        window_size: Rolling window size for frequency calculations
    
    Returns:
        Enhanced datasets with temporal features
    """
    logger.info(f"Building enhanced datasets v2 with temporal features (window: {window_size})")
    
    # Start with base enhanced features
    X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(df, window_size)
    
    # Add temporal features
    df_enhanced = add_temporal_features(df.copy())
    temporal_features = extract_temporal_feature_matrix(df_enhanced)
    
    # Add sequence pattern features
    pattern_features = add_sequence_pattern_features(df)
    
    # Add gap analysis features
    gap_features = add_gap_analysis_features(df, window_size)
    
    # Add correlation features
    correlation_features = add_correlation_features(df, window_size)
    
    # Combine all features
    n_samples = X_main.shape[0]
    
    # Ensure all feature matrices have the same number of samples
    temporal_features = temporal_features[-n_samples:] if len(temporal_features) > n_samples else temporal_features
    pattern_features = pattern_features[-n_samples:] if len(pattern_features) > n_samples else pattern_features
    gap_features = gap_features[-n_samples:] if len(gap_features) > n_samples else gap_features
    correlation_features = correlation_features[-n_samples:] if len(correlation_features) > n_samples else correlation_features
    
    # Concatenate features
    X_main_enhanced = np.concatenate([
        X_main, 
        temporal_features,
        pattern_features, 
        gap_features,
        correlation_features
    ], axis=1)
    
    # Star features get the same temporal enhancements (scaled)
    X_star_enhanced = np.concatenate([
        X_star,
        temporal_features,
        pattern_features[:, :12] if pattern_features.shape[1] >= 12 else pattern_features,  # Adapt for stars
        gap_features[:, :12] if gap_features.shape[1] >= 12 else gap_features,
        correlation_features[:, :12] if correlation_features.shape[1] >= 12 else correlation_features
    ], axis=1)
    
    # Update metadata
    meta["features"].extend([
        "temporal_features", "pattern_features", "gap_features", "correlation_features"
    ])
    meta["enhanced_v2"] = True
    meta["total_main_features"] = X_main_enhanced.shape[1]
    meta["total_star_features"] = X_star_enhanced.shape[1]
    
    logger.info(f"Enhanced v2 features: {X_main_enhanced.shape[1]} main, {X_star_enhanced.shape[1]} star")
    
    return X_main_enhanced, y_main, X_star_enhanced, y_star, meta


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajouter des features temporelles cycliques."""
    
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    
    # Features cycliques de base
    df['day_of_week'] = df['draw_date'].dt.dayofweek
    df['month'] = df['draw_date'].dt.month
    df['quarter'] = df['draw_date'].dt.quarter
    df['day_of_year'] = df['draw_date'].dt.dayofyear
    df['week_of_year'] = df['draw_date'].dt.isocalendar().week
    
    # Features cycliques sinusoïdales pour capturer la périodicité
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['year_progress'] = df['day_of_year'] / 365.25
    df['year_sin'] = np.sin(2 * np.pi * df['year_progress'])
    df['year_cos'] = np.cos(2 * np.pi * df['year_progress'])
    
    # Features spéciales
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
    df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
    df['is_end_of_month'] = (df['draw_date'].dt.day >= 25).astype(int)
    df['is_beginning_of_year'] = ((df['month'] == 1) & (df['draw_date'].dt.day <= 15)).astype(int)
    
    return df


def extract_temporal_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Extraire la matrice des features temporelles."""
    
    temporal_cols = [
        'day_of_week', 'month', 'quarter', 'day_of_year', 'week_of_year',
        'day_sin', 'day_cos', 'month_sin', 'month_cos', 'year_sin', 'year_cos',
        'is_weekend', 'is_summer', 'is_winter', 'is_end_of_month', 'is_beginning_of_year'
    ]
    
    # Assurer que toutes les colonnes existent
    available_cols = [col for col in temporal_cols if col in df.columns]
    
    if available_cols:
        return df[available_cols].values
    else:
        # Fallback: créer des features minimales
        n_rows = len(df)
        return np.zeros((n_rows, len(temporal_cols)))


def add_sequence_pattern_features(df: pd.DataFrame) -> np.ndarray:
    """Analyser les patterns de séquences dans les tirages."""
    
    features_list = []
    
    for i, row in df.iterrows():
        balls = sorted([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
        stars = sorted([row['s1'], row['s2']])
        
        # Features pour les boules principales
        consecutive_pairs = sum(1 for j in range(len(balls)-1) if balls[j+1] - balls[j] == 1)
        ball_range = max(balls) - min(balls)
        ball_sum = sum(balls)
        ball_mean = np.mean(balls)
        ball_std = np.std(balls)
        
        # Gaps entre boules
        gaps = [balls[j+1] - balls[j] for j in range(len(balls)-1)]
        avg_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        max_gap = max(gaps)
        min_gap = min(gaps)
        
        # Features pour les étoiles
        star_range = max(stars) - min(stars)
        star_sum = sum(stars)
        star_gap = stars[1] - stars[0]
        
        # Patterns de distribution
        low_balls = sum(1 for b in balls if b <= 17)  # Boules basses (1-17)
        mid_balls = sum(1 for b in balls if 18 <= b <= 34)  # Boules moyennes (18-34)
        high_balls = sum(1 for b in balls if b >= 35)  # Boules hautes (35-50)
        
        # Parité
        even_balls = sum(1 for b in balls if b % 2 == 0)
        odd_balls = 5 - even_balls
        even_stars = sum(1 for s in stars if s % 2 == 0)
        
        features = [
            consecutive_pairs, ball_range, ball_sum, ball_mean, ball_std,
            avg_gap, std_gap, max_gap, min_gap,
            star_range, star_sum, star_gap,
            low_balls, mid_balls, high_balls,
            even_balls, odd_balls, even_stars
        ]
        
        features_list.append(features)
    
    return np.array(features_list)


def add_gap_analysis_features(df: pd.DataFrame, window_size: int) -> np.ndarray:
    """Analyser les patterns d'intervalles entre apparitions."""
    
    n_rows = len(df)
    n_features = 62  # 50 boules + 12 étoiles
    gap_features = np.zeros((n_rows, n_features))
    
    # Pour chaque tirage, calculer les gaps depuis la dernière apparition
    for i in range(n_rows):
        current_row = df.iloc[i]
        current_balls = [current_row['n1'], current_row['n2'], current_row['n3'], current_row['n4'], current_row['n5']]
        current_stars = [current_row['s1'], current_row['s2']]
        
        # Analyser les gaps pour les boules principales
        for ball_num in range(1, 51):
            gap_since_last = 0
            
            # Chercher vers le passé
            for j in range(i - 1, max(0, i - window_size), -1):
                past_row = df.iloc[j]
                past_balls = [past_row['n1'], past_row['n2'], past_row['n3'], past_row['n4'], past_row['n5']]
                
                if ball_num in past_balls:
                    break
                gap_since_last += 1
            
            gap_features[i, ball_num - 1] = min(gap_since_last, window_size)  # Cap au window_size
        
        # Analyser les gaps pour les étoiles
        for star_num in range(1, 13):
            gap_since_last = 0
            
            for j in range(i - 1, max(0, i - window_size), -1):
                past_row = df.iloc[j]
                past_stars = [past_row['s1'], past_row['s2']]
                
                if star_num in past_stars:
                    break
                gap_since_last += 1
            
            gap_features[i, 49 + star_num] = min(gap_since_last, window_size)
    
    return gap_features


def add_correlation_features(df: pd.DataFrame, window_size: int) -> np.ndarray:
    """Ajouter des features basées sur les corrélations entre boules."""
    
    n_rows = len(df)
    correlation_features = np.zeros((n_rows, 20))  # 20 features de corrélation
    
    for i in range(window_size, n_rows):  # Commencer après la fenêtre initiale
        # Analyser la fenêtre précédente
        window_data = df.iloc[i - window_size:i]
        
        # Matrice de co-occurrence pour cette fenêtre
        cooccurrence = np.zeros((50, 50))
        
        for _, row in window_data.iterrows():
            balls = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
            
            for b1 in balls:
                for b2 in balls:
                    if b1 != b2:
                        cooccurrence[b1-1, b2-1] += 1
        
        # Extraire des statistiques de corrélation
        current_row = df.iloc[i]
        current_balls = [current_row['n1'], current_row['n2'], current_row['n3'], current_row['n4'], current_row['n5']]
        
        # Features basées sur les corrélations des boules actuelles
        correlation_stats = []
        
        for ball in current_balls:
            ball_correlations = cooccurrence[ball-1, :]
            correlation_stats.extend([
                np.mean(ball_correlations),
                np.max(ball_correlations),
                np.std(ball_correlations),
                np.sum(ball_correlations > 0)  # Nombre de boules corrélées
            ])
        
        # Prendre les 20 premières statistiques
        correlation_features[i, :] = np.array(correlation_stats[:20])
    
    return correlation_features
