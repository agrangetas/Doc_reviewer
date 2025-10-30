"""
Abstract base class for document processors.
Defines the common interface for Word, PowerPoint, and future formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any


class DocumentProcessor(ABC):
    """Processeur abstrait pour tous les formats de documents."""
    
    def __init__(self, config, image_handler, style_extractor, style_mapper, 
                 language_detector, ai_processor, logger, style_uniformizer):
        """
        Initialise le processeur.
        
        Args:
            config: Configuration
            image_handler: Gestionnaire d'images
            style_extractor: Extracteur de styles
            style_mapper: Mappeur de styles
            language_detector: Détecteur de langue
            ai_processor: Processeur IA
            logger: Logger
            style_uniformizer: Uniformisateur de styles
        """
        self.config = config
        self.image_handler = image_handler
        self.style_extractor = style_extractor
        self.style_mapper = style_mapper
        self.language_detector = language_detector
        self.ai_processor = ai_processor
        self.logger = logger
        self.style_uniformizer = style_uniformizer
        
        self.current_document = None
        self.current_path: Optional[Path] = None
        self.detected_language: Optional[str] = None
    
    @abstractmethod
    def load_document(self, file_path: str) -> None:
        """
        Charge un document.
        
        Args:
            file_path: Chemin vers le document
        """
        pass
    
    @abstractmethod
    def save_document(self, output_path: Optional[str] = None) -> None:
        """
        Sauvegarde le document.
        
        Args:
            output_path: Chemin de sortie (optionnel)
        """
        pass
    
    @abstractmethod
    def process_document(self, instruction: str) -> None:
        """
        Traite le document avec une instruction.
        
        Args:
            instruction: Instruction à exécuter
        """
        pass
    
    @abstractmethod
    def uniformize_styles(self) -> None:
        """Uniformise les styles du document."""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """
        Retourne le nom du format (pour l'affichage).
        
        Returns:
            Nom du format (ex: 'Word', 'PowerPoint')
        """
        pass

