"""
Intelligent style mapping for text modifications.
"""

import difflib
from typing import List, Dict


class StyleMapper:
    """Mappeur intelligent de styles entre textes."""
    
    @staticmethod
    def map_styles_to_new_text(original_text: str, new_text: str, styles_map: List[Dict]) -> List[Dict]:
        """
        Mappe intelligemment les styles de l'ancien texte vers le nouveau en utilisant difflib.
        
        Args:
            original_text: Texte original
            new_text: Nouveau texte
            styles_map: Carte des styles de l'original
            
        Returns:
            Nouvelle carte de styles adaptée au nouveau texte
        """
        if not styles_map:
            return []
        
        # Utiliser SequenceMatcher pour comprendre les changements
        matcher = difflib.SequenceMatcher(None, original_text, new_text)
        new_styles_map = []
        
        for style in styles_map:
            style_start = style['start']
            style_end = style['end']
            
            # Trouver les nouvelles positions pour ce style
            new_start = None
            new_end = None
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                # Si le style commence dans cette plage
                if i1 <= style_start < i2:
                    if tag == 'equal':
                        # Texte identique : position directe
                        new_start = j1 + (style_start - i1)
                    elif tag == 'replace':
                        # Texte remplacé : début de la nouvelle portion
                        new_start = j1
                    elif tag == 'delete':
                        # Texte supprimé : chercher la position suivante
                        new_start = j1
                    elif tag == 'insert':
                        # Insertion : ajuster
                        new_start = j1
                
                # Si le style se termine dans cette plage
                if i1 < style_end <= i2:
                    if tag == 'equal':
                        # Texte identique : position directe
                        new_end = j1 + (style_end - i1)
                    elif tag == 'replace':
                        # Texte remplacé : fin de la nouvelle portion
                        new_end = j2
                    elif tag == 'delete':
                        # Texte supprimé : position au début du bloc suivant
                        new_end = j1
                    elif tag == 'insert':
                        # Insertion : ajuster
                        new_end = j2
            
            # Si on a trouvé des positions valides
            if new_start is not None and new_end is not None and new_end > new_start:
                new_style = {
                    'start': new_start,
                    'end': min(new_end, len(new_text)),  # Ne pas dépasser la longueur du texte
                    'bold': style['bold'],
                    'italic': style['italic'],
                    'underline': style['underline'],
                    'font_name': style['font_name'],
                    'font_size': style['font_size'],
                    'font_color': style['font_color'],
                }
                new_styles_map.append(new_style)
        
        # Si aucun style n'a pu être mappé, utiliser le style dominant de l'original
        if not new_styles_map and styles_map:
            # Prendre le premier style (ou le dominant)
            dominant_style = styles_map[0]
            new_styles_map.append({
                'start': 0,
                'end': len(new_text),
                'bold': dominant_style['bold'],
                'italic': dominant_style['italic'],
                'underline': dominant_style['underline'],
                'font_name': dominant_style['font_name'],
                'font_size': dominant_style['font_size'],
                'font_color': dominant_style['font_color'],
            })
        
        return new_styles_map
    
    @staticmethod
    def apply_styles_map(paragraph, new_text: str, styles_map: List[Dict]) -> None:
        """
        Applique une carte de styles à un paragraphe.
        
        Args:
            paragraph: Paragraphe docx
            new_text: Texte à insérer
            styles_map: Carte des styles à appliquer
        """
        # Supprimer tous les runs existants
        for run in paragraph.runs:
            run.text = ''
        
        if not styles_map:
            # Aucun style : créer un run simple
            paragraph.add_run(new_text)
            return
        
        # Trier les styles par position de début
        sorted_styles = sorted(styles_map, key=lambda x: x['start'])
        
        # Créer des runs pour chaque section de style
        last_end = 0
        
        for style in sorted_styles:
            start = max(style['start'], last_end)
            end = min(style['end'], len(new_text))
            
            if start >= len(new_text):
                break
            
            # Texte avant ce style (si gap)
            if start > last_end:
                gap_text = new_text[last_end:start]
                if gap_text:
                    paragraph.add_run(gap_text)
            
            # Texte avec ce style
            if end > start:
                styled_text = new_text[start:end]
                run = paragraph.add_run(styled_text)
                
                # Appliquer le style
                if style['bold'] is not None:
                    run.bold = style['bold']
                if style['italic'] is not None:
                    run.italic = style['italic']
                if style['underline'] is not None:
                    run.underline = style['underline']
                if style['font_name']:
                    run.font.name = style['font_name']
                if style['font_size']:
                    run.font.size = style['font_size']
                if style['font_color']:
                    run.font.color.rgb = style['font_color']
                
                last_end = end
        
        # Texte restant après tous les styles
        if last_end < len(new_text):
            remaining_text = new_text[last_end:]
            if remaining_text:
                run = paragraph.add_run(remaining_text)
                # Utiliser le style du dernier segment
                if sorted_styles:
                    last_style = sorted_styles[-1]
                    if last_style['bold'] is not None:
                        run.bold = last_style['bold']
                    if last_style['italic'] is not None:
                        run.italic = last_style['italic']
                    if last_style['underline'] is not None:
                        run.underline = last_style['underline']
                    if last_style['font_name']:
                        run.font.name = last_style['font_name']
                    if last_style['font_size']:
                        run.font.size = last_style['font_size']
                    if last_style['font_color']:
                        run.font.color.rgb = last_style['font_color']

