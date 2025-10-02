# 📥 Guide d'Import CSV FDJ

## 🎯 Comment ajouter de nouvelles données EuroMillions

### 📋 Étapes à suivre :

#### 1. **📄 Téléchargez les données FDJ**
   - Allez sur [FDJ.fr](https://www.fdj.fr) ou [Euro-Millions.com](https://www.euro-millions.com)
   - Téléchargez les historiques CSV récents (2017-2025)
   - Sauvegardez les fichiers dans ce dossier

#### 2. **🔧 Lancez l'import**
   ```bash
   # Activez l'environnement
   .\.venv\Scripts\activate.ps1
   
   # Lancez l'import automatique
   python import_new_fdj_csv.py
   ```

#### 3. **🤖 Re-entraînez le modèle**
   ```bash
   # Avec les nouvelles données
   python cli_train.py train
   ```

### 📊 **Formats CSV supportés :**

✅ **Format FDJ classique :**
```
date_de_tirage,boule_1,boule_2,boule_3,boule_4,boule_5,etoile_1,etoile_2
13/02/2024,7,16,25,31,49,8,11
```

✅ **Format Euro-Millions.com :**
```
Date,Number1,Number2,Number3,Number4,Number5,Star1,Star2
2024-02-13,7,16,25,31,49,8,11
```

✅ **Format numérique :**
```
20240213,7,16,25,31,49,8,11
```

### ⚡ **Détection automatique :**

Le script détecte automatiquement :
- 📅 Le format de date (DD/MM/YYYY, YYYY-MM-DD, YYYYMMDD)
- 🎱 Les colonnes de numéros (boule_1-5, n1-5, numero_1-5)
- ⭐ Les colonnes d'étoiles (etoile_1-2, star_1-2, lucky_star_1-2)
- 📊 La plage d'étoiles (1-11 ou 1-12) selon la période

### 🔍 **Vérifications incluses :**
- ✅ Suppression automatique des doublons
- ✅ Validation des plages (numéros 1-50, étoiles 1-12)
- ✅ Gestion des formats de date multiples
- ✅ Protection contre les données invalides

### 📈 **Après l'import :**

1. **Vérifiez les données :**
   ```bash
   python check_database.py
   ```

2. **Re-entraînez avec toutes les données :**
   ```bash
   python cli_train.py train
   ```

3. **Testez les nouvelles prédictions :**
   ```bash
   python cli_train.py suggest
   ```

4. **Lancez l'interface :**
   ```bash
   python -m streamlit run ui\streamlit_app.py --server.port 8501
   ```

### 🎉 **Résultat attendu :**

Avec des données complètes 2011-2025, vous devriez avoir :
- 📊 **~1400 tirages** (au lieu de 562)
- 📈 **Couverture ~95%** (au lieu de 77%)
- 🤖 **Modèles plus précis** avec 14 ans de données
- 🎯 **Prédictions améliorées** grâce à plus de patterns

---

**🚀 Prêt à importer vos nouveaux CSV FDJ ?**
Placez-les dans ce dossier et lancez `python import_new_fdj_csv.py` !