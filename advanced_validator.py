"""
Stratégies de Validation et Métriques Avancées
==============================================

Système d'évaluation sophistiqué pour mesurer la performance réelle
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

class AdvancedValidator:
    """Validateur avancé pour les prédictions EuroMillions."""
    
    def __init__(self):
        self.metrics_history = []
        self.prediction_cache = {}
        
    def evaluate_prediction_system(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Évaluation complète du système de prédiction."""
        
        print("📊 Évaluation complète du système de prédiction...")
        
        results = {
            'accuracy_metrics': self.calculate_accuracy_metrics(predictions, actual_draws),
            'probability_calibration': self.evaluate_probability_calibration(predictions, actual_draws),
            'temporal_performance': self.analyze_temporal_performance(predictions, actual_draws),
            'strategy_comparison': self.compare_prediction_strategies(predictions, actual_draws),
            'roi_analysis': self.calculate_roi_analysis(predictions, actual_draws),
            'confidence_analysis': self.analyze_prediction_confidence(predictions, actual_draws)
        }
        
        # Générer un rapport complet
        report = self.generate_comprehensive_report(results)
        
        return {**results, 'report': report}
    
    def calculate_accuracy_metrics(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer des métriques de précision avancées."""
        
        metrics = {}
        
        # 1. Précision exacte (combinaison complète)
        exact_matches = self.count_exact_matches(predictions, actual_draws)
        metrics['exact_match_rate'] = exact_matches / len(predictions) if predictions else 0.0
        
        # 2. Précision partielle (nombre de boules correctes)
        partial_accuracies = self.calculate_partial_accuracies(predictions, actual_draws)
        metrics.update(partial_accuracies)
        
        # 3. Précision pondérée (selon la difficulté)
        weighted_accuracy = self.calculate_weighted_accuracy(predictions, actual_draws)
        metrics['weighted_accuracy'] = weighted_accuracy
        
        # 4. Métriques par position
        position_metrics = self.calculate_position_metrics(predictions, actual_draws)
        metrics.update(position_metrics)
        
        # 5. Métriques de distribution
        distribution_metrics = self.calculate_distribution_metrics(predictions, actual_draws)
        metrics.update(distribution_metrics)
        
        return metrics
    
    def evaluate_probability_calibration(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Évaluer la calibration des probabilités."""
        
        calibration_results = {
            'reliability_curve': self.calculate_reliability_curve(predictions, actual_draws),
            'brier_score': self.calculate_brier_score(predictions, actual_draws),
            'log_loss': self.calculate_log_loss(predictions, actual_draws),
            'probability_sharpness': self.calculate_probability_sharpness(predictions),
            'overconfidence_ratio': self.calculate_overconfidence_ratio(predictions, actual_draws)
        }
        
        return calibration_results
    
    def analyze_temporal_performance(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Analyser la performance dans le temps."""
        
        temporal_analysis = {
            'monthly_performance': self.calculate_monthly_performance(predictions, actual_draws),
            'seasonal_trends': self.analyze_seasonal_trends(predictions, actual_draws),
            'learning_curve': self.calculate_learning_curve(predictions, actual_draws),
            'prediction_drift': self.analyze_prediction_drift(predictions, actual_draws),
            'consistency_score': self.calculate_consistency_score(predictions, actual_draws)
        }
        
        return temporal_analysis
    
    def compare_prediction_strategies(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Comparer différentes stratégies de prédiction."""
        
        # Grouper les prédictions par stratégie
        strategies = defaultdict(list)
        
        for pred in predictions:
            strategy = pred.get('method', 'unknown')
            strategies[strategy].append(pred)
        
        comparison = {}
        
        for strategy_name, strategy_predictions in strategies.items():
            # Trouver les tirages correspondants
            matching_draws = self.match_predictions_to_draws(strategy_predictions, actual_draws)
            
            if matching_draws:
                strategy_metrics = self.calculate_strategy_metrics(strategy_predictions, matching_draws)
                comparison[strategy_name] = strategy_metrics
        
        # Classement des stratégies
        strategy_ranking = self.rank_strategies(comparison)
        
        return {
            'individual_strategies': comparison,
            'ranking': strategy_ranking,
            'best_strategy': strategy_ranking[0] if strategy_ranking else None
        }
    
    def calculate_roi_analysis(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Analyser le retour sur investissement."""
        
        roi_analysis = {
            'theoretical_roi': self.calculate_theoretical_roi(predictions, actual_draws),
            'practical_roi': self.calculate_practical_roi(predictions, actual_draws),
            'risk_adjusted_returns': self.calculate_risk_adjusted_returns(predictions, actual_draws),
            'breakeven_analysis': self.calculate_breakeven_analysis(predictions, actual_draws),
            'kelly_criterion': self.calculate_kelly_criterion(predictions, actual_draws)
        }
        
        return roi_analysis
    
    def calculate_partial_accuracies(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer les précisions partielles (1-5 boules correctes)."""
        
        accuracies = {}
        
        for num_correct in range(1, 6):  # 1 à 5 boules correctes
            total_predictions = 0
            correct_predictions = 0
            
            for pred in predictions:
                # Trouver le tirage correspondant
                matching_draw = self.find_matching_draw(pred, actual_draws)
                
                if matching_draw:
                    total_predictions += 1
                    
                    # Compter les boules correctes
                    pred_balls = set(pred.get('balls', []))
                    actual_balls = set([
                        matching_draw['n1'], matching_draw['n2'], matching_draw['n3'],
                        matching_draw['n4'], matching_draw['n5']
                    ])
                    
                    correct_count = len(pred_balls.intersection(actual_balls))
                    
                    if correct_count >= num_correct:
                        correct_predictions += 1
            
            if total_predictions > 0:
                accuracies[f'accuracy_{num_correct}_balls'] = correct_predictions / total_predictions
            else:
                accuracies[f'accuracy_{num_correct}_balls'] = 0.0
        
        # Même chose pour les étoiles
        for num_correct_stars in range(1, 3):  # 1 à 2 étoiles correctes
            total_predictions = 0
            correct_predictions = 0
            
            for pred in predictions:
                matching_draw = self.find_matching_draw(pred, actual_draws)
                
                if matching_draw:
                    total_predictions += 1
                    
                    pred_stars = set(pred.get('stars', []))
                    actual_stars = set([matching_draw['s1'], matching_draw['s2']])
                    
                    correct_count = len(pred_stars.intersection(actual_stars))
                    
                    if correct_count >= num_correct_stars:
                        correct_predictions += 1
            
            if total_predictions > 0:
                accuracies[f'accuracy_{num_correct_stars}_stars'] = correct_predictions / total_predictions
            else:
                accuracies[f'accuracy_{num_correct_stars}_stars'] = 0.0
        
        return accuracies
    
    def calculate_weighted_accuracy(self, predictions: List[Dict], actual_draws: List[Dict]) -> float:
        """Calculer la précision pondérée selon la difficulté."""
        
        # Poids selon le nombre de boules/étoiles correctes
        weights = {
            5: 100,    # 5 boules = jackpot
            4: 20,     # 4 boules
            3: 5,      # 3 boules
            2: 2,      # 2 boules
            1: 1,      # 1 boule
            0: 0       # Aucune
        }
        
        total_weighted_score = 0
        total_max_possible = 0
        
        for pred in predictions:
            matching_draw = self.find_matching_draw(pred, actual_draws)
            
            if matching_draw:
                # Score pour les boules
                pred_balls = set(pred.get('balls', []))
                actual_balls = set([
                    matching_draw['n1'], matching_draw['n2'], matching_draw['n3'],
                    matching_draw['n4'], matching_draw['n5']
                ])
                
                correct_balls = len(pred_balls.intersection(actual_balls))
                ball_score = weights.get(correct_balls, 0)
                
                # Score pour les étoiles
                pred_stars = set(pred.get('stars', []))
                actual_stars = set([matching_draw['s1'], matching_draw['s2']])
                
                correct_stars = len(pred_stars.intersection(actual_stars))
                star_score = weights.get(correct_stars, 0) * 0.5  # Étoiles moins pondérées
                
                total_weighted_score += ball_score + star_score
                total_max_possible += weights[5] + weights[2] * 0.5  # Max possible
        
        return total_weighted_score / total_max_possible if total_max_possible > 0 else 0.0
    
    def calculate_brier_score(self, predictions: List[Dict], actual_draws: List[Dict]) -> float:
        """Calculer le score de Brier pour les probabilités."""
        
        brier_scores = []
        
        for pred in predictions:
            matching_draw = self.find_matching_draw(pred, actual_draws)
            
            if matching_draw and 'probabilities' in pred:
                # Récupérer les probabilités prédites
                pred_probs = pred['probabilities']
                
                # Créer le vecteur de vérité (0 ou 1 pour chaque boule/étoile)
                truth_vector = self.create_truth_vector(matching_draw)
                
                # Calculer le score de Brier
                if len(pred_probs) == len(truth_vector):
                    brier = np.mean((np.array(pred_probs) - np.array(truth_vector)) ** 2)
                    brier_scores.append(brier)
        
        return np.mean(brier_scores) if brier_scores else 1.0  # 1.0 = pire score possible
    
    def calculate_monthly_performance(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer la performance par mois."""
        
        monthly_scores = defaultdict(list)
        
        for pred in predictions:
            if 'generated_at' in pred:
                date = pd.to_datetime(pred['generated_at'])
                month_key = f"{date.year}-{date.month:02d}"
                
                # Calculer le score pour cette prédiction
                score = self.calculate_single_prediction_score(pred, actual_draws)
                monthly_scores[month_key].append(score)
        
        # Moyenne par mois
        monthly_averages = {
            month: np.mean(scores) for month, scores in monthly_scores.items()
        }
        
        return monthly_averages
    
    def calculate_theoretical_roi(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer le ROI théorique."""
        
        # Gains théoriques selon le nombre de boules correctes
        payout_structure = {
            5: 1000000,  # Jackpot (simplifié)
            4: 1000,     # 4 boules correctes
            3: 50,       # 3 boules correctes
            2: 10,       # 2 boules correctes
            1: 0,        # 1 boule = pas de gain
            0: 0         # Aucune boule = pas de gain
        }
        
        total_investment = len(predictions) * 2.5  # 2.50€ par ticket
        total_winnings = 0
        
        win_distribution = defaultdict(int)
        
        for pred in predictions:
            matching_draw = self.find_matching_draw(pred, actual_draws)
            
            if matching_draw:
                # Compter les boules correctes
                pred_balls = set(pred.get('balls', []))
                actual_balls = set([
                    matching_draw['n1'], matching_draw['n2'], matching_draw['n3'],
                    matching_draw['n4'], matching_draw['n5']
                ])
                
                correct_balls = len(pred_balls.intersection(actual_balls))
                
                # Ajouter les gains
                winnings = payout_structure.get(correct_balls, 0)
                total_winnings += winnings
                win_distribution[correct_balls] += 1
        
        roi = ((total_winnings - total_investment) / total_investment) * 100 if total_investment > 0 else -100
        
        return {
            'total_investment': total_investment,
            'total_winnings': total_winnings,
            'net_profit': total_winnings - total_investment,
            'roi_percentage': roi,
            'win_distribution': dict(win_distribution),
            'hit_rate': sum(win_distribution[i] for i in range(2, 6)) / len(predictions) if predictions else 0
        }
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Générer un rapport complet d'évaluation."""
        
        report_lines = [
            "=" * 60,
            "📊 RAPPORT D'ÉVALUATION COMPLET - EUROMILLIONS ML",
            "=" * 60,
            "",
            "🎯 MÉTRIQUES DE PRÉCISION",
            "-" * 30
        ]
        
        # Métriques de précision
        accuracy = results.get('accuracy_metrics', {})
        
        for i in range(1, 6):
            acc_key = f'accuracy_{i}_balls'
            if acc_key in accuracy:
                percentage = accuracy[acc_key] * 100
                report_lines.append(f"  • {i} boule(s) correcte(s): {percentage:.2f}%")
        
        for i in range(1, 3):
            acc_key = f'accuracy_{i}_stars'
            if acc_key in accuracy:
                percentage = accuracy[acc_key] * 100
                report_lines.append(f"  • {i} étoile(s) correcte(s): {percentage:.2f}%")
        
        # ROI Analysis
        roi_data = results.get('roi_analysis', {})
        if roi_data:
            report_lines.extend([
                "",
                "💰 ANALYSE ROI",
                "-" * 20,
                f"  • Investissement total: {roi_data.get('theoretical_roi', {}).get('total_investment', 0):.2f}€",
                f"  • Gains totaux: {roi_data.get('theoretical_roi', {}).get('total_winnings', 0):.2f}€",
                f"  • Profit net: {roi_data.get('theoretical_roi', {}).get('net_profit', 0):.2f}€",
                f"  • ROI: {roi_data.get('theoretical_roi', {}).get('roi_percentage', -100):.2f}%",
                f"  • Taux de réussite: {roi_data.get('theoretical_roi', {}).get('hit_rate', 0)*100:.2f}%"
            ])
        
        # Comparaison des stratégies
        strategy_comparison = results.get('strategy_comparison', {})
        best_strategy = strategy_comparison.get('best_strategy')
        
        if best_strategy:
            report_lines.extend([
                "",
                "🏆 MEILLEURE STRATÉGIE",
                "-" * 25,
                f"  • Stratégie: {best_strategy.get('name', 'Inconnue')}",
                f"  • Score: {best_strategy.get('score', 0):.4f}"
            ])
        
        # Recommandations
        report_lines.extend([
            "",
            "💡 RECOMMANDATIONS",
            "-" * 25,
            "  • Augmenter la taille de l'historique de données",
            "  • Implémenter des features temporelles avancées",
            "  • Utiliser des ensembles de modèles",
            "  • Optimiser la calibration des probabilités",
            "  • Analyser les patterns saisonniers"
        ])
        
        report_lines.extend([
            "",
            "=" * 60,
            f"Rapport généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    # Méthodes utilitaires
    def count_exact_matches(self, predictions: List[Dict], actual_draws: List[Dict]) -> int:
        """Compter les correspondances exactes."""
        
        exact_matches = 0
        
        for pred in predictions:
            matching_draw = self.find_matching_draw(pred, actual_draws)
            
            if matching_draw:
                pred_balls = set(pred.get('balls', []))
                pred_stars = set(pred.get('stars', []))
                
                actual_balls = set([
                    matching_draw['n1'], matching_draw['n2'], matching_draw['n3'],
                    matching_draw['n4'], matching_draw['n5']
                ])
                actual_stars = set([matching_draw['s1'], matching_draw['s2']])
                
                if pred_balls == actual_balls and pred_stars == actual_stars:
                    exact_matches += 1
        
        return exact_matches
    
    def find_matching_draw(self, prediction: Dict, actual_draws: List[Dict]) -> Dict:
        """Trouver le tirage correspondant à une prédiction."""
        
        pred_date = None
        
        if 'target_date' in prediction:
            pred_date = pd.to_datetime(prediction['target_date'])
        elif 'generated_at' in prediction:
            # Approximation: le tirage suivant la génération
            gen_date = pd.to_datetime(prediction['generated_at'])
            # Chercher le prochain mardi ou vendredi
            for draw in actual_draws:
                draw_date = pd.to_datetime(draw['draw_date'])
                if draw_date > gen_date:
                    return draw
        
        # Chercher par date exacte
        if pred_date:
            for draw in actual_draws:
                if pd.to_datetime(draw['draw_date']) == pred_date:
                    return draw
        
        return None
    
    def create_truth_vector(self, actual_draw: Dict) -> List[int]:
        """Créer un vecteur de vérité pour un tirage."""
        
        truth_vector = []
        
        # Boules principales (50 éléments)
        actual_balls = set([
            actual_draw['n1'], actual_draw['n2'], actual_draw['n3'],
            actual_draw['n4'], actual_draw['n5']
        ])
        
        for ball_num in range(1, 51):
            truth_vector.append(1 if ball_num in actual_balls else 0)
        
        # Étoiles (12 éléments)
        actual_stars = set([actual_draw['s1'], actual_draw['s2']])
        
        for star_num in range(1, 13):
            truth_vector.append(1 if star_num in actual_stars else 0)
        
        return truth_vector
    
    def calculate_single_prediction_score(self, prediction: Dict, actual_draws: List[Dict]) -> float:
        """Calculer le score d'une seule prédiction."""
        
        matching_draw = self.find_matching_draw(prediction, actual_draws)
        
        if not matching_draw:
            return 0.0
        
        # Score basé sur le nombre de boules/étoiles correctes
        pred_balls = set(prediction.get('balls', []))
        pred_stars = set(prediction.get('stars', []))
        
        actual_balls = set([
            matching_draw['n1'], matching_draw['n2'], matching_draw['n3'],
            matching_draw['n4'], matching_draw['n5']
        ])
        actual_stars = set([matching_draw['s1'], matching_draw['s2']])
        
        correct_balls = len(pred_balls.intersection(actual_balls))
        correct_stars = len(pred_stars.intersection(actual_stars))
        
        # Score pondéré
        ball_score = correct_balls / 5.0  # Normaliser sur [0, 1]
        star_score = correct_stars / 2.0  # Normaliser sur [0, 1]
        
        return (ball_score * 0.7 + star_score * 0.3)  # Pondération 70/30
    
    # Méthodes supplémentaires (stubs pour l'exemple)
    def calculate_position_metrics(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer les métriques par position."""
        return {}
    
    def calculate_distribution_metrics(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, float]:
        """Calculer les métriques de distribution."""
        return {}
    
    def calculate_reliability_curve(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer la courbe de fiabilité."""
        return {}
    
    def calculate_log_loss(self, predictions: List[Dict], actual_draws: List[Dict]) -> float:
        """Calculer la log-loss."""
        return 1.0
    
    def calculate_probability_sharpness(self, predictions: List[Dict]) -> float:
        """Calculer la netteté des probabilités."""
        return 0.5
    
    def calculate_overconfidence_ratio(self, predictions: List[Dict], actual_draws: List[Dict]) -> float:
        """Calculer le ratio de surconfiance."""
        return 0.5
    
    def analyze_seasonal_trends(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Analyser les tendances saisonnières."""
        return {}
    
    def calculate_learning_curve(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer la courbe d'apprentissage."""
        return {}
    
    def analyze_prediction_drift(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Analyser la dérive des prédictions."""
        return {}
    
    def calculate_consistency_score(self, predictions: List[Dict], actual_draws: List[Dict]) -> float:
        """Calculer le score de cohérence."""
        return 0.5
    
    def match_predictions_to_draws(self, predictions: List[Dict], actual_draws: List[Dict]) -> List[Dict]:
        """Faire correspondre les prédictions aux tirages."""
        return []
    
    def calculate_strategy_metrics(self, predictions: List[Dict], draws: List[Dict]) -> Dict[str, Any]:
        """Calculer les métriques d'une stratégie."""
        return {'score': 0.5}
    
    def rank_strategies(self, comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Classer les stratégies."""
        return []
    
    def calculate_practical_roi(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer le ROI pratique."""
        return {}
    
    def calculate_risk_adjusted_returns(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer les rendements ajustés du risque."""
        return {}
    
    def calculate_breakeven_analysis(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer l'analyse de seuil de rentabilité."""
        return {}
    
    def calculate_kelly_criterion(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Calculer le critère de Kelly."""
        return {}
    
    def analyze_prediction_confidence(self, predictions: List[Dict], actual_draws: List[Dict]) -> Dict[str, Any]:
        """Analyser la confiance des prédictions."""
        return {}


if __name__ == "__main__":
    print("🏆 Système de Validation et Métriques Avancées")
    print("=" * 50)
    print("Métriques disponibles:")
    print("  • Précision exacte et partielle")
    print("  • Calibration des probabilités (Brier, Log-Loss)")
    print("  • Performance temporelle et saisonnière")
    print("  • Comparaison des stratégies")
    print("  • Analyse ROI détaillée")
    print("  • Métriques de confiance")
    print("  • Rapports complets automatisés")