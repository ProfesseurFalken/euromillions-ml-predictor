# 🚀 Démarrage Rapide - EuroMillions ML Predictor

## ⚡ Guide Express (15 minutes)

### 🎯 Objectif
Passer de zéro à la génération de vos premiers tickets en 15 minutes maximum.

---

## 📋 Checklist Express

### ✅ **ÉTAPE 1 : Installation (5 minutes)**

1. **Ouvrez PowerShell en Administrateur**
   ```
   Clic droit Menu Démarrer → "Windows PowerShell (Administrateur)"
   ```

2. **Allez dans le dossier**
   ```powershell
   cd "C:\Path\To\Ai_Euromillions v4"
   ```
   *(Adaptez le chemin à votre installation)*

3. **Installation automatique**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
   ```
   ⏱️ Attendez 3-5 minutes

### ✅ **ÉTAPE 2 : Premier Lancement (2 minutes)**

1. **Double-cliquez sur `launch_app.bat`**
2. **Ou manuellement** :
   ```powershell
   .\.venv\Scripts\activate
   streamlit run ui\streamlit_app.py --server.port 8501
   ```
3. **Ouvrez** : `http://localhost:8501` dans votre navigateur

### ✅ **ÉTAPE 3 : Configuration Initiale (5 minutes)**

#### 3A. Télécharger les Données
- Cliquez **"📥 Télécharger l'historique & Initialiser"**
- ⏱️ Attendez 2-3 minutes

#### 3B. Entraîner l'IA
- Cliquez **"🏋️ Entraîner (from scratch)"**
- ⏱️ Attendez 2-3 minutes

### ✅ **ÉTAPE 4 : Premiers Tickets (3 minutes)**

#### 4A. Configuration Rapide (Sidebar)
- **Nombre de tickets** : `10`
- **Méthode** : `hybrid` (recommandé pour débuter)
- **Ensemble** : ☑️ **Coché**

#### 4B. Génération
- Cliquez **"🎲 Générer les tickets"**
- ⏱️ Attendez 10 secondes

#### 4C. Résultat
Vous obtenez 10 tickets avec scores de confiance !

---

## 🎯 Configuration Recommandée pour Débutants

### 📊 Paramètres Optimaux

```
┌─ SIDEBAR (Paramètres) ─────────────────┐
│ Nombre de tickets: 10                   │
│ Méthode: hybrid                         │
│ Graine: 42                             │
│ ☑️ Utiliser ensemble: OUI               │
└─────────────────────────────────────────┘
```

### 🎫 Tickets Attendus

```
🎫 Ticket 1 ⚡
   03 - 17 - 24 - 38 - 47
   ⭐ 04 - 11
   📊 Confiance: 72.5% (Élevée)
   🎯 Méthode: enhanced_hybrid
```

---

## ⚠️ Points d'Attention Rapide

### 🚨 **Si ça ne marche pas :**

1. **Port occupé ?**
   ```powershell
   streamlit run ui\streamlit_app.py --server.port 8502
   ```

2. **Erreur Python ?**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Pas de données ?**
   - Vérifiez votre connexion Internet
   - Réessayez "📥 Télécharger l'historique"

### 💡 **Premiers Conseils**

- ✅ **Commencez avec `hybrid`** - le plus équilibré
- ✅ **Gardez l'ensemble activé** - meilleures prédictions  
- ✅ **Notez vos résultats** - pour analyser vos préférences
- ⚠️ **Jouez responsable** - Aucune garantie de gain !

---

## 🎯 Une Fois Lancé...

### 📊 **Navigation Intuitive**
L'interface est organisée de haut en bas dans l'ordre d'utilisation :
1. **Initialisation** (une seule fois)
2. **Entraînement** (une seule fois, puis occasionnel)
3. **Probabilités** (consultation)
4. **Génération de tickets** ⭐ (utilisation principale)

### 🔄 **Utilisation Quotidienne**
Une fois configuré, générer des tickets prend **30 secondes** :
1. Ajustez les paramètres dans la sidebar si souhaité
2. Cliquez "🎲 Générer les tickets"
3. Analysez les scores de confiance
4. Exportez vos favoris

### 📈 **Maintenance Hebdomadaire**
- **"🔄 Mise à jour incrémentale"** pour récupérer les nouveaux tirages
- Optionnel : **"🤖 Ensemble de modèles"** pour améliorer les prédictions

---

## 🎉 **Vous êtes prêt !**

Avec ce guide express, vous devriez avoir vos premiers tickets générés par l'IA en **15 minutes maximum**. 

Pour approfondir, consultez le **Guide Utilisateur Complet** (`GUIDE_UTILISATEUR_COMPLET.md`).

**🍀 Bonne chance ! 🍀**

---
*Guide Express créé le 5 octobre 2025*