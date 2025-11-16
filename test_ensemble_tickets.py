#!/usr/bin/env python3
"""
Test spécifique de la génération de tickets avec le modèle ensemble
================================================================

Teste la fonction _generate_ensemble_tickets pour vérifier qu'elle fonctionne correctement.
"""

import sys
import traceback
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

def test_ensemble_ticket_generation():
    """Test spécifique de la génération de tickets ensemble."""
    print("🧪 TEST DE GÉNÉRATION DE TICKETS ENSEMBLE")
    print("=" * 50)
    
    try:
        # Import des modules nécessaires
        print("📦 Chargement des modules...")
        from streamlit_adapters import StreamlitAdapters
        from ensemble_models import EnsembleTrainer
        
        print("✅ Modules chargés avec succès")
        
        # Vérifier que les modèles ensemble existent
        print("\n🔍 Vérification de l'existence des modèles ensemble...")
        trainer = EnsembleTrainer()
        
        if not trainer.models_exist():
            print("❌ Les modèles ensemble n'existent pas!")
            print("💡 Lancez d'abord l'entraînement ensemble dans l'interface")
            return False
            
        print("✅ Modèles ensemble trouvés")
        
        # Test de génération de tickets
        print("\n🎲 Test de génération de 3 tickets ensemble...")
        
        try:
            # Créer une instance du générateur
            adapters = StreamlitAdapters()
            tickets = adapters._generate_ensemble_tickets(n=3, seed=42)
            
            if not tickets:
                print("❌ Aucun ticket généré!")
                return False
                
            print(f"✅ {len(tickets)} tickets générés avec succès!")
            
            # Afficher les tickets générés
            print("\n📋 TICKETS GÉNÉRÉS:")
            print("-" * 30)
            
            for i, ticket in enumerate(tickets, 1):
                print(f"\n🎫 Ticket {i}:")
                print(f"   🎱 Numéros: {ticket.get('balls_str', 'N/A')}")
                print(f"   ⭐ Étoiles: {ticket.get('stars_str', 'N/A')}")
                print(f"   📊 Confiance: {ticket.get('base_confidence', 0):.3f}")
                print(f"   🔧 Méthode: {ticket.get('method', 'N/A')}")
                
                # Vérifier la validité du ticket
                balls = ticket.get('balls', [])
                stars = ticket.get('stars', [])
                
                if len(balls) != 5 or len(stars) != 2:
                    print(f"   ⚠️  Format invalide: {len(balls)} numéros, {len(stars)} étoiles")
                    return False
                    
                if not all(1 <= b <= 50 for b in balls):
                    print(f"   ⚠️  Numéros hors limite: {balls}")
                    return False
                    
                if not all(1 <= s <= 12 for s in stars):
                    print(f"   ⚠️  Étoiles hors limite: {stars}")
                    return False
                    
                print(f"   ✅ Ticket valide")
            
            print(f"\n🎉 SUCCÈS: Génération de tickets ensemble fonctionnelle!")
            return True
            
        except Exception as ticket_error:
            print(f"❌ Erreur lors de la génération de tickets:")
            print(f"   {type(ticket_error).__name__}: {ticket_error}")
            print("\n📋 Stack trace complète:")
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Vérifiez que tous les modules sont bien installés")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
        print("\n📋 Stack trace:")
        traceback.print_exc()
        return False


def test_ensemble_api_directly():
    """Test direct de l'API ensemble."""
    print("\n🔬 TEST DIRECT DE L'API ENSEMBLE")
    print("-" * 40)
    
    try:
        from ensemble_models import EnsembleTrainer
        from build_datasets import build_enhanced_datasets
        from repository import get_repository
        
        print("📊 Chargement des données...")
        repo = get_repository()
        df = repo.all_draws_df()
        
        if df.empty:
            print("❌ Aucune donnée disponible")
            return False
            
        print(f"✅ {len(df)} tirages chargés")
        
        print("🏗️  Construction des datasets...")
        X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(
            df, window_size=min(100, len(df) // 3)
        )
        
        print(f"✅ Datasets construits: {X_main.shape[0]} échantillons")
        
        print("🤖 Test de prédiction ensemble...")
        trainer = EnsembleTrainer()
        
        # Prendre les dernières features pour test
        latest_main = X_main[-1:] 
        latest_star = X_star[-1:]
        
        main_proba, star_proba = trainer.predict_with_ensemble(latest_main, latest_star)
        
        print(f"✅ Prédiction réussie:")
        print(f"   📊 Shape main_proba: {main_proba.shape}")
        print(f"   📊 Shape star_proba: {star_proba.shape}")
        print(f"   🎯 Range main: [{main_proba.min():.3f}, {main_proba.max():.3f}]")
        print(f"   🎯 Range star: [{star_proba.min():.3f}, {star_proba.max():.3f}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur API ensemble: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 DIAGNOSTIC COMPLET - GÉNÉRATION TICKETS ENSEMBLE")
    print("=" * 60)
    
    success1 = test_ensemble_ticket_generation()
    success2 = test_ensemble_api_directly()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 RÉSULTAT: La génération de tickets ensemble FONCTIONNE PARFAITEMENT!")
    elif success2:
        print("🔧 RÉSULTAT: L'API ensemble fonctionne, mais il y a un problème dans la génération de tickets")
    else:
        print("❌ RÉSULTAT: Problèmes détectés dans le système ensemble")
    
    print("=" * 60)