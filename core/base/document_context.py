"""
Document Context - Extraction de structure pour identification LLM
Fournit une représentation structurée du document pour l'identification d'éléments.
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# Tentative d'import de win32com pour accès aux vraies pages
try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


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
    def _get_real_page_numbers_via_word(file_path: str) -> Optional[Dict[int, int]]:
        """
        Obtient les VRAIS numéros de page via l'API COM Word.
        
        Args:
            file_path: Chemin du fichier Word
            
        Returns:
            Dict {paragraph_index: page_number} ou None si échec
        """
        if not WIN32COM_AVAILABLE:
            return None
        
        try:
            print("   🔍 Tentative d'obtention des VRAIES pages via Word...")
            
            # Ouvrir Word
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            # Ouvrir le document
            doc = word.Documents.Open(file_path)
            
            # Mapper chaque paragraphe à sa page
            paragraph_pages = {}
            
            for i, para in enumerate(doc.Paragraphs, 1):
                try:
                    # Obtenir le vrai numéro de page
                    page_num = para.Range.Information(3)  # wdActiveEndPageNumber = 3
                    paragraph_pages[i] = page_num
                except:
                    # Si erreur, garder la page précédente ou 1
                    paragraph_pages[i] = paragraph_pages.get(i-1, 1)
            
            total_pages = doc.ComputeStatistics(2)  # wdStatisticPages = 2
            
            # Fermer
            doc.Close(False)
            word.Quit()
            
            print(f"   ✅ VRAIES pages obtenues via Word ! ({total_pages} pages)")
            
            return paragraph_pages, total_pages
        
        except Exception as e:
            print(f"   ⚠️  Word API non disponible: {e}")
            return None
    
    @staticmethod
    def extract_for_word(document, parsed_input=None, file_path=None) -> Dict[str, Any]:
        """
        Extrait la structure d'un document Word avec détection de pages.
        
        Args:
            document: Document Word (python-docx)
            parsed_input: ParsedInput optionnel pour ciblage
            file_path: Chemin du fichier (pour API Word)
            
        Returns:
            Structure JSON du document
        """
        paragraphs = []
        
        # Tenter d'obtenir les VRAIES pages via Word API
        real_pages_result = None
        if file_path:
            import os
            abs_path = os.path.abspath(file_path)
            real_pages_result = DocumentContext._get_real_page_numbers_via_word(abs_path)
        
        # Si on a les vraies pages, les utiliser
        if real_pages_result:
            paragraph_pages, total_pages = real_pages_result
            print(f"   📄 Utilisation des VRAIES pages ({total_pages} pages détectées)")
        else:
            # Fallback : estimation
            print("   ⚠️  Fallback sur estimation (python-docx limitation)")
            
            # Estimation ajustable selon le type de document
            import os
            chars_per_page = int(os.getenv('CHARS_PER_PAGE', '1500'))
            cumulative_chars = 0
            current_page = 1
        
        # Parser le scope si fourni via ParsedInput
        target_page = None
        target_para = None
        relative_pos = None
        
        if parsed_input:
            if parsed_input.scope_type == "page":
                if parsed_input.relative_position == "first":
                    target_page = 1
                elif parsed_input.relative_position == "last":
                    # On calculera après avoir parcouru tout
                    target_page = -1
                elif parsed_input.page_number:
                    target_page = parsed_input.page_number
                print(f"   🎯 Extraction ciblée: Page {target_page}")
            elif parsed_input.scope_type == "paragraphe":
                if parsed_input.relative_position == "first":
                    target_para = 1
                elif parsed_input.relative_position == "last":
                    target_para = -1
                elif parsed_input.paragraph_number:
                    target_para = parsed_input.paragraph_number
                print(f"   🎯 Extraction ciblée: Paragraphe {target_para}")
        
        # Si on n'a pas les vraies pages, calculer l'estimation
        if not real_pages_result:
            paragraph_pages = {}
            cumulative_chars = 0
            current_page = 1
            
            for i, para in enumerate(document.paragraphs, 1):
                text = para.text.strip()
                
                # Poids ajusté selon le style (titres prennent plus de place visuellement)
                para_weight = len(text)
                
                # Si c'est un titre, augmenter le poids (les titres prennent plus de place)
                if para.style and para.style.name and ('Heading' in para.style.name or 'Titre' in para.style.name):
                    para_weight = int(para_weight * 1.5)  # Les titres comptent pour 1.5x
                
                cumulative_chars += para_weight
                
                # Estimation du numéro de page
                current_page = max(1, (cumulative_chars // chars_per_page) + 1)
                paragraph_pages[i] = current_page
            
            total_pages = current_page
            
            # Log de l'estimation (utile pour ajuster si nécessaire)
            if parsed_input and parsed_input.scope_type == "page":
                print(f"   📊 Estimation: ~{chars_per_page} chars/page (ajustable via CHARS_PER_PAGE dans .env)")
        
        # Gérer "dernière page/paragraphe"
        if target_page == -1:
            target_page = total_pages
            print(f"   📄 Dernière page détectée: page {target_page}")
        if target_para == -1:
            target_para = len(document.paragraphs)
            print(f"   📄 Dernier paragraphe détecté: paragraphe {target_para}")
        
        # Deuxième passage : extraire selon le scope
        for i, para in enumerate(document.paragraphs, 1):
            text = para.text.strip()
            if not text:
                continue
            
            para_page = paragraph_pages.get(i, 1)
            
            # Filtrage selon le scope
            if target_page:
                # Si ciblage par page, garder seulement la page ciblée et voisines
                if abs(para_page - target_page) > 1:
                    continue
            elif target_para:
                # Si ciblage par paragraphe, garder ±5 voisins
                if abs(i - target_para) > 5:
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
                'page': para_page,  # Ajout du numéro de page estimé
                'text_preview': text[:150] + ('...' if len(text) > 150 else ''),
                'text_length': len(text),
                'style': style_info if style_info else None
            }
            
            paragraphs.append(element)
        
        result = {
            'type': 'document_word',
            'total_paragraphs': len(document.paragraphs),
            'total_pages': total_pages,
            'paragraphs_shown': len(paragraphs),
            'paragraphs': paragraphs
            # Note: parsed_input n'est pas inclus car non-sérialisable en JSON
        }
        
        # Log de l'optimisation
        if target_page or target_para:
            saved = len(document.paragraphs) - len(paragraphs)
            if saved > 0:
                scope_desc = f"page {target_page}" if target_page else f"paragraphe {target_para}"
                print(f"   ⚡ Optimisation: {saved} paragraphes non envoyés ({scope_desc})")
                print(f"   📊 Économie: {saved}/{len(document.paragraphs)} paragraphes ({saved/len(document.paragraphs)*100:.0f}%)")
        
        return result
    
    @staticmethod
    def extract_for_powerpoint(presentation, parsed_input=None) -> Dict[str, Any]:
        """
        Extrait la structure d'une présentation PowerPoint.
        
        Args:
            presentation: Présentation PowerPoint (python-pptx)
            parsed_input: ParsedInput optionnel pour ciblage
            
        Returns:
            Structure JSON de la présentation
        """
        # Parser le scope si fourni via ParsedInput
        target_slide = None
        
        if parsed_input and parsed_input.scope_type == "slide":
            if parsed_input.relative_position == "first":
                target_slide = 1
            elif parsed_input.relative_position == "last":
                target_slide = len(presentation.slides)
            elif parsed_input.slide_number:
                target_slide = parsed_input.slide_number
            print(f"   🎯 Extraction ciblée: Slide {target_slide} uniquement")
        
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
        
        result = {
            'type': 'presentation_powerpoint',
            'total_slides': len(presentation.slides),
            'slides_shown': len(slides),
            'slides': slides
            # Note: parsed_input n'est pas inclus car non-sérialisable en JSON
        }
        
        # Log de l'optimisation
        if target_slide:
            saved = len(presentation.slides) - len(slides)
            if saved > 0:
                print(f"   ⚡ Optimisation: {saved} slides non envoyées (slide {target_slide})")
                print(f"   📊 Économie: {saved}/{len(presentation.slides)} slides ({saved/len(presentation.slides)*100:.0f}%)")
        
        return result
    
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

