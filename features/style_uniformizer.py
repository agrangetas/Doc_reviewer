"""
Style uniformization without LLM.
Uniformise les styles du document selon une configuration.
"""

from typing import Dict, List, Optional, Tuple
from collections import Counter


class StyleUniformizer:
    """Uniformise les styles d'un document Word sans utiliser de LLM."""
    
    def __init__(self, config):
        """
        Initialise l'uniformizer.
        
        Args:
            config: Objet Config contenant la configuration des styles
        """
        self.config = config
        self.style_config = config.load_style_config()
    
    def analyze_document_styles(self, document) -> Dict:
        """
        Analyse les styles du document pour détecter le style majoritaire.
        
        Args:
            document: Document docx
            
        Returns:
            Dictionnaire avec les statistiques de style
        """
        fonts = []
        sizes_text = []
        sizes_headings = []
        total_runs = 0
        runs_with_font = 0
        runs_without_font = 0
        heading_count = 0
        
        for paragraph in document.paragraphs:
            # Détecter si c'est un titre
            is_heading = self._is_heading(paragraph)
            if is_heading:
                heading_count += 1
            
            for run in paragraph.runs:
                if run.text.strip():
                    total_runs += 1
                    # Ignorer les polices None
                    if run.font.name:
                        fonts.append(run.font.name)
                        runs_with_font += 1
                    else:
                        runs_without_font += 1
                    if run.font.size:
                        if is_heading:
                            sizes_headings.append(run.font.size)
                        else:
                            sizes_text.append(run.font.size)
        
        # Calculer les valeurs majoritaires
        most_common_font = Counter(fonts).most_common(1)[0] if fonts else (None, 0)
        most_common_size_text = Counter(sizes_text).most_common(1)[0] if sizes_text else (None, 0)
        most_common_size_heading = Counter(sizes_headings).most_common(1)[0] if sizes_headings else (None, 0)
        
        return {
            'font': {
                'most_common': most_common_font[0],
                'percentage': (most_common_font[1] / len(fonts) * 100) if fonts else 0,
                'all_fonts': Counter(fonts)
            },
            'size_text': {
                'most_common': most_common_size_text[0],
                'percentage': (most_common_size_text[1] / len(sizes_text) * 100) if sizes_text else 0
            },
            'size_heading': {
                'most_common': most_common_size_heading[0],
                'percentage': (most_common_size_heading[1] / len(sizes_headings) * 100) if sizes_headings else 0
            },
            'debug': {
                'total_runs': total_runs,
                'runs_with_font': runs_with_font,
                'runs_without_font': runs_without_font,
                'heading_count': heading_count
            }
        }
    
    def _is_heading(self, paragraph) -> bool:
        """
        Détermine si un paragraphe est un titre.
        
        Args:
            paragraph: Paragraphe docx
            
        Returns:
            True si c'est un titre
        """
        # Vérifier le style Word en priorité
        if self.style_config['heading_detection']['use_word_styles']:
            style_name = paragraph.style.name if hasattr(paragraph.style, 'name') else str(paragraph.style)
            if 'Heading' in style_name or 'Titre' in style_name:
                return True
        
        # Utiliser les heuristiques si configuré
        if self.style_config['heading_detection']['use_heuristics']:
            # Titre court
            if len(paragraph.text.strip()) == 0:
                return False
            if len(paragraph.text) > self.style_config['heading_detection']['heuristic_rules']['max_length']:
                return False
            
            # Vérifier la taille de police (plus grande que le texte normal)
            if paragraph.runs:
                first_run = paragraph.runs[0]
                if first_run.font.size:
                    # Si la taille est > 12pt (152400 EMUs), probablement un titre
                    if first_run.font.size > 152400:
                        return True
            
            # Vérifier le bold
            if paragraph.runs and paragraph.runs[0].bold:
                # Bold + court = probablement un titre
                if len(paragraph.text) < 100:
                    return True
        
        return False
    
    def _is_intentional_emphasis(self, paragraph, run_index: int) -> bool:
        """
        Détermine si un style est une emphase intentionnelle.
        
        Args:
            paragraph: Paragraphe docx
            run_index: Index du run
            
        Returns:
            True si c'est une emphase intentionnelle à préserver
        """
        if not self.style_config['exceptions']['preserve_if_single_word']:
            return False
        
        run = paragraph.runs[run_index]
        
        # Si c'est un seul mot avec un style différent, c'est intentionnel
        words_in_run = len(run.text.split())
        if words_in_run <= 1:
            # Vérifier si le style est différent des runs adjacents
            has_different_style = False
            
            if run.bold or run.italic or run.underline:
                # Comparer avec les runs adjacents
                if run_index > 0:
                    prev_run = paragraph.runs[run_index - 1]
                    if (run.bold != prev_run.bold or 
                        run.italic != prev_run.italic or 
                        run.underline != prev_run.underline):
                        has_different_style = True
                
                if run_index < len(paragraph.runs) - 1:
                    next_run = paragraph.runs[run_index + 1]
                    if (run.bold != next_run.bold or 
                        run.italic != next_run.italic or 
                        run.underline != next_run.underline):
                        has_different_style = True
            
            return has_different_style
        
        return False
    
    def uniformize(self, document) -> Dict:
        """
        Uniformise les styles du document.
        
        Args:
            document: Document docx
            
        Returns:
            Dictionnaire avec les statistiques de modifications
        """
        # Analyser le document
        analysis = self.analyze_document_styles(document)
        
        # Déterminer les valeurs cibles
        target_font = self.style_config['font']['name']
        if target_font == 'auto':
            target_font = analysis['font']['most_common']
        
        target_size_text = self.style_config['sizes']['text_normal']
        if target_size_text == 'auto':
            target_size_text = analysis['size_text']['most_common']
        
        print("\n" + "=" * 60)
        print("UNIFORMISATION DES STYLES")
        print("=" * 60)
        print(f"\nAnalyse du document:")
        print(f"  Paragraphes totaux: {len(document.paragraphs)}")
        print(f"  Titres détectés: {analysis['debug']['heading_count']}")
        print(f"  Runs analysés: {analysis['debug']['total_runs']}")
        print(f"  Runs avec police: {analysis['debug']['runs_with_font']}")
        print(f"  Runs sans police: {analysis['debug']['runs_without_font']}")
        print(f"\n  Police majoritaire: {analysis['font']['most_common'] or '(non détectée)'} ({analysis['font']['percentage']:.1f}%)")
        
        # Afficher les polices détectées si utile
        if analysis['font']['all_fonts']:
            top_fonts = analysis['font']['all_fonts'].most_common(3)
            if len(top_fonts) > 1:
                print(f"  Autres polices: {', '.join([f'{font} ({count})' for font, count in top_fonts[1:]])}")
        
        # Convertir EMUs en points pour l'affichage (12700 EMUs = 1 point)
        size_in_points = analysis['size_text']['most_common'] / 12700 if analysis['size_text']['most_common'] else None
        print(f"  Taille texte majoritaire: {size_in_points:.1f}pt ({analysis['size_text']['most_common']} EMUs)" if size_in_points else "  Taille texte majoritaire: (non détectée)")
        
        # Vérifier qu'on a au moins une valeur à uniformiser
        if not target_font and not target_size_text:
            print("\n⚠️  Impossible d'uniformiser : aucune police ou taille détectée.")
            print("   Le document ne contient peut-être pas d'informations de formatage exploitables.")
            return {'error': 'no_valid_styles'}
        
        # Demander confirmation si configuré
        if self.style_config['application']['ask_confirmation']:
            print(f"\nUniformisation proposée:")
            print(f"  Police: {target_font or '(inchangée)'}")
            print(f"  Taille texte: {target_size_text or '(inchangée)'}")
            
            confirm = input("\nAppliquer ces modifications ? (o/n): ").strip().lower()
            if confirm != 'o':
                print("❌ Annulé")
                return {'cancelled': True}
        
        # Appliquer l'uniformisation
        modified_paragraphs = 0
        preserved_emphasis = 0
        font_changes = 0
        size_changes = 0
        
        print("\n🔄 Application des modifications...")
        
        for paragraph in document.paragraphs:
            is_heading = self._is_heading(paragraph)
            paragraph_modified = False
            
            for i, run in enumerate(paragraph.runs):
                if not run.text.strip():
                    continue
                
                # Vérifier si c'est une emphase intentionnelle
                is_emphasis = self._is_intentional_emphasis(paragraph, i)
                
                if is_emphasis and self.style_config['preserve']['intentional_emphasis']:
                    preserved_emphasis += 1
                    # Changer la police mais garder le style (bold/italic)
                    if target_font and run.font.name != target_font:
                        run.font.name = target_font
                        paragraph_modified = True
                        font_changes += 1
                    continue
                
                # Uniformiser la police
                if target_font and run.font.name != target_font:
                    run.font.name = target_font
                    paragraph_modified = True
                    font_changes += 1
                
                # Uniformiser la taille (seulement pour texte normal)
                if not is_heading and target_size_text and run.font.size != target_size_text:
                    run.font.size = target_size_text
                    paragraph_modified = True
                    size_changes += 1
            
            if paragraph_modified:
                modified_paragraphs += 1
        
        print(f"\n✓ Uniformisation terminée !")
        print(f"  Paragraphes modifiés: {modified_paragraphs}")
        print(f"  Changements de police: {font_changes}")
        print(f"  Changements de taille: {size_changes}")
        print(f"  Emphases préservées: {preserved_emphasis}")
        print("=" * 60)
        
        return {
            'modified_paragraphs': modified_paragraphs,
            'preserved_emphasis': preserved_emphasis,
            'target_font': target_font,
            'target_size': target_size_text
        }

