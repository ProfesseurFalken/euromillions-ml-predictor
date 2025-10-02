# 📖 Manuel Utilisateur Beta - EuroMillions ML Prediction

> **Version Beta** - Guide pratique pour les testeurs  
> **Dernière mise à jour :** 28 septembre 2025

---

## 🚀 **Démarrage rapide**

### **1. Lancement du programme**

```powershell
# Ouvrir PowerShell dans le dossier du programme
.\bootstrap.ps1
```

Le programme va :
- ✅ Créer l'environnement virtuel Python
- ✅ Installer les dépendances automatiquement
- ✅ Lancer l'interface web

**➡️ L'interface s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`**

### **2. Si l'interface ne se lance pas automatiquement**

```powershell
# Lancer manuellement
streamlit run ui\streamlit_app.py
```

---

## 🎯 **Utilisation de l'interface**

L'interface contient **5 sections principales** :

### **📥 Section 1 : Initialisation & Mise à jour**

#### **🔧 Première utilisation (OBLIGATOIRE)**
1. Cliquez sur **"📥 Télécharger l'historique & Initialiser"**
2. ⏳ Attendez 2-5 minutes (téléchargement des données historiques)
3. ✅ Message de confirmation avec nombre de tirages téléchargés

#### **🔄 Mise à jour régulière**
- Cliquez sur **"🔄 Mettre à jour (derniers tirages)"**
- À faire **2 fois par semaine** (après les tirages mardi et vendredi soir)

---

### **🧠 Section 2 : Entraînement des modèles**

#### **🏋️ Premier entraînement (OBLIGATOIRE après initialisation)**
1. Cliquez sur **"🏋️ Entraîner (from scratch)"**
2. ⏳ Attendez 1-2 minutes
3. ✅ Vérifiez les métriques affichées (Log-loss < 0.70 = bon)

#### **📦 Rechargement des modèles**
- Cliquez sur **"📦 Recharger le modèle"** si erreur ou problème

#### **🔄 Quand re-entraîner ?**
- **Chaque semaine** après avoir mis à jour les données
- **Si les prédictions semblent moins bonnes**
- **Après 20-30 nouveaux tirages**

---

### **📊 Section 3 : Probabilités actuelles**

#### **🔄 Consulter les probabilités**
1. Cliquez sur **"🔄 Actualiser les probabilités"**
2. 📈 Consultez le **Top 15 boules** et **Top 5 étoiles**
3. 🎯 Les pourcentages indiquent les chances de sortie

**💡 Conseil :** Actualisez avant chaque génération de tickets.

---

### **🎫 Section 4 : Génération de tickets**

#### **⚙️ Paramètres (barre latérale)**
- **Nombre de tickets :** 1-20 (recommandé : 5-10)
- **Méthode :**
  - `hybrid` 🔥 **RECOMMANDÉE** (mélange intelligent)
  - `topk` (sélection des plus probables)
  - `random` (échantillonnage pondéré)
- **Graine aléatoire :** Pour reproductibilité (optionnel)

#### **🎲 Générer vos tickets**
1. Ajustez les paramètres dans la barre latérale
2. Cliquez sur **"🎲 Générer les tickets"**
3. 📋 Vos tickets s'affichent au format :
   ```
   🎫 Ticket 1
   
      16 - 30 - 38 - 43 - 48
      ⭐ 07 - 08
   ```

#### **💾 Télécharger vos tickets**
- **⬇️ CSV** : Format tableur pour impression
- **⬇️ JSON** : Format complet avec métadonnées

---

### **🗂️ Section 5 : Historique**

#### **📜 Consulter l'historique**
- **"📜 Voir les 20 derniers tirages"** : Vérification rapide
- **"⬇️ Exporter l'historique (CSV)"** : Sauvegarde complète

---

## ⏰ **Planning d'utilisation recommandé**

### **🗓️ Routine hebdomadaire**

#### **Mercredi matin** (après tirage du mardi)
1. 🔄 **Mettre à jour** les données
2. 🧠 **Re-entraîner** le modèle (si >10 nouveaux tirages)
3. 🎫 **Générer** tickets pour vendredi

#### **Samedi matin** (après tirage du vendredi)
1. 🔄 **Mettre à jour** les données
2. 🧠 **Re-entraîner** le modèle (si >10 nouveaux tirages)
3. 🎫 **Générer** tickets pour mardi suivant

### **📅 Maintenance mensuelle**
- **Re-entraînement complet** (bouton "🏋️ Entraîner from scratch")
- **Vérification** des performances du modèle
- **Sauvegarde** de l'historique (export CSV)

---

## 🚨 **Situations et solutions**

### **❌ "Aucune donnée disponible"**
**Solution :** Faire l'initialisation complète (Section 1)

### **❌ "Aucun modèle entraîné"**
**Solution :** Entraîner les modèles (Section 2)

### **❌ "Erreur lors de la génération"**
**Solutions :**
1. Recharger les modèles
2. Actualiser les probabilités
3. Réduire le nombre de tickets demandés

### **❌ L'interface ne répond plus**
**Solutions :**
1. Actualiser la page du navigateur
2. Relancer le programme : `Ctrl+C` puis `streamlit run ui\streamlit_app.py`

### **❌ "Données trop anciennes"**
**Solution :** Mettre à jour les données (Section 1)

---

## 📈 **Optimisation des résultats**

### **🎯 Meilleures pratiques**

#### **Qualité des données**
- ✅ Mettre à jour **systématiquement** après chaque tirage officiel
- ✅ Re-entraîner **régulièrement** (hebdomadaire recommandé)
- ✅ Vérifier que l'historique contient **300+ tirages**

#### **Génération de tickets**
- 🔥 **Méthode "hybrid"** pour les meilleurs résultats
- 🎲 **5-10 tickets** par session (équilibre quantité/qualité)
- 📊 **Consulter les probabilités** avant génération
- 🔄 **Varier la graine aléatoire** pour diversifier

#### **Suivi des performances**
- 📝 **Noter vos tickets** et résultats
- 📈 **Comparer** avec les tirages officiels
- 🎯 **Ajuster** la fréquence d'entraînement selon les résultats

---

## 🔧 **Paramètres avancés**

### **⚙️ Configuration (.env)**
Accessible via la barre latérale > **"⚙️ Paramètres (.env)"**

**Paramètres modifiables :**
- `STORAGE_DIR` : Dossier de stockage (défaut : `./data`)
- `REQUEST_TIMEOUT` : Timeout web (défaut : 15 sec)
- `MAX_RETRIES` : Tentatives en cas d'échec (défaut : 3)

**⚠️ Attention :** Redémarrer le programme après modification.

---

## 📊 **Comprendre les métriques**

### **🎯 Log-loss (performance du modèle)**
- **< 0.60** : Excellent 🔥
- **0.60 - 0.70** : Très bon ✅
- **0.70 - 0.80** : Correct 🆗
- **> 0.80** : À améliorer ⚠️

### **📈 Probabilités affichées**
- **> 3%** : Très probable 🔥
- **2-3%** : Probable ✅
- **1-2%** : Moyen 🆗
- **< 1%** : Peu probable ⚠️

---

## 🆘 **Support Beta**

### **📝 Feedback attendu**
- 🐛 **Bugs rencontrés** (avec captures d'écran si possible)
- 💡 **Suggestions d'amélioration**
- 📈 **Retours sur les performances** des prédictions
- 🎨 **Commentaires sur l'interface**

### **📞 Contact**
- **Issues GitHub** : [Créer un rapport de bug](https://github.com/ProfesseurFalken/euromillions-ml-prediction/issues)
- **Logs système** : Fichiers dans `data/logs/` (si problème technique)

---

## 🎉 **Bonne chance !**

Ce système utilise l'intelligence artificielle pour analyser les patterns historiques, mais rappelez-vous :
- 🎲 **L'EuroMillions reste un jeu de hasard**
- 📈 **Les prédictions augmentent les chances** mais ne garantissent pas le gain
- 🍀 **Jouez responsable** et amusez-vous !

**Que la chance soit avec vous ! 🍀🎰**

---

*Manuel Utilisateur Beta v1.0 - EuroMillions ML Prediction System*