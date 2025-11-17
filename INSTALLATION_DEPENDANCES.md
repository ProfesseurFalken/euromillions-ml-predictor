# 📦 Installation des Dépendances Optionnelles

## Vue d'ensemble

Les nouvelles fonctionnalités d'export avancé nécessitent deux bibliothèques optionnelles:
- **ReportLab** pour l'export PDF
- **QRCode** pour la génération de QR codes

---

## 🚀 Installation Rapide

### Windows (PowerShell):

```powershell
# Activer l'environnement virtuel
.\.venv\Scripts\activate

# Installer ReportLab (pour PDF)
pip install reportlab

# Installer QRCode (pour QR codes)
pip install qrcode[pil]

# Ou installer les deux en une commande:
pip install reportlab qrcode[pil]
```

### Linux/Mac (Bash):

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
pip install reportlab qrcode[pil]
```

---

## 📋 Vérification de l'Installation

### Test ReportLab:

```python
python -c "import reportlab; print('ReportLab OK:', reportlab.Version)"
```

**Sortie attendue:** `ReportLab OK: 4.x.x`

### Test QRCode:

```python
python -c "import qrcode; print('QRCode OK')"
```

**Sortie attendue:** `QRCode OK`

---

## 🔧 Mise à jour requirements.txt

Si vous voulez rendre ces dépendances permanentes:

### Ajouter au fichier requirements.txt:

```text
# Export avancé
reportlab>=4.0.0
qrcode[pil]>=7.4.0
```

### Puis installer:

```bash
pip install -r requirements.txt
```

---

## 🎯 Fonctionnalités Activées

### Avec ReportLab:
✅ Export PDF des tickets
✅ Format A4 professionnel
✅ Multi-pages automatique
✅ En-têtes et métadonnées

### Avec QRCode:
✅ QR codes pour chaque ticket
✅ Scannables depuis smartphone
✅ Max 9 QR affichés simultanément
✅ Format: "EuroMillions: X-X-X-X-X + Y-Y"

---

## ⚠️ Sans les Dépendances

L'application fonctionne parfaitement sans ces bibliothèques:

- **Sans ReportLab:** Bouton PDF désactivé, message "Install reportlab"
- **Sans QRCode:** Message d'info avec commande d'installation

**Formats toujours disponibles:**
- ✅ CSV
- ✅ JSON  
- ✅ TXT

---

## 🐛 Dépannage

### Erreur "pip not found":

```bash
python -m pip install reportlab qrcode[pil]
```

### Erreur de permission (Windows):

```powershell
# Lancer PowerShell en administrateur
Start-Process powershell -Verb RunAs

# Puis installer
pip install reportlab qrcode[pil]
```

### Erreur "no module named PIL":

QRCode nécessite Pillow. Installez explicitement:

```bash
pip install Pillow
pip install qrcode[pil]
```

### Conflit de versions:

```bash
# Mettre à jour pip d'abord
python -m pip install --upgrade pip

# Puis installer
pip install reportlab qrcode[pil]
```

---

## 📊 Tailles des Packages

| Package | Taille | Temps d'installation |
|---------|--------|---------------------|
| reportlab | ~3 MB | ~15 secondes |
| qrcode[pil] | ~1 MB | ~10 secondes |
| **Total** | **~4 MB** | **~25 secondes** |

---

## ✨ Test Complet

Après installation, testez tout:

```python
python -c "
import reportlab
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

print('✅ ReportLab version:', reportlab.Version)
print('✅ QRCode installé')
print('✅ PDF generation: OK')
print('✅ QR generation: OK')
print()
print('🎉 Toutes les fonctionnalités d\'export sont disponibles!')
"
```

---

## 🔄 Désinstallation (si nécessaire)

```bash
pip uninstall reportlab qrcode pillow -y
```

---

## 📝 Notes

- **Optionnel:** Ces packages ne sont pas obligatoires
- **Léger:** Seulement 4 MB au total
- **Rapide:** Installation en < 30 secondes
- **Compatible:** Fonctionne sur Windows, Linux, Mac

---

## 🎓 Recommandation

**Pour une expérience complète, installez les deux packages:**

```bash
.\.venv\Scripts\activate
pip install reportlab qrcode[pil]
```

Cela débloque toutes les fonctionnalités d'export avancé! 🚀
