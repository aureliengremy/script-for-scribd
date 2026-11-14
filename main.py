#!/usr/bin/env python3
"""
Script de lancement unifié pour le Scribd Scraper
Détecte automatiquement si l'interface graphique est disponible
et lance l'interface appropriée (GUI ou CLI)
"""

import sys
import argparse
import os

def check_gui_available():
    """Vérifier si l'interface graphique est disponible"""
    try:
        import tkinter as tk
        # Test simple pour voir si on peut créer une fenêtre
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre de test
        root.destroy()
        return True
    except Exception:
        return False

def main():
    """Fonction principale de lancement"""
    parser = argparse.ArgumentParser(
        description="🚀 Scribd Scraper - Extracteur de documents Scribd en PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes disponibles:
  --gui         Force l'utilisation de l'interface graphique
  --cli         Force l'utilisation de l'interface en ligne de commande
  
Sans argument, le script détecte automatiquement le meilleur mode.

Exemples:
  python3 main.py              # Détection automatique
  python3 main.py --gui        # Force l'interface graphique
  python3 main.py --cli        # Force l'interface CLI
        """
    )
    
    parser.add_argument('--gui', action='store_true', 
                       help='Forcer l\'utilisation de l\'interface graphique')
    parser.add_argument('--cli', action='store_true', 
                       help='Forcer l\'utilisation de l\'interface en ligne de commande')
    parser.add_argument('--version', action='version', version='Scribd Scraper 2.0')
    
    args = parser.parse_args()
    
    # Vérifier les arguments conflictuels
    if args.gui and args.cli:
        print("❌ Erreur: --gui et --cli ne peuvent pas être utilisés ensemble")
        return 1
    
    # Déterminer le mode à utiliser
    if args.cli:
        use_gui = False
        print("🖥️  Mode CLI forcé par l'utilisateur")
    elif args.gui:
        if check_gui_available():
            use_gui = True
            print("🖼️  Mode GUI forcé par l'utilisateur")
        else:
            print("❌ Interface graphique non disponible, basculement vers CLI")
            use_gui = False
    else:
        # Détection automatique
        use_gui = check_gui_available()
        if use_gui:
            print("🖼️  Interface graphique détectée, lancement en mode GUI")
        else:
            print("🖥️  Interface graphique non disponible, lancement en mode CLI")
    
    # Lancer l'interface appropriée
    try:
        if use_gui:
            print("📊 Chargement de l'interface graphique...")
            from scribd_gui import main as gui_main
            return gui_main()
        else:
            print("📊 Chargement de l'interface en ligne de commande...")
            from scribd_interface import main as cli_main
            return cli_main()
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        
        # Fallback vers l'autre interface
        if use_gui:
            print("💡 Tentative de basculement vers l'interface CLI...")
            try:
                from scribd_interface import main as cli_main
                return cli_main()
            except ImportError:
                print("❌ Impossible de charger l'interface CLI")
                return 1
        else:
            print("💡 Vérifiez que scribd_interface.py est présent")
            return 1
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return 1

def show_startup_info():
    """Afficher les informations de démarrage"""
    print("=" * 60)
    print("🚀 SCRIBD SCRAPER - LAUNCHER UNIFIÉ")
    print("=" * 60)
    print("Interface moderne pour extraire des documents Scribd en PDF")
    print("✨ Modes: Interface graphique (GUI) + Ligne de commande (CLI)")
    print("📁 Organisation automatique dans le dossier PDFs/")
    print("=" * 60)

def check_dependencies():
    """Vérifier les dépendances essentielles"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append('requests')
    
    try:
        import selenium
    except ImportError:
        missing_deps.append('selenium')
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append('Pillow')
    
    try:
        import beautifulsoup4
    except ImportError:
        try:
            import bs4
        except ImportError:
            missing_deps.append('beautifulsoup4')
    
    if missing_deps:
        print("❌ Dépendances manquantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Installez avec: pip3 install", " ".join(missing_deps))
        return False
    
    return True

if __name__ == "__main__":
    show_startup_info()
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Vérifier que les fichiers principaux existent
    if not os.path.exists('scribd_interface.py'):
        print("❌ Fichier scribd_interface.py manquant")
        sys.exit(1)
    
    # Lancer l'application
    exit_code = main()
    sys.exit(exit_code or 0)