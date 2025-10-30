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


def interactive_mode(processor, file_path: str, format_name: str, format_type: str):
    """
    Mode interactif pour le traitement de documents.
    
    Args:
        processor: Processeur de document
        file_path: Chemin vers le fichier
        format_name: Nom du format (pour l'affichage)
        format_type: Type de format ('word' ou 'powerpoint')
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
    print("  - 'change_doc' : Changer de document")
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
            
            if user_input.lower() == 'change_doc':
                print("\n🔄 Changement de document...")
                return True  # Signal pour retourner au menu principal
            
            if user_input.lower() == 'uniformise':
                processor.uniformize_styles()
                continue
            
            if user_input.lower() == 'help':
                print("\n" + "=" * 60)
                print("COMMANDES DISPONIBLES")
                print("=" * 60)
                print("\n📝 Modification du contenu (GLOBAL):")
                print("  corrige              - Corrige l'orthographe et la grammaire")
                print("  traduis [langue]     - Traduit le document (ex: traduis anglais)")
                print("  améliore             - Améliore le style et la clarté")
                print("\n🎯 Modification CIBLÉE (en langage naturel):")
                print("  Exemples Word:")
                print("    • 'sur le paragraphe 5, traduis en anglais'")
                print("    • 'le paragraphe qui parle de budget, améliore le'")
                print("  Exemples PowerPoint:")
                print("    • 'sur la slide 3, traduis le titre en chinois'")
                print("    • 'sur la slide 3, le texte en bas à droite, corrige le'")
                print("    • 'la slide avec le graphique, améliore la légende'")
                print("\n🎨 Mise en forme:")
                print("  uniformise           - Uniformise les styles (police, tailles, couleurs, interligne)")
                print("\n💾 Gestion du document:")
                print("  save                 - Sauvegarde le document modifié")
                print("  change_doc           - Change de document (retour au menu)")
                print("  quit                 - Quitte l'application")
                print("  help                 - Affiche cette aide")
                print("\n💡 Le système utilise l'IA pour identifier automatiquement")
                print("   les éléments à modifier depuis vos descriptions !")
                print("\n" + "=" * 60)
                continue
            
            # Traiter l'instruction
            # D'abord, essayer de détecter si c'est une commande standard ou ciblée
            is_standard_command = False
            instruction = user_input
            
            if user_input.lower().startswith('corrige'):
                instruction = "Corrige toutes les fautes d'orthographe et de grammaire dans ce texte."
                is_standard_command = True
            elif user_input.lower().startswith('traduis'):
                langue = user_input.split(maxsplit=1)[1] if ' ' in user_input else "anglais"
                instruction = f"Traduis ce texte en {langue}."
                is_standard_command = True
            elif user_input.lower() == 'améliore':
                instruction = "Améliore le style et la clarté de ce texte."
                is_standard_command = True
            
            # Si commande standard, traiter globalement
            if is_standard_command:
                processor.process_document(instruction)
            else:
                # Instruction personnalisée ou ciblée : utiliser le parsing LLM
                print("\n🔍 Analyse de l'instruction...")
                
                # Importer les modules nécessaires
                from core.base.document_context import DocumentContext
                from features.element_resolver import ElementResolver
                from features.input_parser import InputParser
                
                print(f"📄 Type de document: {format_type}")
                
                # Parser l'input avec LLM
                input_parser = InputParser(processor.ai_processor)
                parsed_input = input_parser.parse(user_input, format_type)
                
                # Afficher ce qui a été parsé
                parsed_desc = InputParser.format_parsed_input(parsed_input)
                print(f"   ✓ Parsé: {parsed_desc}")
                print(f"   Confiance: {parsed_input.confidence:.0%}")
                
                # Si scope global sans ciblage précis, avertir
                if parsed_input.scope_type == "global" and parsed_input.confidence > 0.5:
                    print("\n⚠️  Scope global détecté")
                    print("   💡 Pour une identification ciblée précise, mentionnez:")
                    if format_type == 'word':
                        print("      • 'page X', 'paragraphe X', 'première page', etc.")
                    else:
                        print("      • 'slide X', 'diapo X', 'première slide', etc.")
                    print("   ⚡ Cela réduira les coûts API et améliorera la précision")
                    
                    # Demander confirmation
                    confirm = input("\n   Continuer avec l'analyse complète ? (o/n): ").strip().lower()
                    if confirm != 'o':
                        print("❌ Annulé. Reformulez votre commande avec un scope spécifique.")
                        continue
                
                # Extraire le contexte selon le parsing
                if format_type == 'word':
                    print("📊 Extraction de la structure Word...")
                    doc_context = DocumentContext.extract_for_word(
                        processor.current_document, 
                        parsed_input,
                        cached_page_info=processor.cached_page_info  # Utiliser le cache du processeur
                    )
                    print(f"   ✓ {doc_context['paragraphs_shown']} paragraphes extraits")
                    if 'total_pages' in doc_context:
                        print(f"   📄 Document: {doc_context['total_pages']} pages")
                else:  # powerpoint
                    print("📊 Extraction de la structure PowerPoint...")
                    doc_context = DocumentContext.extract_for_powerpoint(processor.presentation, parsed_input)
                    print(f"   ✓ {doc_context['slides_shown']} slides extraites")
                
                # Résoudre la cible avec le LLM
                print("🤖 Envoi au LLM pour identification...")
                resolver = ElementResolver(processor.ai_processor)
                target = resolver.resolve(user_input, doc_context)
                print("   ✓ Réponse LLM reçue")
                
                # Afficher ce qui a été identifié
                target_desc = ElementResolver.format_target_description(target, doc_context['type'])
                print(f"✓ Cible identifiée: {target_desc}")
                print(f"  Instruction: {target.instruction}")
                print(f"  Confiance: {target.confidence:.0%}")
                
                # Si confiance basse, demander confirmation
                if not target.is_confident():
                    print(f"\n⚠️  Confiance faible ({target.confidence:.0%})")
                    if target.ambiguity:
                        print(f"   Raison: {target.ambiguity}")
                    
                    print(f"\n📋 Structure identifiée complète:")
                    if format_type == 'word' and target.paragraph:
                        # Afficher le paragraphe identifié
                        para = processor.current_document.paragraphs[target.paragraph - 1]
                        print(f"   Paragraphe {target.paragraph}: {para.text[:150]}...")
                    elif format_type == 'powerpoint' and target.slide:
                        # Afficher la slide/shape identifiée
                        slide = processor.presentation.slides[target.slide - 1]
                        if target.shape is not None:
                            shape = slide.shapes[target.shape]
                            if shape.has_text_frame:
                                text = shape.text[:150]
                                print(f"   Slide {target.slide}, Shape {target.shape}: {text}...")
                        else:
                            print(f"   Slide {target.slide} (toute la slide)")
                    
                    confirmation = input("\n   Continuer avec cette cible ? (o/n): ").strip().lower()
                    if confirmation != 'o':
                        print("❌ Annulé.")
                        continue
                
                # Traiter selon le scope
                if target.scope == "global":
                    # Valider l'instruction globale comme avant
                    print("\n🔍 Validation de l'instruction globale...")
                    is_valid, reason, reformulation = processor.ai_processor.validate_instruction(target.instruction)
                    
                    if not is_valid:
                        # Cas 1 : Reformulation proposée
                        if reason == "reformulation_proposée" and reformulation:
                            print(f"\n⚠️  Votre instruction contient des éléments impossibles (formatage).")
                            print(f"\n💡 Reformulation proposée :")
                            print(f"   '{reformulation}'")
                            print(f"\n   (Le LLM peut modifier le TEXTE mais pas le formatage comme gras/italic/police)")
                            
                            confirmation = input("\n   Accepter cette reformulation ? (o/n): ").strip().lower()
                            if confirmation == 'o':
                                target.instruction = reformulation
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
                    processor.process_document(target.instruction)
                
                else:
                    # Traitement ciblé
                    processor.process_targeted(target, target.instruction)
            
        except KeyboardInterrupt:
            print("\n\nInterruption détectée.")
            save = input("Voulez-vous sauvegarder avant de quitter ? (o/n): ").strip().lower()
            if save == 'o':
                processor.save_document()
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


def main():
    """Fonction principale avec boucle pour changement de document."""
    print("=" * 60)
    print("DOCUMENT REVIEWER - Point d'Entrée Unifié")
    print("Supporte : Word (.docx, .doc) • PowerPoint (.pptx, .ppt)")
    print("=" * 60)
    
    # Vérifier la clé API une seule fois
    config = Config()
    api_key = config.get_api_key()
    
    if not api_key:
        print("\n⚠️  Clé API OpenAI non trouvée.")
        print("Définissez OPENAI_API_KEY dans votre fichier .env")
        return
    
    print("✓ Clé API OpenAI chargée depuis l'environnement")
    
    # Boucle principale pour permettre le changement de document
    while True:
        try:
            # Demander le fichier
            file_path = input("\n➤ Chemin du document (Word/PowerPoint): ").strip().strip('"')
            
            if not file_path:
                print("❌ Aucun fichier spécifié.")
                continue
            
            # Détecter le format
            format_type = detect_format(file_path)
            format_names = {'word': 'Word', 'powerpoint': 'PowerPoint'}
            format_name = format_names.get(format_type, format_type)
            
            print(f"\n📄 Format détecté : {format_name}")
            
            # Obtenir le processeur approprié
            processor = get_processor(format_type)
            
            # Lancer le mode interactif
            should_change_doc = interactive_mode(processor, file_path, format_name, format_type)
            
            # Si l'utilisateur a demandé à changer de document, continuer la boucle
            if should_change_doc:
                continue
            else:
                # Sinon (quit), sortir de la boucle
                break
                
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

