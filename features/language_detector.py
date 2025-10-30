"""
Language detection for documents.
"""

from langdetect import detect
from typing import Optional


class LanguageDetector:
    """Détecteur de langue pour les documents."""
    
    # Mapping des codes de langue vers les noms complets
    LANGUAGE_NAMES = {
        'fr': 'Français',
        'en': 'Anglais',
        'es': 'Espagnol',
        'de': 'Allemand',
        'it': 'Italien',
        'pt': 'Portugais',
        'nl': 'Néerlandais',
        'ru': 'Russe',
        'zh-cn': 'Chinois (simplifié)',
        'zh-tw': 'Chinois (traditionnel)',
        'ja': 'Japonais',
        'ko': 'Coréen',
        'ar': 'Arabe',
        'tr': 'Turc',
        'pl': 'Polonais',
        'sv': 'Suédois',
        'da': 'Danois',
        'no': 'Norvégien',
        'fi': 'Finnois',
    }
    
    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """
        Détecte la langue d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Code de langue (ex: 'fr', 'en') ou None si échec
        """
        try:
            return detect(text)
        except Exception:
            return None
    
    @classmethod
    def get_language_name(cls, lang_code: str) -> str:
        """
        Convertit un code de langue en nom complet.
        
        Args:
            lang_code: Code de langue (ex: 'fr', 'en', 'es')
            
        Returns:
            Nom de la langue
        """
        return cls.LANGUAGE_NAMES.get(lang_code, f"Langue inconnue ({lang_code})")

