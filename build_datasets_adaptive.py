#!/usr/bin/env python3
"""
Version adaptée de build_datasets.py pour gérer 11 étoiles au lieu de 12
"""

import numpy as np
import pandas as pd
from loguru import logger

def build_datasets_adaptive(df, max_stars=11):
    """
    Build features and labels for Euromillions predictions with adaptive star range.
    
    Args:
        df: DataFrame with columns ['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']
        max_stars: Maximum number of stars (detected automatically from data)
    
    Returns:
        - X_main: Features for main balls (n_samples, 50 * n_features)
        - y_main: Labels for main balls (n_samples, 50) - binary whether ball appears  
        - X_star: Features for star balls (n_samples, max_stars * n_features) 
        - y_star: Labels for star balls (n_samples, max_stars) - binary whether star appears
        - meta: Metadata dictionary
    """
    
    # Detect actual star range from data
    all_stars = []
    for col in ['s1', 's2']:
        if col in df.columns:
            all_stars.extend(df[col].dropna().tolist())
    
    actual_max_stars = max(all_stars) if all_stars else max_stars
    logger.info(f"Detected star range: 1 to {actual_max_stars}")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Ensure DataFrame is sorted by date
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    n_samples = len(df) - 1  # We need previous draws to build features
    
    # Features: frequency and gap (days since last appearance)
    n_main_features = 2  # freq, gap
    n_star_features = 2  # freq, gap
    
    X_main = np.zeros((n_samples, 50, n_main_features))  # 50 main balls
    y_main = np.zeros((n_samples, 50), dtype=int)
    
    X_star = np.zeros((n_samples, actual_max_stars, n_star_features))  # adaptive stars
    y_star = np.zeros((n_samples, actual_max_stars), dtype=int)
    
    # Keep track of last seen indices
    main_last_seen = np.full(50, -1)  # Index of last draw where each main ball appeared
    star_last_seen = np.full(actual_max_stars, -1)  # Index of last draw where each star appeared
    
    # Running counts
    main_counts = np.zeros(50)  # Running count for each main ball
    star_counts = np.zeros(actual_max_stars)  # Running count for each star
    
    for i in range(1, len(df)):  # Start from 1 to have previous history
        current_draw = df.iloc[i]
        sample_idx = i - 1
        
        # Extract current draw numbers
        main_numbers = [current_draw[f'n{j}'] for j in range(1, 6)]
        star_numbers = [current_draw['s1'], current_draw['s2']]
        
        # Build labels for this draw
        for num in main_numbers:
            if 1 <= num <= 50:
                y_main[sample_idx, num - 1] = 1
        
        for star in star_numbers:
            if 1 <= star <= actual_max_stars:
                y_star[sample_idx, star - 1] = 1
        
        # Build features based on history up to (but not including) current draw
        for ball_idx in range(50):
            ball_number = ball_idx + 1
            
            # Frequency: how often this ball appeared in previous draws
            freq = main_counts[ball_idx] / max(1, i)
            
            # Gap: days since last appearance
            if main_last_seen[ball_idx] >= 0:
                gap = i - main_last_seen[ball_idx]
            else:
                gap = i + 1  # Never seen before
            
            X_main[sample_idx, ball_idx, 0] = freq
            X_main[sample_idx, ball_idx, 1] = gap
        
        # Build features for each star
        for star_idx in range(actual_max_stars):
            star_number = star_idx + 1
            
            # Frequency
            freq = star_counts[star_idx] / max(1, i)
            
            # Gap
            if star_last_seen[star_idx] >= 0:
                gap = i - star_last_seen[star_idx]
            else:
                gap = i + 1
            
            X_star[sample_idx, star_idx, 0] = freq
            X_star[sample_idx, star_idx, 1] = gap
        
        # Update counts and last seen for PREVIOUS draw (not current)
        if i > 1:  # Only update if we have a previous draw
            prev_draw = df.iloc[i - 1]
            prev_main = [prev_draw[f'n{j}'] for j in range(1, 6)]
            prev_stars = [prev_draw['s1'], prev_draw['s2']]
            
            for num in prev_main:
                if 1 <= num <= 50:
                    main_counts[num - 1] += 1
                    main_last_seen[num - 1] = i - 1
            
            for star in prev_stars:
                if 1 <= star <= actual_max_stars:
                    star_counts[star - 1] += 1
                    star_last_seen[star - 1] = i - 1
    
    # Flatten features for sklearn compatibility
    X_main_flat = X_main.reshape(n_samples, -1)  # Shape: (n_samples, 50 * 2)
    X_star_flat = X_star.reshape(n_samples, -1)  # Shape: (n_samples, actual_max_stars * 2)
    
    meta = {
        "n_samples": n_samples,
        "feature_dims": {
            "main": (50, n_main_features),
            "star": (actual_max_stars, n_star_features)
        },
        "main_range": "1-50",
        "stars_range": f"1-{actual_max_stars}",
        "date_range": (df['draw_date'].min(), df['draw_date'].max()),
        "features": ["frequency", "gap"],
        "feature_names_main": [f"ball_{b+1}_{feat}" for b in range(50) for feat in ["freq", "gap"]],
        "feature_names_star": [f"star_{s+1}_{feat}" for s in range(actual_max_stars) for feat in ["freq", "gap"]],
        "adaptive_stars": True,
        "max_stars_detected": actual_max_stars
    }
    
    logger.info(f"Built adaptive datasets: X_main{X_main_flat.shape}, y_main{y_main.shape}, X_star{X_star_flat.shape}, y_star{y_star.shape}")
    
    return X_main_flat, y_main, X_star_flat, y_star, meta

if __name__ == "__main__":
    # Test the adaptive function
    from repository import EuromillionsRepository
    
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    try:
        X_main, y_main, X_star, y_star, meta = build_datasets_adaptive(df)
        print("✅ Adaptive datasets built successfully!")
        print(f"📊 Meta: {meta}")
        
        # Check if all star columns have some positive examples
        for star_idx in range(y_star.shape[1]):
            count = y_star[:, star_idx].sum()
            print(f"   ⭐ Star {star_idx + 1}: {count} occurrences")
            
    except Exception as e:
        print(f"❌ Error: {e}")