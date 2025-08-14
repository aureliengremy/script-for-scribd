# 🚀 Scraper Scribd Complet

Interface simple pour télécharger et convertir des documents Scribd en PDF.

## 📋 Fonctionnalités

- ✅ **Extraction automatique** des images avec lazy loading
- ✅ **Tri intelligent** par numéro de page
- ✅ **Création PDF** haute qualité
- ✅ **Interface utilisateur** simple
- ✅ **Workflow complet** en 3 étapes
- ✅ **Cleanup automatique** des fichiers temporaires

## 🛠️ Installation

```bash
# Installer les dépendances
pip3 install selenium beautifulsoup4 Pillow requests

# ChromeDriver requis pour Selenium
# Installer via Homebrew (macOS) :
brew install chromedriver

# Ou télécharger depuis : https://chromedriver.chromium.org/
```

## 🚀 Utilisation

### Interface complète (recommandée)

```bash
python3 scribd_interface.py
```

L'interface vous demandera :
- 🌐 **URL du document Scribd**
- 📄 **Nom du PDF de sortie**  
- 📊 **Nombre max de pages à traiter**

### Scripts individuels

#### 1. Extraction des liens

```bash
python3 enhanced_lazy_scraper.py
```

#### 2. Création PDF avec cleanup automatique

```bash
# Mode interactif
python3 pdf_creator.py --interactive

# Avec paramètres et cleanup
python3 pdf_creator.py --pdf "Mon Document.pdf" --cleanup
python3 pdf_creator.py -j liens.json -p "Livre.pdf" --cleanup
```

## 📁 Structure des fichiers

```
script-for-scribd/
├── scribd_interface.py          # 🎯 Interface principale
├── enhanced_lazy_scraper.py     # Extraction des liens
├── pdf_creator.py               # Création PDF avec cleanup
├── demo_interface.py            # Démonstration
├── requirements.txt             # Dépendances Python
├── README.md                    # Ce fichier
└── exemple_utilisation.md       # Guide détaillé
```

## 🔧 Workflow automatique

```mermaid
graph LR
    A[URL Scribd] --> B[Extraction]
    B --> C[Tri par page]
    C --> D[Téléchargement]
    D --> E[PDF final]
```

1. **📥 Extraction** : Scroll automatique et récupération des liens d'images
2. **🔢 Tri** : Classement par numéro de page (1, 2, 3...)
3. **📄 PDF** : Téléchargement des images et création du PDF

## 💡 Exemples d'utilisation

### Interface simple

```bash
python3 scribd_interface.py
```

**Entrez :**
- URL : `https://www.scribd.com/document/845261765/Progressions-Classics-Vol-1-1`
- PDF : `Progressions Classics Vol 1.pdf`
- Pages : `100`

**Résultat :** PDF complet avec toutes les pages dans l'ordre

### Scripts séparés

```bash
# 1. Extraire les liens (avec tri automatique)
python3 enhanced_lazy_scraper.py
# Crée : scribd_sorted_links.json

# 2. Créer le PDF avec cleanup
python3 pdf_creator.py --pdf "Mon Document.pdf" --cleanup
# Crée : Mon Document.pdf et supprime les fichiers JSON temporaires
```

## 🎯 Sélecteur JavaScript utilisé

Le scraper utilise le sélecteur CSS découvert :

```javascript
document.querySelectorAll('.newpage .image_layer .absimg')
```

## ⚙️ Options avancées

### PDF Creator

```bash
# Aide complète
python3 pdf_creator.py --help

# Options disponibles
python3 pdf_creator.py -j source.json -p "output.pdf" --temp-dir temp/
```

### Interface paramétrable

Modifiez `demo_interface.py` pour des tests automatisés.

## 📊 Statistiques typiques

- **83 pages** récupérées en moyenne
- **9-12 MB** pour un document complet
- **2-5 minutes** de traitement total

## 🐛 Dépannage

### ChromeDriver introuvable

```bash
# macOS avec Homebrew
brew install chromedriver

# Ou ajouter au PATH
export PATH=$PATH:/path/to/chromedriver
```

### Timeout des requêtes

Augmentez les délais dans le script si votre connexion est lente.

### Peu d'images extraites

- Vérifiez l'URL du document
- Augmentez le nombre max de pages
- Le document peut avoir moins de pages que prévu

## 🎉 Résultat final

Vous obtenez un **PDF haute qualité** avec :
- ✅ Toutes les pages dans l'ordre
- ✅ Images en résolution originale
- ✅ Fichier optimisé et compact
- ✅ Prêt à imprimer ou partager

---

**🚀 Interface créée pour simplifier le scraping Scribd !**