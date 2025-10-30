"""
Document Reviewer - Point d'Entrée Unifié
Supporte : Word (.docx, .doc) et PowerPoint (.pptx, .ppt)
"""

import sys
from pathlib import Path

# Configuration UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Charger .env et fixer le seed pour langdetect
from dotenv import load_dotenv
from langdetect import DetectorFactory
load_dotenv()
DetectorFactory.seed = 0

from utils.config import Config


def detect_format(file_path: str) -> str:
    """
    Détecte le format du document depuis son extension.
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        Format détecté : 'word' ou 'powerpoint'
        
    Raises:
        ValueError: Si le format n'est pas supporté
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension in ['.docx', '.doc']:
        return 'word'
    elif extension in ['.pptx', '.ppt']:
        return 'powerpoint'
    else:
        raise ValueError(
            f"Format non supporté : {extension}\n"
            f"Formats acceptés : .docx, .doc, .pptx, .ppt"
        )


def get_processor(format_type: str):
    """
    Retourne le processeur approprié selon le format.
    
    Args:
        format_type: Type de format ('word' ou 'powerpoint')
        
    Returns:
        Instance du processeur approprié
    """
    # Initialiser les dépendances communes
    from core.image_handler import ImageHandler
    from core.style_extractor import StyleExtractor
    from core.style_mapper import StyleMapper
    from features.language_detector import LanguageDetector
    from features.ai_processor import AIProcessor
    from features.style_uniformizer import StyleUniformizer
    from change_logging.logger import ChangeLogger
    
    config = Config()
    api_key = config.get_api_key()
    model = config.get_model()
    
    image_handler = ImageHandler()
    style_extractor = StyleExtractor()
    style_mapper = StyleMapper()
    language_detector = LanguageDetector()
    ai_processor = AIProcessor(api_key, model)
    logger = ChangeLogger()
    style_uniformizer = StyleUniformizer(config)
    
    if format_type == 'word':
        from core.word.word_processor import WordProcessor
        return WordProcessor(
            config, image_handler, style_extractor, style_mapper,
            language_detector, ai_processor, logger, style_uniformizer
        )
    
    elif format_type == 'powerpoint':
        from core.powerpoint.ppt_processor import PowerPointProcessor
        return PowerPointProcessor(
            config, image_handler, style_extractor, style_mapper,
            language_detector, ai_processor, logger, style_uniformizer
        )
    
    else:
        raise ValueError(f"Format inconnu : {format_type}")


def interactive_mode(processor, file_path: str, format_name: str):
    """
    Mode interactif pour le traitement de documents.
    
    Args:
        processor: Processeur de document
        file_path: Chemin vers le fichier
        format_name: Nom du format (pour l'affichage)
    """
    processor.load_document(file_path)
    
    print("\n" + "=" * 60)
    print(f"MODE INTERACTIF - Document Reviewer ({format_name})")
    print("=" * 60)
    print("\nCommandes disponibles:")
    print("  - 'corrige' : Corrige les fautes d'orthographe")
    print("  - 'traduis [langue]' : Traduit le document")
    print("  - 'améliore' : Améliore le style")
    print("  - 'uniformise' : Uniformise les styles (police, tailles, couleurs, etc.)")
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
                processor.save_document()
                continue
            
            if user_input.lower() == 'uniformise':
                processor.uniformize_styles()
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
                print("  uniformise           - Uniformise les styles (police, tailles, couleurs, interligne)")
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
                is_valid, reason, reformulation = processor.ai_processor.validate_instruction(instruction)
                
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
            
            processor.process_document(instruction)
            
        except KeyboardInterrupt:
            print("\n\nInterruption détectée.")
            save = input("Voulez-vous sauvegarder avant de quitter ? (o/n): ").strip().lower()
            if save == 'o':
                processor.save_document()
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


def main():
    """Fonction principale."""
    print("=" * 60)
    print("DOCUMENT REVIEWER - Point d'Entrée Unifié")
    print("Supporte : Word (.docx, .doc) • PowerPoint (.pptx, .ppt)")
    print("=" * 60)
    
    # Vérifier la clé API
    config = Config()
    api_key = config.get_api_key()
    
    if not api_key:
        print("\n⚠️  Clé API OpenAI non trouvée.")
        print("Définissez OPENAI_API_KEY dans votre fichier .env")
        return
    
    print("✓ Clé API OpenAI chargée depuis l'environnement")
    
    # Demander le fichier
    file_path = input("\n➤ Chemin du document (Word/PowerPoint): ").strip().strip('"')
    
    if not file_path:
        print("❌ Aucun fichier spécifié.")
        return
    
    try:
        # Détecter le format
        format_type = detect_format(file_path)
        format_names = {'word': 'Word', 'powerpoint': 'PowerPoint'}
        format_name = format_names.get(format_type, format_type)
        
        print(f"\n📄 Format détecté : {format_name}")
        
        # Obtenir le processeur approprié
        processor = get_processor(format_type)
        
        # Lancer le mode interactif
        interactive_mode(processor, file_path, format_name)
        
    except ValueError as e:
        print(f"\n❌ {e}")
    except NotImplementedError as e:
        print(f"\n⚠️  {e}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

