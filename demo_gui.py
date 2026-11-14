#!/usr/bin/env python3
"""
Démonstration de l'interface graphique Scribd
Test automatisé des fonctionnalités sans interaction utilisateur
"""

import tkinter as tk
from scribd_gui import ScribdGUI
import time

def demo_gui_features():
    """Démonstration automatique des fonctionnalités GUI"""
    print("🎬 DÉMONSTRATION DE L'INTERFACE GRAPHIQUE")
    print("=" * 50)
    
    # Créer l'interface
    app = ScribdGUI()
    
    # Test de configuration automatique
    print("📝 Test de configuration automatique...")
    
    # Remplir le mode simple automatiquement
    app.simple_url.set("https://www.scribd.com/document/845261765/test-document")
    app.simple_pdf_name.set("Document de test")
    app.simple_max_pages.set(50)
    
    print(f"✅ URL configurée: {app.simple_url.get()}")
    print(f"✅ PDF configuré: {app.simple_pdf_name.get()}.pdf")
    print(f"✅ Pages max: {app.simple_max_pages.get()}")
    
    # Test d'ajout de documents pour le mode multi
    print(f"\n📚 Test du mode multi-documents...")
    
    test_documents = [
        {
            'url': 'https://www.scribd.com/document/123456/doc1',
            'pdf_name': 'Document 1.pdf',
            'max_pages': 30
        },
        {
            'url': 'https://www.scribd.com/document/789012/doc2',
            'pdf_name': 'Document 2.pdf',
            'max_pages': 45
        },
        {
            'url': 'https://www.scribd.com/document/345678/doc3',
            'pdf_name': 'Document 3.pdf',
            'max_pages': 25
        }
    ]
    
    # Ajouter les documents
    app.documents_list.extend(test_documents)
    app.refresh_documents_tree()
    
    print(f"✅ {len(test_documents)} documents ajoutés au mode multi")
    
    # Test des logs
    print(f"\n📝 Test du système de logs...")
    app.log_message("🚀 Démonstration démarrée")
    app.log_message("📄 Configuration du mode simple terminée")
    app.log_message("📚 Configuration du mode multi terminée")
    app.log_message("✅ Tous les tests passés avec succès")
    
    # Test de mise à jour des barres de progression
    print(f"\n📊 Test des barres de progression...")
    app.global_progress.set(75)
    app.current_progress.set(50)
    app.global_status_text.set("Démonstration en cours...")
    app.status_text.set("Test des fonctionnalités")
    
    print("✅ Barres de progression mises à jour")
    
    # Simulation de traitement
    print(f"\n⚡ Simulation rapide de traitement...")
    app.log_message("🔄 Début de la simulation de traitement")
    
    for i in range(1, 4):
        app.global_progress.set((i / 3) * 100)
        app.global_status_text.set(f"Document {i}/3 en cours...")
        
        for step in ["Extraction", "Tri", "PDF", "Finalisation"]:
            app.status_text.set(f"{step}...")
            app.log_message(f"📄 Document {i}: {step}")
            app.root.update()  # Rafraîchir l'interface
            time.sleep(0.1)  # Pause courte pour visualiser
    
    app.global_status_text.set("Simulation terminée !")
    app.status_text.set("Prêt")
    app.log_message("🎉 Simulation de traitement terminée")
    
    print("✅ Simulation de traitement terminée")
    
    # Afficher le résumé
    print(f"\n📋 RÉSUMÉ DE LA DÉMONSTRATION")
    print("-" * 40)
    print(f"✅ Interface graphique initialisée")
    print(f"✅ Mode simple configuré")
    print(f"✅ Mode multi-documents configuré ({len(test_documents)} docs)")
    print(f"✅ Système de logs fonctionnel")
    print(f"✅ Barres de progression fonctionnelles")
    print(f"✅ Simulation de traitement réussie")
    
    print(f"\n💡 PROCHAINES ÉTAPES:")
    print("1. Lancez l'interface: python3 main.py --gui")
    print("2. Ou utilisez: python3 scribd_gui.py")
    print("3. Testez les fonctionnalités interactives")
    
    # Garder la fenêtre ouverte quelques secondes
    print(f"\n🖼️  Interface visible pendant 5 secondes...")
    app.root.after(5000, app.root.destroy)  # Fermer après 5 secondes
    
    try:
        app.root.mainloop()
    except tk.TclError:
        pass  # Ignore les erreurs de fermeture
    
    print("🎬 Démonstration terminée")

def test_launcher():
    """Tester le launcher unifié"""
    print(f"\n🚀 TEST DU LAUNCHER UNIFIÉ")
    print("=" * 40)
    
    from main import check_gui_available, check_dependencies
    
    # Test de détection GUI
    gui_available = check_gui_available()
    print(f"🖼️  Interface graphique disponible: {'✅ Oui' if gui_available else '❌ Non'}")
    
    # Test des dépendances
    deps_ok = check_dependencies()
    print(f"📦 Dépendances installées: {'✅ Oui' if deps_ok else '❌ Non'}")
    
    if gui_available and deps_ok:
        print("🎉 Système prêt pour l'interface graphique !")
    elif deps_ok:
        print("🖥️  Système prêt pour l'interface CLI uniquement")
    else:
        print("❌ Installation incomplète")

if __name__ == "__main__":
    test_launcher()
    
    # Tester l'interface seulement si GUI est disponible
    from main import check_gui_available
    if check_gui_available():
        try:
            demo_gui_features()
        except Exception as e:
            print(f"❌ Erreur lors de la démonstration GUI: {e}")
    else:
        print("⚠️  Interface graphique non disponible pour la démonstration")