# Guide de Maintenance EuroMillions ML

## 🎯 Résumé de votre système

Votre système EuroMillions ML est maintenant **entièrement opérationnel** avec :
- **2063 tirages officiels** (du 10/05/2011 au 26/09/2025)
- **Base de données à jour** (seulement 2 jours de retard)
- **Modèles entraînés** sur les règles modernes (post-2016)
- **Interface Streamlit** fonctionnelle sur http://localhost:8501

## 🔄 Maintenance des données

### Vérification rapide du statut
```bash
# Option 1: Script de statut rapide
python status.py

# Option 2: Menu interactif Windows
menu.bat
```

### Mise à jour des tirages

#### Automatique (recommandé)
```bash
# Mode interactif
python update_tirages_windows.py

# Mode automatique (sans confirmation)
python update_tirages_windows.py --auto
```

#### Manuel (si nécessaire)
1. **Télécharger les CSV récents** depuis https://www.fdj.fr/jeux/jeux-de-tirage/euromillions
2. **Placer les fichiers CSV** dans le dossier racine du projet
3. **Lancer l'import** : `python import_fdj_special.py`
4. **Re-entraîner** : `python cli_train.py train`

### Fréquence recommandée
- **Vérification** : 1 fois par semaine
- **Mise à jour** : Quand le retard dépasse 7 jours
- **Re-entraînement** : Après chaque import de nouvelles données

## 🚀 Utilisation quotidienne

### Lancement de l'interface
```bash
# Via le menu Windows
menu.bat

# Direct
.\.venv\Scripts\activate
streamlit run ui\streamlit_app.py --server.port 8501
```

### Génération de prédictions
```bash
# Suggestions complètes
python cli_train.py suggest

# Top 5 combinaisons
python cli_train.py score --top 5
```

### Tests du système
```bash
# Tests complets
python -m pytest test_*.py -v

# Test spécifique
python test_repository.py
```

## 📊 Indicateurs de santé du système

### Statut des données
- **VERT (À JOUR)** : Retard ≤ 3 jours → Aucune action requise
- **ORANGE (ACCEPTABLE)** : Retard 4-7 jours → Mise à jour recommandée
- **ROUGE (OBSOLÈTE)** : Retard > 7 jours → Mise à jour urgente

### Performance des modèles
- **Modèle principal** (1-50) : Score ~0.50 = Excellent
- **Modèle étoiles** (1-12) : Score ~0.62 = Excellent
- **Données d'entraînement** : 940 tirages post-2016

## 🛠️ Résolution de problèmes

### Erreurs communes

#### Base de données corrompue
```bash
# Sauvegarder
copy data\draws.db data\draws_backup.db

# Reconstruire
python build_datasets.py
python cli_train.py train
```

#### Problème d'environnement Python
```bash
# Reconstruire l'environnement
bootstrap.ps1
```

#### Interface Streamlit ne se lance pas
```bash
# Vérifier le port
netstat -an | findstr 8501

# Utiliser un autre port
streamlit run ui\streamlit_app.py --server.port 8502
```

### Fichiers de logs
- **Erreurs d'import** : Affichées dans le terminal
- **Logs Streamlit** : Dans le terminal de lancement
- **Base de données** : `data\draws.db`

## 📁 Structure des fichiers importants

```
EuroMillions/
├── data/draws.db              # Base de données principale
├── models/                    # Modèles ML entraînés
├── status.py                  # Vérification rapide
├── update_tirages_windows.py  # Mise à jour automatique
├── menu.bat                   # Interface Windows
├── check_freshness_windows.py # Vérification détaillée
└── ui/streamlit_app.py        # Interface web
```

## 🎯 Prochaines étapes suggérées

1. **Automatisation** : Créer une tâche Windows planifiée pour `status.py`
2. **Alertes** : Configurer des notifications en cas de retard important
3. **Backup** : Sauvegarder régulièrement `data\draws.db`
4. **Optimisation** : Re-entraîner les modèles tous les 50 nouveaux tirages

## 📞 Support

- **Statut système** : `python status.py`
- **Logs détaillés** : `python check_freshness_windows.py`
- **Tests** : `python -m pytest -v`
- **Menu interactif** : `menu.bat`

---

**Système opérationnel ✅ | Prêt pour les prédictions 🎯**