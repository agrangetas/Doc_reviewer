"""
PowerPoint Processor - Implémentation complète
Traitement de présentations PowerPoint avec IA.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

from core.base.document_processor import DocumentProcessor


class PowerPointProcessor(DocumentProcessor):
    """Processeur pour les présentations PowerPoint."""
    
    def __init__(self, config, image_handler, style_extractor, style_mapper,
                 language_detector, ai_processor, logger, style_uniformizer):
        """Initialise le processeur PowerPoint."""
        if not PPTX_AVAILABLE:
            raise ImportError(
                "python-pptx n'est pas installé.\n"
                "Installez-le avec : pip install python-pptx==0.6.23"
            )
        
        super().__init__(
            config, image_handler, style_extractor, style_mapper,
            language_detector, ai_processor, logger, style_uniformizer
        )
        self.presentation = None
        self.initial_slide_count = 0
        self.text_shapes_count = 0
    
    def load_document(self, file_path: str) -> None:
        """
        Charge une présentation PowerPoint.
        
        Args:
            file_path: Chemin vers le fichier .pptx ou .ppt
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
        
        self.presentation = Presentation(file_path)
        self.current_path = path
        self.current_document = self.presentation  # Pour compatibilité
        
        # Compter les slides et shapes avec texte
        self.initial_slide_count = len(self.presentation.slides)
        self.text_shapes_count = sum(
            1 for slide in self.presentation.slides
            for shape in slide.shapes
            if shape.has_text_frame
        )
        
        # Détecter la langue
        sample_text = self._extract_sample_text()
        if sample_text:
            lang_code = self.language_detector.detect_language(sample_text)
            if lang_code:
                self.detected_language = lang_code
        
        # Afficher les infos
        print(f"✓ Présentation chargée: {path.name}")
        print(f"  Nombre de slides: {self.initial_slide_count}")
        print(f"  Formes avec texte: {self.text_shapes_count}")
        print(f"  Modèle OpenAI: {self.ai_processor.model}")
        if self.detected_language:
            print(f"  Langue détectée: {self.language_detector.get_language_name(self.detected_language)}")
        
        # Initialiser le log
        doc_info = {
            'slide_count': self.initial_slide_count,
            'text_shapes_count': self.text_shapes_count,
            'language': self.language_detector.get_language_name(self.detected_language) if self.detected_language else None
        }
        self.logger.init_log_file(path.name, doc_info)
    
    def _extract_sample_text(self, max_slides: int = 5) -> str:
        """
        Extrait un échantillon de texte pour la détection de langue.
        
        Args:
            max_slides: Nombre max de slides à analyser
            
        Returns:
            Échantillon de texte
        """
        texts = []
        for i, slide in enumerate(self.presentation.slides):
            if i >= max_slides:
                break
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text.strip()
                    if text and len(text) > 20:
                        texts.append(text)
        
        return " ".join(texts[:10])
    
    def save_document(self, output_path: Optional[str] = None) -> None:
        """
        Sauvegarde la présentation.
        
        Args:
            output_path: Chemin de sortie (optionnel)
        """
        if not self.presentation:
            raise ValueError("Aucune présentation à sauvegarder.")
        
        if output_path is None:
            output_path = self.current_path.parent / f"{self.current_path.stem}_modifié{self.current_path.suffix}"
        
        self.presentation.save(output_path)
        print(f"\n💾 Présentation sauvegardée: {output_path}")
    
    def process_document(self, instruction: str) -> None:
        """
        Traite la présentation avec une instruction.
        
        Args:
            instruction: Instruction à exécuter
        """
        if not self.presentation:
            raise ValueError("Aucune présentation chargée.")
        
        is_correction = any(word in instruction.lower() for word in ['corrige', 'correction', 'orthographe', 'grammaire'])
        
        from features.language_detector import LanguageDetector
        language_name = LanguageDetector.get_language_name(self.detected_language) if self.detected_language else None
        
        print(f"\n🔄 Traitement: {instruction}")
        if is_correction and language_name:
            print(f"   Langue: {language_name}")
        print("=" * 60)
        
        modified_count = 0
        total_text_elements = 0
        
        for slide_num, slide in enumerate(self.presentation.slides, 1):
            for shape_idx, shape in enumerate(slide.shapes):
                if not shape.has_text_frame:
                    continue
                
                # Traiter chaque paragraphe dans la shape
                for para_idx, paragraph in enumerate(shape.text_frame.paragraphs):
                    if not paragraph.text.strip():
                        continue
                    
                    total_text_elements += 1
                    
                    # Créer un contexte (paragraphes précédents de la slide)
                    context = self._get_context(slide, shape, para_idx)
                    
                    print(f"Slide {slide_num}, Forme {shape_idx+1}, Para {para_idx+1}...", end=" ")
                    
                    original_text = paragraph.text
                    processed_text = self.ai_processor.call_openai(
                        instruction, original_text, context, is_correction, language_name
                    )
                    
                    if processed_text and processed_text != original_text:
                        # Extraire et mapper les styles
                        styles_map = self.style_extractor.extract_styles_map(paragraph)
                        new_styles_map = self.style_mapper.map_styles_to_new_text(
                            original_text, processed_text, styles_map
                        )
                        
                        # Appliquer les styles (identique à Word !)
                        self.style_mapper.apply_styles_map(paragraph, processed_text, new_styles_map)
                        
                        # Logger
                        self.logger.log_change(
                            total_text_elements,
                            original_text,
                            processed_text,
                            f"{instruction} (Slide {slide_num}, Shape {shape_idx+1})"
                        )
                        print("✓ Modifié")
                        modified_count += 1
                    else:
                        print("○ Inchangé")
        
        print("=" * 60)
        print(f"✓ Traitement terminé ! ({modified_count} éléments modifiés)")
    
    def _get_context(self, slide, current_shape, current_para_idx: int) -> str:
        """
        Récupère le contexte (paragraphes précédents) pour améliorer la cohérence.
        
        Args:
            slide: Slide actuelle
            current_shape: Shape actuelle
            current_para_idx: Index du paragraphe actuel
            
        Returns:
            Contexte textuel
        """
        context_parts = []
        
        # Ajouter les paragraphes précédents de la même shape
        if current_shape.has_text_frame:
            for i, para in enumerate(current_shape.text_frame.paragraphs):
                if i >= current_para_idx:
                    break
                if para.text.strip():
                    context_parts.append(para.text.strip())
        
        # Prendre les 2 derniers éléments de contexte
        return " [...] ".join(context_parts[-2:]) if context_parts else ""
    
    def process_targeted(self, target, instruction: str) -> None:
        """
        Traite un élément ciblé spécifiquement dans la présentation.
        
        Args:
            target: ResolvedTarget avec slide/shape/paragraph ciblé
            instruction: Instruction à appliquer
        """
        if not self.presentation:
            raise ValueError("Aucune présentation chargée.")
        
        slide_num = target.slide
        shape_idx = target.shape
        
        if not slide_num:
            raise ValueError("Aucune slide ciblée.")
        
        # Vérifier que la slide existe
        if slide_num < 1 or slide_num > len(self.presentation.slides):
            raise ValueError(f"Slide {slide_num} n'existe pas (présentation a {len(self.presentation.slides)} slides).")
        
        slide = self.presentation.slides[slide_num - 1]  # Index 0-based
        
        print(f"\n🎯 Traitement ciblé: Slide {slide_num}", end="")
        if shape_idx is not None:
            print(f", Shape {shape_idx}")
        else:
            print()
        print(f"   Instruction: {instruction}")
        print("=" * 60)
        
        from features.language_detector import LanguageDetector
        is_correction = any(word in instruction.lower() for word in ['corrige', 'correction', 'orthographe', 'grammaire'])
        language_name = LanguageDetector.get_language_name(self.detected_language) if self.detected_language else None
        
        modified_count = 0
        
        # Si shape spécifique
        if shape_idx is not None:
            # Vérifier que la shape existe
            if shape_idx < 0 or shape_idx >= len(slide.shapes):
                raise ValueError(f"Shape {shape_idx} n'existe pas sur la slide {slide_num} ({len(slide.shapes)} shapes).")
            
            shape = slide.shapes[shape_idx]
            if not shape.has_text_frame:
                print(f"⚠️  Shape {shape_idx} n'a pas de texte, ignorée.")
                return
            
            # Traiter tous les paragraphes de cette shape
            for para_idx, paragraph in enumerate(shape.text_frame.paragraphs, 1):
                if not paragraph.text.strip():
                    continue
                
                # Contexte : paragraphes précédents dans la même shape
                context = self._get_context_in_shape(shape, para_idx - 1)
                
                original_text = paragraph.text
                processed_text = self.ai_processor.call_openai(
                    instruction, original_text, context, is_correction, language_name
                )
                
                if processed_text and processed_text != original_text:
                    # Extraire et mapper les styles
                    styles_map = self.style_extractor.extract_styles_map(paragraph)
                    new_styles_map = self.style_mapper.map_styles_to_new_text(
                        original_text, processed_text, styles_map
                    )
                    
                    # Appliquer
                    self.style_mapper.apply_styles_map(paragraph, processed_text, new_styles_map)
                    
                    # Logger
                    self.logger.log_change(
                        f"S{slide_num}-Sh{shape_idx}-P{para_idx}",
                        original_text,
                        processed_text,
                        f"{instruction} (ciblé)"
                    )
                    print(f"  ✓ Paragraphe {para_idx} modifié")
                    modified_count += 1
        
        else:
            # Traiter toutes les shapes de la slide
            for shape_idx, shape in enumerate(slide.shapes):
                if not shape.has_text_frame:
                    continue
                
                for para_idx, paragraph in enumerate(shape.text_frame.paragraphs):
                    if not paragraph.text.strip():
                        continue
                    
                    context = self._get_context_in_shape(shape, para_idx)
                    
                    original_text = paragraph.text
                    processed_text = self.ai_processor.call_openai(
                        instruction, original_text, context, is_correction, language_name
                    )
                    
                    if processed_text and processed_text != original_text:
                        # Extraire et mapper les styles
                        styles_map = self.style_extractor.extract_styles_map(paragraph)
                        new_styles_map = self.style_mapper.map_styles_to_new_text(
                            original_text, processed_text, styles_map
                        )
                        
                        # Appliquer
                        self.style_mapper.apply_styles_map(paragraph, processed_text, new_styles_map)
                        
                        # Logger
                        self.logger.log_change(
                            f"S{slide_num}-Sh{shape_idx}-P{para_idx+1}",
                            original_text,
                            processed_text,
                            f"{instruction} (ciblé)"
                        )
                        modified_count += 1
        
        print("=" * 60)
        print(f"✓ Traitement ciblé terminé ! ({modified_count} éléments modifiés)")
    
    def _get_context_in_shape(self, shape, current_para_idx: int) -> str:
        """
        Récupère le contexte (paragraphes précédents) dans une shape.
        
        Args:
            shape: Shape PowerPoint
            current_para_idx: Index du paragraphe actuel
            
        Returns:
            Contexte textuel
        """
        if not shape.has_text_frame:
            return ""
        
        context_parts = []
        for i, para in enumerate(shape.text_frame.paragraphs):
            if i >= current_para_idx:
                break
            if para.text.strip():
                context_parts.append(para.text.strip())
        
        return " [...] ".join(context_parts[-2:]) if context_parts else ""
    
    def uniformize_styles(self) -> None:
        """
        Uniformise les styles de la présentation.
        """
        if not self.presentation:
            raise ValueError("Aucune présentation chargée.")
        
        print("\n⚠️  Uniformisation PowerPoint : fonctionnalité de base")
        print("L'uniformisation complète (couleurs, interlignes) sera ajoutée prochainement.\n")
        
        # Pour l'instant, uniformisation simple de police et taille
        result = self._uniformize_basic_styles()
        
        # Logger l'opération
        if self.logger.log_file and not result.get('cancelled'):
            with open(self.logger.log_file, 'a', encoding='utf-8') as f:
                f.write("-" * 80 + "\n")
                f.write(f"UNIFORMISATION DES STYLES (PowerPoint)\n")
                f.write(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 80 + "\n\n")
                f.write(f"Police cible: {result.get('target_font', 'N/A')}\n")
                f.write(f"Taille cible: {result.get('target_size', 'N/A')} EMUs\n")
                f.write(f"\nModifications appliquées:\n")
                f.write(f"  Éléments modifiés: {result.get('modified_count', 0)}\n")
                f.write(f"\nNote: Uniformisation de base (police et taille).\n")
                f.write("\n" + "=" * 80 + "\n\n")
    
    def _uniformize_basic_styles(self) -> dict:
        """
        Uniformisation basique : police et taille majoritaires.
        
        Returns:
            Statistiques des modifications
        """
        # Analyser les styles
        from collections import Counter
        fonts = []
        sizes = []
        
        for slide in self.presentation.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.text.strip():
                                if run.font.name:
                                    fonts.append(run.font.name)
                                if run.font.size:
                                    sizes.append(run.font.size)
        
        if not fonts:
            print("⚠️  Aucune police détectée.")
            return {'cancelled': True}
        
        # Valeurs majoritaires
        target_font = Counter(fonts).most_common(1)[0][0]
        target_size = Counter(sizes).most_common(1)[0][0] if sizes else None
        
        print(f"Police majoritaire: {target_font}")
        if target_size:
            print(f"Taille majoritaire: {target_size / 12700:.1f}pt")
        
        confirm = input("\nAppliquer ces styles ? (o/n): ").strip().lower()
        if confirm != 'o':
            print("❌ Annulé")
            return {'cancelled': True}
        
        # Appliquer
        modified_count = 0
        for slide in self.presentation.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.text.strip():
                                if run.font.name != target_font:
                                    run.font.name = target_font
                                    modified_count += 1
                                if target_size and run.font.size != target_size:
                                    run.font.size = target_size
                                    modified_count += 1
        
        print(f"\n✓ Uniformisation terminée ! ({modified_count} changements)")
        
        return {
            'target_font': target_font,
            'target_size': target_size,
            'modified_count': modified_count
        }
    
    def get_format_name(self) -> str:
        """Retourne 'PowerPoint'."""
        return "PowerPoint"
