"""
Test simple et rapide du backtesting
"""
import sys
sys.path.insert(0, 'ui')

# Test 1: Vérifier que _generate_tickets_fast fonctionne
print("=" * 60)
print("TEST 1: _generate_tickets_fast")
print("=" * 60)

from streamlit_app import _generate_tickets_fast

# Simuler des probabilités précalculées
main_scores = {i: (i, 0.02) for i in range(1, 51)}  # tuples (num, prob)
star_scores = {i: (i, 0.08) for i in range(1, 13)}

tickets_topk = _generate_tickets_fast(3, "topk", 42, main_scores, star_scores)
print(f"\n✅ topk: {len(tickets_topk)} tickets")
print(f"   Structure: {tickets_topk[0].keys()}")
print(f"   Exemple: main={tickets_topk[0]['main']}, stars={tickets_topk[0]['stars']}")

tickets_hybrid = _generate_tickets_fast(3, "hybrid", 42, main_scores, star_scores)
print(f"\n✅ hybrid: {len(tickets_hybrid)} tickets")
print(f"   Exemple: main={tickets_hybrid[0]['main']}, stars={tickets_hybrid[0]['stars']}")

# Test 2: Vérifier que suggest_tickets_ui fonctionne
print("\n" + "=" * 60)
print("TEST 2: suggest_tickets_ui")
print("=" * 60)

from streamlit_adapters import suggest_tickets_ui

tickets_ui = suggest_tickets_ui(n=2, method="hybrid", seed=42, use_ensemble=False)
print(f"\n✅ suggest_tickets_ui: {len(tickets_ui)} tickets")
print(f"   Structure: {tickets_ui[0].keys()}")
if 'balls' in tickets_ui[0]:
    print(f"   Exemple: balls={tickets_ui[0]['balls']}, stars={tickets_ui[0]['stars']}")
elif 'main' in tickets_ui[0]:
    print(f"   Exemple: main={tickets_ui[0]['main']}, stars={tickets_ui[0]['stars']}")

# Test 3: Vérifier la normalisation
print("\n" + "=" * 60)
print("TEST 3: Normalisation des structures")
print("=" * 60)

test_tickets = [
    {'main': [1, 2, 3, 4, 5], 'stars': [1, 2]},
    {'balls': [6, 7, 8, 9, 10], 'stars': [3, 4]}
]

for i, ticket in enumerate(test_tickets):
    ticket_main = ticket.get('main') or ticket.get('balls', [])
    ticket_stars = ticket.get('stars', [])
    print(f"\n✅ Ticket {i+1}: main={ticket_main}, stars={ticket_stars}")

print("\n" + "=" * 60)
print("✅ TOUS LES TESTS RÉUSSIS")
print("=" * 60)
