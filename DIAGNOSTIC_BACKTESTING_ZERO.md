# 🔍 Diagnostic - Résultats Backtesting à ZÉRO

## 🚨 Problème Constaté

Tous les résultats du backtesting affichent **0** dans toutes les colonnes :

| Colonne | Valeur Attendue | Valeur Obtenue |
|---------|----------------|----------------|
| Score Moy | 5-20 | **0** ❌ |
| Nums Moy | 0.5-2.5 | **0** ❌ |
| Étoiles Moy | 0.2-0.8 | **0** ❌ |
| Meilleur Nums | 2-5 | **0** ❌ |
| Meilleur Étoiles | 0-2 | **0** ❌ |
| Taux Gain % | 10-40% | **0** ❌ |

**Durée de l'exécution :** Plusieurs heures  
**Résultat :** Aucune correspondance trouvée !

---

## 🔬 Analyse de la Cause

### Cause Racine Identifiée

**Problème :** Incompatibilité de structure de données entre tickets générés et tirages historiques

#### Code bugué (v2.0 initial) :

```python
# Dans run_backtesting()
test_draws = all_draws.tail(n_draws)  # DataFrame brut

for idx, actual_draw in test_draws.iterrows():
    tickets = _generate_tickets_fast(...)
    
    for ticket in tickets:
        # ❌ ERREUR ICI
        main_matches = len(set(ticket['main']) & set(actual_draw['main']))
        star_matches = len(set(ticket['stars']) & set(actual_draw['stars']))
```

**Pourquoi ça échoue ?**

1. `ticket['main']` retourne `[1, 5, 12, 23, 45]` ✅
2. `actual_draw['main']` cherche une colonne **'main'** qui **n'existe pas** ❌

**Structure réelle du DataFrame :**
```python
# Colonnes dans repository.py all_draws_df():
['draw_id', 'draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2', 'jackpot', ...]

# actual_draw est une Series pandas avec :
actual_draw['n1'] = 5
actual_draw['n2'] = 12
actual_draw['n3'] = 23
...
# PAS DE actual_draw['main'] !
```

**Résultat :**
```python
set(actual_draw['main'])  # KeyError: 'main'
# Exception attrapée par try/except
# continue → passe au suivant
# Aucun score calculé → tout reste à 0
```

### Pourquoi l'exception était silencieuse ?

Code original :
```python
try:
    # Génération et évaluation
    ...
except Exception as e:
    continue  # ❌ Ignore l'erreur sans rien dire
```

**Conséquence :**
- Chaque évaluation échouait
- `continue` passait au tirage suivant
- Aucun compteur incrémenté
- Résultats finaux = tous à zéro
- **Utilisateur attend plusieurs heures pour rien**

---

## ✅ Solution Implémentée

### Correctif 1 : Conversion des données

```python
# AVANT (bugué)
test_draws = all_draws.tail(n_draws)

# APRÈS (corrigé)
test_draws = all_draws.tail(n_draws).copy()
test_draws['main'] = test_draws.apply(
    lambda row: [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']], 
    axis=1
)
test_draws['stars'] = test_draws.apply(
    lambda row: [row['s1'], row['s2']], 
    axis=1
)
```

**Effet :**
- Crée les colonnes 'main' et 'stars'
- `actual_draw['main']` retourne maintenant `[5, 12, 23, 34, 45]` ✅
- L'évaluation peut se faire correctement

### Correctif 2 : Logging des erreurs

```python
# AVANT (silencieux)
except Exception as e:
    continue

# APRÈS (informatif)
except Exception as e:
    import traceback
    error_msg = f"Erreur seed={seed}, method={method}: {str(e)}"
    st.warning(error_msg)
    print(f"{error_msg}\n{traceback.format_exc()}")
    continue
```

**Effet :**
- Les erreurs sont maintenant visibles
- L'utilisateur sait immédiatement si quelque chose ne va pas
- Diagnostic rapide des problèmes

### Correctif 3 : Vérification des données

```python
# Nouveau : validation au démarrage
if len(test_draws) == 0:
    st.error("❌ Aucun tirage trouvé dans la base de données !")
    return pd.DataFrame()

st.info(f"📊 {len(test_draws)} tirages historiques chargés")

# Afficher un exemple
first_draw = test_draws.iloc[0]
st.text(f"Exemple: {first_draw['main']} + {first_draw['stars']}")
```

**Effet :**
- Détecte immédiatement si la base de données est vide
- Montre un exemple de tirage pour vérification visuelle
- Rassure l'utilisateur que les données sont bien chargées

---

## 🎯 Tests de Validation

### Test 1 : Données correctement converties

```python
# Vérifier la structure
repo = get_repository()
df = repo.all_draws_df()
test_draws = df.tail(10).copy()

# Avant
print(test_draws.columns)
# ['draw_id', 'draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2', ...]

# Après conversion
test_draws['main'] = test_draws.apply(lambda r: [r['n1'], r['n2'], r['n3'], r['n4'], r['n5']], axis=1)
test_draws['stars'] = test_draws.apply(lambda r: [r['s1'], r['s2']], axis=1)

print(test_draws['main'].iloc[0])
# [5, 12, 23, 34, 45] ✅

print(test_draws['stars'].iloc[0])
# [3, 9] ✅
```

### Test 2 : Évaluation fonctionnelle

```python
# Simuler un ticket
ticket = {'main': [5, 12, 23, 34, 45], 'stars': [3, 9]}

# Simuler un tirage réel
actual_draw = test_draws.iloc[0]

# Évaluation
main_matches = len(set(ticket['main']) & set(actual_draw['main']))
star_matches = len(set(ticket['stars']) & set(actual_draw['stars']))

print(f"Correspondances : {main_matches} nums, {star_matches} étoiles")
# Correspondances : 5 nums, 2 étoiles ✅ (jackpot !)
```

### Test 3 : Score non-nul

```python
# Lancer backtesting corrigé
results = run_backtesting(
    seeds=[42],
    methods=['topk'],
    n_draws=10,
    n_tickets=5
)

# Vérifier résultats
assert results['avg_score'].iloc[0] > 0, "Score devrait être > 0"
assert results['avg_main'].iloc[0] > 0, "Nums moyens devrait être > 0"
print("✅ Test réussi : résultats non-nuls")
```

---

## 📊 Résultats Attendus (Après Correctif)

### Exemple de résultats normaux :

| Rang | Graine | Méthode | Score Moy | Nums Moy | Étoiles Moy | Meilleur Nums | Meilleur Étoiles | Taux Gain % |
|------|--------|---------|-----------|----------|-------------|---------------|------------------|-------------|
| 1 | 42 | hybrid | **12.5** | **1.2** | **0.5** | **3** | **2** | **25%** |
| 2 | 87 | random | **11.8** | **1.1** | **0.48** | **3** | **1** | **23%** |
| 3 | 23 | topk | **11.2** | **1.15** | **0.42** | **2** | **2** | **22%** |

**Indicateurs de santé :**
- ✅ Score Moy : 8-20 (normal)
- ✅ Nums Moy : 0.8-2.0 (attendu statistiquement)
- ✅ Étoiles Moy : 0.3-0.8 (cohérent)
- ✅ Taux Gain : 15-40% (tickets avec au moins 2 nums ou 1 étoile)

**Interprétation :**
- Meilleur configuration : seed=42, méthode=hybrid
- Obtient en moyenne 1.2 numéros corrects sur 5
- 25% des tickets ont au moins un petit gain

---

## 🚀 Actions Correctives Déployées

### Fichiers modifiés :

1. **`ui/streamlit_app.py`**
   - Ajout conversion `n1-n5 → main`, `s1-s2 → stars`
   - Ajout logging des erreurs
   - Ajout validation des données
   - Ajout affichage exemple de tirage

2. **`DIAGNOSTIC_BACKTESTING_ZERO.md`** (ce document)
   - Documentation du problème
   - Explication technique
   - Guide de prévention future

### Prochains tests à faire :

1. **Relancer le backtesting** avec Mode Rapide (10 graines)
   - Durée : ~30 secondes
   - Vérifier que les résultats sont **NON-NULS**

2. **Vérifier les logs**
   - Aucun `st.warning()` ne devrait apparaître
   - Message "📊 X tirages historiques chargés" doit s'afficher
   - Exemple de tirage doit être visible

3. **Analyser le TOP 10**
   - Scores entre 8 et 20
   - Taux de gain entre 15% et 40%
   - Graines variées dans le top

---

## 🔒 Prévention Future

### Checklist avant déploiement :

- [ ] Toujours vérifier la structure du DataFrame avec `.columns`
- [ ] Ne JAMAIS utiliser `except: pass` ou `except: continue` sans logging
- [ ] Ajouter des assertions de validation de données
- [ ] Tester avec un petit échantillon avant le run complet
- [ ] Afficher des exemples de données au début

### Code review pattern :

```python
# ❌ MAUVAIS
try:
    result = process(data)
except:
    pass  # Erreur silencieuse !

# ✅ BON
try:
    result = process(data)
except Exception as e:
    logger.error(f"Erreur: {e}")
    st.warning(f"Problème détecté: {e}")
    raise  # Ou continue avec logging
```

---

## 📝 Résumé Exécutif

**Problème :** Backtesting retournait 0 partout après plusieurs heures  
**Cause :** Colonnes 'main'/'stars' inexistantes dans le DataFrame  
**Impact :** Toutes les évaluations échouaient silencieusement  
**Solution :** Conversion explicite `n1-n5 → main`, `s1-s2 → stars`  
**Statut :** ✅ Corrigé et documenté  
**Prochaine étape :** Tester avec l'application relancée  

---

**Note :** Ce bug souligne l'importance de :
1. Ne jamais ignorer les exceptions silencieusement
2. Valider la structure des données au plus tôt
3. Afficher des exemples de données pour vérification visuelle
4. Tester sur petit échantillon avant run massif
