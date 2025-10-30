# 🏗️ Architecture du Projet

## 📁 Structure des Dossiers

```
Doc_review/
├── main_review.py              # 🚀 Point d'entrée principal
├── doc_reviewer.py              # (Ancienne version, conservée)
│
├── .env                         # 🔑 Configuration API
├── style_config.yaml            # 🎨 Configuration des styles
├── requirements.txt             # 📦 Dépendances Python
│
├── core/                        # 💼 Traitement des documents
│   ├── base/                    # Classe abstraite commune
│   │   ├── document_processor.py
│   │   └── document_context.py
│   │
│   ├── word/                    # 📄 Traitement Word
│   │   └── word_processor.py
│   │
│   ├── powerpoint/              # 🎬 Traitement PowerPoint
│   │   └── ppt_processor.py
│   │
│   ├── image_handler.py         # 🖼️ Gestion des images
│   ├── style_extractor.py       # 🔍 Extraction des styles
│   └── style_mapper.py          # 🗺️ Mapping des styles
│
├── features/                    # ✨ Fonctionnalités IA
│   ├── ai_processor.py          # 🤖 Intégration OpenAI
│   ├── language_detector.py     # 🌐 Détection de langue
│   ├── style_uniformizer.py     # 🎨 Uniformisation
│   ├── element_resolver.py      # 🎯 Identification ciblée
│   └── input_parser.py          # 📝 Parsing des commandes
│
├── change_logging/              # 📊 Historique des modifications
│   ├── logger.py                # Enregistrement des logs
│   └── diff_analyzer.py         # Analyse des différences
│
├── utils/                       # 🛠️ Utilitaires
│   └── config.py                # Gestion configuration
│
└── LOGS/                        # 📂 Fichiers de logs
```

---

## 🔄 Flux d'Exécution

### 1. Démarrage (`main_review.py`)

```python
# L'utilisateur lance l'application
python main_review.py

# Le système :
# 1. Charge la configuration (.env)
# 2. Demande le chemin du document
# 3. Détecte le format (Word ou PowerPoint)
# 4. Charge le processeur approprié
```

### 2. Chargement du Document

```python
# Word
WordProcessor.load_document()
  → Charge le .docx avec python-docx
  → Détecte la langue
  → Compte les images
  → Calcule les pages (une seule fois)

# PowerPoint
PowerPointProcessor.load_document()
  → Charge le .pptx avec python-pptx
  → Détecte la langue
  → Analyse la structure des slides
```

### 3. Traitement d'une Commande

#### A. Commande Globale (ex: `corrige`)

```python
processor.process_document(instruction)
  ↓
  Pour chaque paragraphe/shape :
    1. Extraire le texte
    2. Extraire les styles (bold, italic, etc.)
    3. Envoyer à l'IA
    4. Recevoir le texte modifié
    5. Mapper les styles sur le nouveau texte
    6. Appliquer avec préservation du format
    7. Vérifier les images (Word)
    8. Logger les changements
```

#### B. Commande Ciblée (ex: `"page 3, corrige le titre"`)

```python
1. InputParser : Parse la commande avec LLM
   → Identifie : page=3, target="titre", action="corrige"

2. DocumentContext : Extrait la structure du document
   → Utilise le cache des pages (Word)
   → Filtre pour ne garder que la page 3 et voisines

3. ElementResolver : Identifie l'élément précis avec LLM
   → Envoie la structure filtrée au LLM
   → Reçoit : paragraphe_num=15, confiance=95%

4. Processor : Traite UNIQUEMENT cet élément
   → process_targeted(target, instruction)
   → Même logique que global mais pour 1 élément
```

### 4. Sauvegarde

```python
processor.save_document()
  → Sauvegarde avec suffix "_modifié"
  → Préserve le format original
```

---

## 🧩 Modules Clés

### `core/base/document_processor.py`
**Rôle** : Interface abstraite commune à Word et PowerPoint

**Méthodes** :
- `load_document()` : Charge le fichier
- `save_document()` : Sauvegarde
- `process_document()` : Traitement global
- `process_targeted()` : Traitement ciblé
- `uniformize_styles()` : Uniformisation

### `features/ai_processor.py`
**Rôle** : Communication avec l'API OpenAI

**Fonctionnalités** :
- Envoi de texte à corriger/traduire/améliorer
- Gestion du contexte de conversation
- Détection des traductions inutiles
- Validation des instructions

### `core/style_mapper.py`
**Rôle** : Préservation intelligente du formatage

**Fonctionnement** :
1. Extrait tous les styles du texte original (positions + propriétés)
2. Utilise `difflib` pour trouver les correspondances avec le nouveau texte
3. Mappe les styles sur les positions correspondantes
4. Gère les styles uniformes (tout en gras) et mixtes

### `change_logging/logger.py`
**Rôle** : Traçabilité des modifications

**Contenu des logs** :
- Horodatage
- Paragraphe/Shape modifié
- Texte avant
- Texte après
- Instruction appliquée
- Type (global/ciblé)

---

## 🎯 Différences Word vs PowerPoint

### Navigation dans le Document

**Word** :
```python
document.paragraphs
  → paragraph.runs
    → run.text, run.font
```

**PowerPoint** :
```python
presentation.slides
  → slide.shapes (avec texte)
    → shape.text_frame.paragraphs
      → paragraph.runs
        → run.text, run.font  # ← Identique à Word !
```

### Préservation du Format

**Commun** (via `StyleMapper`) :
- Bold, italic, underline
- Font name, size
- Color

**Spécifique Word** :
- Images dans les runs (backup XML)
- Styles de paragraphe

**Spécifique PowerPoint** :
- Alignement des text_frames
- Bullet points et indentations
- Niveaux de paragraphes

---

## 🔧 Points d'Extension

### Ajouter un Nouveau Format (ex: PDF)

1. Créer `core/pdf/pdf_processor.py` héritant de `DocumentProcessor`
2. Implémenter les méthodes abstraites
3. Ajouter la détection dans `main_review.py` :
```python
elif extension == '.pdf':
    processor = PDFProcessor(...)
```

### Ajouter une Nouvelle Commande

Dans `main_review.py` :
```python
elif user_input.lower() == 'ma_commande':
    processor.process_document("Mon instruction")
```

### Ajouter une Fonctionnalité IA

1. Créer un module dans `features/`
2. Utiliser `AIProcessor` pour communiquer avec l'API
3. Intégrer dans les processeurs

---

## 💡 Principes de Design

### 1. **Séparation des Responsabilités**
- `core/` : Manipulation des documents
- `features/` : Intelligence artificielle
- `change_logging/` : Traçabilité
- `utils/` : Configuration

### 2. **Abstraction**
- `DocumentProcessor` définit l'interface
- Word et PowerPoint l'implémentent à leur façon
- Le code appelant ne voit que l'interface

### 3. **Réutilisabilité**
- `AIProcessor`, `StyleMapper`, `LanguageDetector` : agnostiques du format
- Utilisables pour Word, PowerPoint, et futurs formats

### 4. **Performance**
- Calcul des pages : **une seule fois** au chargement (cache)
- Extraction ciblée : ne charge que les sections pertinentes
- Économie d'API : 90-97% sur les commandes ciblées

---

## 📚 Pour Aller Plus Loin

- **Détails sur le ciblage** : `TARGETED_PROCESSING.md`
- **Guide PowerPoint** : `GUIDE_POWERPOINT.md`
- **Calibration pages** : `calibrate_pages.py` + guide
- **Configuration** : `style_config.yaml` + `.env`

---

**Architecture Modulaire** - Extensible et Maintenable
