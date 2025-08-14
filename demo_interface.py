#!/usr/bin/env python3
"""
Démonstration de l'interface Scribd avec des valeurs par défaut
"""

import sys
import os

# Ajouter le chemin du script principal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scribd_interface import ScribdInterface

def demo():
    """Démonstration avec des valeurs par défaut"""
    interface = ScribdInterface()
    
    # Configuration par défaut
    config = {
        'url': 'https://www.scribd.com/document/845261765/Progressions-Classics-Vol-1-1',
        'pdf_name': 'Demo Progressions Classics Vol 1.pdf',
        'max_pages': 20  # Limité pour la démo
    }
    
    interface.print_header()
    
    print(f"\n📋 DÉMONSTRATION")
    print(f"   🌐 URL : {config['url']}")
    print(f"   📄 PDF : {config['pdf_name']}")
    print(f"   📊 Max pages : {config['max_pages']}")
    
    print(f"\n🚀 Lancement automatique du workflow de démonstration...")
    
    success = interface.run_complete_workflow(config)
    
    if success:
        print(f"\n🎉 DÉMONSTRATION RÉUSSIE !")
        print(f"📁 PDF créé : {config['pdf_name']}")
        
        # Afficher les fichiers créés
        print(f"\n📂 Fichiers dans le dossier :")
        for file in os.listdir('.'):
            if file.endswith('.pdf'):
                size = os.path.getsize(file)
                size_mb = size / (1024 * 1024)
                print(f"   📄 {file} ({size_mb:.1f} MB)")
        
    else:
        print(f"\n❌ Démonstration échouée")

if __name__ == "__main__":
    print("=== DÉMONSTRATION INTERFACE SCRIBD ===")
    print("Cette démo utilise des paramètres prédéfinis")
    print("Pour l'interface interactive, utilisez: python3 scribd_interface.py")
    print()
    
    demo()