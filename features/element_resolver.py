"""
Element Resolver - Identification d'éléments via LLM
Résout les descriptions en langage naturel vers des cibles précises.
"""

import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ResolvedTarget:
    """Cible résolue par le LLM."""
    scope: str  # "global" ou "specific"
    
    # Pour Word
    paragraph: Optional[int] = None
    
    # Pour PowerPoint
    slide: Optional[int] = None
    shape: Optional[int] = None
    paragraph_in_shape: Optional[int] = None
    
    # Métadonnées
    instruction: str = ""
    element_description: str = ""
    confidence: float = 0.0
    ambiguity: Optional[str] = None
    
    def is_confident(self, threshold: float = 0.7) -> bool:
        """Vérifie si la confiance dépasse le seuil."""
        return self.confidence >= threshold


class ElementResolver:
    """Résout les descriptions en langage naturel vers des cibles précises."""
    
    IDENTIFICATION_PROMPT = """Tu es un assistant qui identifie précisément des éléments dans un document.

STRUCTURE DU DOCUMENT :
{document_structure}

INSTRUCTION UTILISATEUR :
"{user_instruction}"

TÂCHE :
1. Analyse l'instruction pour identifier :
   - La portée (élément spécifique ou global)
   - La description de l'élément à modifier
   - L'action à effectuer

2. Identifie l'élément correspondant dans la structure

3. Retourne UNIQUEMENT un JSON (sans texte avant/après, sans markdown) :

Pour un document Word :
{{
  "scope": "specific",
  "target": {{
    "paragraph": <numéro>
  }},
  "instruction": "<action à effectuer>",
  "element_description": "<description de ce qui a été identifié>",
  "confidence": <0.0-1.0>,
  "ambiguity": null
}}

Pour une présentation PowerPoint :
{{
  "scope": "specific",
  "target": {{
    "slide": <numéro>,
    "shape": <id>,
    "paragraph_in_shape": <numéro ou null>
  }},
  "instruction": "<action à effectuer>",
  "element_description": "<description de ce qui a été identifié>",
  "confidence": <0.0-1.0>,
  "ambiguity": null
}}

Si l'instruction est GLOBALE (pas de cible spécifique mentionnée) :
{{
  "scope": "global",
  "target": {{}},
  "instruction": "<action à effectuer>",
  "element_description": "document entier",
  "confidence": 1.0,
  "ambiguity": null
}}

Si AMBIGU ou impossible à identifier avec certitude :
{{
  "scope": "specific",
  "target": {{...meilleure estimation...}},
  "instruction": "...",
  "element_description": "...",
  "confidence": << 0.7>,
  "ambiguity": "<explication de l'ambiguïté ou des alternatives>"
}}

RÈGLES :
- Si "slide X" ou "paragraphe Y" est explicitement mentionné, utilise ces numéros
- Utilise la position sémantique (haut, bas, gauche, droite, centre) pour identifier
- Utilise le contenu (mots-clés dans text_preview) pour confirmer
- Si plusieurs éléments correspondent, choisis le plus probable et mets confidence < 0.7
- Extrais l'ACTION pure (ex: "traduis en chinois", "corrige", "améliore")
- confidence = 1.0 si identification certaine, < 0.7 si doute
"""
    
    def __init__(self, ai_processor):
        """
        Initialise le resolver.
        
        Args:
            ai_processor: Instance de AIProcessor pour appels LLM
        """
        self.ai_processor = ai_processor
    
    def resolve(self, user_input: str, document_context: Dict[str, Any]) -> ResolvedTarget:
        """
        Résout une instruction en langage naturel.
        
        Args:
            user_input: Instruction utilisateur (ex: "sur la slide 3, traduis le titre")
            document_context: Structure du document (de DocumentContext)
            
        Returns:
            ResolvedTarget avec la cible identifiée
        """
        # Préparer le prompt
        doc_structure_json = json.dumps(document_context, ensure_ascii=False, indent=2)
        
        prompt = self.IDENTIFICATION_PROMPT.format(
            document_structure=doc_structure_json,
            user_instruction=user_input
        )
        
        # Appeler le LLM
        try:
            response = self.ai_processor._call_openai_raw(
                system_message="Tu es un assistant d'identification d'éléments dans des documents. Réponds UNIQUEMENT en JSON valide.",
                user_message=prompt,
                temperature=0.1  # Basse température pour plus de déterminisme
            )
            
            # Parser la réponse
            return self._parse_response(response, document_context['type'])
        
        except Exception as e:
            # En cas d'erreur, retourner une cible globale par défaut
            return ResolvedTarget(
                scope="global",
                instruction=user_input,
                element_description="document entier (erreur d'identification)",
                confidence=0.0,
                ambiguity=f"Erreur lors de l'identification: {str(e)}"
            )
    
    def _parse_response(self, response: str, doc_type: str) -> ResolvedTarget:
        """
        Parse la réponse JSON du LLM.
        
        Args:
            response: Réponse brute du LLM
            doc_type: Type de document ("document_word" ou "presentation_powerpoint")
            
        Returns:
            ResolvedTarget
        """
        try:
            # Nettoyer la réponse (enlever les markdown blocks si présents)
            response = response.strip()
            if response.startswith('```'):
                # Enlever les blocs markdown
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                response = response.strip()
                if response.startswith('json'):
                    response = response[4:].strip()
            
            # Parser le JSON
            data = json.loads(response)
            
            # Créer le ResolvedTarget
            target = ResolvedTarget(
                scope=data.get('scope', 'global'),
                instruction=data.get('instruction', ''),
                element_description=data.get('element_description', ''),
                confidence=float(data.get('confidence', 0.0)),
                ambiguity=data.get('ambiguity')
            )
            
            # Extraire les cibles spécifiques
            target_data = data.get('target', {})
            
            if doc_type == 'document_word':
                target.paragraph = target_data.get('paragraph')
            
            elif doc_type == 'presentation_powerpoint':
                target.slide = target_data.get('slide')
                target.shape = target_data.get('shape')
                target.paragraph_in_shape = target_data.get('paragraph_in_shape')
            
            return target
        
        except json.JSONDecodeError as e:
            # Si le JSON est invalide, retourner une erreur
            return ResolvedTarget(
                scope="global",
                instruction=response,  # Garder la réponse brute
                element_description="erreur de parsing",
                confidence=0.0,
                ambiguity=f"Réponse LLM invalide (JSON): {str(e)}"
            )
        
        except Exception as e:
            return ResolvedTarget(
                scope="global",
                instruction="",
                element_description="erreur inconnue",
                confidence=0.0,
                ambiguity=f"Erreur: {str(e)}"
            )
    
    @staticmethod
    def format_target_description(target: ResolvedTarget, doc_type: str) -> str:
        """
        Formate une description lisible de la cible.
        
        Args:
            target: Cible résolue
            doc_type: Type de document
            
        Returns:
            Description formatée
        """
        if target.scope == "global":
            return "Document entier"
        
        parts = []
        
        if doc_type == 'document_word':
            if target.paragraph:
                parts.append(f"Paragraphe {target.paragraph}")
        
        elif doc_type == 'presentation_powerpoint':
            if target.slide:
                parts.append(f"Slide {target.slide}")
            if target.shape is not None:
                parts.append(f"Shape {target.shape}")
            if target.paragraph_in_shape:
                parts.append(f"Paragraphe {target.paragraph_in_shape}")
        
        description = " > ".join(parts) if parts else "Élément non spécifié"
        
        if target.element_description:
            description += f" ({target.element_description})"
        
        return description

