"""
Streamlit UI Adapters
====================

Thin adapter layer between Streamlit UI and the core ML/data pipeline.
Provides simple, UI-friendly interfaces that handle errors gracefully
and return consistent data structures for the web interface.
"""

import io
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger

def convert_numpy_types(obj):
    """Recursively convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

from config import get_settings
from repository import get_repository, init_database
from hybrid_scraper import get_best_available_draws, scrape_latest_hybrid
from train_models import EuromillionsTrainer, train_latest, get_model_info
# Optional imports for advanced features
try:
    from ensemble_models import EnsembleTrainer, predict_with_ensemble
    ENSEMBLE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Ensemble models not available: {e}")
    ENSEMBLE_AVAILABLE = False

try:
    from hybrid_strategy import HybridPredictionStrategy
    HYBRID_STRATEGY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Hybrid strategy not available: {e}")
    HYBRID_STRATEGY_AVAILABLE = False


class StreamlitAdapters:
    """
    Streamlit UI adapter class providing simple interfaces for web UI.
    All methods return consistent data structures and handle errors gracefully.
    """
    
    def __init__(self):
        """Initialize adapters with database and settings."""
        self.settings = get_settings()
        init_database()
        self.repo = get_repository()
        self.trainer = EuromillionsTrainer()
    
    def init_full_history(self) -> Dict[str, Any]:
        """
        Initialize full historical data by crawling archive pages.
        
        Returns:
            dict: Summary with inserted, updated, skipped counts and date range
                 {inserted, updated, skipped, first_date, last_date, success, message}
        """
        logger.info("Starting full history initialization")
        
        try:
            # Get initial count
            initial_df = self.repo.all_draws_df()
            initial_count = len(initial_df)
            
            # Crawl archive pages (this may take a while)
            logger.info("Crawling historical archive pages...")
            all_draws = []
            
            # Try to scrape a reasonable amount of history
            # We'll loop through pages until we get enough data or hit a limit
            max_pages = 50  # Reasonable limit to prevent infinite loops
            draws_per_page = 20  # Typical number of draws per page
            
            for page in range(1, max_pages + 1):
                try:
                    logger.info(f"Crawling page {page}/{max_pages}")
                    page_draws = scrape_latest_hybrid(limit=draws_per_page, offset=(page-1)*draws_per_page)
                    
                    if not page_draws:
                        logger.info(f"No more draws found at page {page}, stopping")
                        break
                    
                    all_draws.extend(page_draws)
                    
                    # Stop if we have a good amount of data
                    if len(all_draws) >= 1000:
                        logger.info(f"Collected {len(all_draws)} draws, sufficient for analysis")
                        break
                        
                except Exception as e:
                    logger.warning(f"Error on page {page}: {e}")
                    break
            
            if not all_draws:
                return {
                    "success": False,
                    "message": "No historical data could be retrieved",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0,
                    "first_date": None,
                    "last_date": None
                }
            
            # Upsert all draws
            logger.info(f"Upserting {len(all_draws)} historical draws")
            result = self.repo.upsert_draws(all_draws)
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            
            # Get final statistics
            final_df = self.repo.all_draws_df()
            final_count = len(final_df)
            skipped = len(all_draws) - inserted - updated
            
            first_date = final_df['draw_date'].min() if not final_df.empty else None
            last_date = final_df['draw_date'].max() if not final_df.empty else None
            
            result = {
                "success": True,
                "message": f"Successfully initialized with {final_count} total draws",
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "first_date": str(first_date) if first_date else None,
                "last_date": str(last_date) if last_date else None,
                "total_draws": final_count
            }
            
            logger.info(f"Full history initialization complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Full history initialization failed: {e}")
            return {
                "success": False,
                "message": f"Initialization failed: {str(e)}",
                "inserted": 0,
                "updated": 0,
                "skipped": 0,
                "first_date": None,
                "last_date": None
            }
    
    def update_incremental(self) -> Dict[str, Any]:
        """
        Update with recent draws by scraping latest pages.
        
        Returns:
            dict: Summary with inserted, updated, skipped counts
        """
        logger.info("Starting incremental update")
        
        try:
            # Get current latest date
            current_df = self.repo.all_draws_df()
            
            # Scrape recent draws (last few pages)
            recent_draws = get_best_available_draws(limit=100)  # Get recent 100 draws
            
            if not recent_draws:
                return {
                    "success": True,
                    "message": "No new draws found",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0
                }
            
            # Upsert recent draws
            result = self.repo.upsert_draws(recent_draws)
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            skipped = len(recent_draws) - inserted - updated
            
            result = {
                "success": True,
                "message": f"Update complete: {inserted} new, {updated} updated",
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped
            }
            
            logger.info(f"Incremental update complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Incremental update failed: {e}")
            return {
                "success": False,
                "message": f"Update failed: {str(e)}",
                "inserted": 0,
                "updated": 0,
                "skipped": 0
            }
    
    def train_from_scratch(self) -> Dict[str, Any]:
        """
        Train models from scratch using current data.
        
        Returns:
            dict: Training metrics and status
        """
        logger.info("Starting training from scratch")
        
        try:
            # Check if we have enough data
            df = self.repo.all_draws_df()
            
            if df.empty:
                return {
                    "success": False,
                    "message": "No training data available. Please fetch historical data first.",
                    "main_logloss": None,
                    "star_logloss": None
                }
            
            if len(df) < 100:
                return {
                    "success": False,
                    "message": f"Insufficient training data: {len(df)} draws (minimum: 100)",
                    "main_logloss": None,
                    "star_logloss": None
                }
            
            # Train models
            result = train_latest(min_rows=min(len(df), 100))
            
            if result and result.get("success", False):
                metrics = result.get("performance", {})
                
                return {
                    "success": True,
                    "message": f"Training completed successfully with {len(df)} draws",
                    "main_logloss": metrics.get("main_logloss"),
                    "star_logloss": metrics.get("star_logloss"),
                    "cv_main_mean": metrics.get("cv_details", {}).get("main_mean"),
                    "cv_star_mean": metrics.get("cv_details", {}).get("star_mean"),
                    "training_data_size": len(df)
                }
            else:
                return {
                    "success": False,
                    "message": "Training failed. Check logs for details.",
                    "main_logloss": None,
                    "star_logloss": None
                }
                
        except Exception as e:
            logger.error(f"Training from scratch failed: {e}")
            return {
                "success": False,
                "message": f"Training failed: {str(e)}",
                "main_logloss": None,
                "star_logloss": None
            }
    
    def reload_models(self) -> Dict[str, Any]:
        """
        Reload models from disk, forcing refresh.
        
        Returns:
            dict: Model loading status and info
        """
        logger.info("Reloading models")
        
        try:
            # Force reload models
            self.trainer.load_models(force=True)
            
            # Get model info
            info = get_model_info()
            
            if info.get("models_available", False):
                return {
                    "success": True,
                    "message": "Models reloaded successfully",
                    "trained_at": info.get("trained_at"),
                    "main_logloss": info.get("performance", {}).get("main_logloss"),
                    "star_logloss": info.get("performance", {}).get("star_logloss")
                }
            else:
                return {
                    "success": False,
                    "message": "No trained models found to reload",
                    "trained_at": None,
                    "main_logloss": None,
                    "star_logloss": None
                }
                
        except Exception as e:
            logger.error(f"Model reload failed: {e}")
            return {
                "success": False,
                "message": f"Model reload failed: {str(e)}",
                "trained_at": None,
                "main_logloss": None,
                "star_logloss": None
            }
    
    def get_scores(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get ball and star probability scores as sorted DataFrames.
        
        Returns:
            tuple: (balls_df, stars_df) sorted by probability descending
        """
        try:
            # Ensure models are loaded
            self.trainer.load_models()
            
            # Get scores
            ball_scores = self.trainer.score_balls()
            star_scores = self.trainer.score_stars()
            
            # Convert to DataFrames
            balls_df = pd.DataFrame(ball_scores, columns=['ball', 'probability'])
            balls_df['ball'] = balls_df['ball'].astype(int)  # Ensure Python int
            balls_df['probability'] = balls_df['probability'].astype(float)  # Ensure Python float
            balls_df = balls_df.sort_values('probability', ascending=False).reset_index(drop=True)
            balls_df['rank'] = range(1, len(balls_df) + 1)
            balls_df['percentage'] = (balls_df['probability'] * 100).round(2)
            
            stars_df = pd.DataFrame(star_scores, columns=['star', 'probability'])
            stars_df['star'] = stars_df['star'].astype(int)  # Ensure Python int
            stars_df['probability'] = stars_df['probability'].astype(float)  # Ensure Python float
            stars_df = stars_df.sort_values('probability', ascending=False).reset_index(drop=True)
            stars_df['rank'] = range(1, len(stars_df) + 1)
            stars_df['percentage'] = (stars_df['probability'] * 100).round(2)
            
            return balls_df, stars_df
            
        except Exception as e:
            logger.error(f"Failed to get scores: {e}")
            # Return empty DataFrames with correct structure
            empty_balls = pd.DataFrame(columns=['ball', 'probability', 'rank', 'percentage'])
            empty_stars = pd.DataFrame(columns=['star', 'probability', 'rank', 'percentage'])
            return empty_balls, empty_stars
    
    def suggest_tickets_ui(self, n: int = 10, method: str = "hybrid", seed: int = 42, 
                          use_ensemble: bool = True, hybrid_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Generate enhanced lottery ticket suggestions using multiple strategies.
        
        Args:
            n: Number of tickets to generate
            method: Generation method ("topk", "random", "hybrid", "ensemble", "advanced_hybrid")
            seed: Random seed for reproducibility
            use_ensemble: Whether to use ensemble models
            hybrid_weights: Custom weights for hybrid strategy
            
        Returns:
            list: List of enhanced ticket dictionaries with confidence scores
        """
        try:
            logger.info(f"Generating {n} tickets with method '{method}' (ensemble: {use_ensemble})")
            
            tickets = []
            
            if method == "ensemble" and use_ensemble and ENSEMBLE_AVAILABLE:
                # Use pure ensemble prediction
                tickets = self._generate_ensemble_tickets(n, seed)
                
            elif method == "advanced_hybrid" and HYBRID_STRATEGY_AVAILABLE:
                # Use advanced hybrid strategy
                tickets = self._generate_advanced_hybrid_tickets(n, seed, hybrid_weights)
                
            else:
                # Enhanced version of existing methods
                tickets = self._generate_enhanced_tickets(n, method, seed, use_ensemble)
            
            # Add metadata and confidence scores
            for ticket in tickets:
                # Convert numpy types to native Python types for JSON serialization
                if "balls" in ticket:
                    ticket["balls"] = [int(x) for x in ticket["balls"]]
                if "stars" in ticket:
                    ticket["stars"] = [int(x) for x in ticket["stars"]]
                
                # Convert any numpy floats to Python floats
                if "combined_score" in ticket:
                    ticket["combined_score"] = float(ticket["combined_score"])
                if "base_confidence" in ticket:
                    ticket["base_confidence"] = float(ticket["base_confidence"])
                
                ticket["generated_at"] = datetime.now().isoformat()
                ticket["model_version"] = "v2_enhanced"
                
                # Calculate enhanced confidence score
                confidence = self._calculate_enhanced_confidence(ticket)
                ticket["confidence"] = float(confidence)  # Ensure it's a Python float
                ticket["confidence_level"] = self._get_confidence_level(confidence)
            
            # Sort by confidence (highest first)
            tickets.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Convert all numpy types to Python types for JSON serialization
            tickets = [convert_numpy_types(ticket) for ticket in tickets]
            
            logger.info(f"Generated {len(tickets)} enhanced tickets")
            return tickets
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced ticket suggestions: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Fallback to basic method
            fallback_tickets = self._generate_fallback_tickets(n, method, seed)
            if not fallback_tickets:
                logger.error("Fallback also failed, generating minimal tickets")
                return self._generate_minimal_tickets(n, seed)
            return fallback_tickets
    
    def _generate_ensemble_tickets(self, n: int, seed: int) -> List[Dict[str, Any]]:
        """Generate tickets using ensemble models."""
        
        try:
            if not ENSEMBLE_AVAILABLE:
                logger.warning("Ensemble models not available, using fallback")
                return []
                
            ensemble_trainer = EnsembleTrainer()
            
            if not ensemble_trainer.models_exist():
                logger.warning("Ensemble models not found, using fallback")
                return []
            
            tickets = []
            np.random.seed(seed)
            
            # Get latest data for predictions
            repo = get_repository()
            df = repo.all_draws_df()
            
            # Build features for prediction (use last row as base)
            from build_datasets import build_enhanced_datasets
            X_main, _, X_star, _, _ = build_enhanced_datasets(df, window_size=100)
            
            # Use the most recent features
            latest_main = X_main[-1:] if len(X_main) > 0 else np.zeros((1, 200))
            latest_star = X_star[-1:] if len(X_star) > 0 else np.zeros((1, 48))
            
            for i in range(n):
                # Get ensemble predictions
                main_proba, star_proba = ensemble_trainer.predict_with_ensemble(latest_main, latest_star)
                
                # Extract probabilities for positive class (shape is (n_outputs, n_samples, n_classes))
                # We want the probability of class 1 (ball/star appears) for each position
                if main_proba.ndim == 3:
                    # Shape: (50, 1, 2) -> extract [:, 0, 1] -> (50,)
                    main_proba = main_proba[:, 0, 1]
                elif main_proba.ndim == 2:
                    # Shape: (50, 2) -> extract [:, 1] -> (50,)
                    main_proba = main_proba[:, 1]
                    
                if star_proba.ndim == 3:
                    # Shape: (12, 1, 2) -> extract [:, 0, 1] -> (12,)
                    star_proba = star_proba[:, 0, 1]
                elif star_proba.ndim == 2:
                    # Shape: (12, 2) -> extract [:, 1] -> (12,)
                    star_proba = star_proba[:, 1]
                
                # Add some randomness for variety between tickets
                if i > 0:
                    noise_factor = 0.05 * i  # Small noise for diversity
                    main_proba = main_proba + np.random.normal(0, noise_factor, len(main_proba))
                    star_proba = star_proba + np.random.normal(0, noise_factor, len(star_proba))
                    
                    # Ensure probabilities stay positive
                    main_proba = np.clip(main_proba, 0, 1)
                    star_proba = np.clip(star_proba, 0, 1)
                
                # Select top candidates with some randomness
                top_balls_idx = np.argsort(main_proba)[-10:]  # Top 10 candidates
                top_stars_idx = np.argsort(star_proba)[-6:]   # Top 6 candidates
                
                # Convert to 1-based numbering
                top_balls = top_balls_idx + 1
                top_stars = top_stars_idx + 1
                
                # Random selection from top candidates
                selected_balls = sorted(np.random.choice(top_balls, 5, replace=False))
                selected_stars = sorted(np.random.choice(top_stars, 2, replace=False))
                
                # Calculate confidence based on selected numbers' probabilities
                balls_confidence = np.mean([main_proba[b-1] for b in selected_balls])
                stars_confidence = np.mean([star_proba[s-1] for s in selected_stars])
                combined_confidence = balls_confidence * 0.7 + stars_confidence * 0.3
                
                ticket = {
                    "ticket_id": i + 1,
                    "balls": selected_balls,
                    "stars": selected_stars,
                    "balls_str": " - ".join(f"{b:02d}" for b in selected_balls),
                    "stars_str": " - ".join(f"{s:02d}" for s in selected_stars),
                    "method": "ensemble",
                    "ensemble_type": "multi_algorithm",
                    "base_confidence": float(combined_confidence)
                }
                
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            logger.error(f"Ensemble ticket generation failed: {e}")
            return []
    
    def _generate_advanced_hybrid_tickets(self, n: int, seed: int, 
                                        custom_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Generate tickets using advanced hybrid strategy."""
        
        try:
            if not HYBRID_STRATEGY_AVAILABLE:
                logger.error("Hybrid strategy not available")
                return []
                
            # Initialize hybrid strategy
            hybrid_strategy = HybridPredictionStrategy()
            
            # Apply custom weights if provided
            if custom_weights:
                if "ml_weight" in custom_weights:
                    hybrid_strategy.ml_weight = custom_weights["ml_weight"]
                if "freq_weight" in custom_weights:
                    hybrid_strategy.freq_weight = custom_weights["freq_weight"]
                if "pattern_weight" in custom_weights:
                    hybrid_strategy.pattern_weight = custom_weights["pattern_weight"]
                if "gap_weight" in custom_weights:
                    hybrid_strategy.gap_weight = custom_weights["gap_weight"]
            
            # Get ML predictions
            try:
                if ENSEMBLE_AVAILABLE:
                    ensemble_trainer = EnsembleTrainer()
                    ml_predictions = ensemble_trainer.predict_with_ensemble(return_probabilities=True)
                else:
                    raise ImportError("Ensemble not available")
            except:
                # Fallback to regular trainer
                ml_predictions = self.trainer.predict_next_draw(return_probabilities=True)
            
            # Get historical data
            df = self.repo.all_draws_df()
            
            # Generate hybrid predictions
            combinations = hybrid_strategy.predict_hybrid(df, ml_predictions)
            
            # Convert to ticket format
            tickets = []
            for i, combo in enumerate(combinations[:n], 1):
                ticket = {
                    "ticket_id": i,
                    "balls": combo["balls"],
                    "stars": combo["stars"],
                    "balls_str": " - ".join(f"{b:02d}" for b in combo["balls"]),
                    "stars_str": " - ".join(f"{s:02d}" for s in combo["stars"]),
                    "method": "advanced_hybrid",
                    "strategy": combo.get("method", "unknown"),
                    "base_confidence": combo.get("confidence", 50.0) / 100.0
                }
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            logger.error(f"Advanced hybrid ticket generation failed: {e}")
            return []
    
    def _generate_enhanced_tickets(self, n: int, method: str, seed: int, use_ensemble: bool) -> List[Dict[str, Any]]:
        """Generate enhanced tickets using existing methods with improvements."""
        
        try:
            if use_ensemble and ENSEMBLE_AVAILABLE:
                # Try to use ensemble for scoring, fall back to regular trainer
                try:
                    ensemble_trainer = EnsembleTrainer()
                    ball_scores = ensemble_trainer.score_balls_ensemble()
                    star_scores = ensemble_trainer.score_stars_ensemble()
                    model_type = "ensemble"
                except:
                    logger.warning("Ensemble scoring failed, using regular trainer")
                    self.trainer.load_models()
                    ball_scores = self.trainer.score_balls()
                    star_scores = self.trainer.score_stars()
                    model_type = "lightgbm"
            else:
                self.trainer.load_models()
                ball_scores = self.trainer.score_balls()
                star_scores = self.trainer.score_stars()
                model_type = "lightgbm"
            
            # Generate combinations using enhanced scoring
            combinations = self._generate_combinations_from_scores(
                ball_scores, star_scores, n, method, seed
            )
            
            # Convert to ticket format
            tickets = []
            for i, combo in enumerate(combinations, 1):
                ticket = {
                    "ticket_id": i,
                    "balls": combo["balls"],
                    "stars": combo["stars"],
                    "balls_str": " - ".join(f"{b:02d}" for b in combo["balls"]),
                    "stars_str": " - ".join(f"{s:02d}" for s in combo["stars"]),
                    "method": f"enhanced_{method}",
                    "model_type": model_type,
                    "base_confidence": combo.get("score", 0.5)
                }
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            logger.error(f"Enhanced ticket generation failed: {e}")
            return []
    
    def _generate_combinations_from_scores(self, ball_scores: List[Tuple[int, float]], 
                                         star_scores: List[Tuple[int, float]], 
                                         n: int, method: str, seed: int) -> List[Dict[str, Any]]:
        """Generate combinations from ball and star scores."""
        
        np.random.seed(seed)
        
        combinations = []
        
        # Sort by score
        ball_scores.sort(key=lambda x: x[1], reverse=True)
        star_scores.sort(key=lambda x: x[1], reverse=True)
        
        for i in range(n):
            if method == "topk":
                # Select top balls with slight variation
                top_balls = [ball for ball, _ in ball_scores[:8 + i]]
                selected_balls = sorted(np.random.choice(top_balls, 5, replace=False))
                
                top_stars = [star for star, _ in star_scores[:3 + i]]
                selected_stars = sorted(np.random.choice(top_stars, 2, replace=False))
                
            elif method == "random":
                # Weighted random selection
                ball_weights = np.array([score for _, score in ball_scores])
                ball_weights = ball_weights / np.sum(ball_weights)
                
                star_weights = np.array([score for _, score in star_scores])
                star_weights = star_weights / np.sum(star_weights)
                
                ball_numbers = [ball for ball, _ in ball_scores]
                star_numbers = [star for star, _ in star_scores]
                
                selected_balls = sorted(np.random.choice(ball_numbers, 5, replace=False, p=ball_weights))
                selected_stars = sorted(np.random.choice(star_numbers, 2, replace=False, p=star_weights))
                
            else:  # hybrid
                # Mix of top and random
                if i < n // 2:
                    # First half: more top-heavy
                    top_balls = [ball for ball, _ in ball_scores[:12]]
                    selected_balls = sorted(np.random.choice(top_balls, 5, replace=False))
                    
                    top_stars = [star for star, _ in star_scores[:4]]
                    selected_stars = sorted(np.random.choice(top_stars, 2, replace=False))
                else:
                    # Second half: more random
                    all_balls = [ball for ball, _ in ball_scores]
                    ball_weights = np.array([score for _, score in ball_scores])
                    ball_weights = ball_weights / np.sum(ball_weights)
                    
                    selected_balls = sorted(np.random.choice(all_balls, 5, replace=False, p=ball_weights))
                    
                    all_stars = [star for star, _ in star_scores]
                    star_weights = np.array([score for _, score in star_scores])
                    star_weights = star_weights / np.sum(star_weights)
                    
                    selected_stars = sorted(np.random.choice(all_stars, 2, replace=False, p=star_weights))
            
            # Calculate combination score
            ball_score = np.mean([score for ball, score in ball_scores if ball in selected_balls])
            star_score = np.mean([score for star, score in star_scores if star in selected_stars])
            combined_score = ball_score * 0.7 + star_score * 0.3
            
            combination = {
                "balls": selected_balls,
                "stars": selected_stars,
                "score": combined_score
            }
            
            combinations.append(combination)
        
        return combinations
    
    def _calculate_enhanced_confidence(self, ticket: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score for a ticket."""
        
        base_confidence = ticket.get("base_confidence", 0.5)
        
        # Add factors based on method
        method_bonus = {
            "ensemble": 0.15,
            "advanced_hybrid": 0.12,
            "enhanced_hybrid": 0.08,
            "enhanced_topk": 0.05,
            "enhanced_random": 0.02
        }
        
        bonus = method_bonus.get(ticket.get("method", ""), 0)
        
        # Calculate final confidence (0-100)
        final_confidence = min(95, (base_confidence + bonus) * 100)
        
        return round(final_confidence, 1)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description."""
        
        if confidence >= 80:
            return "Très Élevée"
        elif confidence >= 65:
            return "Élevée"
        elif confidence >= 50:
            return "Moyenne"
        elif confidence >= 35:
            return "Faible"
        else:
            return "Très Faible"
    
    def _generate_fallback_tickets(self, n: int, method: str, seed: int) -> List[Dict[str, Any]]:
        """Generate basic fallback tickets if enhanced methods fail."""
        
        try:
            # Use basic trainer method
            self.trainer.load_models()
            combinations = self.trainer.suggest_combinations(k=n, method=method, seed=seed)
            
            tickets = []
            for i, combo in enumerate(combinations, 1):
                ticket = {
                    "ticket_id": i,
                    "balls": [int(x) for x in combo["balls"]],
                    "stars": [int(x) for x in combo["stars"]],
                    "balls_str": " - ".join(f"{int(b):02d}" for b in combo["balls"]),
                    "stars_str": " - ".join(f"{int(s):02d}" for s in combo["stars"]),
                    "method": f"fallback_{method}",
                    "confidence": 45.0,
                    "confidence_level": "Moyenne",
                    "generated_at": datetime.now().isoformat()
                }
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            logger.error(f"Fallback ticket generation failed: {e}")
            return []
    
    def _generate_minimal_tickets(self, n: int, seed: int) -> List[Dict[str, Any]]:
        """Generate minimal random tickets as last resort."""
        
        try:
            np.random.seed(seed)
            tickets = []
            
            for i in range(n):
                # Generate completely random valid tickets
                balls = sorted(np.random.choice(range(1, 51), 5, replace=False))
                stars = sorted(np.random.choice(range(1, 13), 2, replace=False))
                
                ticket = {
                    "ticket_id": i + 1,
                    "balls": balls.tolist(),
                    "stars": stars.tolist(),
                    "balls_str": " - ".join(f"{b:02d}" for b in balls),
                    "stars_str": " - ".join(f"{s:02d}" for s in stars),
                    "method": "minimal_random",
                    "confidence": 20.0,
                    "confidence_level": "Faible",
                    "generated_at": datetime.now().isoformat()
                }
                tickets.append(ticket)
            
            logger.info(f"Generated {len(tickets)} minimal random tickets")
            return tickets
            
        except Exception as e:
            logger.error(f"Even minimal ticket generation failed: {e}")
            return []
    
    def fetch_last_draws(self, limit: int = 20) -> pd.DataFrame:
        """
        Fetch the most recent draws from database.
        
        Args:
            limit: Number of recent draws to fetch
            
        Returns:
            pd.DataFrame: Recent draws sorted by date descending
        """
        try:
            df = self.repo.all_draws_df()
            
            if df.empty:
                return pd.DataFrame(columns=['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2'])
            
            # Sort by date and take most recent
            recent_df = df.sort_values('draw_date', ascending=False).head(limit).copy()
            
            # Format for display
            recent_df['draw_date'] = pd.to_datetime(recent_df['draw_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            recent_df['balls'] = recent_df.apply(
                lambda row: f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}", 
                axis=1
            )
            recent_df['stars'] = recent_df.apply(
                lambda row: f"{row['s1']:02d}-{row['s2']:02d}", 
                axis=1
            )
            
            # Select display columns
            display_df = recent_df[['draw_date', 'balls', 'stars', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']].copy()
            
            return display_df
            
        except Exception as e:
            logger.error(f"Failed to fetch recent draws: {e}")
            return pd.DataFrame(columns=['draw_date', 'balls', 'stars'])
    
    def export_all_draws_csv(self) -> Tuple[str, bytes]:
        """
        Export all draws to CSV format for download.
        
        Returns:
            tuple: (filename, csv_bytes) for Streamlit download
        """
        try:
            df = self.repo.all_draws_df()
            
            if df.empty:
                # Return empty CSV
                empty_csv = "draw_date,n1,n2,n3,n4,n5,s1,s2\n"
                return "euromillions_draws_empty.csv", empty_csv.encode()
            
            # Sort by date
            df_sorted = df.sort_values('draw_date', ascending=False).copy()
            
            # Format date column
            df_sorted['draw_date'] = pd.to_datetime(df_sorted['draw_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            df_sorted.to_csv(csv_buffer, index=False)
            csv_bytes = csv_buffer.getvalue().encode()
            
            # Generate filename with date range
            first_date = df_sorted['draw_date'].iloc[-1]  # Oldest (last in desc order)
            last_date = df_sorted['draw_date'].iloc[0]    # Newest (first in desc order)
            filename = f"euromillions_draws_{first_date}_to_{last_date}.csv"
            
            return filename, csv_bytes
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            error_csv = f"# Export failed: {str(e)}\n"
            return "euromillions_export_error.csv", error_csv.encode()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for dashboard.
        
        Returns:
            dict: System status including data, models, and recommendations
        """
        try:
            # Database status
            df = self.repo.all_draws_df()
            data_status = {
                "available": not df.empty,
                "count": len(df),
                "first_date": df['draw_date'].min().strftime('%Y-%m-%d') if not df.empty else None,
                "last_date": df['draw_date'].max().strftime('%Y-%m-%d') if not df.empty else None
            }
            
            # Model status
            info = get_model_info()
            model_status = {
                "available": info.get("models_available", False),
                "trained_at": info.get("trained_at"),
                "main_logloss": info.get("performance", {}).get("main_logloss"),
                "star_logloss": info.get("performance", {}).get("star_logloss")
            }
            
            # Recommendations
            recommendations = []
            if not data_status["available"]:
                recommendations.append("Initialize historical data")
            elif data_status["count"] < 300:
                recommendations.append(f"Add more data (current: {data_status['count']}, recommended: 300+)")
            
            if not model_status["available"]:
                recommendations.append("Train prediction models")
            
            if not recommendations:
                recommendations.append("System ready for predictions!")
            
            return {
                "data": data_status,
                "models": model_status,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "data": {"available": False, "count": 0},
                "models": {"available": False},
                "recommendations": ["System check failed"],
                "error": str(e)
            }


# Global instance for easy import
streamlit_adapters = StreamlitAdapters()


# Convenience functions for direct import
def init_full_history() -> dict:
    """Initialize full historical data."""
    return streamlit_adapters.init_full_history()


def update_incremental() -> dict:
    """Update with recent draws."""
    return streamlit_adapters.update_incremental()


def train_from_scratch() -> dict:
    """Train models from scratch."""
    return streamlit_adapters.train_from_scratch()


def reload_models() -> dict:
    """Reload models from disk."""
    return streamlit_adapters.reload_models()


def get_scores() -> tuple:
    """Get ball and star scores as DataFrames."""
    return streamlit_adapters.get_scores()


def suggest_tickets_ui(n: int = 10, method: str = "hybrid", seed: int = 42, 
                      use_ensemble: bool = True, hybrid_weights: Optional[Dict[str, float]] = None) -> list:
    """Generate enhanced lottery ticket suggestions."""
    return streamlit_adapters.suggest_tickets_ui(n, method, seed, use_ensemble, hybrid_weights)


def train_ensemble_models() -> dict:
    """Train ensemble models if available."""
    try:
        from train_models import train_ensemble_models as train_ensemble_func
        return train_ensemble_func()
    except ImportError as e:
        logger.warning(f"Ensemble training not available: {e}")
        return {
            "success": False,
            "message": "Ensemble models not available. Please check installation."
        }
    except Exception as e:
        logger.error(f"Error training ensemble models: {e}")
        return {
            "success": False,
            "message": f"Error training ensemble: {str(e)}"
        }


def fetch_last_draws(limit: int = 20) -> pd.DataFrame:
    """Fetch recent draws."""
    return streamlit_adapters.fetch_last_draws(limit)


def export_all_draws_csv() -> tuple:
    """Export all draws to CSV."""
    return streamlit_adapters.export_all_draws_csv()


def get_system_status() -> dict:
    """Get comprehensive system status."""
    return streamlit_adapters.get_system_status()
