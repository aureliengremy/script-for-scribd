# 📖 Exemple d'utilisation - Interface Scribd

## 🚀 Utilisation de l'interface complète

### 1. Lancer l'interface

```bash
python3 scribd_interface.py
```

### 2. Saisir les informations

L'interface vous demandera :

```
============================================================
🚀 INTERFACE SCRIBD - SCRAPER COMPLET
============================================================
Extrait, trie et convertit en PDF les documents Scribd
3 étapes automatisées : Extraction → Tri → PDF → Cleanup
============================================================

📝 CONFIGURATION
------------------------------
🌐 URL du document Scribd : https://www.scribd.com/document/845261765/Progressions-Classics-Vol-1-1
📄 Nom du PDF de sortie (ex: 'Mon Document.pdf') : Progressions Classics Vol 1.pdf
📊 Nombre max de pages à traiter (Entrée pour 100) : 100
```

### 3. Confirmation et lancement

```
📋 RÉSUMÉ
   🌐 URL : https://www.scribd.com/document/845261765/Progressions-Classics-Vol-1-1
   📄 PDF : Progressions Classics Vol 1.pdf
   📊 Max pages : 100

🚀 Lancer le scraping ? (O/n) : o
```

### 4. Workflow automatique

```
==================================================
📥 ÉTAPE 1/3 : EXTRACTION DES LIENS
==================================================
🌐 Chargement de la page...
🔄 Scroll dynamique pour charger toutes les pages...
   📄 83 pages détectées (tentative 15)
✅ Scroll terminé : 83 pages trouvées
✅ 83 liens extraits avec succès

==================================================
🔢 ÉTAPE 2/3 : TRI DES LIENS
==================================================
🔢 Tri des liens par numéro de page...
📄 Pages 1 à 83
✅ 83 liens triés par numéro de page

==================================================
📄 ÉTAPE 3/3 : CRÉATION DU PDF
==================================================
📥 Téléchargement de 83 images...
   📥 10/83 images téléchargées
   📥 20/83 images téléchargées
   ...
   📥 83/83 images téléchargées
📄 Création du PDF avec 83 pages...
🧹 Nettoyage des fichiers JSON temporaires...

🎉 WORKFLOW TERMINÉ AVEC SUCCÈS !
📁 PDF créé : Progressions Classics Vol 1.pdf
📏 Taille : 9.8 MB
```

### 5. Résultat final

```
✅ SUCCÈS TOTAL en 3m 45s !
📁 Votre PDF : Progressions Classics Vol 1.pdf

============================================================
🔄 Scraper un autre document ? (o/N) : n

👋 Au revoir ! Merci d'avoir utilisé l'interface Scribd
```

## 🎯 Utilisation rapide (version courte)

Pour un usage rapide avec les scripts individuels :

```bash
# 1. Extraire et trier automatiquement
python3 enhanced_lazy_scraper.py
# Suivre les instructions, entrer : 50 (pour 50 pages max)
# Crée automatiquement : scribd_sorted_links.json

# 2. Créer PDF avec cleanup automatique
python3 pdf_creator.py --pdf "Mon Document.pdf" --cleanup
# Supprime automatiquement les fichiers JSON temporaires
```

## 💡 Conseils d'utilisation

### Noms de PDF suggérés
- `Titre du Document.pdf`
- `Livre - Chapitre 1.pdf`
- `Guide Complet 2024.pdf`

### Nombre de pages optimal
- **10-20** pour des tests rapides
- **50-100** pour des documents complets
- **200+** pour de très gros documents

### URLs supportées
- `https://www.scribd.com/document/[ID]/[titre]`
- `https://fr.scribd.com/document/[ID]/[titre]`
- Tous les domaines Scribd

## 📁 Fichiers générés

Après utilisation, vous aurez :

```
script-for-scribd/
├── Progressions Classics Vol 1.pdf    # 📄 Votre PDF final
└── [scripts originaux...]
```

**Les fichiers JSON temporaires sont automatiquement supprimés !**
**Le PDF est le seul fichier que vous devez conserver.**

---

🎉 **Votre document Scribd est maintenant un PDF prêt à utiliser !**