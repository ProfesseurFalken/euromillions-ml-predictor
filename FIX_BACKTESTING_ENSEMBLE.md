# Correctif Backtesting - Méthodes Ensemble et Advanced Hybrid

**Date:** 17 novembre 2025  
**Statut:** ✅ Résolu et testé

## Problème identifié

Lorsque l'utilisateur cochait les cases "ensemble" et "advanced_hybrid" dans le backtesting, aucun résultat n'apparaissait pour ces méthodes.

## Causes racines

### 1. Incompatibilité de structure de données
- **`_generate_tickets_fast()`** retourne : `{'main': [...], 'stars': [...]}`
- **`suggest_tickets_ui()`** retourne : `{'balls': [...], 'stars': [...]}`
- Le code du backtesting utilisait uniquement `ticket['main']`, causant une erreur avec les tickets d'ensemble

### 2. Méthodes ensemble non implémentées dans _generate_tickets_fast()
- `_generate_tickets_fast()` est optimisée pour la vitesse avec des probabilités précalculées
- Les méthodes `ensemble` et `advanced_hybrid` nécessitent de charger **plusieurs modèles ML différents**
- La fonction rapide utilisait simplement le même code que `hybrid` pour ces méthodes
- Résultat : pas de vraie différence entre hybrid, ensemble et advanced_hybrid

## Solutions appliquées

### 1. Normalisation de la structure des tickets (ligne ~336)
```python
# Avant:
main_matches = len(set(ticket['main']) & set(actual_main))

# Après:
ticket_main = ticket.get('main') or ticket.get('balls', [])
ticket_stars = ticket.get('stars', [])
main_matches = len(set(ticket_main) & set(actual_main))
```

Cette modification permet au backtesting d'accepter les deux structures de données.

### 2. Routage vers les vraies fonctions ensemble (ligne ~309)
```python
# Pour ensemble et advanced_hybrid, utiliser toujours suggest_tickets_ui()
# car ces méthodes nécessitent de charger plusieurs modèles différents
if method in ["ensemble", "advanced_hybrid"]:
    tickets = suggest_tickets_ui(
        n=n_tickets,
        method=method,
        seed=seed,
        use_ensemble=True
    )
elif main_scores and star_scores:
    # Utiliser les probabilités précalculées pour les autres méthodes
    tickets = _generate_tickets_fast(n_tickets, method, seed, main_scores, star_scores)
```

Maintenant, les méthodes `ensemble` et `advanced_hybrid` utilisent leurs implémentations réelles via `suggest_tickets_ui()`.

## Impact sur les performances

### Méthodes rapides (topk, hybrid, random)
- ✅ **Très rapide** : ~0.001 seconde par ticket
- Utilise les probabilités précalculées
- Backtesting complet (50 seeds × 50 draws × 20 tickets) : **~2-5 minutes**

### Méthodes ensemble (ensemble, advanced_hybrid)
- ⚠️ **Plus lent** : ~1-2 secondes par ticket
- Doit charger et combiner plusieurs modèles ML
- Backtesting complet (50 seeds × 50 draws × 20 tickets) : **~30-90 minutes**

### Recommandations d'utilisation

1. **Pour trouver la meilleure configuration rapidement:**
   - Utilisez uniquement `topk`, `hybrid`, `random`
   - Mode "Rapide" : 10 seeds, 20 draws
   - Durée : ~30 secondes

2. **Pour comparer ensemble vs autres méthodes:**
   - Mode "Personnalisé" avec moins de seeds (5-10)
   - 20 tirages maximum
   - Durée : ~5-15 minutes

3. **Pour un backtesting complet avec ensemble:**
   - Lancez pendant la nuit ou une pause
   - Attendez-vous à 1-2 heures pour des tests complets

## Tests de validation

### Test 1: Génération de tickets ✅
```
topk               : ✅ 10/10 tickets
hybrid             : ✅ 10/10 tickets  
ensemble           : ✅ 10/10 tickets
advanced_hybrid    : ✅ 10/10 tickets
```

### Test 2: Structure des données ✅
- Normalisation réussie pour les deux formats
- `{'main': [...]}` et `{'balls': [...]}` acceptés

### Test 3: Backtesting complet ✅
- 2 seeds × 4 méthodes × 3 tirages × 5 tickets = 120 tickets
- Tous générés avec succès
- Aucune erreur de structure

## Fichiers modifiés

### ui/streamlit_app.py
- **Ligne ~187** : Commentaire amélioré sur les limites de `_generate_tickets_fast()` pour ensemble
- **Ligne ~309** : Routage vers `suggest_tickets_ui()` pour ensemble et advanced_hybrid
- **Ligne ~336** : Normalisation de la structure des tickets

## Comment tester

### Dans l'interface Streamlit
1. Ouvrir http://localhost:8501
2. Aller dans l'onglet "Backtesting"
3. Sélectionner "Mode Rapide"
4. Cocher "ensemble" et "advanced_hybrid"
5. Cliquer "Lancer le backtesting"
6. **Résultat attendu** : Les deux méthodes apparaissent dans les résultats avec des scores

### En ligne de commande
```bash
python test_backtesting_complet.py
```

Devrait afficher :
```
✅ TOUS LES TESTS RÉUSSIS - Le backtesting devrait fonctionner
```

## FAQ

**Q: Pourquoi ensemble est-il si lent ?**  
R: Les modèles d'ensemble combinent plusieurs algorithmes ML différents (Random Forest, XGBoost, etc.). Chaque génération de ticket nécessite de charger et exécuter tous ces modèles, ce qui prend du temps.

**Q: Est-ce que ensemble donne de meilleurs résultats ?**  
R: En théorie oui, car il combine plusieurs stratégies. En pratique, vous devez lancer le backtesting pour comparer. Souvent, la différence est marginale (quelques points de score).

**Q: Puis-je accélérer le backtesting pour ensemble ?**  
R: Pas sans perdre la fonctionnalité. L'optimisation `_generate_tickets_fast()` ne peut pas vraiment implémenter ensemble car cela nécessite de charger dynamiquement plusieurs modèles. C'est un compromis vitesse vs fonctionnalité.

**Q: Que faire si le backtesting semble bloqué ?**  
R: C'est normal si vous testez ensemble/advanced_hybrid. Regardez les logs dans le terminal - vous devriez voir des messages "Generating tickets with method 'ensemble'". Patience !

## Prochaines étapes

- ✅ Correction appliquée
- ✅ Tests validés
- ⏳ Mettre à jour sur GitHub
- ⏳ Tester en production avec un backtesting réel
