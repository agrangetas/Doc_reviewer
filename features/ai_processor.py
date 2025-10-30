"""
AI processing using OpenAI API.
"""

from openai import OpenAI
from typing import Optional, Tuple


class AIProcessor:
    """Processeur IA utilisant OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """Initialise le processeur IA."""
        if not api_key:
            raise ValueError("Clé API OpenAI requise.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = []
    
    def validate_instruction(self, instruction: str) -> Tuple[bool, str, str]:
        """
        Valide qu'une instruction personnalisée est appropriée pour la révision de document.
        
        Args:
            instruction: Instruction à valider
            
        Returns:
            Tuple (est_valide, message, reformulation_proposée)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es un validateur d'instructions pour un outil de révision de documents Word avec IA.\n"
                            "L'outil utilise un LLM (GPT) pour modifier le TEXTE du document.\n\n"
                            "IMPORTANT : Le LLM peut UNIQUEMENT modifier le texte, PAS le formatage (gras, italic, couleur, police).\n\n"
                            "Tu dois vérifier :\n"
                            "1. L'instruction s'applique-t-elle à TOUT le document (pas un endroit spécifique) ?\n"
                            "2. L'instruction demande-t-elle du formatage impossible (gras, italic, police, couleur) ?\n\n"
                            "CE QUI EST POSSIBLE :\n"
                            "- Modifier le contenu textuel (rendre professionnel, simplifier, etc.)\n"
                            "- MAJUSCULES/minuscules (c'est du texte)\n"
                            "- Traduction, reformulation, ton, style d'écriture\n\n"
                            "CE QUI EST IMPOSSIBLE :\n"
                            "- Gras, italic, souligné\n"
                            "- Changer la police ou la taille\n"
                            "- Couleurs, surlignage\n\n"
                            "EXEMPLES VALIDES :\n"
                            "- 'rends le texte plus professionnel' ✓\n"
                            "- 'met tout en MAJUSCULES' ✓\n"
                            "- 'simplifie le vocabulaire' ✓\n\n"
                            "EXEMPLES À REFORMULER :\n"
                            "- 'met en gras et majuscule' → REFORMULER vers 'met en MAJUSCULES'\n"
                            "- 'change la police en Arial et rends formel' → REFORMULER vers 'rends le texte plus formel'\n\n"
                            "EXEMPLES INVALIDES :\n"
                            "- 'change le titre' (spécifique)\n"
                            "- 'met en gras' (impossible, aucune reformulation textuelle)\n\n"
                            "Réponds UNIQUEMENT par l'un de ces formats :\n"
                            "- 'VALIDE' si l'instruction est entièrement réalisable\n"
                            "- 'REFORMULER: [nouvelle instruction]' si possible en retirant les parties impossibles\n"
                            "- 'INVALIDE: [raison]' si l'instruction cible un endroit spécifique ou est entièrement impossible\n"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Instruction à valider : {instruction}"
                    }
                ],
                temperature=0.3,
            )
            
            result = response.choices[0].message.content.strip()
            
            if result.startswith("VALIDE"):
                return True, "", ""
            elif result.startswith("REFORMULER:"):
                reformulation = result.replace("REFORMULER:", "").strip()
                return False, "reformulation_proposée", reformulation
            elif result.startswith("INVALIDE"):
                reason = result.replace("INVALIDE:", "").strip()
                return False, reason, ""
            else:
                # Par sécurité, si format inattendu, on considère comme invalide
                return False, "Format de réponse inattendu du validateur.", ""
                
        except Exception as e:
            print(f"⚠️  Erreur lors de la validation: {e}")
            # En cas d'erreur, on laisse passer
            return True, "", ""
    
    def call_openai(self, instruction: str, text: str, context: str = "", is_correction: bool = False, language: Optional[str] = None) -> str:
        """
        Appelle l'API OpenAI.
        
        Args:
            instruction: Instruction à exécuter
            text: Texte à traiter
            context: Contexte additionnel
            is_correction: Si True, ajoute la langue au contexte
            language: Nom de la langue détectée
            
        Returns:
            Texte traité
        """
        system_content = (
            "Tu es un assistant expert en révision de documents. "
            "Tu dois UNIQUEMENT retourner le texte modifié, sans explications, "
            "sans commentaires, sans formatage markdown. "
            "Préserve la structure exacte du texte (sauts de ligne, espaces, etc.)."
        )
        
        if is_correction and language:
            system_content += f"\nLe document est en {language}. Effectue la correction dans cette langue."
        
        messages = [{"role": "system", "content": system_content}]
        
        if self.conversation_history:
            messages.extend(self.conversation_history[-5:])
        
        if context:
            messages.append({"role": "system", "content": f"Contexte: {context}"})
        
        messages.append({"role": "user", "content": f"{instruction}\n\nTexte:\n{text}"})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            
            result = response.choices[0].message.content.strip()
            
            self.conversation_history.append({"role": "user", "content": f"{instruction} (paragraphe)"})
            self.conversation_history.append({"role": "assistant", "content": result[:100] + "..." if len(result) > 100 else result})
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur API OpenAI: {e}")
            return text
    
    def _call_openai_raw(self, system_message: str, user_message: str, temperature: float = 0.3) -> str:
        """
        Appel brut à l'API OpenAI sans historique ni traitement.
        
        Args:
            system_message: Message système
            user_message: Message utilisateur
            temperature: Température du modèle
            
        Returns:
            Réponse brute du LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Erreur API OpenAI: {e}")
    
    def process_document(self, document, instruction: str, detected_language: Optional[str], 
                        image_handler, style_extractor, style_mapper, logger) -> int:
        """
        Traite le document avec l'instruction donnée.
        
        Args:
            document: Document docx
            instruction: Instruction à exécuter
            detected_language: Code de langue détectée
            image_handler: Gestionnaire d'images
            style_extractor: Extracteur de styles
            style_mapper: Mappeur de styles
            logger: Logger de changements
            
        Returns:
            Nombre de paragraphes modifiés
        """
        is_correction = any(word in instruction.lower() for word in ['corrige', 'correction', 'orthographe', 'grammaire'])
        
        from features.language_detector import LanguageDetector
        language_name = LanguageDetector.get_language_name(detected_language) if detected_language else None
        
        print(f"\n🔄 Traitement: {instruction}")
        if is_correction and language_name:
            print(f"   Langue: {language_name}")
        print("=" * 60)
        
        paragraphs = list(document.paragraphs)
        total = len(paragraphs)
        modified_count = 0
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.text.strip():
                continue
            
            # Créer un contexte
            context_start = max(0, i - 2)
            context_paragraphs = [p.text for p in paragraphs[context_start:i] if p.text.strip()]
            context = " [...] ".join(context_paragraphs[-2:]) if context_paragraphs else ""
            
            print(f"Paragraphe {i+1}/{total}...", end=" ")
            
            original_text = paragraph.text
            processed_text = self.call_openai(instruction, original_text, context, is_correction, language_name)
            
            if processed_text and processed_text != original_text:
                # Sauvegarder si images
                has_images = image_handler.has_images(paragraph)
                backup_xml = None
                if has_images:
                    backup_xml = image_handler.backup_paragraph_xml(paragraph)
                    print("⚠️  IMAGES - Tentative...", end=" ")
                
                # Extraire et mapper les styles
                styles_map = style_extractor.extract_styles_map(paragraph)
                new_styles_map = style_mapper.map_styles_to_new_text(original_text, processed_text, styles_map)
                
                # Sauvegarder propriétés du paragraphe
                alignment = paragraph.alignment
                paragraph_format = {
                    'left_indent': paragraph.paragraph_format.left_indent,
                    'right_indent': paragraph.paragraph_format.right_indent,
                    'first_line_indent': paragraph.paragraph_format.first_line_indent,
                    'space_before': paragraph.paragraph_format.space_before,
                    'space_after': paragraph.paragraph_format.space_after,
                    'line_spacing': paragraph.paragraph_format.line_spacing,
                }
                
                # Appliquer les styles
                style_mapper.apply_styles_map(paragraph, processed_text, new_styles_map)
                
                # Restaurer propriétés
                paragraph.alignment = alignment
                for key, value in paragraph_format.items():
                    if value is not None:
                        setattr(paragraph.paragraph_format, key, value)
                
                # Vérifier images
                if has_images:
                    if not image_handler.has_images(paragraph):
                        print("❌ Images perdues, RESTAURATION !", end=" ")
                        image_handler.restore_paragraph_xml(paragraph, backup_xml)
                        print("○ Non modifié (images)")
                        continue
                    else:
                        print("✅ Images préservées !", end=" ")
                
                # Logger
                logger.log_change(i + 1, original_text, processed_text, instruction)
                print("✓ Modifié")
                modified_count += 1
            else:
                print("○ Inchangé")
        
        print("=" * 60)
        print(f"✓ Traitement terminé ! ({modified_count} paragraphes modifiés)")
        
        return modified_count

