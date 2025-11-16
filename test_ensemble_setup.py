#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement de l'ensemble de modèles.
"""

def test_ensemble_imports():
    """Test des imports nécessaires pour l'ensemble."""
    print("🔍 Test des imports d'ensemble...")
    
    try:
        import xgboost
        print(f"✅ XGBoost: {xgboost.__version__}")
    except ImportError as e:
        print(f"❌ XGBoost: {e}")
        return False
    
    try:
        import catboost
        print(f"✅ CatBoost: {catboost.__version__}")
    except ImportError as e:
        print(f"❌ CatBoost: {e}")
        return False
    
    try:
        import lightgbm
        print(f"✅ LightGBM: {lightgbm.__version__}")
    except ImportError as e:
        print(f"❌ LightGBM: {e}")
        return False
        
    try:
        from sklearn.ensemble import RandomForestClassifier, VotingClassifier
        from sklearn.ensemble import StackingClassifier
        print("✅ Sklearn ensemble classes")
    except ImportError as e:
        print(f"❌ Sklearn ensemble: {e}")
        return False
    
    return True

def test_ensemble_trainer():
    """Test de la classe EnsembleTrainer."""
    print("\n🤖 Test de EnsembleTrainer...")
    
    try:
        from ensemble_models import EnsembleTrainer
        print("✅ Import EnsembleTrainer")
        
        # Test de création d'instance
        trainer = EnsembleTrainer()
        print("✅ Création d'instance EnsembleTrainer")
        
        # Test des méthodes disponibles
        methods = [method for method in dir(trainer) if not method.startswith('_')]
        print(f"✅ Méthodes disponibles: {len(methods)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import EnsembleTrainer: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur EnsembleTrainer: {e}")
        return False

def test_hybrid_strategy():
    """Test de la stratégie hybride."""
    print("\n🧠 Test de HybridPredictionStrategy...")
    
    try:
        from hybrid_strategy import HybridPredictionStrategy
        print("✅ Import HybridPredictionStrategy")
        
        # Test de création d'instance
        strategy = HybridPredictionStrategy()
        print("✅ Création d'instance HybridPredictionStrategy")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import HybridPredictionStrategy: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur HybridPredictionStrategy: {e}")
        return False

def test_streamlit_integration():
    """Test de l'intégration Streamlit."""
    print("\n🌐 Test de l'intégration Streamlit...")
    
    try:
        from streamlit_adapters import train_ensemble_models
        print("✅ Import train_ensemble_models")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import train_ensemble_models: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur train_ensemble_models: {e}")
        return False

def main():
    """Test principal."""
    print("🚀 Test complet de l'ensemble de modèles\n")
    
    tests = [
        ("Imports d'ensemble", test_ensemble_imports),
        ("EnsembleTrainer", test_ensemble_trainer),
        ("Stratégie hybride", test_hybrid_strategy),
        ("Intégration Streamlit", test_streamlit_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont réussis !")
        print("💡 Le bouton 'Ensemble de modèles' devrait maintenant fonctionner.")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("🔧 Vérifiez les erreurs ci-dessus.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)