"""
Training module for Euromillions prediction models.
Uses LightGBM with time series cross-validation for robust model training.
"""
import json
import joblib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
from sklearn.multioutput import MultiOutputClassifier
from loguru import logger

from config import get_settings
from repository import get_repository
from build_datasets import build_datasets, build_enhanced_datasets


class EuromillionsTrainer:
    """Trainer for Euromillions prediction models using LightGBM."""
    
    def __init__(self):
        """Initialize trainer with settings."""
        self.settings = get_settings()
        self.models_path = Path("models") / "euromillions"
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Cached models
        self._main_model = None
        self._star_model = None
        self._metadata = None
        self._models_loaded_at = None
    
    def train_latest(self, game: str = "euromillions", min_rows: int = 300) -> Dict[str, Any]:
        """
        Train latest models using all available data.
        
        Args:
            game: Game type (currently only "euromillions" supported)
            min_rows: Minimum number of draws required for training
            
        Returns:
            Dict with training metrics and metadata
        """
        logger.info(f"Starting training for {game} with min_rows={min_rows}")
        
        if game != "euromillions":
            raise ValueError(f"Unsupported game type: {game}")
        
        # Load all draws
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            raise ValueError("No draw data available in repository")
        
        if len(df) < min_rows:
            raise ValueError(f"Insufficient data: {len(df)} draws < {min_rows} required")
        
        logger.info(f"Loaded {len(df)} draws from {df['draw_date'].min()} to {df['draw_date'].max()}")
        
        # Filter to modern rules (post-2016) to avoid star 12 issues in cross-validation
        cutoff_date = '2016-09-27'
        modern_df = df[df['draw_date'] >= cutoff_date].copy()
        
        if len(modern_df) >= 200:  # Use modern data if we have enough
            df = modern_df
            logger.info(f"Using modern rules data: {len(df)} draws from {df['draw_date'].min()}")
        else:
            logger.warning(f"Not enough modern data ({len(modern_df)}), using all data with potential cross-validation issues")
        
        # Build datasets
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(
            df, window_size=min(100, len(df) // 3)
        )
        
        logger.info(f"Built datasets: X_main{X_main.shape}, y_main{y_main.shape}, "
                   f"X_star{X_star.shape}, y_star{y_star.shape}")
        
        # Train models with time series cross-validation
        main_model, main_metrics = self._train_model_cv(
            X_main, y_main, "main", n_splits=5
        )
        
        star_model, star_metrics = self._train_model_cv(
            X_star, y_star, "star", n_splits=5
        )
        
        # Save models and metadata
        trained_at = datetime.now().isoformat()
        
        model_meta = {
            "trained_at": trained_at,
            "game": game,
            "data_from": str(meta["data_from"]) if meta["data_from"] is not None else None,
            "data_to": str(meta["data_to"]) if meta["data_to"] is not None else None,
            "n_draws": meta["n_draws"],
            "n_samples": meta["n_samples"],
            "window_size": meta["window_size"],
            "features": meta["features"],
            "logloss_main": main_metrics["best_logloss"],
            "logloss_star": star_metrics["best_logloss"],
            "cv_splits": 5,
            "min_rows": min_rows,
            "main_model_params": main_model.estimator.get_params() if hasattr(main_model, 'estimator') else main_model.get_params(),
            "star_model_params": star_model.estimator.get_params() if hasattr(star_model, 'estimator') else star_model.get_params()
        }
        
        # Save models
        main_model_path = self.models_path / "main_model.joblib"
        star_model_path = self.models_path / "star_model.joblib"
        meta_path = self.models_path / "meta.json"
        
        joblib.dump(main_model, main_model_path)
        joblib.dump(star_model, star_model_path)
        
        with open(meta_path, 'w') as f:
            json.dump(model_meta, f, indent=2)
        
        logger.info(f"Models saved to {self.models_path}")
        logger.info(f"Main model log loss: {main_metrics['best_logloss']:.4f}")
        logger.info(f"Star model log loss: {star_metrics['best_logloss']:.4f}")
        
        # Return comprehensive metrics
        return {
            "success": True,
            "trained_at": trained_at,
            "data_range": {
                "from": meta["data_from"],
                "to": meta["data_to"],
                "n_draws": meta["n_draws"],
                "n_samples": meta["n_samples"]
            },
            "models": {
                "main": {
                    "logloss": main_metrics["best_logloss"],
                    "logloss_std": main_metrics["logloss_std"],
                    "best_fold": main_metrics["best_fold"],
                    "cv_scores": main_metrics["cv_scores"],
                    "path": str(main_model_path)
                },
                "star": {
                    "logloss": star_metrics["best_logloss"],
                    "logloss_std": star_metrics["logloss_std"],
                    "best_fold": star_metrics["best_fold"],
                    "cv_scores": star_metrics["cv_scores"],
                    "path": str(star_model_path)
                }
            },
            "meta_path": str(meta_path),
            "features": meta["features"],
            "cv_splits": 5
        }
    
    def _train_model_cv(self, X: np.ndarray, y: np.ndarray, 
                       target_type: str, n_splits: int = 5) -> Tuple[Any, Dict[str, Any]]:
        """
        Train model with time series cross-validation.
        
        Args:
            X: Feature matrix
            y: Label matrix  
            target_type: "main" or "star" for logging
            n_splits: Number of CV splits
            
        Returns:
            Tuple of (best_model, metrics_dict)
        """
        logger.info(f"Training {target_type} model with {n_splits}-fold time series CV")
        
        # Time series split (chronological)
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        cv_scores = []
        models = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            logger.info(f"Training fold {fold + 1}/{n_splits} for {target_type}")
            
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Configure LightGBM for multi-label classification
            lgb_params = {
                'objective': 'binary',
                'metric': 'binary_logloss',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.1,
                'feature_fraction': 0.8,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1,
                'random_state': 42,
                'n_estimators': 100,
                'force_row_wise': True  # Avoid warnings
            }
            
            # Use MultiOutputClassifier for multi-label classification
            model = MultiOutputClassifier(
                lgb.LGBMClassifier(**lgb_params),
                n_jobs=-1
            )
            
            # Train model
            model.fit(X_train, y_train)
            models.append(model)
            
            # Evaluate on validation set
            y_pred_proba = model.predict_proba(X_val)
            
            # Calculate log loss for each output
            fold_loglosses = []
            n_outputs = y_val.shape[1]
            
            for output_idx in range(n_outputs):
                y_true_output = y_val[:, output_idx]
                y_pred_output = y_pred_proba[output_idx][:, 1]  # Probability of class 1
                
                # Handle edge case where all predictions are 0 or 1
                y_pred_output = np.clip(y_pred_output, 1e-15, 1 - 1e-15)
                
                output_logloss = log_loss(y_true_output, y_pred_output)
                fold_loglosses.append(output_logloss)
            
            # Average log loss across all outputs
            fold_avg_logloss = np.mean(fold_loglosses)
            cv_scores.append(fold_avg_logloss)
            
            logger.info(f"Fold {fold + 1} {target_type} log loss: {fold_avg_logloss:.4f}")
        
        # Find best model (lowest log loss)
        best_fold = np.argmin(cv_scores)
        best_model = models[best_fold]
        best_logloss = cv_scores[best_fold]
        
        # Calculate statistics
        logloss_mean = np.mean(cv_scores)
        logloss_std = np.std(cv_scores)
        
        logger.info(f"Best {target_type} model: fold {best_fold + 1} "
                   f"(log loss: {best_logloss:.4f})")
        logger.info(f"CV {target_type} log loss: {logloss_mean:.4f} ± {logloss_std:.4f}")
        
        metrics = {
            "best_logloss": best_logloss,
            "logloss_mean": logloss_mean,
            "logloss_std": logloss_std,
            "best_fold": best_fold + 1,
            "cv_scores": cv_scores,
            "n_splits": n_splits
        }
        
        return best_model, metrics
    
    def load_models(self, force: bool = False) -> Tuple[Any, Any, Dict[str, Any]]:
        """
        Load trained models from disk with caching.
        
        Args:
            force: If True, force reload even if models are cached
            
        Returns:
            Tuple of (main_model, star_model, metadata)
        """
        # Check if models are already cached and force is not requested
        if not force and self._main_model is not None and self._star_model is not None:
            logger.debug("Using cached models")
            return self._main_model, self._star_model, self._metadata
        
        main_model_path = self.models_path / "main_model.joblib"
        star_model_path = self.models_path / "star_model.joblib"
        meta_path = self.models_path / "meta.json"
        
        if not all(p.exists() for p in [main_model_path, star_model_path, meta_path]):
            raise FileNotFoundError("Trained models not found. Run train_latest() first.")
        
        logger.info("Loading models from disk...")
        self._main_model = joblib.load(main_model_path)
        self._star_model = joblib.load(star_model_path)
        
        with open(meta_path, 'r') as f:
            self._metadata = json.load(f)
        
        self._models_loaded_at = datetime.now().isoformat()
        logger.info(f"Models loaded successfully (trained: {self._metadata['trained_at']})")
        
        return self._main_model, self._star_model, self._metadata
    
    def predict_next_draw(self, return_probabilities: bool = False) -> Dict[str, Any]:
        """
        Predict the next draw using trained models.
        
        Args:
            return_probabilities: Whether to return probability scores
            
        Returns:
            Dict with predictions and metadata
        """
        logger.info("Predicting next draw...")
        
        # Load models
        main_model, star_model, metadata = self.load_models()
        
        # Get latest data for prediction
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            raise ValueError("No data available for prediction")
        
        # Build features using same parameters as training
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(
            df, window_size=metadata.get("window_size", 100)
        )
        
        # Use most recent sample for prediction
        latest_X_main = X_main[-1:] 
        latest_X_star = X_star[-1:]
        
        # Get predictions
        main_proba = main_model.predict_proba(latest_X_main)
        star_proba = star_model.predict_proba(latest_X_star)
        
        # Extract probabilities for positive class (ball appears)
        main_probs = np.array([pred[:, 1] for pred in main_proba]).flatten()
        star_probs = np.array([pred[:, 1] for pred in star_proba]).flatten()
        
        # Select top predictions
        top_main_indices = np.argsort(main_probs)[-5:]  # Top 5 main balls
        top_star_indices = np.argsort(star_probs)[-2:]  # Top 2 stars
        
        # Convert to 1-based numbering and sort
        predicted_main = sorted(top_main_indices + 1)
        predicted_stars = sorted(top_star_indices + 1)
        
        result = {
            "predicted_main": predicted_main,
            "predicted_stars": predicted_stars,
            "prediction_date": datetime.now().isoformat(),
            "model_trained_at": metadata["trained_at"],
            "data_range": {
                "from": metadata["data_from"],
                "to": metadata["data_to"]
            }
        }
        
        if return_probabilities:
            result["main_probabilities"] = {
                f"ball_{i+1}": float(prob) for i, prob in enumerate(main_probs)
            }
            result["star_probabilities"] = {
                f"star_{i+1}": float(prob) for i, prob in enumerate(star_probs)
            }
        
        logger.info(f"Prediction: Main {predicted_main}, Stars {predicted_stars}")
        
        return result
    
    def _get_latest_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get features for the most recent draw for scoring."""
        # Get latest data
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            raise ValueError("No data available for feature extraction")
        
        # Build features using same parameters as training
        _, metadata = self.load_models()[:2], self.load_models()[2]
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(
            df, window_size=metadata.get("window_size", 100)
        )
        
        # Return most recent features
        return X_main[-1:], X_star[-1:]
    
    def score_balls(self) -> list[tuple[int, float]]:
        """
        Score all main balls (1-50) with probability of appearing in next draw.
        
        Returns:
            List of (ball_number, probability) tuples sorted by ball number
        """
        logger.info("Scoring main balls...")
        
        # Load models and get features
        main_model, _, _ = self.load_models()
        latest_X_main, _ = self._get_latest_features()
        
        # Get predictions
        main_proba = main_model.predict_proba(latest_X_main)
        
        # Extract probabilities for positive class (ball appears)
        main_probs = np.array([pred[:, 1] for pred in main_proba]).flatten()
        
        # Create list of (ball_number, probability) tuples
        ball_scores = [(i + 1, float(prob)) for i, prob in enumerate(main_probs)]
        
        logger.info(f"Scored {len(ball_scores)} main balls")
        return ball_scores
    
    def score_stars(self) -> list[tuple[int, float]]:
        """
        Score all stars (1-12) with probability of appearing in next draw.
        
        Returns:
            List of (star_number, probability) tuples sorted by star number
        """
        logger.info("Scoring stars...")
        
        # Load models and get features
        _, star_model, _ = self.load_models()
        _, latest_X_star = self._get_latest_features()
        
        # Get predictions
        star_proba = star_model.predict_proba(latest_X_star)
        
        # Extract probabilities for positive class (star appears)
        star_probs = np.array([pred[:, 1] for pred in star_proba]).flatten()
        
        # Create list of (star_number, probability) tuples
        star_scores = [(i + 1, float(prob)) for i, prob in enumerate(star_probs)]
        
        logger.info(f"Scored {len(star_scores)} stars")
        return star_scores
    
    def suggest_combinations(self, k: int = 10, method: str = "hybrid", seed: int = 42) -> list[dict]:
        """
        Suggest k combinations of balls and stars using different methods.
        
        Args:
            k: Number of combinations to suggest
            method: "topk", "random", or "hybrid"
            seed: Random seed for reproducibility
            
        Returns:
            List of combination dictionaries with balls, stars, and scores
        """
        logger.info(f"Generating {k} combinations using {method} method")
        
        # Set random seed for reproducibility
        np.random.seed(seed)
        
        # Get scores
        ball_scores = self.score_balls()
        star_scores = self.score_stars()
        
        # Sort by probability (descending)
        sorted_balls = sorted(ball_scores, key=lambda x: x[1], reverse=True)
        sorted_stars = sorted(star_scores, key=lambda x: x[1], reverse=True)
        
        combinations = []
        
        for i in range(k):
            if method == "topk":
                combo = self._generate_topk_combination(sorted_balls, sorted_stars)
            elif method == "random":
                combo = self._generate_random_combination(ball_scores, star_scores)
            elif method == "hybrid":
                # Mix of topk and random based on iteration
                if i < k // 2:
                    combo = self._generate_topk_combination(sorted_balls, sorted_stars, top_n=15)
                else:
                    combo = self._generate_random_combination(ball_scores, star_scores)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Add metadata
            combo["combination_id"] = i + 1
            combo["method"] = method
            combo["generated_at"] = datetime.now().isoformat()
            
            combinations.append(combo)
        
        # Save scores to file
        self._save_latest_scores(ball_scores, star_scores, combinations)
        
        logger.info(f"Generated {len(combinations)} combinations")
        return combinations
    
    def _generate_topk_combination(self, sorted_balls: list, sorted_stars: list, 
                                 top_n: int = None) -> dict:
        """Generate combination using top-k approach."""
        if top_n is None:
            # Pure top-k: take top 5 balls and top 2 stars
            selected_balls = [ball for ball, _ in sorted_balls[:5]]
            selected_stars = [star for star, _ in sorted_stars[:2]]
        else:
            # Top-N with some randomness: sample from top N candidates
            ball_candidates = sorted_balls[:min(top_n, len(sorted_balls))]
            star_candidates = sorted_stars[:min(top_n, len(sorted_stars))]
            
            # Weighted sampling from top candidates
            ball_weights = [prob for _, prob in ball_candidates]
            star_weights = [prob for _, prob in star_candidates]
            
            ball_indices = np.random.choice(
                len(ball_candidates), size=5, replace=False, 
                p=np.array(ball_weights) / sum(ball_weights)
            )
            star_indices = np.random.choice(
                len(star_candidates), size=2, replace=False,
                p=np.array(star_weights) / sum(star_weights)
            )
            
            selected_balls = [ball_candidates[i][0] for i in ball_indices]
            selected_stars = [star_candidates[i][0] for i in star_indices]
        
        # Sort the selections
        selected_balls.sort()
        selected_stars.sort()
        
        # Calculate combined score
        ball_probs = [prob for ball, prob in sorted_balls if ball in selected_balls]
        star_probs = [prob for star, prob in sorted_stars if star in selected_stars]
        combined_score = np.mean(ball_probs + star_probs)
        
        return {
            "balls": [int(x) for x in selected_balls],  # Ensure Python int
            "stars": [int(x) for x in selected_stars],  # Ensure Python int
            "ball_probabilities": {int(k): float(v) for k, v in zip(selected_balls, ball_probs)},
            "star_probabilities": {int(k): float(v) for k, v in zip(selected_stars, star_probs)},
            "combined_score": float(combined_score)
        }
    
    def _generate_random_combination(self, ball_scores: list, star_scores: list) -> dict:
        """Generate combination using weighted random sampling."""
        # Extract probabilities
        ball_probs = [prob for _, prob in ball_scores]
        star_probs = [prob for _, prob in star_scores]
        
        # Normalize probabilities
        ball_weights = np.array(ball_probs) / sum(ball_probs)
        star_weights = np.array(star_probs) / sum(star_probs)
        
        # Sample without replacement
        ball_indices = np.random.choice(
            50, size=5, replace=False, p=ball_weights
        )
        star_indices = np.random.choice(
            12, size=2, replace=False, p=star_weights
        )
        
        # Convert to ball/star numbers and sort
        selected_balls = sorted([int(i + 1) for i in ball_indices])  # Ensure Python int
        selected_stars = sorted([int(i + 1) for i in star_indices])  # Ensure Python int
        
        # Get probabilities for selected numbers
        ball_probs_selected = [ball_scores[ball - 1][1] for ball in selected_balls]
        star_probs_selected = [star_scores[star - 1][1] for star in selected_stars]
        
        combined_score = np.mean(ball_probs_selected + star_probs_selected)
        
        return {
            "balls": [int(x) for x in selected_balls],  # Ensure Python int
            "stars": [int(x) for x in selected_stars],  # Ensure Python int
            "ball_probabilities": {int(k): float(v) for k, v in zip(selected_balls, ball_probs_selected)},
            "star_probabilities": {int(k): float(v) for k, v in zip(selected_stars, star_probs_selected)},
            "combined_score": float(combined_score)
        }
    
    def _save_latest_scores(self, ball_scores: list, star_scores: list, 
                          combinations: list) -> None:
        """Save latest scores and combinations to JSON file."""
        scores_data = {
            "scored_at": datetime.now().isoformat(),
            "model_info": {
                "trained_at": self._metadata["trained_at"] if self._metadata else None,
                "data_range": {
                    "from": str(self._metadata["data_from"]) if self._metadata else None,
                    "to": str(self._metadata["data_to"]) if self._metadata else None
                }
            },
            "ball_scores": {
                f"ball_{int(ball)}": float(prob) for ball, prob in ball_scores
            },
            "star_scores": {
                f"star_{int(star)}": float(prob) for star, prob in star_scores
            },
            "top_balls": [[int(ball), float(prob)] for ball, prob in sorted(ball_scores, key=lambda x: x[1], reverse=True)[:10]],
            "top_stars": [[int(star), float(prob)] for star, prob in sorted(star_scores, key=lambda x: x[1], reverse=True)[:5]],
            "combinations": combinations,
            "statistics": {
                "ball_score_mean": float(np.mean([prob for _, prob in ball_scores])),
                "ball_score_std": float(np.std([prob for _, prob in ball_scores])),
                "star_score_mean": float(np.mean([prob for _, prob in star_scores])),
                "star_score_std": float(np.std([prob for _, prob in star_scores])),
                "total_combinations": len(combinations)
            }
        }
        
        scores_path = self.models_path / "latest_scores.json"
        with open(scores_path, 'w') as f:
            json.dump(scores_data, f, indent=2)
        
        logger.info(f"Scores saved to {scores_path}")


# Convenience functions
def train_latest(game: str = "euromillions", min_rows: int = 300) -> Dict[str, Any]:
    """
    Train latest models using all available data.
    
    Args:
        game: Game type (currently only "euromillions" supported)
        min_rows: Minimum number of draws required for training
        
    Returns:
        Dict with training metrics and metadata
    """
    trainer = EuromillionsTrainer()
    return trainer.train_latest(game=game, min_rows=min_rows)


def load_models(force: bool = False) -> Tuple[Any, Any, Dict[str, Any]]:
    """
    Load trained models with caching.
    
    Args:
        force: If True, force reload even if models are cached
        
    Returns:
        Tuple of (main_model, star_model, metadata)
    """
    trainer = EuromillionsTrainer()
    return trainer.load_models(force=force)


def score_balls() -> list[tuple[int, float]]:
    """
    Score all main balls (1-50) with probability of appearing in next draw.
    
    Returns:
        List of (ball_number, probability) tuples sorted by ball number
    """
    trainer = EuromillionsTrainer()
    return trainer.score_balls()


def score_stars() -> list[tuple[int, float]]:
    """
    Score all stars (1-12) with probability of appearing in next draw.
    
    Returns:
        List of (star_number, probability) tuples sorted by star number
    """
    trainer = EuromillionsTrainer()
    return trainer.score_stars()


def suggest_combinations(k: int = 10, method: str = "hybrid", seed: int = 42) -> list[dict]:
    """
    Suggest k combinations of balls and stars using different methods.
    
    Args:
        k: Number of combinations to suggest
        method: "topk", "random", or "hybrid"
        seed: Random seed for reproducibility
        
    Returns:
        List of combination dictionaries with balls, stars, and scores
    """
    trainer = EuromillionsTrainer()
    return trainer.suggest_combinations(k=k, method=method, seed=seed)


def predict_next_draw(return_probabilities: bool = False) -> Dict[str, Any]:
    """
    Predict the next draw using trained models.
    
    Args:
        return_probabilities: Whether to return probability scores
        
    Returns:
        Dict with predictions and metadata
    """
    trainer = EuromillionsTrainer()
    return trainer.predict_next_draw(return_probabilities=return_probabilities)


def get_model_info() -> Dict[str, Any]:
    """Get information about currently trained models."""
    trainer = EuromillionsTrainer()
    try:
        _, _, metadata = trainer.load_models()
        return {
            "models_available": True,
            "trained_at": metadata["trained_at"],
            "data_range": {
                "from": metadata["data_from"],
                "to": metadata["data_to"],
                "n_draws": metadata["n_draws"]
            },
            "performance": {
                "main_logloss": metadata["logloss_main"],
                "star_logloss": metadata["logloss_star"]
            },
            "features": metadata["features"]
        }
    except FileNotFoundError:
        return {
            "models_available": False,
            "message": "No trained models found. Run train_latest() first."
        }
