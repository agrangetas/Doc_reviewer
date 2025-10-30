"""
Image handling for Word documents.
"""

from typing import List
from copy import deepcopy


class ImageHandler:
    """Gestionnaire d'images dans les documents Word."""
    
    @staticmethod
    def has_images(paragraph) -> bool:
        """
        Vérifie si un paragraphe contient des images.
        
        Args:
            paragraph: Paragraphe docx à vérifier
            
        Returns:
            True si le paragraphe contient des images
        """
        try:
            for run in paragraph.runs:
                # Vérifier les inline shapes (images)
                if hasattr(run, '_element'):
                    for child in run._element:
                        # drawing est le tag pour les images/formes inline
                        if 'drawing' in child.tag or 'pict' in child.tag:
                            return True
        except:
            pass
        return False
    
    def count_images(self, document) -> tuple[int, List[int]]:
        """
        Compte toutes les images dans le document et identifie les paragraphes qui en contiennent.
        
        Args:
            document: Document docx
            
        Returns:
            Tuple (nombre total d'images, liste des numéros de paragraphes avec images)
        """
        image_count = 0
        paragraphs_with_images = []
        
        for i, paragraph in enumerate(document.paragraphs):
            if self.has_images(paragraph):
                paragraphs_with_images.append(i + 1)
                # Compter le nombre d'images dans ce paragraphe
                for run in paragraph.runs:
                    if hasattr(run, '_element'):
                        for child in run._element:
                            if 'drawing' in child.tag or 'pict' in child.tag:
                                image_count += 1
        
        return image_count, paragraphs_with_images
    
    @staticmethod
    def backup_paragraph_xml(paragraph):
        """
        Crée une sauvegarde XML du paragraphe pour restauration éventuelle.
        
        Args:
            paragraph: Paragraphe à sauvegarder
            
        Returns:
            Élément XML du paragraphe
        """
        return deepcopy(paragraph._element)
    
    @staticmethod
    def restore_paragraph_xml(paragraph, backup_xml):
        """
        Restaure un paragraphe depuis une sauvegarde XML.
        
        Args:
            paragraph: Paragraphe à restaurer
            backup_xml: Sauvegarde XML
        """
        paragraph._element.getparent().replace(paragraph._element, backup_xml)
        paragraph._element = backup_xml
    
    def verify_images(self, document, initial_count: int, initial_paragraphs: List[int]) -> dict:
        """
        Vérifie que toutes les images sont toujours présentes après le traitement.
        
        Args:
            document: Document docx
            initial_count: Nombre d'images initial
            initial_paragraphs: Liste initiale des paragraphes avec images
            
        Returns:
            Dictionnaire avec le résultat de la vérification
        """
        current_count, current_paragraphs = self.count_images(document)
        
        return {
            'initial_count': initial_count,
            'current_count': current_count,
            'all_preserved': current_count == initial_count,
            'lost_count': initial_count - current_count,
            'initial_paragraphs': initial_paragraphs,
            'current_paragraphs': current_paragraphs
        }

