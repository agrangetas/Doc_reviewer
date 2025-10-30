# 📋 Guide du Système de Logging

## Vue d'ensemble

Le système de logging enregistre automatiquement **toutes les modifications** apportées à vos documents, sans aucune intervention de votre part.

## 🎯 Fonctionnalités principales

### Détection Automatique
- ✅ Détecte automatiquement si c'est une **correction** (orthographe/grammaire)
- ✅ Pour les corrections : analyse détaillée des différences avec **difflib** (Python pur, sans LLM)
- ✅ Pour les autres commandes : enregistrement simple avant/après

### Fichiers de Log
- **Emplacement** : `LOGS/nom_du_document_YYYYMMDD.txt`
- **Format** : Texte UTF-8
- **Nom** : Inclut la date (YYYYMMDD) sans heures/secondes
- **Création** : Automatique au chargement du document

## 📊 Structure d'un Log

### En-tête du fichier
```
================================================================================
LOG DE MODIFICATIONS - 2025-10-30 09:54:33
Document: Documentation Hyper Open X.docx
Nombre de paragraphes: 277
Langue détectée: Français
================================================================================
```

### Pour chaque paragraphe modifié

#### Mode CORRECTION (avec analyse détaillée)
```
--------------------------------------------------------------------------------
PARAGRAPHE 42
Instruction: Corrige les fautes d'orthographe et de grammaire
Date/Heure: 2025-10-30 10:15:23
--------------------------------------------------------------------------------

NOMBRE DE MODIFICATIONS: 3

  [1] REMPLACEMENT
      Position: caractère 15
      Contexte avant: ...Ceci est 
      AVANT: 'un text'
      APRES: 'un texte'
      Contexte après:  avec des...

  [2] AJOUT
      Position: caractère 45
      AJOUTE: ' '
      Contexte avant: ...grammaire
      Contexte après: et de...

  [3] SUPPRESSION
      Position: caractère 67
      SUPPRIME: '  '
      Contexte avant: ...syntaxe
      Contexte après: française...

TEXTE ORIGINAL:
----------------------------------------
Ceci est un text avec des fautes d'orthographe  et grammaire.
----------------------------------------

TEXTE MODIFIE:
----------------------------------------
Ceci est un texte avec des fautes d'orthographe et de grammaire.
----------------------------------------
```

#### Mode TRADUCTION (ou autre commande)
```
--------------------------------------------------------------------------------
PARAGRAPHE 10
Instruction: Traduis ce texte en anglais
Date/Heure: 2025-10-30 10:20:15
--------------------------------------------------------------------------------

TEXTE ORIGINAL:
----------------------------------------
Bonjour, comment allez-vous aujourd'hui ?
----------------------------------------

TEXTE MODIFIE:
----------------------------------------
Hello, how are you today?
----------------------------------------
```

## 🔍 Types de Modifications Détectées

### 1. REMPLACEMENT
Un ou plusieurs caractères sont remplacés par d'autres.

**Exemple :**
- `text` → `texte`
- `faute` → `fautes`

### 2. AJOUT
Des caractères sont ajoutés dans le texte.

**Exemple :**
- `grammaire et` → `grammaire  et` (ajout d'espace)
- `mot` → `motif` (ajout de "if")

### 3. SUPPRESSION
Des caractères sont supprimés du texte.

**Exemple :**
- `texte  avec` → `texte avec` (suppression d'espace double)
- `exemple` → `exemp` (suppression de "le")

## 🎯 Détection Intelligente

Le système détecte automatiquement le type d'opération :

### Commandes de CORRECTION
Mots-clés détectés : `corrige`, `correction`, `orthographe`, `grammaire`

**Comportement :**
- Analyse détaillée avec `difflib.SequenceMatcher`
- Détection de chaque changement individuel
- Position exacte de chaque modification
- Contexte avant/après (20 caractères)

### Autres COMMANDES
Exemples : `traduis`, `améliore`, `résume`, `reformule`

**Comportement :**
- Enregistrement simple AVANT/APRÈS
- Pas d'analyse détaillée (car les changements sont trop importants)

## 💡 Utilisation Pratique

### Consulter les logs

1. **Après chaque session** de modification :
   ```bash
   cd LOGS
   notepad "Documentation Hyper Open X_20251030.txt"
   ```

2. **Rechercher une modification spécifique** :
   - Utilisez Ctrl+F pour chercher un numéro de paragraphe
   - Cherchez par date/heure
   - Cherchez par type d'instruction

3. **Analyser les corrections** :
   - Comptez le nombre de modifications par paragraphe
   - Identifiez les erreurs récurrentes
   - Vérifiez la qualité des corrections

### Exemples d'utilisation

#### Vérifier une correction
```
LOGS/mon_document_20251030.txt

Recherchez : "PARAGRAPHE 15"
Consultez les modifications détectées
Vérifiez si les changements sont appropriés
```

#### Suivre une traduction
```
LOGS/mon_document_20251030.txt

Recherchez : "Traduis"
Comparez les textes AVANT/APRÈS
Vérifiez la cohérence de la traduction
```

#### Analyser l'historique complet
```
Ouvrez le fichier de log
Lisez l'en-tête pour les infos générales
Parcourez chaque modification chronologiquement
```

## 📁 Organisation des Logs

### Fichiers par jour
Chaque jour, un nouveau fichier est créé :
```
LOGS/
├── Documentation Hyper Open X_20251030.txt
├── Documentation Hyper Open X_20251031.txt
├── Rapport Annuel_20251030.txt
└── Contrat Client_20251101.txt
```

### Plusieurs sessions le même jour
Si vous modifiez le même document plusieurs fois le même jour, les modifications sont **ajoutées** au même fichier avec de nouveaux en-têtes.

## ⚙️ Configuration

### Désactiver le logging
Si vous ne voulez pas de logs, commentez ces lignes dans `doc_reviewer.py` :

```python
# Ligne 84 : Commentez l'initialisation
# self._init_log_file()

# Ligne 453 : Commentez l'enregistrement
# self._log_change(i + 1, original_text, processed_text, instruction)
```

### Changer l'emplacement des logs
Modifiez la ligne 206 dans `doc_reviewer.py` :
```python
log_dir = Path("LOGS")  # Changez "LOGS" par votre dossier
```

### Changer le format du nom de fichier
Modifiez la ligne 210 dans `doc_reviewer.py` :
```python
date_str = datetime.now().strftime("%Y%m%d")  # Changez le format
```

Formats possibles :
- `"%Y%m%d"` → 20251030
- `"%Y-%m-%d"` → 2025-10-30
- `"%Y%m%d_%H%M"` → 20251030_1025 (avec heure)

## 🛡️ Sécurité et Confidentialité

### Les logs contiennent :
- ✅ Tout le texte de vos paragraphes (original et modifié)
- ✅ Les instructions que vous avez données
- ✅ Les dates et heures de modification

### Important :
- ⚠️ **Ne partagez pas** les fichiers de log s'ils contiennent des informations confidentielles
- ✅ Le dossier `LOGS/` est **exclu de Git** (via `.gitignore`)
- ✅ Les logs sont **locaux** sur votre machine

## 🔧 Dépannage

### Le dossier LOGS n'est pas créé
→ Vérifiez que vous avez les droits d'écriture dans le dossier du projet

### Le fichier de log est vide
→ Assurez-vous d'avoir effectué au moins une modification sur un paragraphe

### Erreur d'encodage
→ Les logs utilisent UTF-8, ouvrez-les avec un éditeur compatible (Notepad++, VS Code, etc.)

### Les différences ne sont pas détectées
→ Vérifiez que votre commande contient un des mots-clés : `corrige`, `correction`, `orthographe`, `grammaire`

## 📝 Résumé

- ✅ **Automatique** : Aucune configuration nécessaire
- ✅ **Complet** : Toutes les modifications sont enregistrées
- ✅ **Intelligent** : Analyse détaillée pour les corrections
- ✅ **Python pur** : Détection sans LLM (utilise `difflib`)
- ✅ **Local** : Les logs restent sur votre machine
- ✅ **Organisé** : Un fichier par document et par jour

---

**Le système de logging est maintenant actif et enregistre automatiquement toutes vos modifications ! 🎉**

