"""
Advanced Feature Engineering for EuroMillions Prediction
========================================================

Nouvelles features pour améliorer les prédictions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def build_advanced_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Construire des features temporelles avancées."""
    
    # 1. Features cycliques (jour, mois, saison)
    df['day_of_week'] = pd.to_datetime(df['draw_date']).dt.dayofweek
    df['month'] = pd.to_datetime(df['draw_date']).dt.month
    df['quarter'] = pd.to_datetime(df['draw_date']).dt.quarter
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # 2. Features cycliques sinusoïdales (capture la périodicité)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # 3. Proximité avec événements spéciaux
    df['days_to_new_year'] = calculate_days_to_event(df['draw_date'], 'new_year')
    df['days_to_summer'] = calculate_days_to_event(df['draw_date'], 'summer')
    
    return df

def build_sequence_pattern_features(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Analyser les patterns de séquences."""
    
    features = {}
    
    # 1. Patterns de consécutivité
    for i, row in df.iterrows():
        balls = sorted([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
        
        # Nombre de paires consécutives
        consecutive_pairs = sum(1 for j in range(len(balls)-1) if balls[j+1] - balls[j] == 1)
        features[f'consecutive_pairs_{i}'] = consecutive_pairs
        
        # Étendue (max - min)
        features[f'range_{i}'] = max(balls) - min(balls)
        
        # Somme des boules
        features[f'sum_balls_{i}'] = sum(balls)
        
        # Variance des boules
        features[f'variance_balls_{i}'] = np.var(balls)
    
    # 2. Patterns d'espacement
    for i, row in df.iterrows():
        balls = sorted([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
        gaps = [balls[j+1] - balls[j] for j in range(len(balls)-1)]
        
        features[f'avg_gap_{i}'] = np.mean(gaps)
        features[f'std_gap_{i}'] = np.std(gaps)
        features[f'max_gap_{i}'] = max(gaps)
    
    return features

def build_frequency_evolution_features(df: pd.DataFrame, windows: List[int] = [10, 25, 50, 100]) -> Dict[str, np.ndarray]:
    """Analyser l'évolution des fréquences sur différentes fenêtres."""
    
    features = {}
    
    for window in windows:
        for ball_num in range(1, 51):  # Boules principales 1-50
            freq_history = []
            
            for i in range(len(df)):
                # Calculer la fréquence sur la fenêtre
                start_idx = max(0, i - window)
                window_data = df.iloc[start_idx:i+1]
                
                freq = calculate_ball_frequency(window_data, ball_num)
                freq_history.append(freq)
            
            features[f'freq_ball_{ball_num}_w{window}'] = np.array(freq_history)
            
            # Tendance de la fréquence (dérivée)
            if len(freq_history) > 1:
                freq_trend = np.gradient(freq_history)
                features[f'freq_trend_ball_{ball_num}_w{window}'] = freq_trend
    
    return features

def build_correlation_features(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Analyser les corrélations entre boules."""
    
    features = {}
    
    # Matrice de co-occurrence
    cooccurrence_matrix = np.zeros((50, 50))
    
    for _, row in df.iterrows():
        balls = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
        
        # Mettre à jour la matrice de co-occurrence
        for i, ball1 in enumerate(balls):
            for j, ball2 in enumerate(balls):
                if i != j:
                    cooccurrence_matrix[ball1-1, ball2-1] += 1
    
    # Features basées sur les corrélations
    for i in range(50):
        # Boules les plus corrélées avec la boule i
        correlations = cooccurrence_matrix[i, :]
        features[f'top_corr_ball_{i+1}'] = np.argsort(correlations)[-5:]  # Top 5
        features[f'corr_strength_ball_{i+1}'] = correlations[np.argsort(correlations)[-5:]]
    
    return features

def build_jackpot_influence_features(df: pd.DataFrame) -> pd.DataFrame:
    """Analyser l'influence du jackpot sur les patterns."""
    
    # Simulation des montants de jackpot (à remplacer par vraies données)
    df['jackpot_estimate'] = simulate_jackpot_amounts(df)
    
    # Catégoriser les jackpots
    df['jackpot_category'] = pd.cut(df['jackpot_estimate'], 
                                   bins=[0, 20, 50, 100, float('inf')],
                                   labels=['low', 'medium', 'high', 'mega'])
    
    # Analyser les patterns par catégorie de jackpot
    df['is_high_jackpot'] = (df['jackpot_category'].isin(['high', 'mega'])).astype(int)
    
    return df

def calculate_days_to_event(dates: pd.Series, event_type: str) -> pd.Series:
    """Calculer les jours jusqu'au prochain événement."""
    
    def days_to_next_new_year(date):
        year = date.year
        next_new_year = datetime(year + 1, 1, 1)
        return (next_new_year - date).days
    
    def days_to_next_summer(date):
        year = date.year
        summer_start = datetime(year, 6, 21)  # 21 juin
        if date > summer_start:
            summer_start = datetime(year + 1, 6, 21)
        return (summer_start - date).days
    
    if event_type == 'new_year':
        return dates.apply(days_to_next_new_year)
    elif event_type == 'summer':
        return dates.apply(days_to_next_summer)
    
    return pd.Series([0] * len(dates))

def calculate_ball_frequency(df: pd.DataFrame, ball_num: int) -> float:
    """Calculer la fréquence d'apparition d'une boule."""
    
    total_draws = len(df)
    if total_draws == 0:
        return 0.0
    
    appearances = 0
    for _, row in df.iterrows():
        if ball_num in [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]:
            appearances += 1
    
    return appearances / total_draws

def simulate_jackpot_amounts(df: pd.DataFrame) -> List[float]:
    """Simuler des montants de jackpot (à remplacer par vraies données)."""
    
    # Simulation simple basée sur la tendance croissante
    base_amount = 15  # 15 millions de base
    amounts = []
    
    for i, _ in enumerate(df.iterrows()):
        # Jackpot augmente s'il n'y a pas de gagnant (simulation)
        if i == 0:
            amount = base_amount
        else:
            # 70% de chance d'augmentation, 30% de reset
            if np.random.random() < 0.7:
                amount = amounts[-1] * 1.3  # Augmentation
            else:
                amount = base_amount  # Reset après gain
        
        amounts.append(amount)
    
    return amounts

def build_meta_features(df: pd.DataFrame) -> pd.DataFrame:
    """Construire des méta-features complexes."""
    
    # 1. Entropie du tirage (mesure de randomness)
    df['entropy'] = df.apply(calculate_draw_entropy, axis=1)
    
    # 2. Distance par rapport à la distribution théorique
    df['theoretical_distance'] = df.apply(calculate_theoretical_distance, axis=1)
    
    # 3. Similarité avec les tirages précédents
    df['similarity_score'] = calculate_similarity_scores(df)
    
    return df

def calculate_draw_entropy(row) -> float:
    """Calculer l'entropie d'un tirage."""
    
    balls = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
    
    # Calculer l'entropie basée sur la distribution des boules
    # Plus l'entropie est haute, plus le tirage est "aléatoire"
    
    # Simple mesure: écart-type des positions
    return np.std(balls)

def calculate_theoretical_distance(row) -> float:
    """Calculer la distance par rapport à la distribution théorique."""
    
    balls = sorted([row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
    
    # Distribution théorique: boules équi-réparties
    theoretical = [10.2, 20.4, 30.6, 40.8, 51.0]  # Positions théoriques
    
    # Distance euclidienne
    distance = np.sqrt(sum((actual - theo)**2 for actual, theo in zip(balls, theoretical)))
    
    return distance

def calculate_similarity_scores(df: pd.DataFrame) -> List[float]:
    """Calculer les scores de similarité avec les tirages précédents."""
    
    similarity_scores = [0.0]  # Premier tirage n'a pas de référence
    
    for i in range(1, len(df)):
        current_balls = set([df.iloc[i]['n1'], df.iloc[i]['n2'], df.iloc[i]['n3'], 
                           df.iloc[i]['n4'], df.iloc[i]['n5']])
        
        max_similarity = 0.0
        
        # Comparer avec les 10 tirages précédents
        for j in range(max(0, i-10), i):
            prev_balls = set([df.iloc[j]['n1'], df.iloc[j]['n2'], df.iloc[j]['n3'], 
                            df.iloc[j]['n4'], df.iloc[j]['n5']])
            
            # Jaccard similarity
            intersection = len(current_balls.intersection(prev_balls))
            union = len(current_balls.union(prev_balls))
            
            if union > 0:
                similarity = intersection / union
                max_similarity = max(max_similarity, similarity)
        
        similarity_scores.append(max_similarity)
    
    return similarity_scores

if __name__ == "__main__":
    print("🧠 Advanced Feature Engineering for EuroMillions")
    print("=" * 50)
    print("Ces features avancées peuvent améliorer significativement les prédictions:")
    print("  • Features temporelles cycliques")
    print("  • Patterns de séquences et espacement")
    print("  • Évolution des fréquences multi-fenêtres")
    print("  • Corrélations entre boules")
    print("  • Influence du jackpot")
    print("  • Méta-features (entropie, similarité)")