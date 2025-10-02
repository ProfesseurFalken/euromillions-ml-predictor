# 🚀 Guide de Lancement EuroMillions ML

## Options de lancement disponibles

### 🏃‍♂️ Lancement rapide (RECOMMANDÉ)
```bash
.\launch_quick.bat
```
- ✅ Trouve automatiquement un port libre
- ✅ Ouvre le navigateur automatiquement
- ✅ Gestion des erreurs de port

### 📋 Menu interactif complet
```bash
.\menu.bat
```
- ✅ Accès à toutes les fonctions
- ✅ Vérification du statut
- ✅ Mise à jour des données
- ✅ Entraînement des modèles

### 🛠️ Lancement manuel
```bash
# Activer l'environnement
.\.venv\Scripts\activate

# Lancer Streamlit
python -m streamlit run ui\streamlit_app.py --server.port 8501
```

## 🔧 En cas de problème

### Port occupé
Si vous voyez "Port 8501 is already in use" :
- Le script `launch_quick.bat` trouve automatiquement un port libre
- Ou essayez manuellement : `--server.port 8502`

### Environnement virtuel manquant
```bash
# Recréer l'environnement
.\bootstrap.ps1
```

### Streamlit pas installé
```bash
.\.venv\Scripts\activate
pip install streamlit
```

## 🎯 Fonctionnalités dans l'interface

### ➕ Ajouter des tirages manuellement
1. Ouvrez l'interface Streamlit
2. Section "➕ Ajouter un tirage manuellement"
3. Saisissez date + numéros + étoiles
4. Cliquez "💾 Ajouter le tirage"

### 📄 Importer des CSV FDJ
1. Section "📄 Import CSV"
2. Téléchargez votre fichier CSV
3. Prévisualisez le contenu
4. Cliquez "📥 Importer les données"

### 🎲 Générer des prédictions
1. Configurez les paramètres dans la barre latérale
2. Cliquez "🎲 Générer les tickets"
3. Téléchargez au format CSV ou JSON

## 🎊 Accès à l'interface

Une fois lancée, l'interface est disponible sur :
- **Local** : http://localhost:8501 (ou port affiché)
- **Réseau** : http://[votre-ip]:8501

---
**Système opérationnel ✅ | Prêt pour les prédictions 🎯**