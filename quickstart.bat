@echo off
REM Script de démarrage rapide pour Windows

echo ===================================
echo Document Reviewer - Installation
echo ===================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Installer les dépendances
echo Installation des dependances...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERREUR] Echec de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo [OK] Dependances installees avec succes !
echo.
echo ===================================
echo Lancement du script
echo ===================================
echo.

REM Lancer le script principal
python doc_reviewer.py

pause

