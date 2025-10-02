#!/usr/bin/env python3
"""
Entraînement adaptatif des modèles EuroMillions avec détection automatique de la plage d'étoiles
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
import lightgbm as lgb
import pickle
import os
from datetime import datetime
from loguru import logger

from repository import EuromillionsRepository
from build_datasets_adaptive import build_datasets_adaptive

def train_adaptive_models(min_rows=300):
    """
    Train models with adaptive star range detection
    """
    logger.info(f"Starting adaptive training with min_rows={min_rows}")
    
    # Load data
    repo = EuromillionsRepository()
    df = repo.all_draws_df()
    
    if len(df) < min_rows:
        raise ValueError(f"Not enough data: {len(df)} rows, need at least {min_rows}")
    
    logger.info(f"Loaded {len(df)} draws from {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    # Build adaptive datasets
    X_main, y_main, X_star, y_star, meta = build_datasets_adaptive(df)
    max_stars = meta['max_stars_detected']
    
    logger.info(f"Built datasets: X_main{X_main.shape}, y_main{y_main.shape}, X_star{X_star.shape}, y_star{y_star.shape}")
    logger.info(f"Adaptive configuration: {max_stars} stars (1-{max_stars})")
    
    # Train main model
    logger.info("Training main model with 5-fold time series CV")
    main_model, main_cv_score = train_model_cv(X_main, y_main, "main", n_splits=5)
    
    # Train star model  
    logger.info("Training star model with 5-fold time series CV")
    star_model, star_cv_score = train_model_cv(X_star, y_star, "star", n_splits=5)
    
    # Save models with adaptive metadata
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Save main model
    main_model_path = os.path.join(models_dir, "main_model_adaptive.pkl")
    with open(main_model_path, 'wb') as f:
        pickle.dump({
            'model': main_model,
            'meta': meta,
            'cv_score': main_cv_score,
            'trained_at': datetime.now().isoformat(),
            'model_type': 'main_adaptive'
        }, f)
    
    # Save star model
    star_model_path = os.path.join(models_dir, "star_model_adaptive.pkl")
    with open(star_model_path, 'wb') as f:
        pickle.dump({
            'model': star_model,
            'meta': meta,
            'cv_score': star_cv_score,
            'trained_at': datetime.now().isoformat(),
            'model_type': 'star_adaptive',
            'max_stars': max_stars
        }, f)
    
    logger.info(f"✅ Models saved successfully!")
    logger.info(f"   📊 Main model CV score: {main_cv_score:.4f}")
    logger.info(f"   🌟 Star model CV score: {star_cv_score:.4f}")
    logger.info(f"   🔧 Adaptive stars: 1-{max_stars}")
    
    return {
        'main_model': main_model,
        'star_model': star_model,
        'main_cv_score': main_cv_score,
        'star_cv_score': star_cv_score,
        'meta': meta,
        'max_stars': max_stars
    }

def train_model_cv(X, y, model_type, n_splits=5):
    """
    Train model with time series cross-validation
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    cv_scores = []
    best_model = None
    best_score = float('inf')
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        logger.info(f"Training fold {fold + 1}/{n_splits} for {model_type}")
        
        X_train, X_val = X[train_idx], X[val_idx] 
        y_train, y_val = y[train_idx], y[val_idx]
        
        # LightGBM parameters
        params = {
            'objective': 'multiclass' if y.shape[1] > 2 else 'binary',
            'num_class': y.shape[1] if y.shape[1] > 2 else None,
            'metric': 'multi_logloss' if y.shape[1] > 2 else 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.1,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42
        }
        
        # Convert to multi-label format for LightGBM
        models = []
        fold_predictions = np.zeros_like(y_val)
        
        for class_idx in range(y.shape[1]):
            # Train binary classifier for each class
            train_data = lgb.Dataset(X_train, label=y_train[:, class_idx])
            val_data = lgb.Dataset(X_val, label=y_val[:, class_idx], reference=train_data)
            
            binary_params = params.copy()
            binary_params['objective'] = 'binary'
            binary_params['metric'] = 'binary_logloss'
            del binary_params['num_class']
            
            model = lgb.train(
                binary_params,
                train_data,
                valid_sets=[val_data],
                num_boost_round=100,
                callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)]
            )
            
            models.append(model)
            fold_predictions[:, class_idx] = model.predict(X_val)
        
        # Calculate validation score
        val_score = log_loss(y_val.ravel(), fold_predictions.ravel())
        cv_scores.append(val_score)
        
        logger.info(f"Fold {fold + 1} {model_type} log loss: {val_score:.4f}")
        
        if val_score < best_score:
            best_score = val_score
            best_model = models
    
    cv_mean = np.mean(cv_scores)
    cv_std = np.std(cv_scores)
    
    logger.info(f"Best {model_type} model: fold with log loss: {best_score:.4f}")
    logger.info(f"CV {model_type} log loss: {cv_mean:.4f} ± {cv_std:.4f}")
    
    return best_model, cv_mean

if __name__ == "__main__":
    try:
        result = train_adaptive_models()
        print("🎉 ENTRAÎNEMENT ADAPTATIF RÉUSSI!")
        print(f"📊 Score CV numéros: {result['main_cv_score']:.4f}")
        print(f"🌟 Score CV étoiles: {result['star_cv_score']:.4f}")
        print(f"🔧 Étoiles adaptatives: 1-{result['max_stars']}")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        print(f"❌ Échec de l'entraînement: {e}")