# Document Reviewer - Correction de Documents Word avec OpenAI

Script Python pour corriger l'orthographe et effectuer diverses opérations sur des documents Word (.doc/.docx) tout en **préservant le formatage exact** paragraphe par paragraphe.

## 📋 Fonctionnalités

- ✅ **Correction orthographique** automatique
- 🔍 **Détection automatique de la langue** (pour corrections intelligentes)
- 🌍 **Traduction** dans n'importe quelle langue
- ✨ **Amélioration de style**
- 📝 **Résumés** de contenu
- 🎨 **Conservation du formatage** (formatage dominant du paragraphe préservé)
- 🖼️ **Protection des images** (détection automatique et paragraphes avec images non modifiés)
- 💬 **Mode interactif** avec historique de contexte
- 🔄 **Instructions personnalisées** illimitées
- 📋 **Logging automatique** de toutes les modifications avec détection des différences
- ✅ **Vérification des images** avant/après chaque traitement

## 🔑 Prérequis

### Clé API OpenAI

⚠️ **Ce script nécessite une clé API OpenAI** 

1. Créez un compte sur [OpenAI](https://platform.openai.com/)
2. Générez une clé API dans les paramètres
3. Configurez la clé (choisissez UNE des options):

**Option A - Fichier .env (RECOMMANDÉ):**
Créez un fichier `.env` dans le dossier du projet:
```
OPENAI_API_KEY=votre-clé-api-ici
OPENAI_MODEL=gpt-4o
```

Modèles disponibles :
- `gpt-4o` - Plus performant (par défaut)
- `gpt-4o-mini` - Plus rapide et moins cher
- `gpt-3.5-turbo` - Le moins cher (~$0.05 pour 277 paragraphes)
- `gpt-4-turbo` - GPT-4 optimisé

**Option B - Variable d'environnement (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "votre-clé-api-ici"
```

**Option C - Variable d'environnement (CMD):**
```cmd
set OPENAI_API_KEY=votre-clé-api-ici
```

**Option D - Le script vous la demandera** au démarrage si non configurée.

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Mode Interactif (Recommandé)

```bash
python doc_reviewer.py
```

Le script vous guidera pour:
1. Entrer votre clé API (si non définie)
2. Spécifier le chemin du document
3. Exécuter des commandes interactives

### Commandes Disponibles

- `corrige` - Corrige les fautes d'orthographe et grammaire
- `traduis [langue]` - Traduit le document (ex: `traduis anglais`)
- `améliore` - Améliore le style et la clarté
- `résume` - Résume le contenu
- `save` - Sauvegarde les modifications
- `save+quit` - Sauvegarde et quitte
- `quit` - Quitte sans sauvegarder

Vous pouvez aussi entrer **n'importe quelle instruction personnalisée** !

### Exemple d'Utilisation

```
➤ Chemin du document Word: Documentation Hyper Open X.docx
✓ Document chargé: Documentation Hyper Open X.docx
  Nombre de paragraphes: 45

➤ Votre commande: corrige
🔄 Traitement: Corrige toutes les fautes d'orthographe et de grammaire...
Paragraphe 1/45... ✓ Modifié
Paragraphe 2/45... ○ Inchangé
...
✓ Traitement terminé !

➤ Votre commande: traduis anglais
🔄 Traitement: Traduis ce texte en anglais...
...

➤ Votre commande: save
💾 Document sauvegardé: Documentation Hyper Open X_modifié.docx
```

### Usage Programmatique

```python
from doc_reviewer import DocumentReviewer

# Initialiser avec votre clé API
reviewer = DocumentReviewer(api_key="votre-clé-api")

# Charger un document
reviewer.load_document("mon_document.docx")

# Corriger l'orthographe
reviewer.process_document("Corrige les fautes d'orthographe")

# Traduire
reviewer.process_document("Traduis ce texte en anglais")

# Sauvegarder
reviewer.save_document("mon_document_corrigé.docx")
```

## 🎯 Conservation du Format

Le script préserve le **formatage dominant** de chaque paragraphe:
- ✅ Polices (nom, taille, couleur) - Format majoritaire
- ✅ Styles (gras, italique, souligné) - Format majoritaire
- ✅ Alignement des paragraphes
- ✅ Indentations (gauche, droite, première ligne)
- ✅ Espacements (avant/après paragraphes)
- ✅ Interligne
- ✅ Structure du document

### ⚠️ Note importante sur le formatage
Le système utilise le **formatage dominant** (le style qui apparaît sur le plus de caractères dans le paragraphe).
Cela évite que le formatage du premier mot (ex: bold) ne "contamine" tout le paragraphe.

**Exemple** : Si un paragraphe contient 100 caractères normaux et 5 caractères en bold, le texte modifié sera en normal.

## 🖼️ Protection des Images

Le système **détecte et préserve automatiquement** toutes les images :
- ✅ **Détection automatique** au chargement du document
- ✅ **Protection totale** : les paragraphes contenant des images ne sont PAS modifiés
- ✅ **Rapport détaillé** des images trouvées
- ✅ **Vérification après traitement** pour confirmer qu'aucune image n'est perdue

**Important** : Les paragraphes contenant des images seront marqués comme "non modifiés" pour garantir la préservation des images.

## 💡 Gestion du Contexte

Le script garde automatiquement:
- Les 2 paragraphes précédents comme contexte
- Un historique des 5 dernières interactions
- **Détection automatique de la langue** lors du chargement du document
- La langue détectée est passée à l'IA en mode "correction" pour garantir des corrections dans la bonne langue
- Cela permet des corrections cohérentes sur tout le document

### 🔍 Détection Automatique de Langue

Quand vous utilisez la commande `corrige`, le système :
1. Détecte automatiquement la langue du document (Français, Anglais, Espagnol, etc.)
2. Informe l'IA de la langue détectée
3. L'IA corrige dans la langue appropriée sans confusion

**Exemple** : Si votre document est en français, pas besoin de dire "corrige en français", le système le fait automatiquement !

## 📋 Logging Automatique des Modifications

Le système enregistre automatiquement TOUTES les modifications dans le dossier `LOGS/`.

### Format des fichiers de log
- **Nom** : `nom_du_document_YYYYMMDD.txt` (sans heures/secondes)
- **Localisation** : `LOGS/` (créé automatiquement)
- **Encodage** : UTF-8

### Ce qui est enregistré pour CHAQUE paragraphe modifié :

1. **Numéro du paragraphe**
2. **Instruction exécutée** (ex: "Corrige les fautes d'orthographe")
3. **Date et heure** de la modification
4. **Texte AVANT** (complet)
5. **Texte APRÈS** (complet)

### Pour les CORRECTIONS (détection automatique) :

En plus du texte complet, le système détecte et enregistre **chaque différence** :
- **Type** : REMPLACEMENT, SUPPRESSION, AJOUT
- **Position exacte** (numéro de caractère)
- **Contexte avant/après** le changement
- **Texte original** et **texte modifié**

**Exemple de log pour une correction :**
```
--------------------------------------------------------------------------------
PARAGRAPHE 15
Instruction: Corrige les fautes d'orthographe et de grammaire
Date/Heure: 2025-10-30 09:55:00
--------------------------------------------------------------------------------

NOMBRE DE MODIFICATIONS: 2

  [1] REMPLACEMENT
      Position: caractère 13
      Contexte avant: ...est un 
      AVANT: 'text'
      APRES: 'texte'
      Contexte après:  avec des...

  [2] REMPLACEMENT
      Position: caractère 28
      Contexte avant: ...vec des 
      AVANT: 'faute'
      APRES: 'fautes'
      Contexte après:  d'orthogr...

TEXTE ORIGINAL:
----------------------------------------
Ceci est un text avec des faute d'ortographe.
----------------------------------------

TEXTE MODIFIE:
----------------------------------------
Ceci est un texte avec des fautes d'orthographe.
----------------------------------------
```

### Pour les TRADUCTIONS et autres commandes :

Enregistre simplement le texte AVANT et APRÈS complet.

### Avantages :
- ✅ **Traçabilité complète** de toutes les modifications
- ✅ **Historique détaillé** des corrections
- ✅ **Analyse des changements** (pour les corrections)
- ✅ **Révision facile** des modifications
- ✅ **Sans utiliser le LLM** (détection en Python pur avec difflib)

## ⚙️ Configuration

### Via le fichier .env (RECOMMANDÉ)
```
OPENAI_MODEL=gpt-4o           # Modèle à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo, etc.)
```

### Directement dans le code
```python
# Température (ligne 633 dans doc_reviewer.py)
temperature=0.3  # Plus bas = plus conservateur

# Contexte (ligne 679)
context_start = max(0, i - 2)  # 2 paragraphes de contexte avant
```

## 💰 Coûts

Le script utilise l'API OpenAI (payante). Coûts approximatifs:
- **GPT-4o**: ~$0.005 par paragraphe
- **GPT-3.5-turbo**: ~$0.0002 par paragraphe

Un document de 50 paragraphes coûte environ **$0.25** avec GPT-4o.

## 🛠️ Dépannage

**"Clé API requise"**
→ Définissez `OPENAI_API_KEY` ou entrez la clé manuellement

**"Le fichier n'existe pas"**
→ Vérifiez le chemin (utilisez des guillemets si espaces: `"Mon Document.docx"`)

**Formatage perdu**
→ Vérifiez que le document original a bien du formatage (pas de texte brut)

## 📄 Licence

MIT - Libre d'utilisation et de modification.

## 🤝 Contribution

N'hésitez pas à améliorer ce script selon vos besoins !

