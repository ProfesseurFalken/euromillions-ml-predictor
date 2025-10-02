#!/usr/bin/env python3
"""
Script de debug pour vérifier la génération des tickets EuroMillions
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

def test_ticket_generation():
    """Test de génération de tickets pour identifier le problème."""
    print("🔍 Test de génération des tickets EuroMillions")
    print("=" * 50)
    
    try:
        from streamlit_adapters import suggest_tickets_ui
        
        # Test avec différentes méthodes
        methods = ["topk", "random", "hybrid"]
        
        for method in methods:
            print(f"\n🎲 Test méthode: {method}")
            try:
                tickets = suggest_tickets_ui(2, method, 42)
                
                if tickets:
                    for i, ticket in enumerate(tickets, 1):
                        balls = ticket['balls']
                        stars = ticket['stars']
                        
                        print(f"  Ticket {i}:")
                        print(f"    Boules: {balls} (count: {len(balls)})")
                        print(f"    Étoiles: {stars} (count: {len(stars)})")
                        print(f"    Affichage: {ticket['balls_str']} | ⭐ {ticket['stars_str']}")
                        
                        # Vérification des règles EuroMillions
                        if len(balls) != 5:
                            print(f"    ❌ ERREUR: {len(balls)} boules au lieu de 5!")
                        if len(stars) != 2:
                            print(f"    ❌ ERREUR: {len(stars)} étoiles au lieu de 2!")
                        if len(set(balls)) != len(balls):
                            print(f"    ❌ ERREUR: Doublons dans les boules!")
                        if len(set(stars)) != len(stars):
                            print(f"    ❌ ERREUR: Doublons dans les étoiles!")
                        if any(b < 1 or b > 50 for b in balls):
                            print(f"    ❌ ERREUR: Boules hors limites (1-50)!")
                        if any(s < 1 or s > 12 for s in stars):
                            print(f"    ❌ ERREUR: Étoiles hors limites (1-12)!")
                            
                        if len(balls) == 5 and len(stars) == 2:
                            print(f"    ✅ Format correct")
                else:
                    print(f"    ❌ Aucun ticket généré")
                    
            except Exception as e:
                print(f"    ❌ Erreur avec {method}: {e}")
                import traceback
                traceback.print_exc()
                
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_raw_model_generation():
    """Test direct du modèle pour identifier le problème à la source."""
    print(f"\n🤖 Test direct des modèles ML")
    print("=" * 30)
    
    try:
        from train_models import EuromillionsTrainer
        
        trainer = EuromillionsTrainer()
        
        # Test de génération directe
        combinations = trainer.suggest_combinations(k=2, method="topk", seed=42)
        
        print(f"Combinaisons générées: {len(combinations)}")
        
        for i, combo in enumerate(combinations, 1):
            balls = combo.get("balls", [])
            stars = combo.get("stars", [])
            
            print(f"  Combo {i}:")
            print(f"    balls raw: {balls} (type: {type(balls)}, len: {len(balls)})")
            print(f"    stars raw: {stars} (type: {type(stars)}, len: {len(stars)})")
            
            # Vérifications
            if len(balls) != 5:
                print(f"    ❌ PROBLÈME DÉTECTÉ: {len(balls)} boules au lieu de 5!")
            if len(stars) != 2:
                print(f"    ❌ PROBLÈME DÉTECTÉ: {len(stars)} étoiles au lieu de 2!")
            
    except Exception as e:
        print(f"❌ Erreur test modèle: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    success = test_ticket_generation()
    test_raw_model_generation()
    
    if success:
        print(f"\n✅ Tests terminés")
    else:
        print(f"\n❌ Tests échoués")