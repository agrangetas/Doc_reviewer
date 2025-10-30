# 📄 Document Reviewer - Architecture Modulaire

Outil de révision automatique de documents **Word** et **PowerPoint** avec IA (OpenAI) et uniformisation des styles.

**Formats supportés** : `.docx`, `.doc`, `.pptx`, `.ppt`

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

**Point d'entrée unifié (recommandé)** :
```bash
python main_review.py
```

**Ou spécifique à Word** :
```bash
python doc_reviewer.py
```

```
➤ Chemin du document: mon_document.docx  # ou .pptx
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
- Uniformise **police**, **tailles**, **couleurs** et **interlignes** automatiquement
- **Couleurs par niveau de titre** : cohérence entre titres de même niveau
- **Interlignes** : uniformise les paragraphes de texte (pas les titres)
- **Préserve les emphases intentionnelles** (bold/italic sur 1 mot)
- Détecte et traite les **titres** séparément (non modifiés en taille)
- Enregistre les actions dans les **logs**
- Configurable via `style_config.yaml`

**Note** : *L'uniformisation des puces est en développement (détection implémentée).*

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

## 📊 Support PowerPoint

Le support PowerPoint est **maintenant opérationnel** ! 

### Fonctionnalités disponibles pour PowerPoint :
- ✅ Correction orthographique et grammaticale
- ✅ Traduction
- ✅ Instructions personnalisées (amélioration, simplification, etc.)
- ✅ Conservation du formatage (bold, italic, couleur, taille, etc.)
- ✅ Détection automatique de la langue
- ✅ Logging détaillé des modifications
- ✅ Uniformisation de base (police et taille)
- ⚠️ Uniformisation avancée (couleurs, interlignes) - prochainement

### Utilisation :
```bash
python main_review.py
➤ Chemin du document (Word/PowerPoint): ma_presentation.pptx
```

Le système détecte automatiquement le format et utilise le processeur approprié.

---

## 🏗️ Architecture Modulaire

Le projet est organisé en modules :
- **`core/base/`** : Classe abstraite pour les processeurs
- **`core/word/`** : Processeur Word (.docx, .doc)
- **`core/powerpoint/`** : Processeur PowerPoint (.pptx, .ppt)
- **`features/`** : IA, détection de langue, uniformisation
- **`change_logging/`** : Logging des modifications
- **`utils/`** : Configuration (.env, YAML)

Voir `ARCHITECTURE.md` pour plus de détails.

---

## 🔧 Dépendances

- `python-docx==1.1.2` - Manipulation de documents Word
- `python-pptx==0.6.23` - Manipulation de présentations PowerPoint
- `openai==1.12.0` - API OpenAI
- `python-dotenv==1.0.1` - Gestion variables d'environnement
- `httpx==0.27.0` - Client HTTP
- `langdetect==1.0.9` - Détection de langue
- `PyYAML==6.0` - Configuration YAML

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

**Document Reviewer - Version Modulaire**

