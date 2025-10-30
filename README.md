# 📄 Document Reviewer

Outil de révision automatique de documents **Word** et **PowerPoint** avec intelligence artificielle (OpenAI).

**Formats supportés** : `.docx`, `.doc`, `.pptx`, `.ppt`

---

## 🚀 Installation

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer l'API OpenAI

Créez un fichier `.env` à la racine :
```env
OPENAI_API_KEY=sk-votre-cle-api-openai
OPENAI_MODEL=gpt-4o
```

### 3. Lancer l'application
```bash
python main_review.py
```

---

## 📝 Utilisation

```bash
$ python main_review.py

➤ Chemin du document (Word/PowerPoint): mon_document.docx

✓ Document chargé
  Nombre de paragraphes: 127
  Langue détectée: Français

➤ Votre commande: corrige
```

---

## ✨ Commandes Disponibles

### 🔧 Modifications Globales

| Commande | Description |
|----------|-------------|
| `corrige` | Corrige l'orthographe et la grammaire |
| `traduis [langue]` | Traduit le document (ex: `traduis anglais`) |
| `améliore` | Améliore le style et la clarté |
| `uniformise` | Uniformise les styles (police, tailles, couleurs) |

### 🎯 Modifications Ciblées (langage naturel)

Décrivez simplement ce que vous voulez modifier :

**Word :**
- `"sur la page 3, reformule le paragraphe en gras"`
- `"première page corrige l'orthographe"`
- `"le paragraphe qui parle de budget, améliore le"`

**PowerPoint :**
- `"sur la slide 3, traduis le titre en chinois"`
- `"première slide corrige"`
- `"slide 7 le texte en bas à droite, améliore le"`

### 💾 Gestion

| Commande | Description |
|----------|-------------|
| `save` | Sauvegarde le document modifié |
| `change_doc` | Change de document |
| `help` | Affiche l'aide |
| `quit` | Quitte l'application |

---

## 🎨 Fonctionnalités

### ✅ Préservation du Format
- **Styles de texte** : bold, italic, underline, couleurs
- **Alignements** : paragraphes, bullet points, indentations
- **Images** : protection automatique (Word)
- **Structure** : préserve la mise en page

### 🧠 Intelligence Artificielle
- **Détection de langue** : automatique
- **Ciblage intelligent** : compréhension du langage naturel
- **Traduction intelligente** : ne traduit pas si déjà dans la bonne langue
- **Contexte** : maintient la cohérence du document

### 📊 Logs Détaillés
Toutes les modifications sont enregistrées dans `LOGS/nom_document_YYYYMMDD.txt` :
- Texte avant/après
- Différences détaillées
- Horodatage

---

## ⚙️ Configuration Avancée

### Style (`style_config.yaml`)

```yaml
font:
  name: auto                   # 'auto' ou 'Calibri', 'Arial', etc.

sizes:
  text_normal: auto            # 'auto' ou 11, 12, etc.

preserve:
  intentional_emphasis: true   # Préserver bold/italic sur 1 mot
```

### Pages Word (`.env`)

Pour obtenir les **vraies pages** sur Word (nécessite Windows + Word installé) :
```bash
pip install pywin32
```

Sinon, le système utilise une estimation intelligente (ajustable via `CHARS_PER_PAGE` dans `.env`).

---

## 🆘 Aide

### L'API ne répond pas
Vérifiez votre clé dans `.env` :
```env
OPENAI_API_KEY=sk-votre-cle
```

### Le formatage n'est pas préservé
Le système préserve automatiquement les styles. Si vous rencontrez un problème, vérifiez les logs.

### Les pages Word sont mal estimées
1. **Windows + Word installé** : Installez `pywin32` pour utiliser l'API Word
2. **Sans Word** : Ajustez `CHARS_PER_PAGE` dans `.env` (voir `calibrate_pages.py`)

---

## 📂 Structure du Projet

```
Doc_review/
├── main_review.py           # Point d'entrée principal
├── .env                      # Configuration (à créer)
├── style_config.yaml         # Configuration des styles
│
├── core/                     # Processeurs de documents
│   ├── word/                 # Traitement Word
│   └── powerpoint/           # Traitement PowerPoint
│
├── features/                 # Fonctionnalités IA
│   ├── ai_processor.py       # Intégration OpenAI
│   ├── language_detector.py  # Détection de langue
│   └── style_uniformizer.py  # Uniformisation
│
└── LOGS/                     # Historique des modifications
```

Voir `ARCHITECTURE.md` pour plus de détails.

---

## 📄 Licence

MIT

---

**Document Reviewer** - Révision intelligente de documents
