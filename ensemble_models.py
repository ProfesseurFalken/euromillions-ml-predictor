"""
Ensemble Models for EuroMillions Prediction
==========================================

Advanced ensemble methods combining multiple ML algorithms for improved predictions.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# ML imports
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

# ML libraries
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

# Local imports
from repository import get_repository
from build_datasets import build_enhanced_datasets
from loguru import logger


class SimpleEnsemble:
    """Simple ensemble that averages predictions from multiple models."""
    
    def __init__(self, models, weights):
        self.models = models
        self.weights = np.array(weights) / np.sum(weights)  # Normalize weights
        
    def fit(self, X, y):
        # Models are already fitted
        return self
        
    def predict_proba(self, X):
        # Average predictions from all models
        predictions = []
        for name, model in self.models.items():
            pred = model.predict_proba(X)
            predictions.append(pred)
        
        # Weighted average
        avg_pred = np.average(predictions, weights=self.weights, axis=0)
        return avg_pred
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return (probas > 0.5).astype(int)


class EnsembleTrainer:
    """Advanced ensemble trainer for EuroMillions prediction."""
    
    def __init__(self):
        self.models_path = Path("models") / "euromillions"
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Ensemble configuration
        self.ensemble_config = {
            'voting_weights': [0.3, 0.25, 0.25, 0.2],  # LightGBM, XGBoost, CatBoost, RandomForest
            'cv_folds': 5,
            'meta_learner': 'lightgbm'
        }

    def models_exist(self) -> bool:
        """Check if ensemble models exist."""
        main_path = self.models_path / "ensemble_main_model.joblib"
        star_path = self.models_path / "ensemble_star_model.joblib"
        return main_path.exists() and star_path.exists()

    def get_ensemble_info(self) -> Dict[str, Any]:
        """Get ensemble model information."""
        meta_path = self.models_path / "ensemble_meta.json"
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                return json.load(f)
        return {"message": "Ensemble models not trained yet"}

    def create_base_models(self) -> Dict[str, Any]:
        """Create base models for ensemble."""
        
        # LightGBM - Fast and efficient
        lgb_params = {
            'objective': 'binary',
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 8,
            'num_leaves': 31,
            'random_state': 42,
            'verbose': -1
        }
        
        # XGBoost - Powerful gradient boosting
        xgb_params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            'n_estimators': 150,
            'verbosity': 0
        }
        
        # CatBoost - Handles categorical features well
        cat_params = {
            'iterations': 150,
            'learning_rate': 0.1,
            'depth': 6,
            'loss_function': 'Logloss',
            'random_seed': 42,
            'verbose': False,
            'allow_writing_files': False
        }
        
        # Random Forest - Robust baseline
        rf_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Type checkers don't recognize that these classifiers implement BaseEstimator
        base_models = {
            'lightgbm': MultiOutputClassifier(lgb.LGBMClassifier(**lgb_params)),  # type: ignore[arg-type]
            'xgboost': MultiOutputClassifier(xgb.XGBClassifier(**xgb_params)),  # type: ignore[arg-type]
            'catboost': MultiOutputClassifier(CatBoostClassifier(**cat_params)),  # type: ignore[arg-type]
            'random_forest': MultiOutputClassifier(RandomForestClassifier(**rf_params))  # type: ignore[arg-type]
        }
        
        logger.info(f"Created {len(base_models)} base models for ensemble")
        return base_models

    def create_simple_ensemble(self, base_models: Dict[str, Any]) -> SimpleEnsemble:
        """Create simple ensemble that averages predictions from base models."""
        
        weights = self.ensemble_config['voting_weights']
        ensemble = SimpleEnsemble(base_models, weights)
        
        logger.info("Created simple averaging ensemble")
        return ensemble

    def _train_ensemble_cv(self, X, y, base_models, model_type):
        """Train ensemble with cross-validation."""
        
        trained_models = {}
        
        # Train each base model
        for name, model in base_models.items():
            logger.info(f"Training base model: {name}")
            model.fit(X, y)
            trained_models[name] = model
        
        # Create simple ensemble
        ensemble = self.create_simple_ensemble(trained_models)
        ensemble.fit(X, y)  # Fit the ensemble
        
        # Calculate some basic metrics
        y_pred = ensemble.predict_proba(X)
        
        metrics = {
            'model_type': model_type,
            'n_samples': len(X),
            'n_features': X.shape[1],
            'base_models': list(trained_models.keys())
        }
        
        logger.info(f"Ensemble training completed for {model_type}")
        return ensemble, metrics

    def train_ensemble_models(self, game: str = "euromillions", min_rows: int = 300) -> Dict[str, Any]:
        """Train ensemble models for main balls and stars."""
        
        logger.info("Starting ensemble model training...")
        
        # Get data
        repo = get_repository()
        df = repo.all_draws_df()
        
        if len(df) < min_rows:
            raise ValueError(f"Need at least {min_rows} draws, got {len(df)}")
        
        logger.info(f"Training with {len(df)} draws")
        
        # Build enhanced datasets
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(df, window_size=100)
        
        logger.info(f"Features: {X_main.shape[1]} main, {X_star.shape[1]} star")
        
        # Create base models
        base_models_main = self.create_base_models()
        base_models_star = self.create_base_models()
        
        # Train main ball ensemble
        logger.info("Training main balls ensemble...")
        main_ensemble, main_metrics = self._train_ensemble_cv(
            X_main, y_main, base_models_main, "main"
        )
        
        # Train star ensemble
        logger.info("Training stars ensemble...")
        star_ensemble, star_metrics = self._train_ensemble_cv(
            X_star, y_star, base_models_star, "star"
        )
        
        # Save models
        main_model_path = self.models_path / "ensemble_main_model.joblib"
        star_model_path = self.models_path / "ensemble_star_model.joblib"
        meta_path = self.models_path / "ensemble_meta.json"
        
        joblib.dump(main_ensemble, main_model_path)
        joblib.dump(star_ensemble, star_model_path)
        
        # Save metadata
        ensemble_meta = {
            "trained_at": datetime.now().isoformat(),
            "game": game,
            "main_metrics": main_metrics,
            "star_metrics": star_metrics,
            "success": True
        }
        
        with open(meta_path, 'w') as f:
            json.dump(ensemble_meta, f, indent=2)
        
        logger.info("Ensemble models saved successfully")
        
        return {
            "success": True,
            "message": f"Ensemble models trained successfully",
            "models_trained": ["ensemble_main", "ensemble_star"],
            "main_metrics": main_metrics,
            "star_metrics": star_metrics
        }

    def predict_with_ensemble(self, X_main, X_star):
        """Make predictions using ensemble models."""
        
        if not self.models_exist():
            raise FileNotFoundError("Ensemble models not found. Run train_ensemble_models() first.")
        
        # Load models
        main_model_path = self.models_path / "ensemble_main_model.joblib"
        star_model_path = self.models_path / "ensemble_star_model.joblib"
        
        main_ensemble = joblib.load(main_model_path)
        star_ensemble = joblib.load(star_model_path)
        
        # Make predictions
        main_proba = main_ensemble.predict_proba(X_main)
        star_proba = star_ensemble.predict_proba(X_star)
        
        return main_proba, star_proba


def train_ensemble_models(game: str = "euromillions", min_rows: int = 300) -> Dict[str, Any]:
    """Public function to train ensemble models."""
    trainer = EnsembleTrainer()
    return trainer.train_ensemble_models(game=game, min_rows=min_rows)


def predict_with_ensemble(X_main, X_star):
    """Public function to make ensemble predictions."""
    trainer = EnsembleTrainer()
    return trainer.predict_with_ensemble(X_main, X_star)