"""
Exemples d'utilisation du DocumentReviewer
"""

from doc_reviewer import DocumentReviewer
import os


def exemple_correction_simple():
    """Exemple 1: Correction simple d'orthographe."""
    print("EXEMPLE 1: Correction d'orthographe")
    print("=" * 60)
    
    reviewer = DocumentReviewer(api_key=os.getenv("OPENAI_API_KEY"))
    reviewer.load_document("Documentation Hyper Open X.docx")
    reviewer.process_document("Corrige les fautes d'orthographe et de grammaire")
    reviewer.save_document("Documentation_corrigée.docx")


def exemple_traduction():
    """Exemple 2: Traduction du document."""
    print("\nEXEMPLE 2: Traduction")
    print("=" * 60)
    
    reviewer = DocumentReviewer(api_key=os.getenv("OPENAI_API_KEY"))
    reviewer.load_document("Documentation Hyper Open X.docx")
    reviewer.process_document("Traduis ce texte en anglais")
    reviewer.save_document("Documentation_EN.docx")


def exemple_multiples_operations():
    """Exemple 3: Plusieurs opérations successives avec contexte."""
    print("\nEXEMPLE 3: Opérations multiples avec contexte")
    print("=" * 60)
    
    reviewer = DocumentReviewer(api_key=os.getenv("OPENAI_API_KEY"))
    reviewer.load_document("Documentation Hyper Open X.docx")
    
    # 1. Corriger l'orthographe
    print("\n1. Correction orthographique...")
    reviewer.process_document("Corrige les fautes d'orthographe")
    
    # 2. Améliorer le style (le contexte de la correction est conservé)
    print("\n2. Amélioration du style...")
    reviewer.process_document("Améliore le style et rends le texte plus professionnel")
    
    # 3. Simplifier le langage
    print("\n3. Simplification...")
    reviewer.process_document("Simplifie le langage pour le rendre accessible à tous")
    
    reviewer.save_document("Documentation_améliorée.docx")


def exemple_instruction_personnalisée():
    """Exemple 4: Instruction personnalisée."""
    print("\nEXEMPLE 4: Instruction personnalisée")
    print("=" * 60)
    
    reviewer = DocumentReviewer(api_key=os.getenv("OPENAI_API_KEY"))
    reviewer.load_document("Documentation Hyper Open X.docx")
    
    # Instruction très spécifique
    reviewer.process_document(
        "Réécris ce texte en adoptant un ton marketing dynamique, "
        "utilise des verbes d'action et ajoute des émojis pertinents"
    )
    
    reviewer.save_document("Documentation_marketing.docx")


def exemple_mode_interactif():
    """Exemple 5: Utilisation du mode interactif."""
    print("\nEXEMPLE 5: Mode interactif")
    print("=" * 60)
    print("Le mode interactif permet de tester plusieurs commandes:")
    print("- corrige")
    print("- traduis espagnol")
    print("- améliore")
    print("- résume")
    print("- save")
    print("\nLancez: python doc_reviewer.py")


if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLES D'UTILISATION - Document Reviewer")
    print("=" * 60)
    print("\nChoisissez un exemple:")
    print("1. Correction simple d'orthographe")
    print("2. Traduction en anglais")
    print("3. Opérations multiples avec contexte")
    print("4. Instruction personnalisée")
    print("5. Mode interactif (info)")
    
    choix = input("\n➤ Votre choix (1-5): ").strip()
    
    exemples = {
        "1": exemple_correction_simple,
        "2": exemple_traduction,
        "3": exemple_multiples_operations,
        "4": exemple_instruction_personnalisée,
        "5": exemple_mode_interactif,
    }
    
    if choix in exemples:
        exemples[choix]()
    else:
        print("❌ Choix invalide")

