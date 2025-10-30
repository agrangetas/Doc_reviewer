"""
Configuration management for the document reviewer.
"""

import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv
import yaml


class Config:
    """Gestionnaire de configuration depuis .env et YAML."""
    
    def __init__(self):
        """Initialise et charge les configurations."""
        # Charger .env
        load_dotenv()
        
        # Configuration depuis .env
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # Configuration style (chargée à la demande)
        self._style_config = None
    
    def get_api_key(self) -> Optional[str]:
        """Retourne la clé API OpenAI."""
        return self.api_key
    
    def get_model(self) -> str:
        """Retourne le modèle OpenAI à utiliser."""
        return self.model
    
    def load_style_config(self, config_path: str = "style_config.yaml") -> dict:
        """
        Charge la configuration des styles depuis un fichier YAML.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Dictionnaire de configuration
        """
        if self._style_config is not None:
            return self._style_config
        
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self._style_config = yaml.safe_load(f)
        else:
            # Configuration par défaut si le fichier n'existe pas
            self._style_config = self._get_default_style_config()
        
        return self._style_config
    
    def _get_default_style_config(self) -> dict:
        """Retourne une configuration de style par défaut."""
        return {
            'font': {'name': 'auto'},
            'sizes': {
                'text_normal': 'auto',
                'heading_1': 'auto',
                'heading_2': 'auto',
                'heading_3': 'auto',
            },
            'preserve': {
                'intentional_emphasis': True,
                'quotes': True,
                'code_blocks': True,
            },
            'heading_detection': {
                'use_word_styles': True,
                'use_heuristics': True,
            },
            'exceptions': {
                'preserve_if_single_word': True,
                'preserve_style_emphasis': True,
            },
            'application': {
                'ask_confirmation': True,
                'show_preview': True,
                'create_backup': True,
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration (ex: 'font.name')
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration
        """
        # Essayer dans la config style
        if self._style_config is not None:
            keys = key.split('.')
            value = self._style_config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        
        return default

