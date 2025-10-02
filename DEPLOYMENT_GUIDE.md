# 💻 Guide de Récupération - EuroMillions ML Predictor

## 🎯 Comment récupérer le programme sur un autre ordinateur

### 🚀 **Méthode Express (Recommandée)**

#### **Windows - Installation en 1 clic**
1. **Téléchargez** le script d'installation : [install_from_github.bat](install_from_github.bat)
2. **Double-cliquez** sur le fichier
3. **Suivez** les instructions automatiques
4. **C'est tout !** L'interface se lance automatiquement

#### **Prérequis**
- **Git** : https://git-scm.com/download/win
- **Python 3.8+** : https://www.python.org/downloads/
- **Connexion Internet**

### 🛠️ **Méthode Manuelle Complète**

#### **1. Cloner le repository**
```bash
# Ouvrir PowerShell/Terminal
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
cd euromillions-ml-predictor
```

#### **2. Installation des dépendances**
```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows :
.venv\Scripts\activate
# macOS/Linux :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### **3. Configuration**
```bash
# Copier la configuration
cp .env.example .env

# Optionnel : personnaliser .env
notepad .env  # Windows
nano .env     # Linux/macOS
```

#### **4. Initialisation des données**
```bash
# Option A : Importer des CSV FDJ
python import_fdj_special.py

# Option B : Téléchargement automatique
python scraper.py

# Option C : Interface web (ajout manuel)
streamlit run ui/streamlit_app.py
```

#### **5. Entraînement des modèles**
```bash
python cli_train.py train
```

#### **6. Lancement**
```bash
# Windows
start_euromillions.bat

# Universel
streamlit run ui/streamlit_app.py
```

### 🐳 **Méthode Docker (Avancée)**

#### **Installation avec Docker**
```bash
# Cloner le repo
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
cd euromillions-ml-predictor

# Créer l'image Docker
docker build -t euromillions-ml .

# Lancer le container
docker run -p 8501:8501 euromillions-ml
```

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.address", "0.0.0.0"]
```

### 🌐 **Accès depuis n'importe quel ordinateur**

#### **Repository GitHub**
- **URL** : https://github.com/ProfesseurFalken/euromillions-ml-predictor
- **Status** : Privé (accès avec votre compte GitHub)
- **Branches** : `main` (principale)

#### **Commandes de synchronisation**
```bash
# Récupérer les dernières mises à jour
git pull origin main

# Voir l'historique des versions
git log --oneline

# Revenir à une version précédente
git checkout v1.0.0
```

### 📱 **Installation Multi-Plateforme**

#### **Windows 10/11**
```powershell
# PowerShell
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
cd euromillions-ml-predictor
.\bootstrap.ps1  # Si disponible
```

#### **macOS**
```bash
# Terminal
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
cd euromillions-ml-predictor
chmod +x bootstrap.sh
./bootstrap.sh
```

#### **Linux (Ubuntu/Debian)**
```bash
# Installer les dépendances système
sudo apt update
sudo apt install python3-pip python3-venv git

# Cloner et installer
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
cd euromillions-ml-predictor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🔄 **Migration des données**

#### **Transférer vos données existantes**
```bash
# Sur l'ancien ordinateur
# Exporter la base de données
python -c "from repository import EuromillionsRepository; repo = EuromillionsRepository(); repo.all_draws_df().to_csv('mes_tirages.csv')"

# Sur le nouvel ordinateur
# Importer vos données
python import_fdj_special.py mes_tirages.csv
```

#### **Synchronisation des modèles**
```bash
# Copier le dossier models/ depuis l'ancien ordinateur
# Ou re-entraîner sur le nouvel ordinateur
python cli_train.py train
```

### ⚡ **Script d'installation rapide**

Créez un fichier `quick_install.ps1` :
```powershell
# Quick install script
Write-Host "🚀 Installation EuroMillions ML Predictor" -ForegroundColor Green

# Clone repository
git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
Set-Location euromillions-ml-predictor

# Setup Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Launch
Write-Host "✅ Installation terminée!" -ForegroundColor Green
.\start_euromillions.bat
```

### 🔧 **Résolution de problèmes**

#### **Erreurs courantes**

**1. Git non installé**
```bash
# Erreur : 'git' n'est pas reconnu
# Solution : Installer Git depuis https://git-scm.com/
```

**2. Python non trouvé**
```bash
# Erreur : 'python' n'est pas reconnu  
# Solution : Installer Python depuis https://python.org/
# Ou utiliser python3 sur macOS/Linux
```

**3. Repository privé inaccessible**
```bash
# Erreur : Permission denied
# Solution : Se connecter à GitHub
git config --global user.name "VotreNom"
git config --global user.email "votre@email.com"
```

**4. Dépendances manquantes**
```bash
# Solution : Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

### 🎯 **Checklist de déploiement**

- [ ] Git installé
- [ ] Python 3.8+ installé
- [ ] Connexion Internet active
- [ ] Accès au repository GitHub
- [ ] Dossier de destination choisi
- [ ] Droits d'écriture sur le dossier

### 📚 **Documentation complète**

Une fois installé, consultez :
- `README.md` - Vue d'ensemble
- `INSTALLATION.md` - Guide détaillé
- `USAGE.md` - Manuel d'utilisation
- `GUIDE_MAINTENANCE.md` - Maintenance

---

🎉 **Votre EuroMillions ML Predictor est maintenant disponible partout !**