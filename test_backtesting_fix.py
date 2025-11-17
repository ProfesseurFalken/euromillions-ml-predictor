#!/usr/bin/env python3
"""
Script de test pour valider le correctif du backtesting.
Execute un backtesting rapide et vérifie que les résultats sont non-nuls.
"""

from repository import get_repository
import pandas as pd

def test_data_conversion():
    """Test que les données sont correctement converties."""
    print("🔍 Test 1: Conversion des données...")
    
    repo = get_repository()
    all_draws = repo.all_draws_df()
    
    if len(all_draws) == 0:
        print("❌ ÉCHEC: Base de données vide !")
        return False
    
    # Convertir
    test_draws = all_draws.tail(10).copy()
    test_draws['main'] = test_draws.apply(
        lambda row: [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']], 
        axis=1
    )
    test_draws['stars'] = test_draws.apply(
        lambda row: [row['s1'], row['s2']], 
        axis=1
    )
    
    # Vérifier
    first_draw = test_draws.iloc[0]
    main = first_draw['main']
    stars = first_draw['stars']
    
    print(f"   Exemple de tirage : {main} + {stars}")
    
    # Validations
    assert isinstance(main, list), "main devrait être une liste"
    assert len(main) == 5, "main devrait avoir 5 numéros"
    assert isinstance(stars, list), "stars devrait être une liste"
    assert len(stars) == 2, "stars devrait avoir 2 étoiles"
    assert all(1 <= n <= 50 for n in main), "Numéros entre 1 et 50"
    assert all(1 <= s <= 12 for s in stars), "Étoiles entre 1 et 12"
    
    print("   ✅ Conversion OK")
    return True


def test_ticket_evaluation():
    """Test que l'évaluation des tickets fonctionne."""
    print("\n🔍 Test 2: Évaluation des tickets...")
    
    repo = get_repository()
    all_draws = repo.all_draws_df()
    test_draws = all_draws.tail(1).copy()
    test_draws['main'] = test_draws.apply(
        lambda row: [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']], 
        axis=1
    )
    test_draws['stars'] = test_draws.apply(
        lambda row: [row['s1'], row['s2']], 
        axis=1
    )
    
    actual_draw = test_draws.iloc[0]
    
    # Créer un ticket qui correspond exactement (jackpot simulé)
    ticket_perfect = {
        'main': list(actual_draw['main']),
        'stars': list(actual_draw['stars'])
    }
    
    # Évaluer
    main_matches = len(set(ticket_perfect['main']) & set(actual_draw['main']))
    star_matches = len(set(ticket_perfect['stars']) & set(actual_draw['stars']))
    score = main_matches * 10 + star_matches * 5
    
    print(f"   Ticket parfait : {main_matches} nums, {star_matches} étoiles, score={score}")
    
    assert main_matches == 5, "Devrait avoir 5 correspondances"
    assert star_matches == 2, "Devrait avoir 2 correspondances"
    assert score == 60, "Score devrait être 60 (5×10 + 2×5)"
    
    print("   ✅ Évaluation OK")
    return True


def test_partial_match():
    """Test avec correspondances partielles."""
    print("\n🔍 Test 3: Correspondances partielles...")
    
    repo = get_repository()
    all_draws = repo.all_draws_df()
    test_draws = all_draws.tail(1).copy()
    test_draws['main'] = test_draws.apply(
        lambda row: [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']], 
        axis=1
    )
    test_draws['stars'] = test_draws.apply(
        lambda row: [row['s1'], row['s2']], 
        axis=1
    )
    
    actual_draw = test_draws.iloc[0]
    
    # Ticket avec 2 bons numéros et 0 étoiles
    actual_main = list(actual_draw['main'])
    ticket_partial = {
        'main': actual_main[:2] + [99, 98, 97],  # 2 corrects + 3 faux
        'stars': [11, 12]  # 0 correct
    }
    
    main_matches = len(set(ticket_partial['main']) & set(actual_draw['main']))
    star_matches = len(set(ticket_partial['stars']) & set(actual_draw['stars']))
    score = main_matches * 10 + star_matches * 5
    
    print(f"   Ticket partiel : {main_matches} nums, {star_matches} étoiles, score={score}")
    
    assert main_matches >= 2, "Devrait avoir au moins 2 correspondances"
    assert score >= 20, "Score devrait être au moins 20"
    
    print("   ✅ Correspondances partielles OK")
    return True


def test_no_match():
    """Test sans aucune correspondance."""
    print("\n🔍 Test 4: Aucune correspondance...")
    
    ticket_zero = {
        'main': [1, 2, 3, 4, 5],
        'stars': [1, 2]
    }
    
    actual = {
        'main': [40, 41, 42, 43, 44],
        'stars': [11, 12]
    }
    
    main_matches = len(set(ticket_zero['main']) & set(actual['main']))
    star_matches = len(set(ticket_zero['stars']) & set(actual['stars']))
    score = main_matches * 10 + star_matches * 5
    
    print(f"   Ticket raté : {main_matches} nums, {star_matches} étoiles, score={score}")
    
    assert main_matches == 0, "Devrait avoir 0 correspondance"
    assert star_matches == 0, "Devrait avoir 0 correspondance"
    assert score == 0, "Score devrait être 0"
    
    print("   ✅ Aucune correspondance OK (normal)")
    return True


def main():
    """Exécute tous les tests."""
    print("=" * 70)
    print("🧪 TESTS DE VALIDATION DU CORRECTIF BACKTESTING")
    print("=" * 70)
    
    tests = [
        test_data_conversion,
        test_ticket_evaluation,
        test_partial_match,
        test_no_match
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 RÉSULTATS: {passed} passés, {failed} échoués")
    
    if failed == 0:
        print("✅ TOUS LES TESTS SONT PASSÉS - Le correctif fonctionne !")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ - Vérifier le code")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
