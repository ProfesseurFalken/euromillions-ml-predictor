"""
Test rapide du backtesting avec les méthodes ensemble et advanced_hybrid
"""
import sys
sys.path.insert(0, 'ui')

from streamlit_app import run_backtesting
import pandas as pd

print("🧪 Test du backtesting avec ensemble et advanced_hybrid")
print("=" * 60)

# Test minimal : 2 graines, 2 tirages, 3 tickets
seeds = [42, 123]
methods = ["ensemble", "advanced_hybrid"]
n_draws = 2
n_tickets = 3

print(f"\n📊 Configuration:")
print(f"  - Graines: {seeds}")
print(f"  - Méthodes: {methods}")
print(f"  - Tirages: {n_draws}")
print(f"  - Tickets par tirage: {n_tickets}")
print(f"  - Total tests: {len(seeds) * len(methods)} configurations")

print(f"\n⏱️ Démarrage du test...\n")

# Mock de Streamlit pour le test
class MockStreamlit:
    @staticmethod
    def progress(val):
        return lambda x: None
    
    @staticmethod
    def empty():
        class Empty:
            def text(self, msg): print(f"  {msg}")
            def empty(self): pass
        return Empty()
    
    @staticmethod
    def info(msg): print(f"ℹ️  {msg}")
    
    @staticmethod
    def error(msg): print(f"❌ {msg}")
    
    @staticmethod
    def warning(msg): print(f"⚠️  {msg}")
    
    @staticmethod
    def text(msg): print(f"📝 {msg}")

# Remplacer st par le mock
import streamlit_app
streamlit_app.st = MockStreamlit()

# Lancer le backtesting
try:
    df_results = run_backtesting(seeds, methods, n_draws, n_tickets)
    
    print("\n" + "=" * 60)
    print("✅ RÉSULTATS DU BACKTESTING")
    print("=" * 60)
    
    if df_results.empty:
        print("❌ ERREUR: DataFrame vide, aucun résultat!")
    else:
        print(f"\n📊 {len(df_results)} configurations testées\n")
        
        # Afficher les résultats
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 120)
        print(df_results.to_string(index=False))
        
        print("\n" + "=" * 60)
        print("🎯 VÉRIFICATION DES MÉTHODES")
        print("=" * 60)
        
        for method in methods:
            method_results = df_results[df_results['method'] == method]
            if len(method_results) > 0:
                print(f"\n✅ {method}: {len(method_results)} résultats trouvés")
                avg_score = method_results['avg_score'].mean()
                print(f"   Score moyen: {avg_score:.2f}")
            else:
                print(f"\n❌ {method}: AUCUN RÉSULTAT TROUVÉ!")
        
except Exception as e:
    print(f"\n❌ ERREUR lors du backtesting: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🏁 Test terminé")
print("=" * 60)
