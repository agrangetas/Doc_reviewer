# 🎯 Traitement Ciblé avec IA - Documentation Complète

## ✅ IMPLÉMENTATION TERMINÉE

Date : 30 octobre 2025

## 🎯 Vue d'Ensemble

Le système de **traitement ciblé avec IA** permet aux utilisateurs de décrire en **langage naturel** les éléments à modifier, et le LLM identifie automatiquement les cibles précises dans le document.

### Avant / Après

**AVANT** (syntaxe rigide) :
```
paragraphe 5: traduis en anglais
slide 3 shape 2: corrige
```

**MAINTENANT** (langage naturel) 🌟 :
```
sur le paragraphe 5, traduis en anglais
sur la slide 3, le texte en bas à droite, corrige le
le paragraphe qui parle de budget, améliore le
la slide avec le graphique, traduis la légende en chinois
```

## 🏗️ Architecture

### Composants Créés

```
core/base/
  └── document_context.py         # Extraction de structure pour LLM

features/
  └── element_resolver.py         # Résolution LLM d'éléments

features/ai_processor.py          # + _call_openai_raw()

core/word/word_processor.py       # + process_targeted()
core/powerpoint/ppt_processor.py  # + process_targeted()

main_review.py                    # Workflow complet intégré
```

### Pipeline de Traitement

```
1. USER INPUT
   "sur la slide 3, modifie le texte en bas à droite et traduis le en chinois"
   
2. EXTRACTION DE CONTEXTE
   DocumentContext extrait la structure du document
   → Pour PowerPoint : slides, shapes, positions, contenus
   → Pour Word : paragraphes, styles, contenus
   
3. RÉSOLUTION LLM
   ElementResolver envoie au LLM :
   - Structure du document (JSON)
   - Instruction utilisateur
   
   LLM retourne :
   {
     "scope": "specific",
     "target": {"slide": 3, "shape": 1},
     "instruction": "traduis en chinois",
     "confidence": 0.95,
     "element_description": "textbox en bas à droite"
   }
   
4. VALIDATION
   Si confidence < 70% → demander confirmation utilisateur
   Afficher la structure identifiée
   
5. TRAITEMENT
   processor.process_targeted(target, instruction)
   → Traite uniquement l'élément ciblé
   → Préserve le formatage
   → Log détaillé
```

## 📋 Détails Techniques

### 1. DocumentContext (`core/base/document_context.py`)

**Rôle** : Extraire et formater la structure du document pour le LLM

#### Pour Word :
```python
{
  "type": "document_word",
  "total_paragraphs": 50,
  "paragraphs": [
    {
      "number": 1,
      "text_preview": "Introduction...",
      "text_length": 250,
      "style": {"bold": true, "size_pt": 14, "style_name": "Heading 1"}
    },
    ...
  ]
}
```

#### Pour PowerPoint :
```python
{
  "type": "presentation_powerpoint",
  "total_slides": 10,
  "slides": [
    {
      "number": 3,
      "shapes": [
        {
          "id": 0,
          "type": "title",
          "text_preview": "Budget 2025",
          "position": {"semantic": "haut-centre"}
        },
        {
          "id": 1,
          "type": "textbox",
          "text_preview": "Contact: info@...",
          "position": {"semantic": "bas-droite"}
        }
      ]
    }
  ]
}
```

**Position sémantique** : Convertit les coordonnées en descriptions (haut/milieu/bas, gauche/centre/droite)

### 2. ElementResolver (`features/element_resolver.py`)

**Rôle** : Utiliser le LLM pour identifier les éléments depuis une description

#### Prompt LLM :
```
STRUCTURE DU DOCUMENT : [JSON]
INSTRUCTION UTILISATEUR : "sur la slide 3, le texte en bas à droite, traduis"

TÂCHE : Identifier l'élément et retourner JSON :
{
  "scope": "specific",
  "target": {"slide": 3, "shape": 1},
  "instruction": "traduis",
  "confidence": 0.95,
  "ambiguity": null
}
```

#### ResolvedTarget :
```python
@dataclass
class ResolvedTarget:
    scope: str                      # "global" ou "specific"
    paragraph: Optional[int]        # Pour Word
    slide: Optional[int]            # Pour PowerPoint
    shape: Optional[int]            # Pour PowerPoint
    instruction: str                # Action à effectuer
    element_description: str        # Description humaine
    confidence: float               # 0.0 - 1.0
    ambiguity: Optional[str]        # Si plusieurs candidats
```

### 3. Processeurs - process_targeted()

#### WordProcessor :
```python
def process_targeted(self, target: ResolvedTarget, instruction: str):
    """Traite un paragraphe ciblé."""
    paragraph_num = target.paragraph
    paragraph = self.current_document.paragraphs[paragraph_num - 1]
    
    # Contexte : paragraphes voisins
    # Traitement avec LLM
    # Mapping des styles
    # Vérification images
    # Logging
```

#### PowerPointProcessor :
```python
def process_targeted(self, target: ResolvedTarget, instruction: str):
    """Traite slide/shape ciblée."""
    slide = self.presentation.slides[target.slide - 1]
    
    if target.shape is not None:
        # Traiter shape spécifique
    else:
        # Traiter toute la slide
```

### 4. Workflow dans main_review.py

```python
# Détection de commande
if user_input.startswith('corrige'):
    # Commande standard → traitement global
    processor.process_document(instruction)
else:
    # Commande personnalisée → résolution LLM
    
    # 1. Extraire contexte
    doc_context = DocumentContext.extract_for_word(processor.current_document)
    
    # 2. Résoudre cible
    resolver = ElementResolver(processor.ai_processor)
    target = resolver.resolve(user_input, doc_context)
    
    # 3. Afficher identification
    print(f"Cible: {target_desc}")
    print(f"Confiance: {target.confidence:.0%}")
    
    # 4. Si confiance basse → confirmer
    if not target.is_confident():
        # Afficher structure identifiée
        # Demander confirmation
    
    # 5. Traiter selon scope
    if target.scope == "global":
        processor.process_document(target.instruction)
    else:
        processor.process_targeted(target, target.instruction)
```

## 🎯 Exemples d'Utilisation

### Word

#### 1. Cible explicite :
```
➤ sur le paragraphe 5, traduis en anglais

🔍 Analyse de l'instruction...
✓ Cible identifiée: Paragraphe 5 (paragraphe sur le budget)
  Instruction: traduis en anglais
  Confiance: 100%

🎯 Traitement ciblé: Paragraphe 5
Texte original: Notre budget prévisionnel pour 2025...
✓ Paragraphe 5 modifié
Nouveau texte: Our projected budget for 2025...
```

#### 2. Description sémantique :
```
➤ le paragraphe qui parle de conclusion, améliore le

🔍 Analyse de l'instruction...
✓ Cible identifiée: Paragraphe 15 (contient "conclusion")
  Instruction: améliore le
  Confiance: 85%

🎯 Traitement ciblé: Paragraphe 15
✓ Paragraphe 15 modifié
```

#### 3. Confiance basse :
```
➤ le paragraphe en italique, traduis

🔍 Analyse de l'instruction...
✓ Cible identifiée: Paragraphe 8
  Instruction: traduis
  Confiance: 60%

⚠️  Confiance faible (60%)
   Raison: Plusieurs paragraphes en italique trouvés

📋 Structure identifiée complète:
   Paragraphe 8: Ce texte est en italique...

   Continuer avec cette cible ? (o/n): o
```

### PowerPoint

#### 1. Cible slide + position :
```
➤ sur la slide 3, le texte en bas à droite, traduis en chinois

🔍 Analyse de l'instruction...
✓ Cible identifiée: Slide 3 > Shape 1 (textbox en bas à droite)
  Instruction: traduis en chinois
  Confiance: 95%

🎯 Traitement ciblé: Slide 3, Shape 1
  ✓ Paragraphe 1 modifié
```

#### 2. Description sémantique :
```
➤ sur la slide avec le graphique, améliore la légende

🔍 Analyse de l'instruction...
✓ Cible identifiée: Slide 7 > Shape 3 (légende graphique)
  Instruction: améliore la légende
  Confiance: 80%

🎯 Traitement ciblé: Slide 7, Shape 3
  ✓ Paragraphe 1 modifié
```

#### 3. Slide entière :
```
➤ sur la slide 5, corrige

🔍 Analyse de l'instruction...
✓ Cible identifiée: Slide 5 (toute la slide)
  Instruction: corrige
  Confiance: 100%

🎯 Traitement ciblé: Slide 5
  ✓ Paragraphe 1 modifié
  ✓ Paragraphe 2 modifié
✓ Traitement ciblé terminé ! (2 éléments modifiés)
```

## 🔧 Configuration

### Seuil de confiance :

Par défaut : **70%**

Modifiable dans `ResolvedTarget.is_confident(threshold=0.7)`

### Modèle LLM :

Utilise le modèle défini dans `.env` :
```env
OPENAI_MODEL=gpt-4o
```

Le même modèle est utilisé pour :
- Résolution d'éléments
- Traitement du texte
- Validation des instructions

## 📊 Logging

Les opérations ciblées sont loggées avec le tag `(ciblé)` :

```
================================================================================
Élément #S3-Sh1-P1
Instruction: traduis en chinois (ciblé)
--------------------------------------------------------------------------------
Texte original:
Contact: info@example.com

Texte modifié:
联系方式：info@example.com
--------------------------------------------------------------------------------
```

## ⚙️ Gestion des Erreurs

### 1. JSON invalide du LLM :
```python
try:
    data = json.loads(response)
except json.JSONDecodeError:
    # Retourner target global avec confidence=0
    # Fallback sur traitement global
```

### 2. Élément non trouvé :
```python
if slide_num > len(slides):
    raise ValueError("Slide n'existe pas")
```

### 3. Ambiguïté :
```python
if confidence < 0.7:
    # Afficher structure identifiée
    # Demander confirmation utilisateur
```

## 🎨 Avantages de cette Approche

### ✅ Pour l'Utilisateur :
- **Langage naturel** : Aucune syntaxe à apprendre
- **Descriptions flexibles** : "en haut", "le titre", "qui parle de..."
- **Intelligent** : Le LLM comprend le contexte
- **Sûr** : Confirmation pour les identifications incertaines

### ✅ Pour le Système :
- **Extensible** : Pas de parser rigide à maintenir
- **Adaptatif** : Le LLM s'améliore avec les modèles
- **Réutilisable** : Même code pour Word et PowerPoint
- **Traçable** : Logs avec confiance et ambiguïté

## 🔮 Améliorations Futures

### Court terme :
- ⏳ Cache pour réduire les appels API répétés
- ⏳ Support des ranges ("slides 3 à 5")
- ⏳ Filtrage par contenu ("tous les paragraphes contenant 'budget'")

### Moyen terme :
- ⏳ Apprentissage des patterns utilisateur
- ⏳ Suggestions automatiques
- ⏳ Preview avant application

## 📝 Tests

Tous les tests passent ✅ :

```bash
python test_targeted_processing.py

✅ DocumentContext - Extraction de structure
✅ ElementResolver - Résolution LLM d'éléments
✅ ResolvedTarget - Cibles avec confiance
✅ WordProcessor.process_targeted()
✅ PowerPointProcessor.process_targeted()
✅ Intégration dans main_review.py
```

## 🚀 Conclusion

Le système de **traitement ciblé avec IA** est **opérationnel et robuste** !

Il transforme l'outil en un véritable **assistant intelligent** capable de comprendre des descriptions en langage naturel et d'identifier précisément les éléments à modifier.

**Prêt à l'emploi** : Lancez `python main_review.py` et testez !

---

**Implémenté par** : Assistant IA (Claude Sonnet 4.5)  
**Date** : 30 octobre 2025  
**Statut** : ✅ OPÉRATIONNEL

