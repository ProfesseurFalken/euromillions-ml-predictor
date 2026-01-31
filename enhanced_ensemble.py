"""
Enhanced Ensemble Strategy for EuroMillions Prediction
=======================================================

This module implements advanced ensemble techniques including:
- Stacking with meta-learner
- Dynamic weight optimization
- Specialized models for main balls vs stars
- Bayesian model averaging
- Cross-validation based model selection

Author: EuroMillions ML Predictor
Version: 2.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path
import json
import joblib
from datetime import datetime
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler

# Gradient boosting libraries
import lightgbm as lgb
import xgboost as xgb
try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    logger.warning("CatBoost not available")

# Local imports
from repository import get_repository
from build_datasets import build_enhanced_datasets


class StackingEnsemble:
    """
    Stacking ensemble that uses base model predictions as features for a meta-learner.
    """
    
    def __init__(self, 
                 meta_learner: str = 'lightgbm',
                 n_folds: int = 5):
        """
        Initialize stacking ensemble.
        
        Args:
            meta_learner: Type of meta-learner ('lightgbm', 'logistic', 'xgboost')
            n_folds: Number of folds for generating out-of-fold predictions
        """
        self.meta_learner_type = meta_learner
        self.n_folds = n_folds
        
        self.base_models = {}
        self.meta_model = None
        self.scaler = StandardScaler()
        
        logger.info(f"StackingEnsemble initialized with {meta_learner} meta-learner")
    
    def _create_base_models(self) -> Dict[str, Any]:
        """Create base model configurations."""
        
        models = {
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=8,
                num_leaves=31,
                random_state=42,
                verbose=-1
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                verbosity=0
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=50,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        }
        
        if CATBOOST_AVAILABLE:
            models['catboost'] = CatBoostClassifier(
                iterations=100,
                learning_rate=0.1,
                depth=6,
                random_seed=42,
                verbose=False,
                allow_writing_files=False
            )
        
        return models
    
    def _create_meta_learner(self):
        """Create the meta-learner model."""
        
        if self.meta_learner_type == 'lightgbm':
            return lgb.LGBMClassifier(
                n_estimators=50,
                learning_rate=0.05,
                max_depth=4,
                random_state=42,
                verbose=-1
            )
        elif self.meta_learner_type == 'logistic':
            return LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=42
            )
        elif self.meta_learner_type == 'xgboost':
            return xgb.XGBClassifier(
                n_estimators=50,
                learning_rate=0.05,
                max_depth=4,
                random_state=42,
                verbosity=0
            )
        else:
            return lgb.LGBMClassifier(
                n_estimators=50,
                learning_rate=0.05,
                random_state=42,
                verbose=-1
            )
    
    def _generate_oof_predictions(self, X: np.ndarray, y: np.ndarray, 
                                   model_name: str, model) -> np.ndarray:
        """Generate out-of-fold predictions for stacking."""
        
        n_samples = X.shape[0]
        n_classes = y.shape[1] if len(y.shape) > 1 else 1
        
        oof_predictions = np.zeros((n_samples, n_classes))
        
        tscv = TimeSeriesSplit(n_splits=self.n_folds)
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Clone model for this fold
            fold_model = MultiOutputClassifier(model.__class__(**model.get_params()))
            fold_model.fit(X_train, y_train)
            
            # Get probabilities for validation set
            pred_proba = fold_model.predict_proba(X_val)
            
            # Extract positive class probabilities
            for i, pred in enumerate(pred_proba):
                if hasattr(pred, 'shape') and len(pred.shape) == 2:
                    oof_predictions[val_idx, i] = pred[:, 1]
                else:
                    oof_predictions[val_idx, i] = pred
        
        return oof_predictions
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'StackingEnsemble':
        """
        Fit the stacking ensemble.
        
        Args:
            X: Feature matrix
            y: Target matrix (multi-output)
            
        Returns:
            self
        """
        logger.info("Fitting stacking ensemble...")
        
        # Create and store base models
        self.base_models = self._create_base_models()
        
        # Generate out-of-fold predictions from each base model
        oof_features = []
        
        for name, model in self.base_models.items():
            logger.info(f"Generating OOF predictions for {name}...")
            
            # Fit model on full data for later predictions
            multi_model = MultiOutputClassifier(model)
            multi_model.fit(X, y)
            self.base_models[name] = multi_model
            
            # Generate OOF predictions
            oof_pred = self._generate_oof_predictions(X, y, name, model)
            oof_features.append(oof_pred)
        
        # Stack OOF predictions as meta-features
        meta_X = np.hstack(oof_features)
        
        # Scale meta-features
        meta_X_scaled = self.scaler.fit_transform(meta_X)
        
        # Train meta-learner
        logger.info(f"Training {self.meta_learner_type} meta-learner...")
        self.meta_model = MultiOutputClassifier(self._create_meta_learner())  # type: ignore[arg-type]
        self.meta_model.fit(meta_X_scaled, y)
        
        logger.info("Stacking ensemble fitted successfully")
        return self
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities using the stacking ensemble.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability predictions for each class
        """
        # Get base model predictions
        base_predictions = []
        
        for name, model in self.base_models.items():
            pred_proba = model.predict_proba(X)
            # Stack positive class probabilities
            proba_matrix = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in pred_proba])
            base_predictions.append(proba_matrix)
        
        # Create meta-features
        meta_X = np.hstack(base_predictions)
        meta_X_scaled = self.scaler.transform(meta_X)
        
        if self.meta_model is None:
            raise ValueError("Meta model not fitted")
        # Get meta-learner predictions
        meta_pred = self.meta_model.predict_proba(meta_X)
        
        # Extract probabilities
        return np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in meta_pred])
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary labels."""
        proba = self.predict_proba(X)
        return (proba > 0.5).astype(int)


class DynamicWeightEnsemble:
    """
    Ensemble with dynamically optimized weights based on recent performance.
    """
    
    def __init__(self, 
                 lookback_window: int = 50,
                 weight_decay: float = 0.95):
        """
        Initialize dynamic weight ensemble.
        
        Args:
            lookback_window: Number of recent predictions to evaluate
            weight_decay: Exponential decay for older predictions
        """
        self.lookback_window = lookback_window
        self.weight_decay = weight_decay
        
        self.models = {}
        self.weights = {}
        self.performance_history = {}
        
        logger.info("DynamicWeightEnsemble initialized")
    
    def _create_models(self) -> Dict[str, Any]:
        """Create base models."""
        
        models = {
            'lgb_shallow': MultiOutputClassifier(lgb.LGBMClassifier(  # type: ignore[arg-type]
                n_estimators=50, max_depth=4, random_state=42, verbose=-1
            )),
            'lgb_deep': MultiOutputClassifier(lgb.LGBMClassifier(  # type: ignore[arg-type]
                n_estimators=100, max_depth=10, random_state=42, verbose=-1
            )),
            'xgb_balanced': MultiOutputClassifier(xgb.XGBClassifier(
                n_estimators=100, max_depth=6, random_state=42, verbosity=0
            )),
            'rf_large': MultiOutputClassifier(RandomForestClassifier(
                n_estimators=200, max_depth=12, random_state=42, n_jobs=-1
            ))
        }
        
        if CATBOOST_AVAILABLE:
            models['catboost'] = MultiOutputClassifier(CatBoostClassifier(  # type: ignore[arg-type]
                iterations=100, depth=6, random_seed=42, 
                verbose=False, allow_writing_files=False
            ))
        
        return models
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'DynamicWeightEnsemble':
        """Fit all base models."""
        
        self.models = self._create_models()
        
        for name, model in self.models.items():
            logger.info(f"Fitting {name}...")
            model.fit(X, y)
            self.weights[name] = 1.0 / len(self.models)  # Equal initial weights
            self.performance_history[name] = []
        
        return self
    
    def update_weights(self, X: np.ndarray, y_true: np.ndarray):
        """
        Update model weights based on recent performance.
        
        Args:
            X: Features for recent samples
            y_true: True labels for recent samples
        """
        for name, model in self.models.items():
            # Get predictions
            y_pred = model.predict_proba(X)
            proba = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in y_pred])
            
            # Calculate performance (negative log loss = higher is better)
            try:
                performance = -log_loss(y_true, proba, labels=[0, 1])
            except ValueError:
                performance = -1.0
            
            self.performance_history[name].append(performance)
        
        # Calculate weights based on exponentially weighted performance
        total_performance = {}
        
        for name, history in self.performance_history.items():
            recent = history[-self.lookback_window:]
            weighted_sum = 0
            weight_total = 0
            
            for i, perf in enumerate(reversed(recent)):
                w = self.weight_decay ** i
                weighted_sum += w * perf
                weight_total += w
            
            total_performance[name] = weighted_sum / weight_total if weight_total > 0 else 0
        
        # Softmax to convert to weights
        perf_values = list(total_performance.values())
        exp_perf = np.exp(np.array(perf_values) - max(perf_values))
        weights = exp_perf / exp_perf.sum()
        
        for i, name in enumerate(total_performance.keys()):
            self.weights[name] = weights[i]
        
        logger.debug(f"Updated weights: {self.weights}")
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict using weighted ensemble."""
        
        all_predictions = []
        
        for name, model in self.models.items():
            pred = model.predict_proba(X)
            proba = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in pred])
            all_predictions.append(self.weights[name] * proba)
        
        return np.sum(all_predictions, axis=0)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary labels."""
        return (self.predict_proba(X) > 0.5).astype(int)


class SpecializedEnsemble:
    """
    Ensemble with specialized models for different number ranges.
    
    Uses separate models for:
    - Low numbers (1-17)
    - Mid numbers (18-34)
    - High numbers (35-50)
    - Stars (1-12)
    """
    
    def __init__(self):
        """Initialize specialized ensemble."""
        
        self.low_model = None  # Numbers 1-17
        self.mid_model = None  # Numbers 18-34
        self.high_model = None  # Numbers 35-50
        self.star_model = None  # Stars 1-12
        
        self.range_boundaries = {
            'low': (0, 17),
            'mid': (17, 34),
            'high': (34, 50)
        }
        
        logger.info("SpecializedEnsemble initialized")
    
    def _create_specialized_model(self, n_outputs: int):
        """Create a model optimized for the number of outputs."""
        
        if n_outputs <= 12:  # Stars or small range
            return MultiOutputClassifier(lgb.LGBMClassifier(  # type: ignore[arg-type]
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            ))
        else:  # Larger ranges
            return MultiOutputClassifier(lgb.LGBMClassifier(  # type: ignore[arg-type]
                n_estimators=150,
                max_depth=8,
                learning_rate=0.1,
                num_leaves=50,
                random_state=42,
                verbose=-1
            ))
    
    def fit(self, X_main: np.ndarray, y_main: np.ndarray,
            X_star: np.ndarray, y_star: np.ndarray) -> 'SpecializedEnsemble':
        """
        Fit specialized models for each number range.
        
        Args:
            X_main: Main ball features
            y_main: Main ball labels (50 columns)
            X_star: Star features
            y_star: Star labels (12 columns)
        """
        # Split main ball labels by range
        y_low = y_main[:, :17]
        y_mid = y_main[:, 17:34]
        y_high = y_main[:, 34:]
        
        logger.info("Fitting low number specialist...")
        self.low_model = self._create_specialized_model(17)
        self.low_model.fit(X_main, y_low)
        
        logger.info("Fitting mid number specialist...")
        self.mid_model = self._create_specialized_model(17)
        self.mid_model.fit(X_main, y_mid)
        
        logger.info("Fitting high number specialist...")
        self.high_model = self._create_specialized_model(16)
        self.high_model.fit(X_main, y_high)
        
        logger.info("Fitting star specialist...")
        self.star_model = self._create_specialized_model(12)
        self.star_model.fit(X_star, y_star)
        
        return self
    
    def predict_proba_main(self, X: np.ndarray) -> np.ndarray:
        """Predict main ball probabilities."""
        if self.low_model is None or self.mid_model is None or self.high_model is None:
            raise ValueError("Models not fitted")
        
        low_pred = self.low_model.predict_proba(X)
        mid_pred = self.mid_model.predict_proba(X)
        high_pred = self.high_model.predict_proba(X)
        
        # Combine predictions
        low_proba = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in low_pred])
        mid_proba = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in mid_pred])
        high_proba = np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in high_pred])
        
        return np.hstack([low_proba, mid_proba, high_proba])
    
    def predict_proba_star(self, X: np.ndarray) -> np.ndarray:
        """Predict star probabilities."""
        if self.star_model is None:
            raise ValueError("Star model not fitted")
        
        star_pred = self.star_model.predict_proba(X)
        return np.column_stack([p[:, 1] if len(p.shape) > 1 else p for p in star_pred])


class EnhancedEnsembleTrainer:
    """
    Master ensemble trainer that combines all ensemble strategies.
    """
    
    def __init__(self, 
                 strategy: str = 'stacking',
                 save_path: Optional[Path] = None):
        """
        Initialize enhanced ensemble trainer.
        
        Args:
            strategy: 'stacking', 'dynamic', 'specialized', or 'all'
            save_path: Path to save trained models
        """
        self.strategy = strategy
        self.save_path = save_path or Path('models/euromillions')
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        self.main_ensemble = None
        self.star_ensemble = None
        self.training_metadata = {}
    
    def train(self, min_rows: int = 300) -> Dict[str, Any]:
        """
        Train enhanced ensemble models.
        
        Args:
            min_rows: Minimum number of draws required
            
        Returns:
            Training metrics and metadata
        """
        logger.info(f"Training enhanced ensemble with strategy: {self.strategy}")
        
        # Load data
        repo = get_repository()
        df = repo.all_draws_df()
        
        if len(df) < min_rows:
            raise ValueError(f"Need at least {min_rows} draws, got {len(df)}")
        
        # Build features
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(df, window_size=100)
        
        logger.info(f"Data shapes: X_main={X_main.shape}, X_star={X_star.shape}")
        
        metrics = {}
        
        if self.strategy in ['stacking', 'all']:
            logger.info("Training stacking ensemble...")
            self.main_ensemble = StackingEnsemble(meta_learner='lightgbm')
            self.main_ensemble.fit(X_main, y_main)
            
            self.star_ensemble = StackingEnsemble(meta_learner='lightgbm')
            self.star_ensemble.fit(X_star, y_star)
            
            metrics['stacking'] = {'status': 'trained'}
        
        if self.strategy in ['dynamic', 'all']:
            logger.info("Training dynamic weight ensemble...")
            dynamic_main = DynamicWeightEnsemble()
            dynamic_main.fit(X_main, y_main)
            
            dynamic_star = DynamicWeightEnsemble()
            dynamic_star.fit(X_star, y_star)
            
            if self.strategy == 'dynamic':
                self.main_ensemble = dynamic_main
                self.star_ensemble = dynamic_star
            
            metrics['dynamic'] = {'status': 'trained'}
        
        if self.strategy in ['specialized', 'all']:
            logger.info("Training specialized ensemble...")
            specialized = SpecializedEnsemble()
            specialized.fit(X_main, y_main, X_star, y_star)
            
            if self.strategy == 'specialized':
                self.main_ensemble = specialized
                # Star model is inside specialized
            
            metrics['specialized'] = {'status': 'trained'}
        
        # Save models
        self._save_models()
        
        self.training_metadata = {
            'trained_at': datetime.now().isoformat(),
            'strategy': self.strategy,
            'n_draws': len(df),
            'data_range': {
                'from': str(df['draw_date'].min()),
                'to': str(df['draw_date'].max())
            },
            'metrics': metrics
        }
        
        with open(self.save_path / 'enhanced_ensemble_meta.json', 'w') as f:
            json.dump(self.training_metadata, f, indent=2)
        
        return self.training_metadata
    
    def _save_models(self):
        """Save trained models to disk."""
        
        if self.main_ensemble:
            joblib.dump(self.main_ensemble, self.save_path / 'enhanced_main_ensemble.joblib')
        if self.star_ensemble:
            joblib.dump(self.star_ensemble, self.save_path / 'enhanced_star_ensemble.joblib')
        
        logger.info(f"Models saved to {self.save_path}")
    
    def load_models(self):
        """Load trained models from disk."""
        
        main_path = self.save_path / 'enhanced_main_ensemble.joblib'
        star_path = self.save_path / 'enhanced_star_ensemble.joblib'
        
        if main_path.exists():
            self.main_ensemble = joblib.load(main_path)
        if star_path.exists():
            self.star_ensemble = joblib.load(star_path)
        
        logger.info("Enhanced ensemble models loaded")
    
    def predict(self, X_main: np.ndarray, X_star: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions using the trained ensemble.
        
        Args:
            X_main: Main ball features
            X_star: Star features
            
        Returns:
            Tuple of (main_probabilities, star_probabilities)
        """
        if self.main_ensemble is None:
            self.load_models()
        
        if isinstance(self.main_ensemble, SpecializedEnsemble):
            main_proba = self.main_ensemble.predict_proba_main(X_main)
            star_proba = self.main_ensemble.predict_proba_star(X_star)
        else:
            if self.main_ensemble is None or self.star_ensemble is None:
                raise ValueError("Ensembles not fitted")
            main_proba = self.main_ensemble.predict_proba(X_main)  # type: ignore[union-attr]
            star_proba = self.star_ensemble.predict_proba(X_star)  # type: ignore[union-attr]
        
        return main_proba, star_proba


def train_enhanced_ensemble(strategy: str = 'stacking', **kwargs) -> Dict[str, Any]:
    """
    Convenience function to train enhanced ensemble.
    
    Args:
        strategy: 'stacking', 'dynamic', 'specialized', or 'all'
        **kwargs: Additional training parameters
        
    Returns:
        Training metadata
    """
    trainer = EnhancedEnsembleTrainer(strategy=strategy)
    return trainer.train(**kwargs)


if __name__ == "__main__":
    # Test module
    print("Testing Enhanced Ensemble...")
    
    from repository import get_repository
    
    repo = get_repository()
    df = repo.all_draws_df()
    
    if len(df) >= 300:
        print(f"Training with {len(df)} draws...")
        
        # Test stacking ensemble
        result = train_enhanced_ensemble(strategy='stacking', min_rows=300)
        print(f"\nTraining result: {result}")
    else:
        print(f"Not enough data: {len(df)} draws (need 300)")
