# 🏗️ Architecture - Document Reviewer

## 📊 Structure Actuelle

```
Doc_review/
├── main_review.py              ⭐ Point d'entrée UNIFIÉ (Word + PowerPoint)
├── doc_reviewer.py              # Point d'entrée Word (conservé pour compatibilité)
│
├── core/
│   ├── base/                    # 🆕 Abstractions communes
│   │   └── document_processor.py  # Interface abstraite
│   │
│   ├── word/                    # 🔄 Implémentation Word (à migrer)
│   │   └── __init__.py
│   │
│   ├── powerpoint/              # 🆕 Implémentation PowerPoint (en dev)
│   │   ├── __init__.py
│   │   └── ppt_processor.py     # Stub avec notes d'implémentation
│   │
│   ├── image_handler.py         # Gestion images (Word actuellement)
│   ├── style_extractor.py       # ✅ Compatible Word & PowerPoint
│   └── style_mapper.py          # ✅ Compatible Word & PowerPoint
│
├── features/                    # ✅ Modules format-agnostiques
│   ├── ai_processor.py          # Traitement IA (100% réutilisable)
│   ├── language_detector.py     # Détection langue (100% réutilisable)
│   └── style_uniformizer.py     # Uniformisation (à adapter légèrement)
│
├── change_logging/              # ✅ Logging (100% réutilisable)
│   ├── logger.py
│   └── diff_analyzer.py
│
└── utils/                       # ✅ Utilitaires (100% réutilisable)
    └── config.py
```

---

## 🎯 Fonctionnement du Point d'Entrée Unifié

### `main_review.py`

```python
# 1. Détection automatique du format
extension = fichier.suffix  # .docx → Word, .pptx → PowerPoint

# 2. Routage vers le bon processeur
if extension in ['.docx', '.doc']:
    processor = DocumentReviewer()  # Word
elif extension in ['.pptx', '.ppt']:
    processor = PowerPointProcessor()  # PowerPoint

# 3. Interface commune
processor.load_document(fichier)
processor.process_document(instruction)
processor.uniformize_styles()
processor.save_document()
```

**Avantages** :
- ✅ Une seule commande pour tous les formats
- ✅ Détection automatique
- ✅ Interface identique
- ✅ Extensible (PDF, Excel...)

---

## 📦 Compatibilité des Modules

### Modules 100% Réutilisables (60%)

| Module | Word | PowerPoint | Notes |
|--------|------|------------|-------|
| `ai_processor.py` | ✅ | ✅ | Traite du texte brut |
| `language_detector.py` | ✅ | ✅ | Analyse du texte |
| `diff_analyzer.py` | ✅ | ✅ | Comparaison de textes |
| `config.py` | ✅ | ✅ | Configuration générique |
| `style_extractor.py` | ✅ | ✅ | Les `runs` sont identiques ! |
| `style_mapper.py` | ✅ | ✅ | Les `runs` sont identiques ! |

### Modules à Adapter (40%)

| Module | Status | Action Requise |
|--------|--------|----------------|
| `image_handler.py` | ⚠️ | Adapter pour shapes PPT |
| `style_uniformizer.py` | ⚠️ | Itération slides/shapes |
| `logger.py` | ⚠️ | "slide" au lieu de "paragraphe" |

---

## 🔄 Migration Progressive

### Phase 1 : ✅ TERMINÉ
- ✅ Structure de base créée
- ✅ Point d'entrée unifié (`main_review.py`)
- ✅ Abstraction `DocumentProcessor`
- ✅ Stub PowerPoint avec notes
- ✅ Requirements mis à jour

### Phase 2 : 🔄 EN COURS
- 🔄 Migration Word vers `core/word/`
- ⏳ Tests du point d'entrée unifié

### Phase 3 : ⏳ À VENIR
- ⏳ Implémentation PowerPoint complète
- ⏳ Adaptation `image_handler` pour PPT
- ⏳ Adaptation `style_uniformizer` pour PPT
- ⏳ Tests sur vrais fichiers `.pptx`

---

## 🎓 Détails Techniques

### Similarités Word ↔ PowerPoint

**Structure des runs (identique !) :**
```python
# Word
for paragraph in document.paragraphs:
    for run in paragraph.runs:
        run.font.name
        run.font.size
        run.bold

# PowerPoint - EXACTEMENT PAREIL !
for slide in presentation.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:  # ← Identique !
                    run.font.name
                    run.font.size
                    run.bold
```

**Donc :**
- ✅ `StyleExtractor` fonctionne tel quel
- ✅ `StyleMapper` fonctionne tel quel
- ✅ `AIProcessor` fonctionne tel quel

### Différences à Gérer

**1. Navigation**
```python
# Word : 2 niveaux
document.paragraphs → runs

# PowerPoint : 4 niveaux
presentation.slides → shapes → text_frames → paragraphs → runs
```

**2. Détection de Titres**
```python
# Word : via styles
paragraph.style.name.startswith('Heading')

# PowerPoint : via layouts
shape.placeholder_format.type == 1  # TITLE
```

**3. Images**
```python
# Word : dans les runs
run._element (XML)

# PowerPoint : shapes dédiés
shape.image
```

---

## 🚀 Utilisation

### Commande Unique (Recommandée)

```bash
python main_review.py

# Supporte automatiquement :
➤ Chemin: rapport.docx    # → Word
➤ Chemin: slides.pptx     # → PowerPoint (bientôt)
```

### Commandes Spécifiques

```bash
# Word uniquement
python doc_reviewer.py

# PowerPoint (quand disponible)
python ppt_reviewer.py  # À créer si besoin
```

---

## 📝 Notes pour le Développement PowerPoint

### Déjà Préparé

**Fichier `core/powerpoint/ppt_processor.py`** contient :
- ✅ Structure de classe complète
- ✅ Notes d'implémentation détaillées
- ✅ Exemples de code commentés
- ✅ Liste des compatibilités

### À Implémenter (~10h)

1. **Chargement** (2h)
   ```python
   from pptx import Presentation
   self.presentation = Presentation(file_path)
   ```

2. **Itération** (3h)
   ```python
   for slide in self.presentation.slides:
       for shape in slide.shapes:
           if shape.has_text_frame:
               # Traiter comme Word !
   ```

3. **Images** (2h)
   - Adapter `ImageHandler`
   - Gérer `shape.image`

4. **Tests** (3h)
   - Vrais fichiers `.pptx`
   - Validation résultats

---

## ✅ Checklist Complète

### Infrastructure
- ✅ Structure `core/base/`
- ✅ Structure `core/word/`
- ✅ Structure `core/powerpoint/`
- ✅ Point d'entrée unifié
- ✅ Détection automatique de format
- ✅ `python-pptx` dans requirements

### Word (Actuel)
- ✅ Pleinement fonctionnel
- ✅ Compatible avec nouvelle architecture
- ✅ Accessible via `main_review.py`

### PowerPoint (Futur)
- ✅ Structure préparée
- ✅ Notes d'implémentation
- ⏳ Implémentation à finaliser
- ⏳ Tests à effectuer

---

## 🎉 Conclusion

**Architecture prête pour l'extension PowerPoint !**

- ✅ **Point d'entrée unifié** créé
- ✅ **60% du code réutilisable** tel quel
- ✅ **Structure propre** et extensible
- ⏳ **~10h de dev** pour PowerPoint complet

**Prochaine étape** : Implémenter `ppt_processor.py` quand prêt !

