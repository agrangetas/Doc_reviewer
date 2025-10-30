"""
Diff analysis for tracking text changes.
"""

import difflib
from typing import List, Dict


class DiffAnalyzer:
    """Analyse les différences entre deux textes."""
    
    @staticmethod
    def detect_differences(original: str, modified: str) -> List[Dict[str, any]]:
        """
        Détecte les différences entre deux textes en utilisant difflib.
        
        Args:
            original: Texte original
            modified: Texte modifié
            
        Returns:
            Liste de dictionnaires décrivant chaque différence
        """
        differences = []
        
        # Utiliser SequenceMatcher pour détecter les changements
        matcher = difflib.SequenceMatcher(None, original, modified)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                differences.append({
                    'type': 'REMPLACEMENT',
                    'position': i1,
                    'original': original[i1:i2],
                    'modifie': modified[j1:j2],
                    'contexte_avant': original[max(0, i1-20):i1],
                    'contexte_apres': original[i2:min(len(original), i2+20)]
                })
            elif tag == 'delete':
                differences.append({
                    'type': 'SUPPRESSION',
                    'position': i1,
                    'original': original[i1:i2],
                    'contexte_avant': original[max(0, i1-20):i1],
                    'contexte_apres': original[i2:min(len(original), i2+20)]
                })
            elif tag == 'insert':
                differences.append({
                    'type': 'AJOUT',
                    'position': i1,
                    'modifie': modified[j1:j2],
                    'contexte_avant': original[max(0, i1-20):i1] if i1 > 0 else '',
                    'contexte_apres': original[i1:min(len(original), i1+20)] if i1 < len(original) else ''
                })
        
        return differences

