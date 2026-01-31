"""
Train Deep Learning Models with Custom Epochs
==============================================

This script trains LSTM/Transformer models with configurable epochs.
200 epochs can help find subtle patterns but uses EarlyStopping to prevent overfitting.

Usage:
    python train_deep_learning.py --epochs 200
    python train_deep_learning.py --epochs 200 --model lstm
    python train_deep_learning.py --epochs 200 --model transformer
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

def main():
    parser = argparse.ArgumentParser(description="Train Deep Learning Models")
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs (default: 100)')
    parser.add_argument('--model', type=str, default='all', choices=['lstm', 'transformer', 'all'], 
                        help='Model type to train')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size (default: 32)')
    parser.add_argument('--sequence-length', type=int, default=20, help='Sequence length for LSTM (default: 20)')
    parser.add_argument('--patience', type=int, default=20, help='Early stopping patience (default: 20)')
    args = parser.parse_args()
    
    # Check TensorFlow availability
    try:
        from deep_learning_models import (
            is_deep_learning_available, 
            LSTMPredictor, 
            TransformerPredictor,
            TF_AVAILABLE
        )
    except ImportError as e:
        logger.error(f"Failed to import deep learning models: {e}")
        sys.exit(1)
    
    if not TF_AVAILABLE:
        logger.error("❌ TensorFlow is not installed!")
        logger.info("Install with: pip install tensorflow")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🧠 Deep Learning Training for EuroMillions")
    logger.info("=" * 60)
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Sequence length: {args.sequence_length}")
    logger.info(f"  Early stopping patience: {args.patience}")
    logger.info("=" * 60)
    
    # Load data
    from repository import get_repository
    repo = get_repository()
    df = repo.all_draws_df()
    
    if df.empty:
        logger.error("❌ No draws found in database!")
        sys.exit(1)
    
    logger.info(f"📊 Loaded {len(df)} draws from database")
    
    # Ensure we have enough data
    min_required = args.sequence_length + 50
    if len(df) < min_required:
        logger.error(f"❌ Need at least {min_required} draws, got {len(df)}")
        sys.exit(1)
    
    # Create models directory
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Train LSTM
    if args.model in ['lstm', 'all']:
        logger.info("\n" + "=" * 60)
        logger.info("🔄 Training LSTM Model...")
        logger.info("=" * 60)
        
        lstm = LSTMPredictor(
            sequence_length=args.sequence_length,
            hidden_units=128,
            dropout_rate=0.3
        )
        
        # Custom training with more epochs
        import tensorflow as tf
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, Callback
        
        # Custom progress callback for console output
        class ConsoleProgressCallback(Callback):
            def __init__(self, phase_name: str, max_epochs: int):
                super().__init__()
                self.phase_name = phase_name
                self.max_epochs = max_epochs
                self.best_val_loss = float('inf')
                self.start_time = None
                
            def on_train_begin(self, logs=None):
                import time
                self.start_time = time.time()
                logger.info(f"  ⏳ {self.phase_name}: Starting training...")
                
            def on_epoch_end(self, epoch, logs=None):
                import time
                logs = logs or {}
                val_loss = logs.get('val_loss', 0)
                loss = logs.get('loss', 0)
                improved = ""
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    improved = " ⭐ BEST"
                    
                # Progress bar
                progress = (epoch + 1) / self.max_epochs
                bar_length = 30
                filled = int(bar_length * progress)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                elapsed = time.time() - self.start_time
                eta = (elapsed / (epoch + 1)) * (self.max_epochs - epoch - 1)
                
                logger.info(f"  [{bar}] {epoch+1}/{self.max_epochs} | loss: {loss:.4f} | val_loss: {val_loss:.4f}{improved} | ETA: {eta:.0f}s")
                
            def on_train_end(self, logs=None):
                import time
                elapsed = time.time() - self.start_time
                logger.info(f"  ✅ {self.phase_name}: Completed in {elapsed:.1f}s | Best val_loss: {self.best_val_loss:.4f}")
        
        # Prepare data
        X_main, y_main, X_star, y_star = lstm.prepare_sequences(df)
        logger.info(f"  Data shapes: X_main={X_main.shape}, X_star={X_star.shape}")
        
        # Build models
        lstm.main_model = lstm._build_main_model((args.sequence_length, 50))
        lstm.star_model = lstm._build_star_model((args.sequence_length, 12))
        
        # Custom callbacks with more patience for 200 epochs
        def get_callbacks(phase_name: str):
            return [
                EarlyStopping(
                    patience=args.patience, 
                    restore_best_weights=True, 
                    monitor='val_loss',
                    verbose=0
                ),
                ReduceLROnPlateau(
                    factor=0.5, 
                    patience=args.patience // 2, 
                    min_lr=1e-7,
                    verbose=0
                ),
                ModelCheckpoint(
                    str(models_dir / f"lstm_{phase_name.lower()}_best.keras"),
                    save_best_only=True,
                    monitor='val_loss',
                    verbose=0
                ),
                ConsoleProgressCallback(phase_name, args.epochs)
            ]
        
        logger.info(f"\n  📊 Training main balls for up to {args.epochs} epochs...")
        main_history = lstm.main_model.fit(
            X_main, y_main,
            validation_split=0.2,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=get_callbacks("Main Balls"),
            verbose=0
        )
        
        logger.info(f"\n  ⭐ Training stars for up to {args.epochs} epochs...")
        star_history = lstm.star_model.fit(
            X_star, y_star,
            validation_split=0.2,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=get_callbacks("Stars"),
            verbose=0
        )
        
        # Save models
        lstm.save(models_dir / "lstm_predictor")
        
        results['lstm'] = {
            'main_epochs_trained': len(main_history.history['loss']),
            'star_epochs_trained': len(star_history.history['loss']),
            'main_best_val_loss': min(main_history.history['val_loss']),
            'star_best_val_loss': min(star_history.history['val_loss']),
        }
        
        logger.info(f"\n✅ LSTM Training Complete:")
        logger.info(f"   Main balls: {results['lstm']['main_epochs_trained']} epochs (val_loss: {results['lstm']['main_best_val_loss']:.4f})")
        logger.info(f"   Stars: {results['lstm']['star_epochs_trained']} epochs (val_loss: {results['lstm']['star_best_val_loss']:.4f})")
    
    # Train Transformer
    if args.model in ['transformer', 'all']:
        logger.info("\n" + "=" * 60)
        logger.info("🔄 Training Transformer Model...")
        logger.info("=" * 60)
        
        transformer = TransformerPredictor(
            sequence_length=args.sequence_length,
            num_heads=4,
            dff=128,
            dropout_rate=0.2
        )
        
        # Prepare data and build models for manual training with progress
        X_main, y_main, X_star, y_star = transformer.prepare_sequences(df)
        logger.info(f"  Data shapes: X_main={X_main.shape}, X_star={X_star.shape}")
        
        transformer.main_model = transformer._build_main_model((args.sequence_length, transformer.n_main_balls))
        transformer.star_model = transformer._build_star_model((args.sequence_length, transformer.n_stars))
        
        # Import callbacks (reuse ConsoleProgressCallback if not in scope)
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, Callback
        
        # Define ConsoleProgressCallback if not already defined
        if 'ConsoleProgressCallback' not in dir():
            class ConsoleProgressCallback(Callback):
                def __init__(self, phase_name: str, max_epochs: int):
                    super().__init__()
                    self.phase_name = phase_name
                    self.max_epochs = max_epochs
                    self.best_val_loss = float('inf')
                    self.start_time = None
                    
                def on_train_begin(self, logs=None):
                    import time
                    self.start_time = time.time()
                    logger.info(f"  ⏳ {self.phase_name}: Starting training...")
                    
                def on_epoch_end(self, epoch, logs=None):
                    import time
                    logs = logs or {}
                    val_loss = logs.get('val_loss', 0)
                    loss = logs.get('loss', 0)
                    improved = ""
                    if val_loss < self.best_val_loss:
                        self.best_val_loss = val_loss
                        improved = " ⭐ BEST"
                        
                    progress = (epoch + 1) / self.max_epochs
                    bar_length = 30
                    filled = int(bar_length * progress)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    elapsed = time.time() - self.start_time
                    eta = (elapsed / (epoch + 1)) * (self.max_epochs - epoch - 1)
                    
                    logger.info(f"  [{bar}] {epoch+1}/{self.max_epochs} | loss: {loss:.4f} | val_loss: {val_loss:.4f}{improved} | ETA: {eta:.0f}s")
                    
                def on_train_end(self, logs=None):
                    import time
                    elapsed = time.time() - self.start_time
                    logger.info(f"  ✅ {self.phase_name}: Completed in {elapsed:.1f}s | Best val_loss: {self.best_val_loss:.4f}")
        
        def get_transformer_callbacks(phase_name: str):
            return [
                EarlyStopping(patience=args.patience, restore_best_weights=True, monitor='val_loss', verbose=0),
                ReduceLROnPlateau(factor=0.5, patience=args.patience // 2, min_lr=1e-7, verbose=0),
                ConsoleProgressCallback(phase_name, args.epochs)
            ]
        
        logger.info(f"\n  📊 Training main balls for up to {args.epochs} epochs...")
        main_history = transformer.main_model.fit(
            X_main, y_main,
            validation_split=0.2,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=get_transformer_callbacks("Transformer Main"),
            verbose=0
        )
        
        logger.info(f"\n  ⭐ Training stars for up to {args.epochs} epochs...")
        star_history = transformer.star_model.fit(
            X_star, y_star,
            validation_split=0.2,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=get_transformer_callbacks("Transformer Stars"),
            verbose=0
        )
        
        # Save model
        transformer.save(models_dir / "transformer_predictor")
        
        results['transformer'] = {
            'main_epochs': len(main_history.history['loss']),
            'star_epochs': len(star_history.history['loss']),
            'main_loss': min(main_history.history['val_loss']),
            'star_loss': min(star_history.history['val_loss'])
        }
        logger.info(f"\n✅ Transformer Training Complete:")
        logger.info(f"   Main balls: {results['transformer']['main_epochs']} epochs (val_loss: {results['transformer']['main_loss']:.4f})")
        logger.info(f"   Stars: {results['transformer']['star_epochs']} epochs (val_loss: {results['transformer']['star_loss']:.4f})")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TRAINING SUMMARY")
    logger.info("=" * 60)
    
    for model_name, result in results.items():
        logger.info(f"\n{model_name.upper()}:")
        for key, value in result.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.4f}")
            else:
                logger.info(f"  {key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Models saved to data/models/")
    logger.info("=" * 60)
    
    # Show early stopping message
    if args.epochs == 200:
        logger.info("\n💡 Note: With 200 epochs and EarlyStopping, training may stop earlier")
        logger.info("   if validation loss stops improving. This prevents overfitting!")


if __name__ == "__main__":
    main()
