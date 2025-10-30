"""
Input Parser - Parse les instructions utilisateur avec LLM
Transforme le langage naturel en structure exploitable.
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedInput:
    """Résultat du parsing de l'input utilisateur."""
    
    # Scope type: "page", "slide", "paragraphe", "section", "global"
    scope_type: str
    
    # Valeurs possibles
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    section_name: Optional[str] = None
    
    # Références relatives: "première", "dernière", etc.
    relative_position: Optional[str] = None  # "first", "last"
    
    # Description de l'élément à cibler
    target_description: Optional[str] = None
    
    # Instruction à exécuter
    instruction: str = ""
    
    # Confiance du parsing
    confidence: float = 1.0


class InputParser:
    """Parse les instructions utilisateur avec un LLM."""
    
    PARSING_PROMPT = """Tu es un assistant qui parse des instructions utilisateur pour un outil de révision de documents.

L'utilisateur peut mentionner différents types de cibles :
- **Pages** : "page 3", "sur la page 5", "première page", "dernière page"
- **Slides** (PowerPoint) : "slide 3", "diapo 5", "première slide"
- **Paragraphes** : "paragraphe 3", "premier paragraphe", "le paragraphe qui..."
- **Sections** : "section introduction", "dans la section budget"
- **Global** : "dans tout le document", pas de cible spécifique

INSTRUCTION UTILISATEUR :
"{user_input}"

TYPE DE DOCUMENT : {doc_type}

TÂCHE :
Parse l'instruction et retourne UNIQUEMENT un JSON (sans texte, sans markdown) :

{{
  "scope_type": "<page|slide|paragraphe|section|global>",
  "page_number": <numéro ou null>,
  "slide_number": <numéro ou null>,
  "paragraph_number": <numéro ou null>,
  "section_name": "<nom ou null>",
  "relative_position": "<first|last|null>",
  "target_description": "<description de l'élément à cibler ou null>",
  "instruction": "<action à effectuer>",
  "confidence": <0.0-1.0>
}}

RÈGLES :
1. Si "page X" → scope_type="page", page_number=X
2. Si "slide X" → scope_type="slide", slide_number=X
3. Si "paragraphe X" → scope_type="paragraphe", paragraph_number=X
4. Si "première/dernière" → utilise relative_position="first"/"last"
5. Si description ("le texte en gras", "le titre") → target_description
6. Instruction = l'action pure ("traduis", "corrige", etc.)
7. confidence = 1.0 si clair, < 0.8 si ambigu

EXEMPLES :

Input: "sur la page 3, reformule le paragraphe en gras"
Output:
{{
  "scope_type": "page",
  "page_number": 3,
  "slide_number": null,
  "paragraph_number": null,
  "section_name": null,
  "relative_position": null,
  "target_description": "paragraphe en gras",
  "instruction": "reformule",
  "confidence": 1.0
}}

Input: "slide 7 traduis le titre"
Output:
{{
  "scope_type": "slide",
  "page_number": null,
  "slide_number": 7,
  "paragraph_number": null,
  "section_name": null,
  "relative_position": null,
  "target_description": "titre",
  "instruction": "traduis",
  "confidence": 1.0
}}

Input: "première page corrige"
Output:
{{
  "scope_type": "page",
  "page_number": null,
  "slide_number": null,
  "paragraph_number": null,
  "section_name": null,
  "relative_position": "first",
  "target_description": null,
  "instruction": "corrige",
  "confidence": 1.0
}}

Input: "améliore le style"
Output:
{{
  "scope_type": "global",
  "page_number": null,
  "slide_number": null,
  "paragraph_number": null,
  "section_name": null,
  "relative_position": null,
  "target_description": null,
  "instruction": "améliore le style",
  "confidence": 1.0
}}
"""
    
    def __init__(self, ai_processor):
        """
        Initialise le parser.
        
        Args:
            ai_processor: Instance de AIProcessor
        """
        self.ai_processor = ai_processor
    
    def parse(self, user_input: str, doc_type: str) -> ParsedInput:
        """
        Parse l'instruction utilisateur.
        
        Args:
            user_input: Instruction brute
            doc_type: "word" ou "powerpoint"
            
        Returns:
            ParsedInput structuré
        """
        print(f"   🧠 Parsing de l'instruction avec LLM...")
        
        try:
            # Préparer le prompt
            prompt = self.PARSING_PROMPT.format(
                user_input=user_input,
                doc_type=doc_type
            )
            
            # Appeler le LLM
            response = self.ai_processor._call_openai_raw(
                system_message="Tu es un parser d'instructions. Réponds UNIQUEMENT en JSON valide.",
                user_message=prompt,
                temperature=0.1
            )
            
            # Parser la réponse
            return self._parse_response(response)
        
        except Exception as e:
            print(f"   ⚠️  Erreur parsing: {e}")
            # Fallback: considérer comme global
            return ParsedInput(
                scope_type="global",
                instruction=user_input,
                confidence=0.0
            )
    
    def _parse_response(self, response: str) -> ParsedInput:
        """
        Parse la réponse JSON du LLM.
        
        Args:
            response: Réponse brute
            
        Returns:
            ParsedInput
        """
        try:
            # Nettoyer markdown si présent
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                response = response.strip()
                if response.startswith('json'):
                    response = response[4:].strip()
            
            # Parser JSON
            data = json.loads(response)
            
            print(f"   ✓ Parsed: scope={data['scope_type']}, instruction={data['instruction']}")
            
            return ParsedInput(
                scope_type=data.get('scope_type', 'global'),
                page_number=data.get('page_number'),
                slide_number=data.get('slide_number'),
                paragraph_number=data.get('paragraph_number'),
                section_name=data.get('section_name'),
                relative_position=data.get('relative_position'),
                target_description=data.get('target_description'),
                instruction=data.get('instruction', ''),
                confidence=float(data.get('confidence', 1.0))
            )
        
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON invalide: {e}")
            print(f"   Réponse brute: {response[:200]}")
            return ParsedInput(
                scope_type="global",
                instruction=response,
                confidence=0.0
            )
        
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
            return ParsedInput(
                scope_type="global",
                instruction="",
                confidence=0.0
            )
    
    @staticmethod
    def format_parsed_input(parsed: ParsedInput) -> str:
        """
        Formate un ParsedInput en description lisible.
        
        Args:
            parsed: ParsedInput
            
        Returns:
            Description formatée
        """
        parts = []
        
        if parsed.scope_type == "page":
            if parsed.relative_position == "first":
                parts.append("Première page")
            elif parsed.relative_position == "last":
                parts.append("Dernière page")
            elif parsed.page_number:
                parts.append(f"Page {parsed.page_number}")
        
        elif parsed.scope_type == "slide":
            if parsed.relative_position == "first":
                parts.append("Première slide")
            elif parsed.relative_position == "last":
                parts.append("Dernière slide")
            elif parsed.slide_number:
                parts.append(f"Slide {parsed.slide_number}")
        
        elif parsed.scope_type == "paragraphe":
            if parsed.relative_position == "first":
                parts.append("Premier paragraphe")
            elif parsed.relative_position == "last":
                parts.append("Dernier paragraphe")
            elif parsed.paragraph_number:
                parts.append(f"Paragraphe {parsed.paragraph_number}")
        
        elif parsed.scope_type == "section":
            if parsed.section_name:
                parts.append(f"Section '{parsed.section_name}'")
        
        elif parsed.scope_type == "global":
            parts.append("Document entier")
        
        if parsed.target_description:
            parts.append(f"({parsed.target_description})")
        
        description = " ".join(parts) if parts else "Non spécifié"
        
        return f"{description} → {parsed.instruction}"

