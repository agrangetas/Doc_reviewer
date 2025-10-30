"""
Style extraction from Word documents.
"""

from typing import List, Dict


class StyleExtractor:
    """Extracteur de styles depuis les paragraphes Word."""
    
    @staticmethod
    def extract_styles_map(paragraph) -> List[Dict]:
        """
        Extrait une carte détaillée des styles du paragraphe avec positions exactes.
        
        Args:
            paragraph: Paragraphe docx
            
        Returns:
            Liste de dictionnaires avec le style et la plage de caractères
        """
        styles_map = []
        char_position = 0
        
        for run in paragraph.runs:
            if run.text:  # Inclure même les runs vides pour les images
                style = {
                    'start': char_position,
                    'end': char_position + len(run.text),
                    'text': run.text,
                    'bold': run.bold,
                    'italic': run.italic,
                    'underline': run.underline,
                    'font_name': run.font.name,
                    'font_size': run.font.size,
                    'font_color': run.font.color.rgb if run.font.color.rgb else None,
                }
                styles_map.append(style)
                char_position += len(run.text)
        
        return styles_map
    
    @staticmethod
    def get_run_format(run) -> Dict:
        """
        Extrait le formatage d'un run.
        
        Args:
            run: Run docx
            
        Returns:
            Dictionnaire avec les propriétés de formatage
        """
        return {
            'bold': run.bold,
            'italic': run.italic,
            'underline': run.underline,
            'font_name': run.font.name,
            'font_size': run.font.size,
            'font_color': run.font.color.rgb if run.font.color.rgb else None,
        }
    
    @staticmethod
    def get_dominant_format(paragraph) -> Dict:
        """
        Détermine le formatage dominant d'un paragraphe (pour le texte majoritaire).
        
        Args:
            paragraph: Paragraphe docx
            
        Returns:
            Dictionnaire de formatage dominant
        """
        # Compter la longueur de texte pour chaque format
        format_list = []
        
        for run in paragraph.runs:
            if run.text.strip():  # Ignorer les runs vides
                # Stocker directement les objets (pas de conversion en string)
                run_format = {
                    'bold': run.bold,
                    'italic': run.italic,
                    'underline': run.underline,
                    'font_name': run.font.name,
                    'font_size': run.font.size,
                    'font_color': run.font.color.rgb if run.font.color.rgb else None,
                    'text_length': len(run.text)
                }
                format_list.append(run_format)
        
        # Trouver le format avec le plus de caractères
        if format_list:
            # Grouper par format similaire et sommer les longueurs
            format_groups = {}
            for fmt in format_list:
                # Créer une clé unique pour ce format
                key = (
                    fmt['bold'],
                    fmt['italic'],
                    fmt['underline'],
                    fmt['font_name'],
                    str(fmt['font_size']),
                    str(fmt['font_color'])
                )
                
                if key in format_groups:
                    format_groups[key]['total_length'] += fmt['text_length']
                else:
                    format_groups[key] = {
                        'bold': fmt['bold'],
                        'italic': fmt['italic'],
                        'underline': fmt['underline'],
                        'font_name': fmt['font_name'],
                        'font_size': fmt['font_size'],
                        'font_color': fmt['font_color'],
                        'total_length': fmt['text_length']
                    }
            
            # Trouver le groupe avec la plus grande longueur totale
            dominant = max(format_groups.values(), key=lambda x: x['total_length'])
            
            return {
                'bold': dominant['bold'],
                'italic': dominant['italic'],
                'underline': dominant['underline'],
                'font_name': dominant['font_name'],
                'font_size': dominant['font_size'],
                'font_color': dominant['font_color'],
            }
        
        # Format par défaut si aucun run avec texte
        return {
            'bold': False,
            'italic': False,
            'underline': False,
            'font_name': 'Calibri',
            'font_size': None,
            'font_color': None,
        }

