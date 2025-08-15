#!/usr/bin/env python3
"""
Démonstration de l'interface multi-documents Scribd
Montre comment utiliser programmatiquement l'interface
"""

from scribd_interface import ScribdInterface

def demo_multi_documents():
    """Démonstration avec plusieurs documents simulés"""
    print("🎬 DÉMONSTRATION MULTI-DOCUMENTS")
    print("="*50)
    
    # Créer l'interface
    interface = ScribdInterface()
    
    # Documents d'exemple (simulés)
    documents_list = [
        {
            'url': 'https://www.scribd.com/document/123456/document-1',
            'pdf_name': 'Document 1 - Introduction.pdf',
            'max_pages': 20
        },
        {
            'url': 'https://www.scribd.com/document/789012/document-2', 
            'pdf_name': 'Document 2 - Développement.pdf',
            'max_pages': 50
        },
        {
            'url': 'https://www.scribd.com/document/345678/document-3',
            'pdf_name': 'Document 3 - Conclusion.pdf', 
            'max_pages': 15
        }
    ]
    
    print(f"📊 Documents à traiter : {len(documents_list)}")
    for i, doc in enumerate(documents_list, 1):
        print(f"   {i}. {doc['pdf_name']} ({doc['max_pages']} pages max)")
    
    print(f"\n📁 Destination : Dossier PDFs/")
    
    # Simuler le traitement (sans vraiment scraper)
    print(f"\n🚀 SIMULATION DU TRAITEMENT")
    print("-" * 30)
    
    # Créer le dossier PDFs
    interface._ensure_pdfs_directory()
    
    for i, doc in enumerate(documents_list, 1):
        print(f"\n📄 Document {i}/{len(documents_list)}: {doc['pdf_name']}")
        print(f"   ✅ Extraction simulée : {doc['max_pages']} images")
        print(f"   ✅ Tri simulé")
        print(f"   ✅ PDF créé dans PDFs/{doc['pdf_name']}")
    
    print(f"\n🎉 SIMULATION TERMINÉE !")
    print(f"✅ {len(documents_list)} documents traités")
    print(f"📁 PDFs disponibles dans le dossier 'PDFs/'")

def demo_interface_choices():
    """Démonstration des choix d'interface"""
    print(f"\n🎭 DÉMONSTRATION DES MODES")
    print("="*40)
    
    print(f"\n📝 CHOIX DU MODE")
    print("-" * 30)
    print("Voulez-vous traiter un ou plusieurs documents ?")
    print("  [1] Un seul document (mode rapide)")
    print("  [2] Plusieurs documents (mode avancé)")
    
    print(f"\n💡 AVANTAGES DU MODE MULTI-DOCUMENTS :")
    print("  ✅ Traite plusieurs URLs en une session")
    print("  ✅ Configuration individuelle par document")
    print("  ✅ Organisation automatique dans PDFs/")
    print("  ✅ Résumé global avec statistiques")
    print("  ✅ Gestion d'erreurs par document")

if __name__ == "__main__":
    demo_interface_choices()
    demo_multi_documents()
    
    print(f"\n📚 UTILISATION RÉELLE :")
    print("Pour utiliser l'interface complète, lancez :")
    print("python3 scribd_interface.py")