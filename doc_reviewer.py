"""
Document Reviewer - Version Refactorisée
Orchestrateur principal qui utilise les modules séparés.
"""

import sys
from pathlib import Path
from typing import Optional
from docx import Document

# Configuration UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Charger .env et fixer le seed pour langdetect
from dotenv import load_dotenv
from langdetect import DetectorFactory
load_dotenv()
DetectorFactory.seed = 0

# Imports des modules
from utils.config import Config
from core.image_handler import ImageHandler
from core.style_extractor import StyleExtractor
from core.style_mapper import StyleMapper
from features.language_detector import LanguageDetector
from features.ai_processor import AIProcessor
from features.style_uniformizer import StyleUniformizer
from change_logging.logger import ChangeLogger


class DocumentReviewer:
    """Reviewer de documents avec architecture modulaire."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialise le reviewer."""
        # Configuration
        self.config = Config()
        
        # API
        api_key = api_key or self.config.get_api_key()
        model = model or self.config.get_model()
        
        # Modules
        self.image_handler = ImageHandler()
        self.style_extractor = StyleExtractor()
        self.style_mapper = StyleMapper()
        self.language_detector = LanguageDetector()
        self.ai_processor = AIProcessor(api_key, model)
        self.logger = ChangeLogger()
        self.style_uniformizer = StyleUniformizer(self.config)
        
        # État
        self.current_document: Optional[Document] = None
        self.current_path: Optional[Path] = None
        self.detected_language: Optional[str] = None
        self.initial_image_count: int = 0
        self.paragraphs_with_images = []
    
    def load_document(self, file_path: str) -> None:
        """Charge un document."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
        
        self.current_document = Document(file_path)
        self.current_path = path
        
        # Détecter la langue
        sample_text = " ".join([p.text.strip() for p in self.current_document.paragraphs if p.text.strip()][:10])
        if sample_text:
            lang_code = self.language_detector.detect_language(sample_text)
            if lang_code:
                self.detected_language = lang_code
        
        # Compter les images
        self.initial_image_count, self.paragraphs_with_images = self.image_handler.count_images(self.current_document)
        
        # Afficher les infos
        print(f"✓ Document chargé: {path.name}")
        print(f"  Nombre de paragraphes: {len(self.current_document.paragraphs)}")
        print(f"  Modèle OpenAI: {self.ai_processor.model}")
        if self.detected_language:
            print(f"  Langue détectée: {self.language_detector.get_language_name(self.detected_language)}")
        
        # Initialiser le log
        doc_info = {
            'paragraph_count': len(self.current_document.paragraphs),
            'language': self.language_detector.get_language_name(self.detected_language) if self.detected_language else None
        }
        self.logger.init_log_file(path.name, doc_info)
        
        # Afficher info images
        if self.initial_image_count > 0:
            print(f"  Images trouvées: {self.initial_image_count} image(s) dans {len(self.paragraphs_with_images)} paragraphe(s)")
            print(f"  ⚠️  Les paragraphes avec images seront traités avec précaution")
    
    def uniformize_styles(self) -> None:
        """
        Uniformise les styles du document (sans LLM).
        """
        if not self.current_document:
            raise ValueError("Aucun document chargé.")
        
        # Lancer l'uniformisation
        result = self.style_uniformizer.uniformize(self.current_document)
        
        # Logger l'opération si pas annulée
        if result.get('cancelled') or result.get('error'):
            return
        
        # Logger l'uniformisation dans le fichier de log
        if self.logger.log_file:
            from datetime import datetime
            with open(self.logger.log_file, 'a', encoding='utf-8') as f:
                f.write("-" * 80 + "\n")
                f.write(f"UNIFORMISATION DES STYLES\n")
                f.write(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 80 + "\n\n")
                f.write(f"Configuration cible:\n")
                f.write(f"  Police: {result.get('target_font', 'N/A')}\n")
                f.write(f"  Taille: {result.get('target_size', 'N/A')} EMUs\n")
                f.write(f"  Couleur: {result.get('target_color', 'N/A')}\n")
                f.write(f"  Interligne: {result.get('target_line_spacing', 'N/A')}\n")
                f.write(f"\nModifications appliquées:\n")
                f.write(f"  Paragraphes modifiés: {result.get('modified_paragraphs', 0)}\n")
                f.write(f"  Changements de police: {result.get('font_changes', 0)}\n")
                f.write(f"  Changements de taille: {result.get('size_changes', 0)}\n")
                f.write(f"  Changements de couleur: {result.get('color_changes', 0)}\n")
                f.write(f"  Changements d'interligne: {result.get('spacing_changes', 0)}\n")
                f.write(f"  Emphases préservées: {result.get('preserved_emphasis', 0)}\n")
                f.write(f"\nNote: Les puces ne sont pas encore uniformisées (détection implémentée).\n")
                f.write("\n" + "=" * 80 + "\n\n")
    
    def process_document(self, instruction: str) -> None:
        """Traite le document avec une instruction."""
        if not self.current_document:
            raise ValueError("Aucun document chargé.")
        
        # Utiliser l'AI processor pour traiter
        modifications = self.ai_processor.process_document(
            self.current_document,
            instruction,
            self.detected_language,
            self.image_handler,
            self.style_extractor,
            self.style_mapper,
            self.logger
        )
        
        # Vérifier les images
        verification = self.image_handler.verify_images(
            self.current_document,
            self.initial_image_count,
            self.paragraphs_with_images
        )
        
        print("\n" + "=" * 60)
        print("VÉRIFICATION DES IMAGES")
        print("=" * 60)
        print(f"Images au début: {verification['initial_count']}")
        print(f"Images maintenant: {verification['current_count']}")
        
        if verification['all_preserved']:
            print("✅ TOUTES LES IMAGES SONT PRÉSERVÉES !")
        else:
            print(f"❌ ATTENTION: {verification['lost_count']} image(s) perdue(s) !")
        
        if len(self.paragraphs_with_images) > 0:
            print(f"\nℹ️  Paragraphes avec images: {', '.join(map(str, self.paragraphs_with_images[:10]))}")
            if len(self.paragraphs_with_images) > 10:
                print(f"   ... et {len(self.paragraphs_with_images) - 10} autres")
        
        print("=" * 60)
    
    def save_document(self, output_path: Optional[str] = None) -> None:
        """Sauvegarde le document."""
        if not self.current_document:
            raise ValueError("Aucun document à sauvegarder.")
        
        if output_path is None:
            output_path = self.current_path.parent / f"{self.current_path.stem}_modifié{self.current_path.suffix}"
        
        self.current_document.save(output_path)
        print(f"\n💾 Document sauvegardé: {output_path}")
    
    def interactive_mode(self, file_path: str) -> None:
        """Mode interactif."""
        self.load_document(file_path)
        
        print("\n" + "=" * 60)
        print("MODE INTERACTIF - Document Reviewer")
        print("=" * 60)
        print("\nCommandes disponibles:")
        print("  - 'corrige' : Corrige les fautes d'orthographe")
        print("  - 'traduis [langue]' : Traduit le document")
        print("  - 'améliore' : Améliore le style")
        print("  - 'uniformise' : Uniformise les styles (police, tailles, etc.)")
        print("  - ou toute autre instruction personnalisée")
        print("  - 'save' : Sauvegarder")
        print("  - 'help' : Afficher l'aide")
        print("  - 'quit' : Quitter")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n➤ Votre commande: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("Au revoir !")
                    break
                
                if user_input.lower() == 'save':
                    self.save_document()
                    continue
                
                if user_input.lower() == 'uniformise':
                    self.uniformize_styles()
                    continue
                
                if user_input.lower() == 'help':
                    print("\n" + "=" * 60)
                    print("COMMANDES DISPONIBLES")
                    print("=" * 60)
                    print("\n📝 Modification du contenu:")
                    print("  corrige              - Corrige l'orthographe et la grammaire")
                    print("  traduis [langue]     - Traduit le document (ex: traduis anglais)")
                    print("  améliore             - Améliore le style et la clarté")
                    print("  [instruction libre]  - Toute instruction personnalisée")
                    print("\n🎨 Mise en forme:")
                    print("  uniformise           - Uniformise les styles (police, tailles)")
                    print("\n💾 Gestion du document:")
                    print("  save                 - Sauvegarde le document modifié")
                    print("  quit                 - Quitte l'application")
                    print("  help                 - Affiche cette aide")
                    print("\n" + "=" * 60)
                    continue
                
                # Traiter l'instruction
                if user_input.lower().startswith('corrige'):
                    instruction = "Corrige toutes les fautes d'orthographe et de grammaire dans ce texte."
                elif user_input.lower().startswith('traduis'):
                    langue = user_input.split(maxsplit=1)[1] if ' ' in user_input else "anglais"
                    instruction = f"Traduis ce texte en {langue}."
                elif user_input.lower() == 'améliore':
                    instruction = "Améliore le style et la clarté de ce texte."
                else:
                    # Instruction personnalisée : valider d'abord
                    instruction = user_input
                    print("\n🔍 Validation de l'instruction...")
                    is_valid, reason, reformulation = self.ai_processor.validate_instruction(instruction)
                    
                    if not is_valid:
                        # Cas 1 : Reformulation proposée
                        if reason == "reformulation_proposée" and reformulation:
                            print(f"\n⚠️  Votre instruction contient des éléments impossibles (formatage).")
                            print(f"\n💡 Reformulation proposée :")
                            print(f"   '{reformulation}'")
                            print(f"\n   (Le LLM peut modifier le TEXTE mais pas le formatage comme gras/italic/police)")
                            
                            confirmation = input("\n   Accepter cette reformulation ? (o/n): ").strip().lower()
                            if confirmation == 'o':
                                instruction = reformulation
                                print("✅ Reformulation acceptée !")
                            else:
                                print("❌ Annulé. Veuillez entrer une nouvelle instruction.")
                                continue
                        
                        # Cas 2 : Instruction totalement invalide
                        else:
                            print(f"\n❌ Instruction invalide : {reason}")
                            print("\n💡 Rappel :")
                            print("  - L'instruction doit s'appliquer à TOUT le document")
                            print("  - Le LLM peut modifier le TEXTE (contenu, majuscules, ton, style)")
                            print("  - Le LLM ne peut PAS modifier le formatage (gras, police, couleur)")
                            print("\n  Exemples valides :")
                            print("    • 'rends le texte plus professionnel'")
                            print("    • 'met tout en MAJUSCULES'")
                            print("    • 'simplifie le vocabulaire'")
                            print("\nVeuillez reformuler votre instruction.")
                            continue
                    
                    print("✅ Instruction validée !")
                
                self.process_document(instruction)
                
            except KeyboardInterrupt:
                print("\n\nInterruption détectée.")
                save = input("Voulez-vous sauvegarder avant de quitter ? (o/n): ").strip().lower()
                if save == 'o':
                    self.save_document()
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")


def main():
    """Fonction principale."""
    print("=" * 60)
    print("DOCUMENT REVIEWER - Version Refactorisée")
    print("=" * 60)
    
    config = Config()
    api_key = config.get_api_key()
    
    if not api_key:
        print("\n⚠️  Clé API OpenAI non trouvée.")
        print("Définissez OPENAI_API_KEY dans votre fichier .env")
        return
    
    print("✓ Clé API OpenAI chargée depuis l'environnement")
    
    reviewer = DocumentReviewer()
    
    file_path = input("\n➤ Chemin du document Word: ").strip().strip('"')
    
    if not file_path:
        print("❌ Aucun fichier spécifié.")
        return
    
    try:
        reviewer.interactive_mode(file_path)
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()

