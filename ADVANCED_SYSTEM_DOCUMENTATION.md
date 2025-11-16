# 🌟 Système Avancé de Prédiction EuroMillions

## Vue d'Ensemble

Ce système révolutionnaire collecte et analyse des **données externes multi-sources** pour rechercher des corrélations avec les tirages EuroMillions. Il part du principe que des patterns mathématiques ou environnementaux pourraient influencer les tirages.

---

## 🎯 Philosophie du Système

### Hypothèse de Travail

> "Le hasard apparent pourrait découler de facteurs mesurables que nous n'avons pas encore identifiés."

Le système explore trois axes principaux :

1. **Facteurs Environnementaux** : Astronomie, météo, géophysique
2. **Patterns Mathématiques** : Théorie des nombres, séquences
3. **Dynamiques Temporelles** : Cycles cachés, mémoire temporelle

---

## 📦 Architecture du Système

### 1. Collecteurs de Données (`collectors/`)

#### 🌙 Collecteur Astronomique (`astronomical_data.py`)

Collecte les données astronomiques au moment du tirage (21h05 CET, Paris) :

- **Phase lunaire** : Pourcentage, illumination, âge de la lune
- **Données solaires** : Lever/coucher, durée du jour
- **Activité solaire** : Indice Kp (activité géomagnétique)
- **Positions planétaires** : Coordonnées écliptiques (à implémenter)

**APIs utilisées** :
- `api.sunrise-sunset.org` (gratuite)
- `api.farmsense.net/v1/moonphases/` (gratuite)
- NOAA Space Weather (gratuite)

**Exemple d'utilisation** :
```python
from collectors.astronomical_data import get_astronomical_data
from datetime import datetime

date_tirage = datetime(2024, 10, 11, 21, 5)
data = get_astronomical_data(date_tirage)

print(f"Phase lunaire: {data['moon']['phase_name']}")
print(f"Illumination: {data['moon']['illumination']}%")
```

#### 🌦️ Collecteur Météorologique (`weather_data.py`)

Collecte les conditions météo à Paris à 21h05 :

- **Température** : Température à 2m, température ressentie
- **Humidité** : Humidité relative, point de rosée
- **Pression** : Pression atmosphérique, tendance
- **Vent** : Vitesse, direction, rafales
- **Couverture nuageuse** : Pourcentage

**API utilisée** :
- Open-Meteo Archive API (gratuite, données depuis 1940)

**Exemple d'utilisation** :
```python
from collectors.weather_data import get_weather_data

data = get_weather_data(date_tirage)
weather = data['weather']

print(f"Température: {weather['temperature_celsius']}°C")
print(f"Pression: {weather['pressure_hpa']} hPa")
print(f"Tendance: {weather['pressure_tendency']}")
```

#### 🌍 Collecteur Géophysique (`geophysical_data.py`)

Collecte les données géophysiques globales :

- **Indice Kp** : Activité géomagnétique (0-9)
- **Flux solaire F10.7** : Indicateur d'activité solaire
- **Activité sismique** : Séismes dans un rayon de 500 km
- **Champ magnétique** : Variations du champ terrestre

**APIs utilisées** :
- NOAA SWPC (gratuite)
- USGS Earthquake API (gratuite)

**Exemple d'utilisation** :
```python
from collectors.geophysical_data import get_geophysical_data

data = get_geophysical_data(date_tirage)

print(f"Indice Kp: {data['geomagnetic']['kp_average']}")
print(f"Activité: {data['geomagnetic']['activity_level']}")
print(f"Séismes: {data['seismic']['earthquake_count']}")
```

---

### 2. Analyseurs Mathématiques (`analyzers/`)

#### 🔢 Analyseur de Théorie des Nombres (`number_theory.py`)

Analyse les propriétés mathématiques des tirages :

**Analyses effectuées** :
- **Nombres premiers** : Comptage, pourcentage
- **Séquence de Fibonacci** : Détection (1, 1, 2, 3, 5, 8, 13, 21, 34...)
- **Golden Ratio φ** : Ratios entre numéros consécutifs
- **Patterns modulo N** : Cycles cachés (mod 2, 3, 5, 7, 11, 13)
- **Suites arithmétiques/géométriques** : Détection de progressions
- **Parité** : Distribution pairs/impairs
- **Divisibilité** : Par 3, 5, 7
- **Sommes et produits** : Propriétés algébriques

**Exemple d'utilisation** :
```python
from analyzers.number_theory import analyze_draw_number_theory

numbers = [3, 13, 21, 34, 42]  # Contient beaucoup de Fibonacci!
stars = [5, 11]  # Nombres premiers

analysis = analyze_draw_number_theory(numbers, stars)

print(f"Fibonacci: {analysis['fibonacci']['count']}/5")
print(f"Nombres premiers: {analysis['primes']['count']}/5")
print(f"Golden ratio: {analysis['golden_ratio']['is_near_golden']}")
```

#### 📈 Analyseur Temporel Avancé (`temporal_analysis.py`)

Recherche de cycles et patterns temporels cachés :

**Analyses effectuées** :

1. **Transformée de Fourier** : Détection de cycles périodiques
   - Périodes dominantes
   - Puissance spectrale
   - Fréquences cachées

2. **Analyse en Ondelettes** : Patterns multi-échelle
   - Décomposition par niveaux
   - Distribution d'énergie
   - Détection de ruptures

3. **Théorie du Chaos** :
   - Entropie de Shannon : Mesure du désordre
   - Approximate Entropy (ApEn) : Régularité
   - Exposant de Hurst : Persistence/anti-persistence
   - Exposant de Lyapunov : Détection du chaos

4. **Autocorrélation** : Mémoire temporelle
   - Détection de patterns répétitifs
   - Lag significatifs

**Exemple d'utilisation** :
```python
from analyzers.temporal_analysis import TemporalAnalyzer
import numpy as np

analyzer = TemporalAnalyzer()

# Analyser la fréquence d'apparition du numéro 7
series = np.array([1, 0, 0, 1, 0, 1, 0, 0, ...])  # 1=sorti, 0=absent

fourier = analyzer.fourier_analysis(series)
print(f"Périodes dominantes: {fourier['dominant_periods']}")

chaos = analyzer.chaos_analysis(series)
print(f"Exposant de Hurst: {chaos['hurst_exponent']}")
print(f"Interprétation: {chaos['hurst_interpretation']}")
```

---

### 3. Moteur de Corrélation (`correlation_engine.py`)

Le cœur du système : **corrèle toutes les sources de données**.

#### Fonctionnalités

1. **Enrichissement des données** :
   - Pour chaque tirage historique
   - Collecte toutes les données externes
   - Ajoute les analyses mathématiques
   - Crée un dataset unifié

2. **Calcul des corrélations** :
   - Corrélation de Pearson (linéaire)
   - Corrélation de Spearman (monotone)
   - Tests de significativité statistique
   - Identification des patterns

3. **Variables testées** :
   - **Externes** : Phase lunaire, météo, géomagnétisme, séismes
   - **Tirages** : Sommes, nombres premiers, Fibonacci, parité

**Exemple d'utilisation** :
```python
from correlation_engine import build_and_analyze_enriched_dataset
import pandas as pd

# Charger vos tirages historiques
draws_df = pd.read_csv('euromillions.csv')

# Enrichir et analyser
enriched_df, correlations = build_and_analyze_enriched_dataset(draws_df)

# Afficher les corrélations significatives
for corr in correlations['significant_correlations']:
    print(f"{corr['external_factor']} vs {corr['draw_variable']}")
    print(f"  Pearson: r={corr['pearson_r']:.3f}")
    print(f"  Spearman: r={corr['spearman_r']:.3f}")
```

---

## 🚀 Installation

### 1. Dépendances de Base

Déjà présentes dans `requirements.txt` :
```bash
numpy, pandas, scikit-learn, lightgbm, requests, beautifulsoup4
```

### 2. Dépendances Avancées

Installer les dépendances supplémentaires :

```powershell
# Windows PowerShell
.\.venv\Scripts\activate
pip install -r requirements_advanced.txt
```

```bash
# Linux/Mac
source .venv/bin/activate
pip install -r requirements_advanced.txt
```

**Contenu de `requirements_advanced.txt`** :
- `PyWavelets==1.4.1` : Analyse en ondelettes
- `scipy==1.11.4` : Analyses scientifiques
- `statsmodels==0.14.1` : Séries temporelles
- `plotly==5.18.0` : Visualisations interactives

---

## 📊 Utilisation Complète

### Scénario 1 : Test Rapide

```powershell
# Tester tout le système
python test_advanced_system.py
```

Ce script :
1. ✅ Teste tous les collecteurs
2. ✅ Teste tous les analyseurs
3. ✅ Crée un dataset enrichi de test
4. ✅ Calcule les corrélations
5. ✅ Génère un rapport JSON

### Scénario 2 : Analyse d'un Tirage Unique

```python
from datetime import datetime
from collectors import get_astronomical_data, get_weather_data, get_geophysical_data
from analyzers import analyze_draw_number_theory

# Tirage du vendredi 11 octobre 2024
date = datetime(2024, 10, 11, 21, 5)
numbers = [7, 18, 25, 32, 44]
stars = [3, 9]

# Collecter toutes les données
astro = get_astronomical_data(date)
weather = get_weather_data(date)
geo = get_geophysical_data(date)
math = analyze_draw_number_theory(numbers, stars)

# Afficher
print(f"🌙 Lune: {astro['moon']['phase_name']}, {astro['moon']['illumination']}%")
print(f"🌡️ Météo: {weather['weather']['temperature_celsius']}°C, {weather['weather']['pressure_hpa']} hPa")
print(f"🌍 Géomagnétisme: Kp={geo['geomagnetic']['kp_average']}")
print(f"🔢 Maths: {math['primes']['count']} premiers, {math['fibonacci']['count']} Fibonacci")
```

### Scénario 3 : Analyse Historique Complète

```python
from repository import get_repository
from correlation_engine import build_and_analyze_enriched_dataset

# Charger tous les tirages historiques
repo = get_repository()
draws_df = repo.all_draws_df()

print(f"Analyse de {len(draws_df)} tirages historiques...")

# Construire le dataset enrichi (⚠️ ATTENTION: peut prendre du temps!)
enriched_df, correlations = build_and_analyze_enriched_dataset(draws_df)

# Les données sont sauvegardées dans:
# - data/correlations/enriched_draws.csv
# - data/correlations/correlations.json

print(f"\n📊 Corrélations trouvées: {correlations['significant_count']}")
print("\nTop 5 corrélations:")
for i, corr in enumerate(correlations['significant_correlations'][:5], 1):
    print(f"{i}. {corr['external_factor']} ↔ {corr['draw_variable']}")
    print(f"   r_pearson={corr['pearson_r']:.3f}, r_spearman={corr['spearman_r']:.3f}")
```

---

## 📈 Interprétation des Résultats

### Corrélations

**Signification des valeurs r** :
- `|r| < 0.2` : Corrélation faible/négligeable
- `0.2 ≤ |r| < 0.5` : Corrélation modérée
- `0.5 ≤ |r| < 0.8` : Corrélation forte
- `|r| ≥ 0.8` : Corrélation très forte

**p-value** :
- `p < 0.05` : Statistiquement significatif (95% de confiance)
- `p < 0.01` : Très significatif (99% de confiance)
- `p < 0.001` : Extrêmement significatif (99.9% de confiance)

⚠️ **Important** : Corrélation ≠ Causalité !

### Exposant de Hurst

- `H < 0.5` : **Anti-persistant** (mean-reverting)
  - Le système tend à retourner à la moyenne
  - Après une valeur élevée, une valeur basse est plus probable
  
- `H ≈ 0.5` : **Marche aléatoire**
  - Pas de mémoire temporelle
  - Chaque tirage est indépendant
  
- `H > 0.5` : **Persistant** (trending)
  - Le système a de la mémoire
  - Une tendance actuelle tend à continuer

### Entropie de Shannon

- **Basse** (< 2) : Système prévisible, peu de désordre
- **Moyenne** (2-4) : Système modérément aléatoire
- **Élevée** (> 4) : Système très aléatoire, imprévisible

---

## 🔬 Cas d'Usage Avancés

### 1. Détecter un Cycle Lunaire

```python
from analyzers.temporal_analysis import TemporalAnalyzer
from repository import get_repository
import pandas as pd

repo = get_repository()
draws_df = repo.all_draws_df()

# Créer une série temporelle de la somme des numéros
sums = draws_df.apply(lambda row: row['n1']+row['n2']+row['n3']+row['n4']+row['n5'], axis=1)

analyzer = TemporalAnalyzer()
fourier = analyzer.fourier_analysis(sums.values)

# Chercher une période proche du cycle lunaire (29.5 jours)
# Diviser par 3.5 (mardi + vendredi = ~2 tirages par semaine)
lunar_period_in_draws = 29.5 / 3.5  # ≈ 8.4 tirages

for period in fourier['dominant_periods']:
    if 7 < period < 10:
        print(f"⚠️ Période détectée proche du cycle lunaire: {period:.1f} tirages")
```

### 2. Analyser l'Impact des Tempêtes Géomagnétiques

```python
from correlation_engine import MultiSourceCorrelator
from repository import get_repository

repo = get_repository()
draws_df = repo.all_draws_df()

correlator = MultiSourceCorrelator()
enriched_df = correlator.build_enriched_dataset(draws_df)

# Filtrer les tirages pendant tempêtes géomagnétiques (Kp > 5)
storms = enriched_df[enriched_df['kp_index'] > 5]

if len(storms) > 0:
    print(f"Tirages pendant tempêtes: {len(storms)}")
    print(f"Somme moyenne: {storms['sum_numbers'].mean():.1f}")
    print(f"Somme normale: {enriched_df['sum_numbers'].mean():.1f}")
    print(f"Différence: {storms['sum_numbers'].mean() - enriched_df['sum_numbers'].mean():.1f}")
```

---

## ⚠️ Avertissements et Limites

### Limites Scientifiques

1. **Nombre de tirages limité** : ~1000 tirages sur 20 ans
   - Difficulté à détecter cycles longs
   - Risque de faux positifs (problème des comparaisons multiples)

2. **Indépendance des tirages** :
   - Les machines modernes sont conçues pour être aléatoires
   - Audits réguliers garantissent l'absence de biais

3. **Correction de Bonferroni** :
   - Avec 100+ tests de corrélation, ~5 seront "significatifs" par hasard
   - Appliquer des corrections statistiques strictes

### Considérations Éthiques

- ⚠️ **Ce système ne peut PAS prédire les tirages** avec certitude
- 🎰 La loterie reste un jeu de hasard
- 💰 Ne jamais miser plus que ce que vous pouvez perdre
- 🧠 Utiliser ce système à des fins **éducatives** et de recherche

---

## 🎓 Apprentissages Possibles

Même si aucune corrélation n'est trouvée (ce qui est le plus probable), le système démontre :

1. **Collecte de données multi-sources** : APIs, parsing, cache
2. **Analyse scientifique rigoureuse** : Statistiques, théorie du chaos
3. **Programmation avancée** : Architecture modulaire, POO
4. **Pensée critique** : Distinguer corrélation et causalité

---

## 📚 Références Scientifiques

### Théorie des Nombres
- "An Introduction to the Theory of Numbers" - Hardy & Wright
- Suite de Fibonacci dans la nature

### Analyse Temporelle
- "Nonlinear Time Series Analysis" - Kantz & Schreiber
- Transformées de Fourier et ondelettes

### Théorie du Chaos
- "Chaos: Making a New Science" - James Gleick
- Exposants de Lyapunov et attracteurs étranges

### Statistiques
- "Statistics for the Utterly Confused" - Lloyd Jaisingh
- Corrélations et tests d'hypothèses

---

## 🚀 Évolutions Futures

### À Implémenter

1. **Calculs planétaires précis** avec `skyfield` ou `ephem`
2. **Machine Learning sur données enrichies**
   - Features externes comme input du modèle
   - Neural Networks profonds
3. **Dashboard interactif** avec Plotly/Dash
4. **API REST** pour interroger le système
5. **Analyse en temps réel** des nouveaux tirages

### Idées Avancées

- **Blockchain** : Intégration avec hash des tirages
- **Quantum Random Number Generator** : Comparaison avec QRNG
- **Crowdsourcing** : Collecter des données personnelles des joueurs
- **IA Générative** : GPT pour patterns narratifs

---

## 📧 Support

Pour questions ou contributions :
- 📁 Créer une issue sur GitHub
- 📧 Contacter via le repository
- 💬 Discussions communautaires

---

**Bon courage dans votre exploration des mystères mathématiques ! 🎲🔬**
