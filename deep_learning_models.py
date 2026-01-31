"""
Deep Learning Models for EuroMillions Prediction
=================================================

This module implements neural network models including:
- LSTM for sequence prediction
- Transformer-based attention models
- Autoencoder for anomaly detection
- Multi-head attention for pattern recognition

Author: EuroMillions ML Predictor
Version: 2.0.0
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path
import json
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

# Check for TensorFlow/Keras availability
TF_AVAILABLE = False
tf: Any = None
keras: Any = None
layers: Any = None
Model: Any = None
regularizers: Any = None
EarlyStopping: Any = None
ReduceLROnPlateau: Any = None
ModelCheckpoint: Any = None
Adam: Any = None

try:
    import tensorflow as _tf  # type: ignore[import-not-found]
    from tensorflow import keras as _keras  # type: ignore[import-not-found]
    from tensorflow.keras import layers as _layers, Model as _Model, regularizers as _regularizers  # type: ignore[import-not-found]
    from tensorflow.keras.callbacks import EarlyStopping as _EarlyStopping, ReduceLROnPlateau as _ReduceLROnPlateau, ModelCheckpoint as _ModelCheckpoint  # type: ignore[import-not-found]
    from tensorflow.keras.optimizers import Adam as _Adam  # type: ignore[import-not-found]
    
    # Assign to module-level variables
    tf = _tf
    keras = _keras
    layers = _layers
    Model = _Model
    regularizers = _regularizers
    EarlyStopping = _EarlyStopping
    ReduceLROnPlateau = _ReduceLROnPlateau
    ModelCheckpoint = _ModelCheckpoint
    Adam = _Adam
    
    TF_AVAILABLE = True
    logger.info(f"TensorFlow {_tf.__version__} available")
except ImportError as e:
    logger.warning(f"TensorFlow not available - deep learning models disabled: {e}")
except Exception as e:
    logger.warning(f"TensorFlow import error ({type(e).__name__}): {e}")

# Check for PyTorch availability as alternative
TORCH_AVAILABLE = False
torch: Any = None

try:
    import torch as _torch  # type: ignore[import-not-found]
    import torch.nn as _nn  # type: ignore[import-not-found]
    import torch.optim as _optim  # type: ignore[import-not-found]
    from torch.utils.data import DataLoader as _DataLoader, TensorDataset as _TensorDataset  # type: ignore[import-not-found]
    
    torch = _torch
    TORCH_AVAILABLE = True
    logger.info(f"PyTorch {torch.__version__} available")
except ImportError:
    pass


def is_deep_learning_available() -> bool:
    """Check if deep learning is available."""
    return TF_AVAILABLE


# Placeholder classes when TensorFlow is not available
class _DummyPredictor:
    """Placeholder when TensorFlow is not available."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise ImportError("TensorFlow is required for deep learning models. Install with: pip install tensorflow")
    
    def train(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        raise ImportError("TensorFlow is required for deep learning models")
    
    def predict(self, *args: Any, **kwargs: Any) -> Tuple[np.ndarray, np.ndarray]:
        raise ImportError("TensorFlow is required for deep learning models")
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        raise ImportError("TensorFlow is required for deep learning models")
    
    def load(self, *args: Any, **kwargs: Any) -> None:
        raise ImportError("TensorFlow is required for deep learning models")


if not TF_AVAILABLE:
    # Define placeholder classes
    LSTMPredictor = _DummyPredictor  # type: ignore[misc]
    TransformerPredictor = _DummyPredictor  # type: ignore[misc]
    HybridDeepLearningPredictor = _DummyPredictor  # type: ignore[misc]
else:
    # Define real classes when TensorFlow is available
    
    class LSTMPredictor:  # type: ignore[no-redef]
        """
        LSTM-based model for lottery number prediction.
        
        Uses sequence of historical draws to predict next draw probabilities.
        """
        
        def __init__(self, 
                     sequence_length: int = 20,
                     n_main_balls: int = 50,
                     n_stars: int = 12,
                     hidden_units: int = 128,
                     dropout_rate: float = 0.3) -> None:
            self.sequence_length = sequence_length
            self.n_main_balls = n_main_balls
            self.n_stars = n_stars
            self.hidden_units = hidden_units
            self.dropout_rate = dropout_rate
            
            self.main_model: Any = None
            self.star_model: Any = None
            self.history: Dict[str, Any] = {}
        
        def _build_main_model(self, input_shape: Tuple[int, ...]) -> Any:
            inputs = layers.Input(shape=input_shape)
            
            x = layers.Bidirectional(layers.LSTM(self.hidden_units, return_sequences=True))(inputs)
            x = layers.Dropout(self.dropout_rate)(x)
            x = layers.Bidirectional(layers.LSTM(self.hidden_units // 2, return_sequences=True))(x)
            x = layers.Dropout(self.dropout_rate)(x)
            x = layers.Bidirectional(layers.LSTM(self.hidden_units // 4))(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            x = layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.01))(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            x = layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01))(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            outputs = layers.Dense(self.n_main_balls, activation='sigmoid')(x)
            
            model = Model(inputs, outputs, name='main_ball_lstm')
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='binary_crossentropy',
                metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
            )
            
            return model
        
        def _build_star_model(self, input_shape: Tuple[int, ...]) -> Any:
            inputs = layers.Input(shape=input_shape)
            
            x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(inputs)
            x = layers.Dropout(self.dropout_rate)(x)
            x = layers.Bidirectional(layers.LSTM(32))(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            x = layers.Dense(32, activation='relu')(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            outputs = layers.Dense(self.n_stars, activation='sigmoid')(x)
            
            model = Model(inputs, outputs, name='star_lstm')
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='binary_crossentropy',
                metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
            )
            
            return model
        
        def prepare_sequences(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            df = df.sort_values('draw_date').reset_index(drop=True)
            n_draws = len(df)
            
            main_cols = [c for c in df.columns if c.startswith('b') and c[1:].isdigit()] or \
                        [c for c in df.columns if c.startswith('n') and c[1:].isdigit()]
            star_cols = ['s1', 's2']
            
            if not main_cols:
                main_cols = ['n1', 'n2', 'n3', 'n4', 'n5']
            
            main_one_hot = np.zeros((n_draws, self.n_main_balls))
            star_one_hot = np.zeros((n_draws, self.n_stars))
            
            for i, row in df.iterrows():
                for col in main_cols[:5]:
                    if col in row:
                        main_one_hot[i, int(row[col]) - 1] = 1  # type: ignore[index]
                for col in star_cols:
                    if col in row:
                        star_one_hot[i, int(row[col]) - 1] = 1  # type: ignore[index]
            
            X_main, y_main, X_star, y_star = [], [], [], []
            
            for i in range(self.sequence_length, n_draws):
                X_main.append(main_one_hot[i-self.sequence_length:i])
                X_star.append(star_one_hot[i-self.sequence_length:i])
                y_main.append(main_one_hot[i])
                y_star.append(star_one_hot[i])
            
            return (np.array(X_main), np.array(y_main), 
                    np.array(X_star), np.array(y_star))
        
        def train(self, df: pd.DataFrame, validation_split: float = 0.2, 
                  epochs: int = 100, batch_size: int = 32, verbose: int = 1) -> Dict[str, Any]:
            logger.info("Preparing sequence data for LSTM training...")
            X_main, y_main, X_star, y_star = self.prepare_sequences(df)
            
            logger.info(f"Data shapes: X_main={X_main.shape}, X_star={X_star.shape}")
            
            self.main_model = self._build_main_model((self.sequence_length, self.n_main_balls))
            self.star_model = self._build_star_model((self.sequence_length, self.n_stars))
            
            callbacks = [
                EarlyStopping(patience=15, restore_best_weights=True, monitor='val_loss'),
                ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6)
            ]
            
            logger.info("Training main ball LSTM...")
            main_history = self.main_model.fit(
                X_main, y_main, validation_split=validation_split, epochs=epochs,
                batch_size=batch_size, callbacks=callbacks, verbose=verbose
            )
            
            logger.info("Training star LSTM...")
            star_history = self.star_model.fit(
                X_star, y_star, validation_split=validation_split, epochs=epochs,
                batch_size=batch_size, callbacks=callbacks, verbose=verbose
            )
            
            self.history = {'main': main_history.history, 'star': star_history.history}
            
            return {
                'main_loss': min(main_history.history['val_loss']),
                'star_loss': min(star_history.history['val_loss']),
                'main_epochs': len(main_history.history['loss']),
                'star_epochs': len(star_history.history['loss'])
            }
        
        def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
            X_main, _, X_star, _ = self.prepare_sequences(df)
            main_proba = self.main_model.predict(X_main[-1:], verbose=0)[0]
            star_proba = self.star_model.predict(X_star[-1:], verbose=0)[0]
            return main_proba, star_proba
        
        def save(self, path: Path | str) -> None:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            if self.main_model:
                self.main_model.save(path / 'main_lstm.keras')
            if self.star_model:
                self.star_model.save(path / 'star_lstm.keras')
            with open(path / 'config.json', 'w') as f:
                json.dump({
                    'sequence_length': self.sequence_length,
                    'n_main_balls': self.n_main_balls,
                    'n_stars': self.n_stars,
                    'hidden_units': self.hidden_units,
                    'dropout_rate': self.dropout_rate
                }, f)
        
        def load(self, path: Path | str) -> None:
            path = Path(path)
            with open(path / 'config.json', 'r') as f:
                config = json.load(f)
            self.sequence_length = config['sequence_length']
            self.n_main_balls = config['n_main_balls']
            self.n_stars = config['n_stars']
            self.hidden_units = config['hidden_units']
            self.dropout_rate = config['dropout_rate']
            self.main_model = keras.models.load_model(path / 'main_lstm.keras')
            self.star_model = keras.models.load_model(path / 'star_lstm.keras')


    class TransformerPredictor:  # type: ignore[no-redef]
        """Transformer-based model for lottery number prediction."""
        
        def __init__(self, sequence_length: int = 20, n_main_balls: int = 50, n_stars: int = 12, 
                     d_model: int = 64, num_heads: int = 4, dff: int = 128, 
                     num_layers: int = 2, dropout_rate: float = 0.1) -> None:
            self.sequence_length = sequence_length
            self.n_main_balls = n_main_balls
            self.n_stars = n_stars
            self.d_model = d_model
            self.num_heads = num_heads
            self.dff = dff
            self.num_layers = num_layers
            self.dropout_rate = dropout_rate
            
            self.main_model: Any = None
            self.star_model: Any = None
            self.history: Dict[str, Any] = {}
        
        def _positional_encoding(self, seq_len: int, d_model: int) -> np.ndarray:
            positions = np.arange(seq_len)[:, np.newaxis]
            dimensions = np.arange(d_model)[np.newaxis, :]
            angles = positions / np.power(10000, (2 * (dimensions // 2)) / d_model)
            angles[:, 0::2] = np.sin(angles[:, 0::2])
            angles[:, 1::2] = np.cos(angles[:, 1::2])
            return angles[np.newaxis, :, :]
        
        def _transformer_encoder(self, inputs: Any, num_outputs: int) -> Any:
            x = layers.Dense(self.d_model)(inputs)
            pos_encoding = self._positional_encoding(self.sequence_length, self.d_model)
            x = x + pos_encoding
            
            for _ in range(self.num_layers):
                attention = layers.MultiHeadAttention(
                    num_heads=self.num_heads,
                    key_dim=self.d_model // self.num_heads
                )(x, x)
                attention = layers.Dropout(self.dropout_rate)(attention)
                x = layers.LayerNormalization()(x + attention)
                
                ff = layers.Dense(self.dff, activation='relu')(x)
                ff = layers.Dense(self.d_model)(ff)
                ff = layers.Dropout(self.dropout_rate)(ff)
                x = layers.LayerNormalization()(x + ff)
            
            x = layers.GlobalAveragePooling1D()(x)
            x = layers.Dense(64, activation='relu')(x)
            x = layers.Dropout(self.dropout_rate)(x)
            outputs = layers.Dense(num_outputs, activation='sigmoid')(x)
            return outputs
        
        def _build_main_model(self, input_shape: Tuple[int, ...]) -> Any:
            inputs = layers.Input(shape=input_shape)
            outputs = self._transformer_encoder(inputs, self.n_main_balls)
            model = Model(inputs, outputs, name='main_transformer')
            model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            return model
        
        def _build_star_model(self, input_shape: Tuple[int, ...]) -> Any:
            inputs = layers.Input(shape=input_shape)
            outputs = self._transformer_encoder(inputs, self.n_stars)
            model = Model(inputs, outputs, name='star_transformer')
            model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            return model
        
        def prepare_sequences(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            df = df.sort_values('draw_date').reset_index(drop=True)
            n_draws = len(df)
            
            main_cols = [c for c in df.columns if c.startswith('b') and c[1:].isdigit()] or \
                        [c for c in df.columns if c.startswith('n') and c[1:].isdigit()]
            star_cols = ['s1', 's2']
            if not main_cols:
                main_cols = ['n1', 'n2', 'n3', 'n4', 'n5']
            
            main_one_hot = np.zeros((n_draws, self.n_main_balls))
            star_one_hot = np.zeros((n_draws, self.n_stars))
            
            for i, row in df.iterrows():
                for col in main_cols[:5]:
                    if col in row:
                        main_one_hot[i, int(row[col]) - 1] = 1  # type: ignore[index]
                for col in star_cols:
                    if col in row:
                        star_one_hot[i, int(row[col]) - 1] = 1  # type: ignore[index]
            
            X_main, y_main, X_star, y_star = [], [], [], []
            for i in range(self.sequence_length, n_draws):
                X_main.append(main_one_hot[i-self.sequence_length:i])
                X_star.append(star_one_hot[i-self.sequence_length:i])
                y_main.append(main_one_hot[i])
                y_star.append(star_one_hot[i])
            
            return (np.array(X_main), np.array(y_main), np.array(X_star), np.array(y_star))
        
        def train(self, df: pd.DataFrame, validation_split: float = 0.2, 
                  epochs: int = 100, batch_size: int = 32, verbose: int = 1) -> Dict[str, Any]:
            logger.info("Preparing sequence data for Transformer training...")
            X_main, y_main, X_star, y_star = self.prepare_sequences(df)
            
            self.main_model = self._build_main_model((self.sequence_length, self.n_main_balls))
            self.star_model = self._build_star_model((self.sequence_length, self.n_stars))
            
            callbacks = [EarlyStopping(patience=15, restore_best_weights=True),
                        ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6)]
            
            main_history = self.main_model.fit(X_main, y_main, validation_split=validation_split,
                                               epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=verbose)
            star_history = self.star_model.fit(X_star, y_star, validation_split=validation_split,
                                               epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=verbose)
            
            self.history = {'main': main_history.history, 'star': star_history.history}
            
            return {
                'main_loss': min(main_history.history['val_loss']),
                'star_loss': min(star_history.history['val_loss']),
                'main_epochs': len(main_history.history['loss']),
                'star_epochs': len(star_history.history['loss'])
            }
        
        def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
            X_main, _, X_star, _ = self.prepare_sequences(df)
            main_proba = self.main_model.predict(X_main[-1:], verbose=0)[0]
            star_proba = self.star_model.predict(X_star[-1:], verbose=0)[0]
            return main_proba, star_proba
        
        def save(self, path: Path | str) -> None:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            if self.main_model:
                self.main_model.save(path / 'main_transformer.keras')
            if self.star_model:
                self.star_model.save(path / 'star_transformer.keras')
            with open(path / 'config.json', 'w') as f:
                json.dump({'sequence_length': self.sequence_length, 'd_model': self.d_model,
                          'num_heads': self.num_heads, 'dff': self.dff, 'num_layers': self.num_layers}, f)
        
        def load(self, path: Path | str) -> None:
            path = Path(path)
            with open(path / 'config.json', 'r') as f:
                config = json.load(f)
            for key, value in config.items():
                setattr(self, key, value)
            self.main_model = keras.models.load_model(path / 'main_transformer.keras')
            self.star_model = keras.models.load_model(path / 'star_transformer.keras')


    class HybridDeepLearningPredictor:  # type: ignore[no-redef]
        """Hybrid model combining LSTM and Transformer predictions."""
        
        def __init__(self, sequence_length: int = 20, n_main_balls: int = 50, 
                     n_stars: int = 12, lstm_weight: float = 0.5, **kwargs: Any) -> None:
            self.sequence_length = sequence_length
            self.n_main_balls = n_main_balls
            self.n_stars = n_stars
            self.lstm_weight = lstm_weight
            
            self.lstm = LSTMPredictor(
                sequence_length=sequence_length, n_main_balls=n_main_balls, n_stars=n_stars,
                **{k: v for k, v in kwargs.items() if k in ['hidden_units', 'dropout_rate']}
            )
            
            self.transformer = TransformerPredictor(
                sequence_length=sequence_length, n_main_balls=n_main_balls, n_stars=n_stars,
                **{k: v for k, v in kwargs.items() if k in ['d_model', 'num_heads', 'dff', 'num_layers']}
            )
            
            self.history: Dict[str, Any] = {}
        
        def train(self, df: pd.DataFrame, **kwargs: Any) -> Dict[str, Any]:
            logger.info("Training LSTM component...")
            lstm_metrics = self.lstm.train(df, **kwargs)
            
            logger.info("Training Transformer component...")
            transformer_metrics = self.transformer.train(df, **kwargs)
            
            self.history = {'lstm': self.lstm.history, 'transformer': self.transformer.history}
            
            return {'lstm': lstm_metrics, 'transformer': transformer_metrics, 'combined': True}
        
        def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
            lstm_main, lstm_star = self.lstm.predict(df)
            trans_main, trans_star = self.transformer.predict(df)
            
            main_proba = self.lstm_weight * lstm_main + (1 - self.lstm_weight) * trans_main
            star_proba = self.lstm_weight * lstm_star + (1 - self.lstm_weight) * trans_star
            
            return main_proba, star_proba
        
        def save(self, path: Path | str) -> None:
            path = Path(path)
            self.lstm.save(path / 'lstm')
            self.transformer.save(path / 'transformer')
            with open(path / 'hybrid_config.json', 'w') as f:
                json.dump({'lstm_weight': self.lstm_weight}, f)
        
        def load(self, path: Path | str) -> None:
            path = Path(path)
            self.lstm.load(path / 'lstm')
            self.transformer.load(path / 'transformer')
            with open(path / 'hybrid_config.json', 'r') as f:
                config = json.load(f)
            self.lstm_weight = config['lstm_weight']


def train_deep_learning_models(df: pd.DataFrame, model_type: str = 'lstm', 
                                save_path: Optional[Path | str] = None, **kwargs: Any) -> Dict[str, Any]:
    """Convenience function to train deep learning models."""
    if not TF_AVAILABLE:
        return {'error': 'TensorFlow not available', 'success': False}
    
    save_path = Path(save_path) if save_path else Path('models/euromillions')
    
    if model_type == 'lstm':
        model = LSTMPredictor()
    elif model_type == 'transformer':
        model = TransformerPredictor()
    elif model_type == 'hybrid':
        model = HybridDeepLearningPredictor()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    metrics = model.train(df, **kwargs)
    model.save(save_path / f'deep_learning_{model_type}')
    
    return {'success': True, 'model_type': model_type, 'metrics': metrics}


if __name__ == "__main__":
    print(f"TensorFlow available: {TF_AVAILABLE}")
    print(f"PyTorch available: {TORCH_AVAILABLE}")
    
    if not TF_AVAILABLE:
        print("\nTensorFlow not installed. Install with: pip install tensorflow")
