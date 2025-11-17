"""
Test complet du backtesting avec toutes les méthodes
"""
import sys
sys.path.insert(0, 'ui')

print("=" * 70)
print("TEST BACKTESTING COMPLET")
print("=" * 70)

# Configuration du test
seeds = [42, 123]
methods = ["topk", "hybrid", "ensemble", "advanced_hybrid"]
n_draws = 3
n_tickets = 5

print(f"\n📊 Configuration:")
print(f"   - Graines: {seeds}")
print(f"   - Méthodes: {methods}")
print(f"   - Tirages: {n_draws}")
print(f"   - Tickets/tirage: {n_tickets}")
print(f"   - Total tests: {len(seeds) * len(methods)}")

# Importer après avoir configuré le path
from repository import get_repository
from streamlit_app import _generate_tickets_fast
from streamlit_adapters import suggest_tickets_ui
import train_models

# Charger les données
print("\n⚡ Chargement des données...")
repo = get_repository()
all_draws = repo.all_draws_df()
test_draws = all_draws.tail(n_draws)

print(f"✅ {len(test_draws)} tirages chargés")

# Précalculer les probabilités
print("\n⚡ Précalcul des probabilités ML...")
main_proba = train_models.score_balls()
star_proba = train_models.score_stars()
main_scores = {i: main_proba[i-1] for i in range(1, 51)}
star_scores = {i: star_proba[i-1] for i in range(1, 13)}
print("✅ Probabilités précalculées")

# Tester chaque méthode
print("\n" + "=" * 70)
print("TESTS DES MÉTHODES")
print("=" * 70)

results = {}

for method in methods:
    print(f"\n🎯 Méthode: {method}")
    print("-" * 70)
    
    total_tickets = 0
    errors = 0
    
    for seed in seeds:
        try:
            # Générer tickets selon la méthode
            if method in ["ensemble", "advanced_hybrid"]:
                tickets = suggest_tickets_ui(
                    n=n_tickets,
                    method=method,
                    seed=seed,
                    use_ensemble=True
                )
            else:
                tickets = _generate_tickets_fast(n_tickets, method, seed, main_scores, star_scores)
            
            # Vérifier la structure
            for ticket in tickets:
                ticket_main = ticket.get('main') or ticket.get('balls', [])
                ticket_stars = ticket.get('stars', [])
                
                if not ticket_main or not ticket_stars:
                    errors += 1
                    print(f"   ❌ Seed {seed}: Ticket invalide - {ticket}")
                else:
                    total_tickets += 1
        
        except Exception as e:
            errors += 1
            print(f"   ❌ Seed {seed}: Erreur - {e}")
    
    # Résumé
    expected = len(seeds) * n_tickets
    if errors == 0 and total_tickets == expected:
        print(f"   ✅ {total_tickets}/{expected} tickets générés avec succès")
        results[method] = "✅ OK"
    else:
        print(f"   ⚠️  {total_tickets}/{expected} tickets valides, {errors} erreurs")
        results[method] = f"⚠️ {errors} erreurs"

# Résumé final
print("\n" + "=" * 70)
print("RÉSUMÉ")
print("=" * 70)

for method, status in results.items():
    print(f"   {method:20s} : {status}")

all_ok = all("✅" in status for status in results.values())

print("\n" + "=" * 70)
if all_ok:
    print("✅ TOUS LES TESTS RÉUSSIS - Le backtesting devrait fonctionner")
else:
    print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ - Vérifier les erreurs ci-dessus")
print("=" * 70)
