"""
Stratégies Hybrides de Prédiction EuroMillions
==============================================

Combiner différentes approches pour maximiser les chances
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict

class HybridPredictionStrategy:
    """Stratégie hybride combinant multiple approches."""
    
    def __init__(self):
        self.ml_weight = 0.4      # Poids du modèle ML
        self.freq_weight = 0.25   # Poids de l'analyse fréquentielle
        self.pattern_weight = 0.2 # Poids des patterns
        self.gap_weight = 0.15    # Poids de l'analyse des gaps
    
    def predict_hybrid(self, df: pd.DataFrame, ml_predictions: Dict) -> List[Dict]:
        """Prédiction hybride combinant toutes les approches."""
        
        # 1. Prédictions ML (probabilités)
        ml_balls = ml_predictions.get('main_probs', [])
        ml_stars = ml_predictions.get('star_probs', [])
        
        # 2. Analyse fréquentielle avancée
        freq_balls = self.analyze_frequency_patterns(df)
        freq_stars = self.analyze_star_frequency_patterns(df)
        
        # 3. Analyse des patterns de récurrence
        pattern_balls = self.analyze_recurrence_patterns(df)
        pattern_stars = self.analyze_star_recurrence_patterns(df)
        
        # 4. Analyse des gaps (intervalles entre apparitions)
        gap_balls = self.analyze_gap_patterns(df)
        gap_stars = self.analyze_star_gap_patterns(df)
        
        # 5. Combiner tous les scores
        final_balls = self.combine_ball_scores(ml_balls, freq_balls, pattern_balls, gap_balls)
        final_stars = self.combine_star_scores(ml_stars, freq_stars, pattern_stars, gap_stars)
        
        # 6. Générer les combinaisons optimales
        combinations = self.generate_optimal_combinations(final_balls, final_stars, n=10)
        
        return combinations
    
    def analyze_frequency_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Analyse fréquentielle sophistiquée avec pondération temporelle."""
        
        ball_scores = {}
        
        # Différentes fenêtres temporelles avec pondération décroissante
        windows = [
            (10, 0.4),   # 10 derniers tirages: poids fort
            (25, 0.3),   # 25 derniers tirages: poids moyen
            (50, 0.2),   # 50 derniers tirages: poids faible
            (100, 0.1)   # 100 derniers tirages: poids très faible
        ]
        
        for ball_num in range(1, 51):
            total_score = 0.0
            
            for window_size, weight in windows:
                recent_draws = df.tail(window_size)
                
                # Fréquence brute
                frequency = self.calculate_ball_frequency(recent_draws, ball_num)
                
                # Tendance (fréquence croissante/décroissante?)
                trend = self.calculate_frequency_trend(recent_draws, ball_num)
                
                # Score pondéré
                score = (frequency + trend * 0.3) * weight
                total_score += score
            
            ball_scores[ball_num] = total_score
        
        return ball_scores
    
    def analyze_recurrence_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Analyser les patterns de récurrence (boules qui reviennent ensemble)."""
        
        ball_scores = {}
        
        # Analyser les 20 derniers tirages pour identifier les co-occurrences
        recent_draws = df.tail(20)
        
        # Matrice de co-occurrence
        cooccurrence = defaultdict(lambda: defaultdict(int))
        
        for _, row in recent_draws.iterrows():
            balls = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
            
            # Compter les co-occurrences
            for i, ball1 in enumerate(balls):
                for j, ball2 in enumerate(balls):
                    if i != j:
                        cooccurrence[ball1][ball2] += 1
        
        # Calculer le score de récurrence pour chaque boule
        for ball_num in range(1, 51):
            # Score basé sur les boules fréquemment associées
            associated_balls = cooccurrence[ball_num]
            
            if associated_balls:
                # Score = moyenne des co-occurrences avec les autres boules
                score = sum(associated_balls.values()) / len(associated_balls)
                ball_scores[ball_num] = score / len(recent_draws)  # Normaliser
            else:
                ball_scores[ball_num] = 0.0
        
        return ball_scores
    
    def analyze_gap_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Analyser les patterns d'intervalles entre apparitions."""
        
        ball_scores = {}
        
        for ball_num in range(1, 51):
            gaps = self.calculate_appearance_gaps(df, ball_num)
            
            if not gaps:
                ball_scores[ball_num] = 0.0
                continue
            
            # Statistiques des gaps
            avg_gap = np.mean(gaps)
            std_gap = np.std(gaps)
            last_gap = gaps[-1] if gaps else 0
            
            # Score basé sur la probabilité de réapparition
            # Si le gap actuel > gap moyen, la boule est "en retard"
            if last_gap > avg_gap:
                # Boule en retard = score élevé
                score = min(1.0, (last_gap - avg_gap) / (std_gap + 1))
            else:
                # Boule récente = score plus faible
                score = max(0.0, 1.0 - (avg_gap - last_gap) / (std_gap + 1))
            
            ball_scores[ball_num] = score
        
        return ball_scores
    
    def analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Analyser les patterns saisonniers."""
        
        ball_scores = {}
        current_month = datetime.now().month
        
        # Analyser les fréquences par mois
        df['month'] = pd.to_datetime(df['draw_date']).dt.month
        
        for ball_num in range(1, 51):
            monthly_frequencies = {}
            
            for month in range(1, 13):
                month_data = df[df['month'] == month]
                if not month_data.empty:
                    freq = self.calculate_ball_frequency(month_data, ball_num)
                    monthly_frequencies[month] = freq
            
            # Score basé sur la fréquence du mois actuel vs moyenne
            if current_month in monthly_frequencies:
                current_freq = monthly_frequencies[current_month]
                avg_freq = np.mean(list(monthly_frequencies.values()))
                
                # Ratio fréquence actuelle / fréquence moyenne
                score = current_freq / (avg_freq + 0.001)  # Éviter division par 0
                ball_scores[ball_num] = min(1.0, score)
            else:
                ball_scores[ball_num] = 0.5  # Score neutre
        
        return ball_scores
    
    def combine_ball_scores(self, ml_scores: List[float], freq_scores: Dict, 
                           pattern_scores: Dict, gap_scores: Dict) -> Dict[int, float]:
        """Combiner tous les scores pour les boules principales."""
        
        combined_scores = {}
        
        for ball_num in range(1, 51):
            # Récupérer les scores (avec valeurs par défaut)
            ml_score = ml_scores[ball_num - 1] if ml_scores and len(ml_scores) >= ball_num else 0.0
            freq_score = freq_scores.get(ball_num, 0.0)
            pattern_score = pattern_scores.get(ball_num, 0.0)
            gap_score = gap_scores.get(ball_num, 0.0)
            
            # Combiner avec les poids définis
            final_score = (
                ml_score * self.ml_weight +
                freq_score * self.freq_weight +
                pattern_score * self.pattern_weight +
                gap_score * self.gap_weight
            )
            
            combined_scores[ball_num] = final_score
        
        return combined_scores
    
    def generate_optimal_combinations(self, ball_scores: Dict, star_scores: Dict, 
                                    n: int = 10) -> List[Dict]:
        """Générer des combinaisons optimales avec différentes stratégies."""
        
        combinations = []
        
        # Trier par scores décroissants
        sorted_balls = sorted(ball_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_stars = sorted(star_scores.items(), key=lambda x: x[1], reverse=True)
        
        for i in range(n):
            if i < n // 3:
                # Stratégie 1: Top scores purs
                combo = self.generate_top_score_combination(sorted_balls, sorted_stars)
            elif i < 2 * n // 3:
                # Stratégie 2: Mix top scores + diversification
                combo = self.generate_diversified_combination(sorted_balls, sorted_stars)
            else:
                # Stratégie 3: Pondération probabiliste
                combo = self.generate_probabilistic_combination(ball_scores, star_scores)
            
            # Ajouter métadonnées
            combo['strategy'] = f"hybrid_{i+1}"
            combo['confidence'] = self.calculate_confidence_score(combo, ball_scores, star_scores)
            combo['generated_at'] = datetime.now().isoformat()
            
            combinations.append(combo)
        
        return combinations
    
    def generate_top_score_combination(self, sorted_balls: List, sorted_stars: List) -> Dict:
        """Générer une combinaison basée sur les meilleurs scores."""
        
        # Prendre les 5 meilleures boules
        balls = [ball for ball, score in sorted_balls[:5]]
        
        # Prendre les 2 meilleures étoiles
        stars = [star for star, score in sorted_stars[:2]]
        
        return {
            'balls': balls,
            'stars': stars,
            'method': 'top_scores'
        }
    
    def generate_diversified_combination(self, sorted_balls: List, sorted_stars: List) -> Dict:
        """Générer une combinaison diversifiée (mélange top + autres)."""
        
        balls = []
        
        # 3 boules du top 10
        top_balls = [ball for ball, score in sorted_balls[:10]]
        balls.extend(np.random.choice(top_balls, 3, replace=False))
        
        # 2 boules du reste (diversification)
        other_balls = [ball for ball, score in sorted_balls[10:30]]
        if len(other_balls) >= 2:
            balls.extend(np.random.choice(other_balls, 2, replace=False))
        else:
            balls.extend(other_balls)
            # Compléter avec top si nécessaire
            while len(balls) < 5:
                remaining_top = [b for b in top_balls if b not in balls]
                if remaining_top:
                    balls.append(remaining_top[0])
                else:
                    break
        
        # Étoiles: 1 top + 1 autre
        stars = []
        stars.append(sorted_stars[0][0])  # Meilleure étoile
        
        other_stars = [star for star, score in sorted_stars[1:6]]
        if other_stars:
            stars.append(np.random.choice(other_stars))
        else:
            stars.append(sorted_stars[1][0])
        
        return {
            'balls': sorted(balls),
            'stars': sorted(stars),
            'method': 'diversified'
        }
    
    def generate_probabilistic_combination(self, ball_scores: Dict, star_scores: Dict) -> Dict:
        """Générer une combinaison par échantillonnage probabiliste."""
        
        # Convertir scores en probabilités
        ball_probs = np.array(list(ball_scores.values()))
        ball_probs = ball_probs / np.sum(ball_probs)  # Normaliser
        
        star_probs = np.array(list(star_scores.values()))
        star_probs = star_probs / np.sum(star_probs)  # Normaliser
        
        # Échantillonnage pondéré
        ball_numbers = list(ball_scores.keys())
        star_numbers = list(star_scores.keys())
        
        selected_balls = np.random.choice(ball_numbers, 5, replace=False, p=ball_probs)
        selected_stars = np.random.choice(star_numbers, 2, replace=False, p=star_probs)
        
        return {
            'balls': sorted(selected_balls.tolist()),
            'stars': sorted(selected_stars.tolist()),
            'method': 'probabilistic'
        }
    
    def calculate_confidence_score(self, combo: Dict, ball_scores: Dict, star_scores: Dict) -> float:
        """Calculer un score de confiance pour la combinaison."""
        
        # Score moyen des boules sélectionnées
        ball_avg = np.mean([ball_scores.get(ball, 0) for ball in combo['balls']])
        
        # Score moyen des étoiles sélectionnées
        star_avg = np.mean([star_scores.get(star, 0) for star in combo['stars']])
        
        # Score de confiance combiné
        confidence = (ball_avg * 0.7 + star_avg * 0.3) * 100
        
        return round(confidence, 2)
    
    # Méthodes utilitaires
    def calculate_ball_frequency(self, df: pd.DataFrame, ball_num: int) -> float:
        """Calculer la fréquence d'apparition d'une boule."""
        if df.empty:
            return 0.0
        
        total_appearances = 0
        for _, row in df.iterrows():
            if ball_num in [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]:
                total_appearances += 1
        
        return total_appearances / len(df)
    
    def calculate_frequency_trend(self, df: pd.DataFrame, ball_num: int) -> float:
        """Calculer la tendance de fréquence (croissante/décroissante)."""
        if len(df) < 4:
            return 0.0
        
        # Diviser en deux moitiés et comparer
        mid = len(df) // 2
        first_half = df.iloc[:mid]
        second_half = df.iloc[mid:]
        
        freq1 = self.calculate_ball_frequency(first_half, ball_num)
        freq2 = self.calculate_ball_frequency(second_half, ball_num)
        
        # Tendance = différence entre les deux moitiés
        return freq2 - freq1
    
    def calculate_appearance_gaps(self, df: pd.DataFrame, ball_num: int) -> List[int]:
        """Calculer les intervalles entre apparitions d'une boule."""
        appearances = []
        
        for i, row in df.iterrows():
            if ball_num in [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]:
                appearances.append(i)
        
        # Calculer les gaps
        gaps = []
        for i in range(1, len(appearances)):
            gap = appearances[i] - appearances[i-1]
            gaps.append(gap)
        
        # Ajouter le gap depuis la dernière apparition
        if appearances:
            last_gap = len(df) - 1 - appearances[-1]
            gaps.append(last_gap)
        
        return gaps
    
    # Méthodes similaires pour les étoiles (simplifiées)
    def analyze_star_frequency_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Version étoiles de analyze_frequency_patterns."""
        star_scores = {}
        
        for star_num in range(1, 13):
            total_score = 0.0
            
            windows = [(10, 0.4), (25, 0.3), (50, 0.2), (100, 0.1)]
            
            for window_size, weight in windows:
                recent_draws = df.tail(window_size)
                frequency = self.calculate_star_frequency(recent_draws, star_num)
                score = frequency * weight
                total_score += score
            
            star_scores[star_num] = total_score
        
        return star_scores
    
    def analyze_star_recurrence_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Version étoiles de analyze_recurrence_patterns."""
        star_scores = {}
        recent_draws = df.tail(20)
        
        for star_num in range(1, 13):
            appearances = 0
            for _, row in recent_draws.iterrows():
                if star_num in [row['s1'], row['s2']]:
                    appearances += 1
            
            star_scores[star_num] = appearances / len(recent_draws) if recent_draws.empty == False else 0.0
        
        return star_scores
    
    def analyze_star_gap_patterns(self, df: pd.DataFrame) -> Dict[int, float]:
        """Version étoiles de analyze_gap_patterns."""
        star_scores = {}
        
        for star_num in range(1, 13):
            gaps = self.calculate_star_appearance_gaps(df, star_num)
            
            if not gaps:
                star_scores[star_num] = 0.0
                continue
            
            avg_gap = np.mean(gaps)
            last_gap = gaps[-1] if gaps else 0
            
            # Score simple basé sur le retard
            if last_gap > avg_gap:
                score = min(1.0, last_gap / (avg_gap + 1))
            else:
                score = max(0.0, 1.0 - last_gap / (avg_gap + 1))
            
            star_scores[star_num] = score
        
        return star_scores
    
    def calculate_star_frequency(self, df: pd.DataFrame, star_num: int) -> float:
        """Calculer la fréquence d'apparition d'une étoile."""
        if df.empty:
            return 0.0
        
        appearances = 0
        for _, row in df.iterrows():
            if star_num in [row['s1'], row['s2']]:
                appearances += 1
        
        return appearances / len(df)
    
    def calculate_star_appearance_gaps(self, df: pd.DataFrame, star_num: int) -> List[int]:
        """Calculer les gaps pour les étoiles."""
        appearances = []
        
        for i, row in df.iterrows():
            if star_num in [row['s1'], row['s2']]:
                appearances.append(i)
        
        gaps = []
        for i in range(1, len(appearances)):
            gap = appearances[i] - appearances[i-1]
            gaps.append(gap)
        
        if appearances:
            last_gap = len(df) - 1 - appearances[-1]
            gaps.append(last_gap)
        
        return gaps
    
    def combine_star_scores(self, ml_scores: List[float], freq_scores: Dict, 
                           pattern_scores: Dict, gap_scores: Dict) -> Dict[int, float]:
        """Combiner tous les scores pour les étoiles."""
        combined_scores = {}
        
        for star_num in range(1, 13):
            ml_score = ml_scores[star_num - 1] if ml_scores and len(ml_scores) >= star_num else 0.0
            freq_score = freq_scores.get(star_num, 0.0)
            pattern_score = pattern_scores.get(star_num, 0.0)
            gap_score = gap_scores.get(star_num, 0.0)
            
            final_score = (
                ml_score * self.ml_weight +
                freq_score * self.freq_weight +
                pattern_score * self.pattern_weight +
                gap_score * self.gap_weight
            )
            
            combined_scores[star_num] = final_score
        
        return combined_scores


if __name__ == "__main__":
    print("🎯 Stratégies Hybrides de Prédiction EuroMillions")
    print("=" * 50)
    print("Cette approche hybride combine:")
    print("  • 40% Modèles ML (LightGBM, etc.)")
    print("  • 25% Analyse fréquentielle avancée")
    print("  • 20% Patterns de récurrence")
    print("  • 15% Analyse des gaps/intervalles")
    print("\nStratégies de génération:")
    print("  • Top scores purs")
    print("  • Combinaisons diversifiées")
    print("  • Échantillonnage probabiliste")