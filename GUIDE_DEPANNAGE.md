# 🛠️ Guide de Dépannage - EuroMillions ML Predictor

## 🎯 Résolution de Problèmes Courants

Ce guide couvre tous les problèmes techniques que vous pourriez rencontrer.

---

## 🚨 Problèmes de Démarrage

### ❌ **Problème #1 : Application ne démarre pas**

#### Symptômes :
- Double-clic sur `launch_app.bat` ne fonctionne pas
- Erreur "python n'est pas reconnu"
- Fenêtre qui se ferme immédiatement

#### Solutions :

**Solution A : Vérification Python**
```powershell
# Vérifier si Python est installé
python --version
# Si erreur : installer Python 3.9+ depuis python.org
```

**Solution B : Réinstallation environnement**
```powershell
cd "C:\Path\To\Ai_Euromillions v4"
# Supprimer l'ancien environnement
Remove-Item -Recurse -Force .venv
# Réinstaller
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
```

**Solution C : Lancement manuel**
```powershell
cd "C:\Path\To\Ai_Euromillions v4"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run ui\streamlit_app.py --server.port 8501
```

### ❌ **Problème #2 : Port déjà utilisé**

#### Symptômes :
```
Port 8501 is already in use
```

#### Solutions :

**Solution A : Utiliser un autre port**
```powershell
streamlit run ui\streamlit_app.py --server.port 8502
```

**Solution B : Tuer le processus existant**
```powershell
# Trouver le processus
netstat -ano | findstr :8501
# Tuer le processus (remplacez XXXX par le PID)
taskkill /PID XXXX /F
```

**Solution C : Redémarrer l'ordinateur**
Le plus simple si vous ne trouvez pas le processus.

---

## 📊 Problèmes de Données

### ❌ **Problème #3 : Échec téléchargement historique**

#### Symptômes :
- "Erreur de connexion"
- "Timeout"
- "Impossible de récupérer les données"

#### Solutions :

**Solution A : Vérifier la connexion**
```powershell
# Tester la connexion
ping fdj.fr
ping euromillions.com
```

**Solution B : Réessayer plus tard**
Les serveurs FDJ peuvent être temporairement surchargés.

**Solution C : Mode manuel**
```powershell
# Télécharger manuellement les fichiers CSV
python import_fdj_csv.py
```

**Solution D : Utiliser les données de sauvegarde**
Si disponible, copiez un fichier `euromillions.db` existant.

### ❌ **Problème #4 : Base de données corrompue**

#### Symptômes :
- "Database is locked"
- "No such table"
- Erreurs SQL aléatoires

#### Solutions :

**Solution A : Réinitialiser la base**
```powershell
# Supprimer la base corrompue
Remove-Item euromillions.db -Force
# Réinitialiser
python -c "from repository import init_database; init_database()"
```

**Solution B : Vérifier l'intégrité**
```powershell
python check_database.py
```

---

## 🤖 Problèmes de Modèles ML

### ❌ **Problème #5 : Échec d'entraînement**

#### Symptômes :
- "Training failed"
- Erreurs mémoire (OutOfMemory)
- Processus qui se ferme pendant l'entraînement

#### Solutions :

**Solution A : Vérifier la mémoire**
```
Minimum requis : 8GB RAM
Recommandé : 16GB RAM pour l'ensemble
```

**Solution B : Entraînement léger**
- Désactiver l'ensemble temporairement
- Utiliser seulement LightGBM
- Fermer autres applications

**Solution C : Nettoyage des données**
```powershell
python clean_database.py
```

### ❌ **Problème #6 : Modèles non trouvés**

#### Symptômes :
```
No trained models found. Run train_latest() first.
```

#### Solutions :

**Solution A : Entraîner manuellement**
```powershell
python cli_train.py
```

**Solution B : Vérifier les fichiers**
```powershell
# Vérifier le dossier models
ls models\
# Doit contenir des fichiers .joblib
```

**Solution C : Réentraînement complet**
1. Interface Streamlit → "🏋️ Entraîner (from scratch)"
2. Attendre la fin complète du processus

### ❌ **Problème #7 : Ensemble de modèles indisponible**

#### Symptômes :
```
Ensemble models not available
```

#### Solutions :

**Solution A : Installer dépendances manquantes**
```powershell
pip install xgboost catboost lightgbm scikit-learn
```

**Solution B : Vérifier les imports**
```powershell
python -c "import xgboost; import catboost; print('OK')"
```

**Solution C : Fallback sur modèle simple**
- Désactiver "Utiliser les modèles d'ensemble"
- Utiliser seulement LightGBM

---

## 🎫 Problèmes de Génération

### ❌ **Problème #8 : Génération échoue**

#### Symptômes :
- "Failed to generate ticket suggestions"
- Tickets vides
- Erreurs lors du clic sur "Générer"

#### Solutions :

**Solution A : Recharger les modèles**
Interface → "📦 Recharger le modèle"

**Solution B : Paramètres par défaut**
- Méthode : `hybrid`
- Nombre : `5`
- Ensemble : ☑️

**Solution C : Diagnostic**
```powershell
python -c "from streamlit_adapters import *; print(get_system_status())"
```

### ❌ **Problème #9 : Scores de confiance faibles**

#### Symptômes :
- Tous les scores < 50%
- Confiance "Très Faible" partout

#### Causes possibles :
- Modèles mal entraînés
- Données insuffisantes
- Paramètres inadaptés

#### Solutions :

**Solution A : Ré-entraîner avec plus de données**
1. "🔄 Mise à jour incrémentale"
2. "🏋️ Entraîner (from scratch)"
3. "🤖 Ensemble de modèles"

**Solution B : Changer de méthode**
- Essayer `ensemble` au lieu de `hybrid`
- Activer l'ensemble de modèles

---

## 🖥️ Problèmes Interface

### ❌ **Problème #10 : Page blanche / Ne charge pas**

#### Symptômes :
- Page blanche dans le navigateur
- "This site can't be reached"
- Chargement infini

#### Solutions :

**Solution A : Vérifier l'URL**
- Essayer `http://localhost:8501`
- Essayer `http://localhost:8502`
- Essayer `http://127.0.0.1:8501`

**Solution B : Vider le cache**
- Ctrl+F5 (refresh forcé)
- Mode navigation privée
- Autre navigateur

**Solution C : Vérifier Streamlit**
```powershell
streamlit --help
# Si erreur : pip install streamlit
```

### ❌ **Problème #11 : Interface lente**

#### Symptômes :
- Boutons qui ne répondent pas
- Temps de chargement très longs
- Interface qui freeze

#### Solutions :

**Solution A : Ressources système**
- Fermer autres applications
- Vérifier utilisation RAM/CPU
- Redémarrer si nécessaire

**Solution B : Paramètres allégés**
- Réduire nombre de tickets (5 au lieu de 20)
- Utiliser `topk` au lieu d'`ensemble`
- Désactiver l'ensemble temporairement

---

## 🔧 Diagnostic Avancé

### 🩺 **Tests Automatiques**

**Test complet du système :**
```powershell
python comprehensive_test.py
```

**Test des modèles :**
```powershell
python test_train_models.py
```

**Test de l'interface :**
```powershell
python test_streamlit_adapters.py
```

### 📊 **Logs de Diagnostic**

**Vérifier les logs :**
```powershell
# Logs dans la console Streamlit
# Ou dans les fichiers .log si configurés
```

**Activer mode debug :**
```powershell
streamlit run ui\streamlit_app.py --server.port 8501 --logger.level debug
```

### 🧹 **Nettoyage Complet**

**Si tout else fails - Reset complet :**
```powershell
# 1. Supprimer l'environnement
Remove-Item -Recurse -Force .venv

# 2. Supprimer les modèles
Remove-Item -Recurse -Force models

# 3. Supprimer la base (ATTENTION : perte des données)
Remove-Item euromillions.db -Force

# 4. Réinstaller depuis zéro
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
```

---

## 📞 Support et Ressources

### 📚 **Documentation Supplémentaire**
- `GUIDE_UTILISATEUR_COMPLET.md` - Guide détaillé
- `DEMARRAGE_RAPIDE.md` - Guide express
- `BUILD_EXECUTABLE.md` - Création d'un exécutable
- `DEPLOYMENT_GUIDE.md` - Guide de déploiement

### 🔍 **Fichiers de Diagnostic**
- `check_database.py` - Vérification base de données
- `status.py` - Statut général du système
- `validate_db.py` - Validation des données

### ⚙️ **Configuration Avancée**
- `.env` - Variables d'environnement
- `config.py` - Configuration du programme
- `requirements.txt` - Dépendances Python

---

## 🎯 **Conseils de Prévention**

### ✅ **Bonnes Pratiques**

1. **Sauvegarde régulière** du fichier `euromillions.db`
2. **Mise à jour hebdomadaire** des données
3. **Ré-entraînement mensuel** des modèles
4. **Monitoring des performances** via les scores

### 🚫 **À Éviter**

1. **Ne pas fermer brutalement** pendant l'entraînement
2. **Ne pas modifier** manuellement la base de données
3. **Ne pas lancer** plusieurs instances simultanément
4. **Ne pas oublier** les mises à jour de données

---

*Guide de Dépannage créé le 5 octobre 2025*