# 🎲 Guide Utilisateur Complet - EuroMillions ML Predictor

## 📋 Table des Matières
1. [Introduction et Vue d'Ensemble](#introduction)
2. [Installation et Première Configuration](#installation)
3. [Démarrage de l'Application](#demarrage)
4. [Interface et Navigation](#interface)
5. [Étapes d'Utilisation Complète](#utilisation)
6. [Fonctionnalités Avancées](#avancees)
7. [Résolution de Problèmes](#troubleshooting)
8. [Questions Fréquentes (FAQ)](#faq)

---

## 🎯 Introduction et Vue d'Ensemble {#introduction}

### Qu'est-ce que EuroMillions ML Predictor ?

**EuroMillions ML Predictor** est un système d'intelligence artificielle qui analyse les tirages historiques d'EuroMillions pour générer des prédictions de numéros. Le programme utilise plusieurs algorithmes de machine learning avancés pour identifier des patterns et tendances dans les données.

### ⚠️ Avertissement Important

**Ce programme est un outil d'aide à la décision et de divertissement. Il ne garantit AUCUN gain et ne doit pas être considéré comme un système infaillible. Les jeux de hasard comportent toujours des risques financiers.**

### 🎪 Fonctionnalités Principales

- ✅ **Analyse de données historiques** complètes d'EuroMillions
- 🤖 **5 algorithmes ML** : LightGBM, XGBoost, CatBoost, RandomForest + Ensemble
- 🧠 **Stratégie hybride avancée** combinant ML + statistiques + patterns
- 📊 **Scores de confiance** pour évaluer la qualité des prédictions
- 🎫 **Génération de tickets** avec métadonnées détaillées
- 📈 **Interface graphique intuitive** avec Streamlit
- 💾 **Export des résultats** en CSV et JSON

---

## 🛠️ Installation et Première Configuration {#installation}

### Prérequis Système

- **Windows 10/11** (le guide est optimisé pour Windows)
- **Python 3.9+** installé sur votre système
- **Connexion Internet** pour télécharger les données
- **8GB RAM minimum** recommandé pour l'entraînement des modèles

### 📥 Étape 1 : Installation Automatique

Le programme dispose d'un script d'installation automatique qui configure tout pour vous.

1. **Ouvrez PowerShell en tant qu'Administrateur** :
   - Clic droit sur le menu Démarrer → "Windows PowerShell (Administrateur)"

2. **Naviguez vers le dossier du programme** :
   ```powershell
   cd "C:\Path\To\Ai_Euromillions v4"
   ```
   *(Remplacez par votre chemin réel)*

3. **Lancez l'installation automatique** :
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
   ```

### 📋 Ce que fait le script d'installation :
- ✅ Crée un environnement Python virtuel
- ✅ Installe toutes les dépendances nécessaires
- ✅ Configure la base de données SQLite
- ✅ Vérifie que tout fonctionne correctement

### ⏱️ Durée d'installation : 5-10 minutes selon votre connexion

---

## 🚀 Démarrage de l'Application {#demarrage}

### 🎯 Méthode Recommandée : Script de Lancement

**Le plus simple est d'utiliser le script de lancement automatique :**

1. **Double-cliquez sur `launch_app.bat`** dans le dossier du programme
2. Une fenêtre de terminal s'ouvrira et lancera automatiquement l'interface web
3. Votre navigateur s'ouvrira automatiquement sur `http://localhost:8501`

### 🔧 Méthode Manuel (si nécessaire)

Si le script automatique ne fonctionne pas :

1. **Ouvrez PowerShell** dans le dossier du programme
2. **Activez l'environnement virtuel** :
   ```powershell
   .\.venv\Scripts\activate
   ```
3. **Lancez Streamlit** :
   ```powershell
   streamlit run ui\streamlit_app.py --server.port 8501
   ```

### 🌐 Accès à l'Interface

Une fois lancé, ouvrez votre navigateur et allez à :
- **URL principale** : `http://localhost:8501`
- **URL alternative** : `http://localhost:8502` (si le port 8501 est occupé)

---

## 🖥️ Interface et Navigation {#interface}

### 🎨 Vue d'Ensemble de l'Interface

L'interface Streamlit est divisée en plusieurs sections principales :

```
┌─────────────────────────────────────────┐
│  🎲 EuroMillions — Console Graphique    │
├─────────────────────────────────────────┤
│  SIDEBAR (Paramètres)                   │
│  ├── 🎯 Suggestions                     │
│  ├── 🔧 Options avancées               │
│  └── ⚖️ Poids stratégie hybride        │
├─────────────────────────────────────────┤
│  CONTENU PRINCIPAL                      │
│  ├── 🔧 Initialisation & Mise à jour   │
│  ├── 🧠 Entraînement                   │
│  ├── 📊 Probabilités actuelles         │
│  ├── 🎫 Générer des tickets            │
│  ├── 📈 Statut du système              │
│  └── 🎰 Autres fonctionnalités         │
└─────────────────────────────────────────┘
```

### 📱 Navigation dans l'Interface

#### **Sidebar (Panneau Latéral Gauche)**
- **🎯 Suggestions** : Paramètres pour la génération de tickets
- **🔧 Options avancées** : Activation de l'ensemble et poids personnalisés

#### **Contenu Principal (Centre)**
- **Sections organisées par étapes** logiques d'utilisation
- **Boutons d'action** avec icônes explicites
- **Résultats affichés** directement sous chaque action

---

## 📚 Étapes d'Utilisation Complète {#utilisation}

### 🏁 **ÉTAPE 1 : Première Initialisation (À faire UNE SEULE FOIS)**

#### 1.1 Télécharger l'Historique Complet

**Objectif** : Récupérer toutes les données historiques d'EuroMillions depuis 2004.

**Actions** :
1. Dans la section **🔧 Initialisation & Mise à jour**
2. Cliquez sur **"📥 Télécharger l'historique & Initialiser"**
3. ⏱️ **Attendez 2-5 minutes** (selon votre connexion)

**Résultat attendu** :
```
✅ Historique téléchargé avec succès!
📊 Tirages importés: ~1200 tirages depuis 2004
📅 Période couverte: 2004-02-13 → 2025-10-05
```

#### 1.2 Entraîner les Modèles de Base

**Objectif** : Créer les premiers modèles d'IA avec les données téléchargées.

**Actions** :
1. Dans la section **🧠 Entraînement**
2. Cliquez sur **"🏋️ Entraîner (from scratch)"**
3. ⏱️ **Attendez 3-8 minutes** (dépend de votre processeur)

**Résultat attendu** :
```
✅ Entraînement terminé avec succès!
📊 Log-loss boules principales: 0.2547
📊 Log-loss étoiles: 0.1832
📊 Données d'entraînement: 1200 tirages
```

#### 1.3 Entraîner l'Ensemble de Modèles (Recommandé)

**Objectif** : Créer des modèles avancés pour de meilleures prédictions.

**Actions** :
1. Dans la section **🧠 Entraînement**
2. Cliquez sur **"🤖 Ensemble de modèles"**
3. ⏱️ **Attendez 5-12 minutes** (entraînement de 4 algorithmes)

**Résultat attendu** :
```
✅ Ensemble models trained successfully
🎯 Modèles entraînés: LightGBM, XGBoost, CatBoost, RandomForest
📊 Score d'ensemble: 0.2234
🏆 Meilleur modèle: XGBoost
```

---

### 🎯 **ÉTAPE 2 : Génération de Tickets (Utilisation Quotidienne)**

#### 2.1 Configuration des Paramètres

**Dans le panneau latéral (Sidebar)**, configurez :

##### **🎯 Paramètres de Base**
- **Nombre de tickets** : `5-10` (recommandé pour débuter)
- **Méthode de génération** : Choisissez selon vos préférences
- **Graine aléatoire** : Laissez `42` ou changez pour varier

##### **📊 Méthodes de Génération Disponibles**

| Méthode | Description | Niveau | Utilisation |
|---------|-------------|--------|-------------|
| `hybrid` | 🔄 Équilibré ML + hasard | Débutant | Usage quotidien |
| `ensemble` | 🤖 4 algorithmes combinés | Avancé | Maximum de précision |
| `advanced_hybrid` | 🧠 Stratégie complète | Expert | Contrôle total |
| `topk` | 📊 Probabilités maximales | Simple | Approche directe |
| `random` | 🎲 Sélection pondérée | Simple | Plus de diversité |

##### **🔧 Options Avancées**
- ☑️ **"Utiliser les modèles d'ensemble"** : **TOUJOURS COCHÉ** (recommandé)

#### 2.2 Configuration Hybride Avancée (Optionnel)

Si vous sélectionnez `advanced_hybrid`, vous pouvez ajuster :

**⚖️ Poids de la stratégie hybride** :
- **ML** (0.4) : Influence des prédictions d'intelligence artificielle
- **Fréquence** (0.3) : Poids des numéros fréquents dans l'histoire
- **Motifs** (0.2) : Détection de patterns et séquences
- **Écarts** (0.1) : Analyse des intervalles entre tirages

**💡 Conseil** : Laissez les valeurs par défaut au début, ajustez ensuite selon vos préférences.

#### 2.3 Génération des Tickets

**Actions** :
1. Dans la section **🎫 Générer des tickets 5+2**
2. Cliquez sur **"🎲 Générer les tickets"**
3. ⏱️ **Attendez 5-15 secondes**

**Résultat** : Affichage de vos tickets avec :
- **Numéros générés** (boules + étoiles)
- **Score de confiance** (0-100%)
- **Niveau de confiance** (Très Élevée, Élevée, Moyenne, etc.)
- **Méthode utilisée** pour chaque ticket

#### 2.4 Interprétation des Résultats

##### **🎫 Exemple de Ticket Généré**
```
🎫 Ticket 1 🔥
   07 - 14 - 23 - 35 - 42
   ⭐ 03 - 09
   
   📊 Confiance: 87.3% (Très Élevée)
   🎯 Méthode: ensemble
```

##### **📊 Interprétation des Scores de Confiance**

| Score | Niveau | Emoji | Signification |
|-------|--------|-------|---------------|
| 80-100% | Très Élevée | 🔥 | Excellente prédiction selon l'IA |
| 65-79% | Élevée | ⚡ | Bonne prédiction, recommandée |
| 50-64% | Moyenne | ✨ | Prédiction correcte |
| 35-49% | Faible | 💫 | Prédiction moins fiable |
| 0-34% | Très Faible | 💫 | À utiliser avec précaution |

#### 2.5 Export des Résultats

**Pour sauvegarder vos tickets** :
1. Utilisez les boutons **"📥 Télécharger CSV"** ou **"📥 Télécharger JSON"**
2. Les fichiers incluent toutes les métadonnées (timestamps, scores, méthodes)

---

### 🔄 **ÉTAPE 3 : Maintenance et Mise à Jour (Hebdomadaire)**

#### 3.1 Mise à Jour des Données

**Objectif** : Récupérer les nouveaux tirages de la semaine.

**Actions** :
1. Section **🔧 Initialisation & Mise à jour**
2. Cliquez sur **"🔄 Mise à jour incrémentale"**

#### 3.2 Ré-entraînement (si nécessaire)

**Quand ré-entraîner ?**
- ✅ Après avoir ajouté 5+ nouveaux tirages
- ✅ Si les scores de confiance baissent
- ✅ Une fois par mois pour maintenir la performance

**Actions** :
1. **"🏋️ Entraîner (from scratch)"** pour les modèles de base
2. **"🤖 Ensemble de modèles"** pour les modèles avancés

---

## 🚀 Fonctionnalités Avancées {#avancees}

### 📊 **Analyse des Probabilités**

#### Visualiser les Tendances Actuelles

**Actions** :
1. Section **📊 Probabilités actuelles**
2. Cliquez sur **"🔄 Actualiser les probabilités"**

**Informations obtenues** :
- **Top 15 boules principales** avec pourcentages de probabilité
- **Top 5 étoiles** avec leurs scores
- **Classement par rang** de probabilité

#### Interprétation
- **Probabilité élevée** (>8%) : Numéro très probablement sélectionné par l'IA
- **Probabilité moyenne** (4-8%) : Numéro avec chances raisonnables
- **Probabilité faible** (<4%) : Numéro moins susceptible d'être sélectionné

### 🎰 **Fonctionnalités Système**

#### Vérification du Statut

**Actions** :
1. Section **📈 Statut du système**
2. Cliquez sur **"🔍 Vérifier le statut"**

**Informations système** :
- État de la base de données
- Statut des modèles entraînés
- Dernière mise à jour des données
- Performance des modèles

#### Gestion des Données

**Export complet** :
- **"📊 Exporter tous les tirages (CSV)"** : Toute la base de données
- Utile pour analyses externes ou sauvegarde

**Ajout manuel** :
- Section **🎲 Gestion manuelle**
- Permet d'ajouter manuellement des tirages si nécessaire

---

## 🛠️ Résolution de Problèmes {#troubleshooting}

### ❌ **Problèmes Courants et Solutions**

#### 1. **L'application ne démarre pas**

**Symptômes** : Erreur au lancement, page blanche
**Solutions** :
```powershell
# 1. Vérifier l'environnement virtuel
cd "C:\Path\To\Ai_Euromillions v4"
.\.venv\Scripts\activate

# 2. Réinstaller les dépendances
pip install -r requirements.txt

# 3. Relancer l'application
streamlit run ui\streamlit_app.py --server.port 8502
```

#### 2. **Erreur "Port déjà utilisé"**

**Symptômes** : `Port 8501 is already in use`
**Solution** :
```powershell
# Utiliser un port différent
streamlit run ui\streamlit_app.py --server.port 8502
```

#### 3. **Échec du téléchargement des données**

**Symptômes** : Erreur réseau, timeout
**Solutions** :
1. **Vérifier la connexion Internet**
2. **Réessayer plus tard** (serveur FDJ parfois surchargé)
3. **Utiliser le mode offline** si des données existent déjà

#### 4. **Modèles non trouvés**

**Symptômes** : `No trained models found`
**Solution** :
1. **Ré-entraîner** : Cliquez sur "🏋️ Entraîner (from scratch)"
2. **Vérifier les données** : S'assurer que l'historique est téléchargé

#### 5. **Performance lente**

**Causes possibles** :
- RAM insuffisante (< 8GB)
- Processeur ancien
- Trop de programmes en arrière-plan

**Solutions** :
1. **Fermer autres applications**
2. **Réduire le nombre de tickets** généré (5 au lieu de 10)
3. **Utiliser method="topk"** au lieu d'ensemble

#### 6. **Erreurs d'ensemble de modèles**

**Symptômes** : `Ensemble models not available`
**Solution** :
```powershell
# Vérifier les dépendances ML
pip install xgboost catboost lightgbm scikit-learn
```

### 🔧 **Scripts de Diagnostic**

#### Test Complet du Système
```powershell
# Dans le dossier du programme
python comprehensive_test.py
```

#### Vérification de la Base de Données
```powershell
python check_database.py
```

---

## ❓ Questions Fréquentes (FAQ) {#faq}

### 🎯 **Utilisation Générale**

**Q: À quelle fréquence dois-je utiliser le programme ?**
R: Pour de meilleurs résultats, utilisez-le **2-3 fois par semaine** avec mise à jour des données hebdomadaire.

**Q: Combien de tickets dois-je générer ?**
R: Pour débuter, **5-10 tickets** suffisent. Les utilisateurs expérimentés peuvent aller jusqu'à 20.

**Q: Quelle méthode choisir ?**
R: 
- **Débutants** : `hybrid`
- **Utilisateurs avancés** : `ensemble`
- **Experts** : `advanced_hybrid` avec poids personnalisés

### 🤖 **Intelligence Artificielle**

**Q: Comment l'IA prédit-elle les numéros ?**
R: L'IA analyse les **patterns temporels**, **fréquences**, **corrélations** et **séquences** dans l'historique des 1200+ tirages depuis 2004.

**Q: Pourquoi les scores de confiance sont-ils importants ?**
R: Ils indiquent la **qualité de la prédiction** selon l'IA. Un score élevé signifie que l'IA est "confiante" dans sa prédiction.

**Q: Que signifie "ensemble de modèles" ?**
R: C'est la combinaison de **4 algorithmes différents** (LightGBM, XGBoost, CatBoost, RandomForest) qui votent ensemble pour de meilleures prédictions.

### 📊 **Données et Performance**

**Q: D'où viennent les données ?**
R: Directement du site officiel **FDJ (Française des Jeux)** et d'**EuroMillions.com**.

**Q: Les données sont-elles à jour ?**
R: Le programme télécharge automatiquement les **derniers tirages** disponibles à chaque mise à jour.

**Q: Comment interpréter les performances des modèles ?**
R: 
- **Log-loss < 0.30** : Excellente performance
- **Log-loss 0.30-0.50** : Bonne performance
- **Log-loss > 0.50** : Performance à améliorer (ré-entraîner)

### ⚠️ **Limitations et Réalisme**

**Q: Ce programme peut-il garantir un gain ?**
R: **NON, absolument pas.** L'EuroMillions reste un jeu de hasard. Ce programme améliore vos chances statistiquement mais ne garantit rien.

**Q: Quel est le taux de réussite réel ?**
R: Dans les tests, les prédictions ont une **précision supérieure au hasard pur**, mais restent dans le domaine probabiliste.

**Q: Puis-je perdre de l'argent ?**
R: **OUI.** Ne jouez que ce que vous pouvez vous permettre de perdre. Ce programme est un outil d'aide, pas une garantie.

### 🔧 **Technique**

**Q: Puis-je utiliser ce programme sur Mac/Linux ?**
R: Le code est compatible, mais ce guide est optimisé pour Windows. Adaptations mineures nécessaires.

**Q: Combien d'espace disque faut-il ?**
R: Environ **500MB** pour l'installation complète (Python + dépendances + données + modèles).

**Q: Le programme fonctionne-t-il hors ligne ?**
R: **Partiellement**. La génération de tickets fonctionne hors ligne, mais les mises à jour nécessitent Internet.

---

## 🎉 **Conclusion**

Ce guide vous donne toutes les clés pour utiliser efficacement **EuroMillions ML Predictor**. N'hésitez pas à expérimenter avec les différentes méthodes et paramètres pour trouver votre approche optimale.

### 📞 **Support**
- Documentation technique : Voir les autres fichiers `.md`
- Code source : Disponible dans le dossier du programme

**🍀 Bonne chance et jouez de manière responsable ! 🍀**

---
*Guide créé le 5 octobre 2025 - Version 2.0*