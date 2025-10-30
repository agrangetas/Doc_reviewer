"""
Document Context - Extraction de structure pour identification LLM
Fournit une représentation structurée du document pour l'identification d'éléments.
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class ElementPosition:
    """Position sémantique d'un élément."""
    x: Optional[float] = None  # Position horizontale relative (0-1)
    y: Optional[float] = None  # Position verticale relative (0-1)
    semantic: Optional[str] = None  # "top-left", "center", "bottom-right", etc.


@dataclass
class ElementInfo:
    """Informations sur un élément du document."""
    id: int
    type: str  # "title", "textbox", "paragraph", etc.
    text_preview: str  # Premiers 150 caractères
    position: Optional[ElementPosition] = None
    style: Optional[Dict[str, Any]] = None  # bold, italic, font, size, etc.
    metadata: Optional[Dict[str, Any]] = None  # Infos supplémentaires


class DocumentContext:
    """Extraction et représentation de la structure du document."""
    
    @staticmethod
    def extract_for_word(document, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrait la structure d'un document Word.
        
        Args:
            document: Document Word (python-docx)
            scope: Scope optionnel (ex: "paragraph 5" pour limiter le contexte)
            
        Returns:
            Structure JSON du document
        """
        paragraphs = []
        
        # Parser le scope si fourni
        target_para = None
        if scope and "paragraphe" in scope.lower():
            try:
                target_para = int(scope.split()[-1])
            except (ValueError, IndexError):
                pass
        
        for i, para in enumerate(document.paragraphs, 1):
            # Si scope défini, ne garder que le paragraphe ciblé et quelques voisins
            if target_para and abs(i - target_para) > 2:
                continue
            
            text = para.text.strip()
            if not text:
                continue
            
            # Extraire le style du premier run
            style_info = {}
            if para.runs:
                first_run = para.runs[0]
                if first_run.font.bold:
                    style_info['bold'] = True
                if first_run.font.italic:
                    style_info['italic'] = True
                if first_run.font.size:
                    style_info['size_pt'] = first_run.font.size.pt
                if first_run.font.name:
                    style_info['font'] = first_run.font.name
            
            # Style de paragraphe
            if para.style and para.style.name:
                style_info['style_name'] = para.style.name
            
            element = {
                'number': i,
                'text_preview': text[:150] + ('...' if len(text) > 150 else ''),
                'text_length': len(text),
                'style': style_info if style_info else None
            }
            
            paragraphs.append(element)
        
        return {
            'type': 'document_word',
            'total_paragraphs': len(document.paragraphs),
            'paragraphs_shown': len(paragraphs),
            'paragraphs': paragraphs,
            'scope': scope
        }
    
    @staticmethod
    def extract_for_powerpoint(presentation, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrait la structure d'une présentation PowerPoint.
        
        Args:
            presentation: Présentation PowerPoint (python-pptx)
            scope: Scope optionnel (ex: "slide 3" pour limiter le contexte)
            
        Returns:
            Structure JSON de la présentation
        """
        # Parser le scope si fourni
        target_slide = None
        if scope and "slide" in scope.lower():
            try:
                # Extraire le numéro de slide
                parts = scope.lower().split()
                for i, part in enumerate(parts):
                    if part == "slide" or part == "s":
                        target_slide = int(parts[i + 1])
                        break
            except (ValueError, IndexError):
                pass
        
        slides = []
        
        for slide_num, slide in enumerate(presentation.slides, 1):
            # Si scope défini, ne garder que la slide ciblée
            if target_slide and slide_num != target_slide:
                continue
            
            shapes = []
            
            for shape_idx, shape in enumerate(slide.shapes):
                if not shape.has_text_frame:
                    continue
                
                # Extraire le texte de tous les paragraphes de la shape
                text_parts = []
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text.strip())
                
                if not text_parts:
                    continue
                
                full_text = ' '.join(text_parts)
                
                # Déterminer le type de shape
                shape_type = "textbox"
                if hasattr(shape, 'is_placeholder') and shape.is_placeholder:
                    if shape.placeholder_format.type == 1:  # Title
                        shape_type = "title"
                    elif shape.placeholder_format.type == 2:  # Body
                        shape_type = "body"
                
                # Position sémantique
                position = DocumentContext._get_semantic_position(shape)
                
                # Style du premier run du premier paragraphe
                style_info = {}
                if shape.text_frame.paragraphs:
                    first_para = shape.text_frame.paragraphs[0]
                    if first_para.runs:
                        first_run = first_para.runs[0]
                        if first_run.font.bold:
                            style_info['bold'] = True
                        if first_run.font.italic:
                            style_info['italic'] = True
                        if first_run.font.size:
                            style_info['size_pt'] = first_run.font.size.pt
                        if first_run.font.name:
                            style_info['font'] = first_run.font.name
                
                shape_info = {
                    'id': shape_idx,
                    'type': shape_type,
                    'text_preview': full_text[:150] + ('...' if len(full_text) > 150 else ''),
                    'text_length': len(full_text),
                    'paragraph_count': len([p for p in shape.text_frame.paragraphs if p.text.strip()]),
                    'position': position,
                    'style': style_info if style_info else None
                }
                
                shapes.append(shape_info)
            
            slide_info = {
                'number': slide_num,
                'shape_count': len(shapes),
                'shapes': shapes
            }
            
            slides.append(slide_info)
        
        return {
            'type': 'presentation_powerpoint',
            'total_slides': len(presentation.slides),
            'slides_shown': len(slides),
            'slides': slides,
            'scope': scope
        }
    
    @staticmethod
    def _get_semantic_position(shape) -> Dict[str, Any]:
        """
        Détermine la position sémantique d'une shape PowerPoint.
        
        Args:
            shape: Shape PowerPoint
            
        Returns:
            Dict avec position relative et description sémantique
        """
        # Dimensions de la slide (en EMU)
        slide_width = 9144000  # ~10 pouces
        slide_height = 6858000  # ~7.5 pouces
        
        # Position relative (0-1)
        x_rel = shape.left / slide_width if shape.left else 0.5
        y_rel = shape.top / slide_height if shape.top else 0.5
        
        # Description sémantique
        h_pos = "gauche" if x_rel < 0.33 else "centre" if x_rel < 0.67 else "droite"
        v_pos = "haut" if y_rel < 0.33 else "milieu" if y_rel < 0.67 else "bas"
        
        semantic = f"{v_pos}-{h_pos}" if v_pos != "milieu" or h_pos != "centre" else "centre"
        
        return {
            'x_relative': round(x_rel, 2),
            'y_relative': round(y_rel, 2),
            'semantic': semantic
        }
    
    @staticmethod
    def to_json(context: Dict[str, Any], pretty: bool = True) -> str:
        """
        Convertit le contexte en JSON.
        
        Args:
            context: Contexte extrait
            pretty: Formater avec indentation
            
        Returns:
            String JSON
        """
        if pretty:
            return json.dumps(context, ensure_ascii=False, indent=2)
        else:
            return json.dumps(context, ensure_ascii=False)

