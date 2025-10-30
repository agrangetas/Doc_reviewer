# 📄 Document Reviewer - Architecture Modulaire

Outil de révision automatique de documents Word avec IA (OpenAI) et uniformisation des styles.

## 🚀 Démarrage Rapide

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Créez un fichier `.env` :

```env
OPENAI_API_KEY=sk-votre-cle-api
OPENAI_MODEL=gpt-4o
```

### 3. Utilisation

```bash
python doc_reviewer.py
```

```
➤ Chemin du document: mon_document.docx
➤ Votre commande: corrige
➤ Votre commande: uniformise
➤ Votre commande: save
```

---

## ✨ Fonctionnalités

### 🔍 Correction Orthographique
- Détection automatique de la langue
- Correction orthographe et grammaire
- Préservation du formatage (bold, italic, etc.)
- Protection des images

### 🌐 Traduction
- Traduction paragraphe par paragraphe
- Maintien du contexte
- Préservation du formatage

### ✨ Amélioration
- Amélioration du style et de la clarté
- Conservation du sens original

### 🎨 Uniformisation des Styles (Nouveau !)
- Uniformise police et tailles automatiquement
- **Préserve les emphases intentionnelles** (bold/italic sur 1 mot)
- Détecte et traite les titres séparément
- Configurable via `style_config.yaml`

---

## 📋 Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `corrige` | Corrige l'orthographe et la grammaire |
| `traduis [langue]` | Traduit le document |
| `améliore` | Améliore le style et la clarté |
| `uniformise` | Uniformise les styles du document |
| `save` | Sauvegarde le document modifié |
| `quit` | Quitte l'application |

---

## 🎯 Exemple d'Utilisation

```bash
$ python doc_reviewer.py

➤ Chemin du document: rapport.docx

✓ Document chargé: rapport.docx
  Nombre de paragraphes: 127
  Modèle OpenAI: gpt-4o
  Langue détectée: Français
  Images trouvées: 3 image(s) dans 2 paragraphe(s)

➤ Votre commande: corrige

🔄 Traitement: Corrige...
Paragraphe 1/127... ✓ Modifié
Paragraphe 2/127... ○ Inchangé
...
✓ Traitement terminé ! (45 paragraphes modifiés)
✅ TOUTES LES IMAGES SONT PRÉSERVÉES !

➤ Votre commande: uniformise

UNIFORMISATION DES STYLES
==========================
Analyse du document:
  Police majoritaire: Calibri (87.3%)
  Taille texte majoritaire: 11pt

Appliquer ces modifications ? (o/n): o

✓ Uniformisation terminée !
  Paragraphes modifiés: 82
  Emphases préservées: 12

➤ Votre commande: save
💾 Document sauvegardé: rapport_modifié.docx
```

---

## 📁 Architecture

```
Doc_review/
├── core/                    # Traitement des documents
│   ├── image_handler.py     # Gestion et protection des images
│   ├── style_extractor.py   # Extraction des styles
│   └── style_mapper.py      # Mapping intelligent des styles
│
├── features/                # Fonctionnalités principales
│   ├── ai_processor.py      # Traitement avec OpenAI
│   ├── language_detector.py # Détection de langue
│   └── style_uniformizer.py # Uniformisation des styles
│
├── change_logging/          # Système de logging
│   ├── logger.py            # Logger principal
│   └── diff_analyzer.py     # Analyse des différences
│
├── utils/                   # Utilitaires
│   └── config.py            # Configuration (.env + YAML)
│
├── doc_reviewer.py          # Point d'entrée principal
├── style_config.yaml        # Configuration uniformisation
└── requirements.txt         # Dépendances
```

---

## ⚙️ Configuration

### `.env` - Configuration de l'API

```env
OPENAI_API_KEY=sk-xxxxx        # Obligatoire
OPENAI_MODEL=gpt-4o            # Optionnel (défaut: gpt-4o)
```

### `style_config.yaml` - Configuration des Styles

```yaml
font:
  name: auto                   # 'auto' ou 'Calibri', 'Arial', etc.

sizes:
  text_normal: auto            # 'auto' ou 11, 12, etc.
  heading_1: auto

preserve:
  intentional_emphasis: true   # Préserver bold/italic sur 1 mot
  quotes: true                 # Préserver les citations

heading_detection:
  use_word_styles: true        # Utiliser les styles Word
  use_heuristics: true         # Détection par taille/bold

application:
  ask_confirmation: true       # Demander confirmation
```

---

## 📊 Logs

Toutes les modifications sont enregistrées dans `LOGS/nom_document_YYYYMMDD.txt`

Contenu des logs :
- Avant/après pour chaque modification
- Différences détaillées pour les corrections
- Horodatage de chaque changement
- Statistiques de traitement

---

## 🛡️ Protection des Données

### Images
- Détection automatique des images
- Backup XML avant modification
- Restauration si images perdues
- Vérification post-traitement

### Formatage
- Extraction précise des styles (bold, italic, underline, etc.)
- Mapping intelligent avec `difflib`
- Préservation des emphases intentionnelles
- Conservation des propriétés de paragraphe

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | Ce fichier |
| `LIRE_EN_PREMIER.md` | Guide de démarrage rapide |
| `GUIDE_UTILISATION_V2.md` | Manuel complet avec exemples |
| `STATUT_REFACTORING.md` | Détails techniques de l'architecture |
| `NOUVELLE_ARCHITECTURE.md` | Guide de l'architecture modulaire |

---

## 🔧 Dépendances

- `python-docx==1.1.2` - Manipulation de documents Word
- `openai==1.12.0` - API OpenAI
- `python-dotenv==1.0.1` - Gestion variables d'environnement
- `httpx==0.27.0` - Client HTTP
- `langdetect==1.0.9` - Détection de langue
- `PyYAML==6.0.1` - Configuration YAML

---

## 🆘 Dépannage

### Erreur : Module 'yaml' not found
```bash
pip install PyYAML==6.0.1
```

### Erreur : API Key not found
Vérifiez votre fichier `.env` :
```env
OPENAI_API_KEY=sk-votre-cle
```

### Images disparues
Le système protège automatiquement les images avec backup/restore.
Si un paragraphe contient des images, il sera restauré si les images sont perdues.

---

## 🎓 Avantages

✅ **Architecture modulaire** - Code clair et maintenable  
✅ **Protection des images** - Backup/restore automatique  
✅ **Mapping intelligent** - Préservation précise du formatage  
✅ **Logs détaillés** - Traçabilité complète  
✅ **Uniformisation intelligente** - Préserve les emphases intentionnelles  
✅ **Configuration flexible** - .env + YAML  

---

## 📝 Licence

MIT

---

## 👨‍💻 Développement

### Tests

```bash
python -c "from utils.config import Config; from core.image_handler import ImageHandler; print('✅ Tous les modules OK')"
```

### Structure du Code

Chaque module a une responsabilité unique :
- `core/` - Traitement bas niveau des documents
- `features/` - Fonctionnalités métier
- `change_logging/` - Journalisation
- `utils/` - Utilitaires transverses

---

**Version 2.0 - Architecture Modulaire**

Pour plus de détails, consultez `GUIDE_UTILISATION_V2.md`

