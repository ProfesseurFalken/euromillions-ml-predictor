"""
Advanced Streamlit UI Components for EuroMillions
=================================================

This module provides advanced UI components including:
- Ticket strategy selection with visual comparison
- Backtesting results visualization
- Model comparison dashboard
- Advanced feature analysis
- Interactive probability explorer

Author: EuroMillions ML Predictor
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_advanced_features_available() -> Dict[str, bool]:
    """Check which advanced features are available."""
    features = {}
    
    try:
        from ticket_strategies import TicketGenerator
        features['ticket_strategies'] = True
    except ImportError:
        features['ticket_strategies'] = False
    
    try:
        from backtesting import BacktestEngine
        features['backtesting'] = True
    except ImportError:
        features['backtesting'] = False
    
    try:
        from advanced_training_pipeline import AdvancedEuromillionsTrainer
        features['advanced_training'] = True
    except ImportError:
        features['advanced_training'] = False
    
    try:
        from advanced_features_v2 import AdvancedFeatureExtractorV2
        features['advanced_features'] = True
    except ImportError:
        features['advanced_features'] = False
    
    try:
        from deep_learning_models import HybridDeepLearningPredictor  # type: ignore[import-not-found]
        features['deep_learning'] = True
    except ImportError:
        features['deep_learning'] = False
    
    return features


def render_strategy_selector():
    """Render strategy selection interface."""
    st.subheader("🎯 Stratégies de Génération de Tickets")
    
    strategies = {
        'probability': {
            'name': 'Probabiliste',
            'description': 'Sélection basée sur les probabilités ML pures',
            'icon': '📊',
            'risk': 'Moyen'
        },
        'balanced': {
            'name': 'Équilibrée',
            'description': 'Équilibre pair/impair, bas/haut, somme contrôlée',
            'icon': '⚖️',
            'risk': 'Faible'
        },
        'coverage': {
            'name': 'Couverture',
            'description': 'Maximise le nombre de numéros couverts',
            'icon': '🎯',
            'risk': 'Moyen'
        },
        'wheel': {
            'name': 'Système (Wheeling)',
            'description': 'Garanties mathématiques de couverture',
            'icon': '🎡',
            'risk': 'Faible'
        },
        'hotcold': {
            'name': 'Chaud/Froid',
            'description': 'Mélange numéros chauds et numéros dus',
            'icon': '🔥',
            'risk': 'Élevé'
        },
        'conservative': {
            'name': 'Conservatrice',
            'description': 'Numéros les plus probables uniquement',
            'icon': '🛡️',
            'risk': 'Faible'
        },
        'aggressive': {
            'name': 'Agressive',
            'description': 'Inclut des numéros à longue cote',
            'icon': '⚡',
            'risk': 'Élevé'
        }
    }
    
    # Display strategy cards
    cols = st.columns(3)
    selected_strategy = st.session_state.get('selected_strategy', 'balanced')
    
    for idx, (key, info) in enumerate(strategies.items()):
        with cols[idx % 3]:
            is_selected = selected_strategy == key
            border_color = "#4CAF50" if is_selected else "#ddd"
            bg_color = "#e8f5e9" if is_selected else "#fafafa"
            
            st.markdown(f"""
            <div style="
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                background-color: {bg_color};
                cursor: pointer;
            ">
                <h4>{info['icon']} {info['name']}</h4>
                <p style="font-size: 12px; color: #666;">{info['description']}</p>
                <span style="
                    background-color: {'#f44336' if info['risk'] == 'Élevé' else '#ff9800' if info['risk'] == 'Moyen' else '#4caf50'};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 11px;
                ">Risque: {info['risk']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Sélectionner", key=f"select_{key}"):
                st.session_state['selected_strategy'] = key
                st.rerun()
    
    return selected_strategy


def render_multi_strategy_generation():
    """Render multi-strategy ticket generation interface."""
    st.subheader("🎲 Génération Multi-Stratégies")
    
    available = check_advanced_features_available()
    
    if not available.get('ticket_strategies'):
        st.warning("⚠️ Module de stratégies avancées non disponible")
        return None
    
    from ticket_strategies import TicketGenerator
    
    # Strategy selection
    selected_strategies = st.multiselect(
        "Sélectionnez les stratégies à utiliser",
        options=['probability', 'balanced', 'coverage', 'wheel', 'hotcold'],
        default=['probability', 'balanced'],
        help="Les tickets seront générés avec chaque stratégie"
    )
    
    n_tickets_per_strategy = st.slider(
        "Tickets par stratégie",
        min_value=1,
        max_value=5,
        value=2
    )
    
    if st.button("🎲 Générer Multi-Stratégies"):
        # Get probabilities (placeholder - in real app, get from models)
        try:
            from train_models import EuromillionsTrainer
            trainer = EuromillionsTrainer()
            trainer.load_models()
            
            ball_scores = dict(trainer.score_balls())
            star_scores = dict(trainer.score_stars())
            
            main_proba = np.array([ball_scores.get(i, 0.02) for i in range(1, 51)])
            star_proba = np.array([star_scores.get(i, 0.167) for i in range(1, 13)])
        except:
            # Fallback to uniform
            main_proba = np.ones(50) / 50
            star_proba = np.ones(12) / 12
        
        generator = TicketGenerator()
        all_tickets = {}
        
        for strategy in selected_strategies:
            tickets = generator.generate(
                main_proba, star_proba,
                strategy=strategy,
                n_tickets=n_tickets_per_strategy
            )
            all_tickets[strategy] = tickets
        
        # Display results
        for strategy, tickets in all_tickets.items():
            st.markdown(f"### 🏷️ Stratégie: {strategy.title()}")
            
            for idx, ticket in enumerate(tickets, 1):
                balls_str = " - ".join(f"{b:02d}" for b in ticket['main'])
                stars_str = " - ".join(f"{s:02d}" for s in ticket['stars'])
                
                st.markdown(f"""
                **Ticket {idx}:** `{balls_str}` ⭐ `{stars_str}`
                """)
        
        # Analysis
        all_flat = [t for tickets in all_tickets.values() for t in tickets]
        analysis = generator.analyze_tickets(all_flat)
        
        st.markdown("### 📊 Analyse des Tickets")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Couverture Boules", f"{analysis['main_coverage']:.0%}")
        with col2:
            st.metric("Couverture Étoiles", f"{analysis['star_coverage']:.0%}")
        with col3:
            st.metric("Somme Moyenne", f"{analysis['average_sum']:.0f}")
        
        return all_tickets
    
    return None


def render_backtesting_dashboard():
    """Render backtesting results dashboard."""
    st.subheader("📈 Résultats de Backtesting")
    
    available = check_advanced_features_available()
    
    if not available.get('backtesting'):
        st.warning("⚠️ Module de backtesting non disponible")
        return
    
    # Check for existing results
    results_path = Path("models/euromillions_advanced/backtest_results.json")
    
    if results_path.exists():
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        st.success("✅ Résultats de backtesting disponibles")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        hit_rates = results.get('hit_rates', {})
        
        with col1:
            rate_2_5 = hit_rates.get('2/5', 0) * 100
            st.metric("Taux 2/5", f"{rate_2_5:.1f}%")
        
        with col2:
            rate_3_5 = hit_rates.get('3/5', 0) * 100
            st.metric("Taux 3/5", f"{rate_3_5:.1f}%")
        
        with col3:
            rate_4_5 = hit_rates.get('4/5', 0) * 100
            st.metric("Taux 4/5", f"{rate_4_5:.1f}%")
        
        with col4:
            ev = results.get('expected_value', 0)
            st.metric("Valeur Espérée", f"€{ev:.2f}")
        
        # Show vs random comparison
        st.markdown("### 📊 Comparaison avec Aléatoire")
        
        improvement = results.get('improvement_vs_random', {})
        
        if improvement:
            col1, col2 = st.columns(2)
            
            with col1:
                for key, value in list(improvement.items())[:3]:
                    color = "green" if value > 0 else "red"
                    st.markdown(f"**{key}:** <span style='color: {color}'>{value:+.1%}</span>", 
                               unsafe_allow_html=True)
            
            with col2:
                for key, value in list(improvement.items())[3:]:
                    color = "green" if value > 0 else "red"
                    st.markdown(f"**{key}:** <span style='color: {color}'>{value:+.1%}</span>",
                               unsafe_allow_html=True)
    
    # Option to run new backtest
    st.markdown("---")
    st.markdown("### 🔄 Exécuter un nouveau Backtest")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_test_draws = st.slider(
            "Nombre de tirages de test",
            min_value=20,
            max_value=100,
            value=50
        )
    
    with col2:
        window_size = st.slider(
            "Fenêtre d'entraînement",
            min_value=100,
            max_value=500,
            value=200
        )
    
    if st.button("🚀 Lancer le Backtest"):
        with st.spinner("Exécution du backtest en cours... (cela peut prendre plusieurs minutes)"):
            try:
                from backtesting import run_full_backtest
                from repository import get_repository
                
                repo = get_repository()
                df = repo.all_draws_df()
                
                results = run_full_backtest(df, test_draws=n_test_draws)  # type: ignore[call-arg]
                
                # Save results
                results_path.parent.mkdir(parents=True, exist_ok=True)
                with open(results_path, 'w') as f:
                    json.dump(results, f, indent=2)
                
                st.success("✅ Backtest terminé!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors du backtest: {e}")


def render_model_comparison():
    """Render model comparison dashboard."""
    st.subheader("🤖 Comparaison des Modèles")
    
    # Check for trained models
    models_path = Path("models/euromillions_advanced")
    meta_path = models_path / "advanced_meta.json"
    
    if meta_path.exists():
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        st.markdown("### 📊 Modèles Disponibles")
        
        available = meta.get('available_modules', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if available.get('advanced_features'):
                st.success("✅ Features Avancées")
            else:
                st.error("❌ Features Avancées")
        
        with col2:
            if available.get('deep_learning'):
                st.success("✅ Deep Learning")
            else:
                st.warning("⚠️ Deep Learning")
        
        with col3:
            if available.get('enhanced_ensemble'):
                st.success("✅ Ensemble Amélioré")
            else:
                st.error("❌ Ensemble Amélioré")
        
        # Training stages
        stages = meta.get('stages', {})
        
        if stages:
            st.markdown("### 📈 Résultats d'Entraînement")
            
            for stage_name, stage_info in stages.items():
                status = stage_info.get('status', 'unknown')
                
                if status == 'success':
                    st.success(f"✅ {stage_name}")
                elif status == 'skipped':
                    st.info(f"⏭️ {stage_name} (ignoré)")
                elif status == 'failed':
                    st.error(f"❌ {stage_name}: {stage_info.get('error', 'erreur inconnue')}")
                else:
                    st.warning(f"⚠️ {stage_name}")
    
    else:
        st.info("ℹ️ Aucun modèle avancé entraîné. Utilisez l'entraînement avancé.")


def render_advanced_training_section():
    """Render advanced training interface."""
    st.subheader("🧠 Entraînement Avancé")
    
    available = check_advanced_features_available()
    
    if not available.get('advanced_training'):
        st.warning("⚠️ Module d'entraînement avancé non disponible")
        return
    
    st.markdown("""
    L'entraînement avancé inclut:
    - **Features avancées**: Analyse multi-fenêtre, décroissance exponentielle
    - **Deep Learning**: LSTM et Transformer (si TensorFlow installé)
    - **Ensemble amélioré**: Stacking, poids dynamiques
    - **Validation**: Backtesting walk-forward
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_deep_learning = st.checkbox(
            "Activer Deep Learning",
            value=False,
            help="Nécessite TensorFlow. Peut être lent."
        )
    
    with col2:
        use_backtesting = st.checkbox(
            "Activer Backtesting",
            value=True,
            help="Valide les modèles sur données historiques"
        )
    
    if st.button("🚀 Lancer l'Entraînement Avancé", use_container_width=True):
        with st.spinner("Entraînement avancé en cours... (cela peut prendre plusieurs minutes)"):
            try:
                from advanced_training_pipeline import AdvancedEuromillionsTrainer
                
                trainer = AdvancedEuromillionsTrainer()
                results = trainer.train_full_pipeline(
                    min_rows=300,
                    use_deep_learning=use_deep_learning,
                    use_backtesting=use_backtesting
                )
                
                st.success("✅ Entraînement avancé terminé!")
                
                # Show summary
                st.text(trainer.get_training_summary())
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'entraînement: {e}")


def render_probability_explorer():
    """Render interactive probability explorer."""
    st.subheader("🔍 Explorateur de Probabilités")
    
    try:
        from train_models import EuromillionsTrainer
        
        trainer = EuromillionsTrainer()
        trainer.load_models()
        
        ball_scores = trainer.score_balls()
        star_scores = trainer.score_stars()
        
        # Create DataFrames
        balls_df = pd.DataFrame(ball_scores, columns=['Numéro', 'Probabilité'])
        balls_df['Pourcentage'] = (balls_df['Probabilité'] * 100).round(2)  # type: ignore[operator]
        balls_df['Rang'] = balls_df['Probabilité'].rank(ascending=False).astype(int)
        balls_df = balls_df.sort_values('Rang')
        
        stars_df = pd.DataFrame(star_scores, columns=['Numéro', 'Probabilité'])
        stars_df['Pourcentage'] = (stars_df['Probabilité'] * 100).round(2)  # type: ignore[operator]
        stars_df['Rang'] = stars_df['Probabilité'].rank(ascending=False).astype(int)
        stars_df = stars_df.sort_values('Rang')
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Classement", "📈 Distribution", "🎯 Sélection"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎱 Top 15 Boules")
                st.dataframe(
                    balls_df.head(15)[['Rang', 'Numéro', 'Pourcentage']],
                    hide_index=True,
                    use_container_width=True
                )
            
            with col2:
                st.markdown("### ⭐ Étoiles")
                st.dataframe(
                    stars_df[['Rang', 'Numéro', 'Pourcentage']],
                    hide_index=True,
                    use_container_width=True
                )
        
        with tab2:
            st.markdown("### 📈 Distribution des Probabilités")
            
            # Simple bar chart using native Streamlit
            chart_data = balls_df.sort_values('Numéro')[['Numéro', 'Probabilité']].set_index('Numéro')
            st.bar_chart(chart_data)
        
        with tab3:
            st.markdown("### 🎯 Numéros Sélectionnés")
            
            # Top picks based on probability
            top_balls = balls_df.head(5)['Numéro'].tolist()
            top_stars = stars_df.head(2)['Numéro'].tolist()
            
            st.markdown(f"""
            **Prédiction Principale:**
            
            🎱 Boules: **{' - '.join(map(str, sorted(top_balls)))}**
            
            ⭐ Étoiles: **{' - '.join(map(str, sorted(top_stars)))}**
            """)
            
            # Show confidence
            avg_ball_prob = balls_df.head(5)['Probabilité'].mean()
            avg_star_prob = stars_df.head(2)['Probabilité'].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Confiance Boules", f"{avg_ball_prob*100:.1f}%")
            with col2:
                st.metric("Confiance Étoiles", f"{avg_star_prob*100:.1f}%")
        
    except FileNotFoundError:
        st.warning("⚠️ Aucun modèle entraîné. Veuillez d'abord entraîner les modèles.")
    except Exception as e:
        st.error(f"❌ Erreur: {e}")


def render_advanced_features_tab():
    """Render the complete advanced features tab."""
    st.header("🚀 Fonctionnalités Avancées")
    
    # Check available features
    available = check_advanced_features_available()
    
    # Display available modules
    st.markdown("### 📦 Modules Disponibles")
    
    cols = st.columns(5)
    module_names = {
        'ticket_strategies': 'Stratégies Tickets',
        'backtesting': 'Backtesting',
        'advanced_training': 'Entraînement Avancé',
        'advanced_features': 'Features Avancées',
        'deep_learning': 'Deep Learning'
    }
    
    for idx, (key, name) in enumerate(module_names.items()):
        with cols[idx]:
            if available.get(key, False):
                st.success(f"✅ {name}")
            else:
                st.error(f"❌ {name}")
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Stratégies",
        "📈 Backtesting",
        "🤖 Modèles",
        "🧠 Entraînement",
        "🔍 Probabilités"
    ])
    
    with tab1:
        render_multi_strategy_generation()
    
    with tab2:
        render_backtesting_dashboard()
    
    with tab3:
        render_model_comparison()
    
    with tab4:
        render_advanced_training_section()
    
    with tab5:
        render_probability_explorer()


# Export function for use in main app
def add_advanced_section_to_app():
    """Add advanced section to the main Streamlit app."""
    st.markdown("---")
    
    # Add expander for advanced features
    with st.expander("🚀 Fonctionnalités Avancées (Beta)", expanded=False):
        render_advanced_features_tab()


if __name__ == "__main__":
    # For testing the module standalone
    st.set_page_config(page_title="EuroMillions Advanced", page_icon="🚀", layout="wide")
    render_advanced_features_tab()
