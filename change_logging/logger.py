"""
Change logging system for document modifications.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
from change_logging.diff_analyzer import DiffAnalyzer


class ChangeLogger:
    """Gestionnaire de logs pour les modifications de documents."""
    
    def __init__(self):
        """Initialise le logger."""
        self.log_file: Optional[Path] = None
        self.diff_analyzer = DiffAnalyzer()
    
    def init_log_file(self, document_name: str, document_info: dict) -> None:
        """
        Initialise le fichier de log pour ce document.
        
        Args:
            document_name: Nom du document
            document_info: Informations sur le document (paragraphes, langue, etc.)
        """
        # Créer le dossier LOGS
        log_dir = Path("LOGS")
        log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier : nom_document_YYYYMMDD.txt
        date_str = datetime.now().strftime("%Y%m%d")
        doc_stem = Path(document_name).stem
        log_filename = f"{doc_stem}_{date_str}.txt"
        
        self.log_file = log_dir / log_filename
        
        # Créer/initialiser le fichier de log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LOG DE MODIFICATIONS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Document: {document_name}\n")
            f.write(f"Nombre de paragraphes: {document_info.get('paragraph_count', 0)}\n")
            if 'language' in document_info:
                f.write(f"Langue détectée: {document_info['language']}\n")
            f.write("=" * 80 + "\n\n")
    
    def log_change(self, paragraph_num: int, original: str, modified: str, instruction: str) -> None:
        """
        Enregistre un changement dans le fichier de log.
        
        Args:
            paragraph_num: Numéro du paragraphe
            original: Texte original
            modified: Texte modifié
            instruction: Instruction qui a causé le changement
        """
        if not self.log_file:
            return
        
        # Déterminer si c'est une correction pour analyser les différences
        is_correction = any(word in instruction.lower() for word in ['corrige', 'correction', 'orthographe', 'grammaire'])
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("-" * 80 + "\n")
            f.write(f"PARAGRAPHE {paragraph_num}\n")
            f.write(f"Instruction: {instruction}\n")
            f.write(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 80 + "\n\n")
            
            # Si c'est une correction, détecter et afficher les différences
            if is_correction and original != modified:
                differences = self.diff_analyzer.detect_differences(original, modified)
                
                if differences:
                    f.write(f"NOMBRE DE MODIFICATIONS: {len(differences)}\n\n")
                    
                    for i, diff in enumerate(differences, 1):
                        f.write(f"  [{i}] {diff['type']}\n")
                        f.write(f"      Position: caractère {diff['position']}\n")
                        
                        if 'contexte_avant' in diff and diff['contexte_avant']:
                            f.write(f"      Contexte avant: ...{diff['contexte_avant']}\n")
                        
                        if diff['type'] == 'REMPLACEMENT':
                            f.write(f"      AVANT: '{diff['original']}'\n")
                            f.write(f"      APRES: '{diff['modifie']}'\n")
                        elif diff['type'] == 'SUPPRESSION':
                            f.write(f"      SUPPRIME: '{diff['original']}'\n")
                        elif diff['type'] == 'AJOUT':
                            f.write(f"      AJOUTE: '{diff['modifie']}'\n")
                        
                        if 'contexte_apres' in diff and diff['contexte_apres']:
                            f.write(f"      Contexte après: {diff['contexte_apres']}...\n")
                        
                        f.write("\n")
                else:
                    f.write("AUCUNE DIFFÉRENCE DÉTECTÉE (textes identiques)\n\n")
            
            # Toujours afficher le avant/après complet
            f.write("TEXTE ORIGINAL:\n")
            f.write("-" * 40 + "\n")
            f.write(original + "\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("TEXTE MODIFIE:\n")
            f.write("-" * 40 + "\n")
            f.write(modified + "\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("\n")

