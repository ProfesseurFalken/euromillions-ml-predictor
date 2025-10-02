# 🔄 Guide de Mise à Jour des Tirages EuroMillions

## 🎯 **Méthodes de mise à jour disponibles :**

### **Option 1: 🚀 Automatique (Recommandée)**
```bash
# Activer l'environnement
.\.venv\Scripts\activate.ps1

# Lancer la mise à jour automatique
python update_tirages.py
```

### **Option 2: 📄 Import CSV Manuel**
```bash
# 1. Télécharger les nouveaux CSV FDJ
# 2. Les placer dans ce dossier  
# 3. Lancer l'import
python import_fdj_special.py
```

### **Option 3: 🌐 Scraping Web**
```bash
# Récupération automatique depuis les sites officiels
python hybrid_scraper.py
```

---

## 📅 **Fréquence de mise à jour recommandée :**

- **🔴 Urgente** : Si > 7 jours de retard
- **🟡 Recommandée** : Si > 3 jours de retard  
- **🟢 Optionnelle** : Si < 3 jours de retard

**🎯 Tirages EuroMillions :** Mardi et Vendredi chaque semaine

---

## 🛠️ **Procédure complète de mise à jour :**

### **1️⃣ Vérification**
```bash
python check_tirage_freshness.py
```

### **2️⃣ Mise à jour**
```bash
python update_tirages.py
```

### **3️⃣ Re-entraînement**
```bash
python cli_train.py train
```

### **4️⃣ Vérification finale**
```bash
python check_tirage_freshness.py
python cli_train.py score --top 10
```

---

## 🔗 **Sources officielles pour vérification :**

- 🇫🇷 **FDJ**: https://www.fdj.fr/jeux/jeux-de-tirage/euromillions
- 🇪🇺 **Euro-Millions**: https://www.euro-millions.com/fr/resultats  
- 🇬🇧 **UK National Lottery**: https://www.national-lottery.co.uk/results/euromillions

---

## ⚡ **Script de mise à jour automatique :**

Le fichier `update_tirages.py` vous permet de :
- ✅ Vérifier l'état actuel
- 📥 Récupérer les nouveaux tirages  
- 🗃️ Les intégrer à la base
- 🤖 Re-entraîner le modèle
- ✅ Valider le résultat

**🚀 Une seule commande pour tout mettre à jour !**