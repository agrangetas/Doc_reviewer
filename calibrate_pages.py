"""
Script de calibration pour l'estimation de pages
Aide à trouver la bonne valeur de CHARS_PER_PAGE pour votre document
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from pathlib import Path

print("🎯 Calibration de l'estimation de pages\n")
print("=" * 60)

# Demander le fichier
file_path = input("\nChemin du document Word: ").strip().strip('"')

if not file_path or not Path(file_path).exists():
    print("❌ Fichier non trouvé")
    sys.exit(1)

# Demander le nombre réel de pages
real_pages = input("Nombre RÉEL de pages dans ce document: ").strip()

try:
    real_pages = int(real_pages)
except ValueError:
    print("❌ Nombre invalide")
    sys.exit(1)

# Charger le document
print(f"\n📄 Chargement de {Path(file_path).name}...")
doc = Document(file_path)

# Calculer les caractères totaux
total_chars = 0
total_paras = 0

for para in doc.paragraphs:
    text = para.text.strip()
    if text:
        weight = len(text)
        
        # Ajuster pour les titres
        if para.style and para.style.name and ('Heading' in para.style.name or 'Titre' in para.style.name):
            weight = int(weight * 1.5)
        
        total_chars += weight
        total_paras += 1

print(f"   ✓ {total_paras} paragraphes")
print(f"   ✓ {total_chars:,} caractères (pondérés)")

# Calculer la meilleure estimation
chars_per_page = total_chars // real_pages

print("\n" + "=" * 60)
print("📊 RÉSULTAT DE LA CALIBRATION")
print("=" * 60)
print(f"\nPour ce document ({real_pages} pages):")
print(f"  Caractères totaux: {total_chars:,}")
print(f"  Caractères/page optimal: ~{chars_per_page}")

print(f"\n💡 Ajoutez ceci dans votre fichier .env :")
print(f"   CHARS_PER_PAGE={chars_per_page}")

# Tester différentes valeurs
print(f"\n📈 Comparaison avec différentes estimations:")
print(f"   {'Valeur':<15} {'Pages estimées':<15} {'Erreur'}")
print("   " + "-" * 50)

for test_value in [800, 1000, 1200, 1500, 1800, 2000, chars_per_page]:
    estimated = max(1, (total_chars // test_value) + 1)
    error = abs(estimated - real_pages)
    marker = " ← OPTIMAL" if test_value == chars_per_page else ""
    print(f"   {test_value:<15} {estimated:<15} {error} pages{marker}")

print("\n" + "=" * 60)
print("✅ Calibration terminée !")
print("=" * 60)

