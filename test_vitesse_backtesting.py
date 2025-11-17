"""
Test de vitesse du backtesting avec toutes les méthodes
"""
import sys
sys.path.insert(0, 'ui')
import time

print("=" * 70)
print("TEST DE VITESSE - BACKTESTING OPTIMISÉ")
print("=" * 70)

# Configuration du test (petit pour mesurer la vitesse)
seeds = [42]
methods = ["topk", "hybrid", "ensemble", "advanced_hybrid"]
n_draws = 5
n_tickets = 10

print(f"\n📊 Configuration:")
print(f"   - Graines: {seeds}")
print(f"   - Méthodes: {methods}")
print(f"   - Tirages: {n_draws}")
print(f"   - Tickets/tirage: {n_tickets}")
print(f"   - Total: {len(seeds)} seed × {len(methods)} méthodes × {n_draws} tirages × {n_tickets} tickets")
print(f"   - = {len(seeds) * len(methods) * n_draws * n_tickets} tickets à générer")

# Importer
from repository import get_repository
from streamlit_app import _generate_tickets_fast
import train_models

# Charger les données
print("\n⚡ Chargement des données...")
repo = get_repository()
all_draws = repo.all_draws_df()

# Précalculer les probabilités
print("⚡ Précalcul des probabilités ML...")
start_precalc = time.time()
main_proba = train_models.score_balls()
star_proba = train_models.score_stars()
main_scores = {i: main_proba[i-1] for i in range(1, 51)}
star_scores = {i: star_proba[i-1] for i in range(1, 13)}
precalc_time = time.time() - start_precalc
print(f"✅ Précalcul terminé en {precalc_time:.2f}s")

# Tester chaque méthode
print("\n" + "=" * 70)
print("TESTS DE VITESSE")
print("=" * 70)

for method in methods:
    print(f"\n🎯 {method}:")
    start = time.time()
    
    for _ in range(n_draws):
        for seed in seeds:
            tickets = _generate_tickets_fast(n_tickets, method, seed, main_scores, star_scores)
    
    elapsed = time.time() - start
    total_tickets = len(seeds) * n_draws * n_tickets
    time_per_ticket = (elapsed / total_tickets) * 1000  # en millisecondes
    
    print(f"   ✅ {total_tickets} tickets en {elapsed:.2f}s")
    print(f"   ⚡ {time_per_ticket:.1f}ms par ticket")

# Test complet simulé
print("\n" + "=" * 70)
print("ESTIMATION BACKTESTING COMPLET")
print("=" * 70)

# Configuration complète typique
full_seeds = 25  # Mode rapide
full_methods = 4  # toutes les méthodes
full_draws = 30
full_tickets = 10

total_tickets_full = full_seeds * full_methods * full_draws * full_tickets
estimated_time = (total_tickets_full * time_per_ticket) / 1000  # en secondes

print(f"\n📊 Configuration Mode Rapide:")
print(f"   - {full_seeds} seeds × {full_methods} méthodes × {full_draws} tirages × {full_tickets} tickets")
print(f"   - = {total_tickets_full} tickets")
print(f"\n⏱️ Temps estimé: {estimated_time:.1f}s ({estimated_time/60:.1f} minutes)")

if estimated_time < 60:
    print(f"   ✅ RAPIDE - Moins d'une minute !")
elif estimated_time < 300:
    print(f"   ✅ ACCEPTABLE - Quelques minutes")
else:
    print(f"   ⚠️ LENT - Plus de 5 minutes")

print("\n" + "=" * 70)
print("✅ TEST TERMINÉ")
print("=" * 70)
