#!/usr/bin/env python3
"""
Interface simple pour scraper Scribd
Combine l'extraction, le tri et la création de PDF en une seule interface
"""

import os
import sys
import json
import time
import requests
import logging
import re
from urllib.parse import urlparse
from typing import List, Dict, Set
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

class ScribdInterface:
    def __init__(self):
        # Configuration du logging pour être moins verbeux
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.all_links = set()
    
    def print_header(self):
        """Afficher l'en-tête de l'interface"""
        print("\n" + "="*60)
        print("🚀 INTERFACE SCRIBD - SCRAPER MULTI-DOCUMENTS")
        print("="*60)
        print("Extrait, trie et convertit en PDF les documents Scribd")
        print("✨ Nouveautés : Mode multi-documents + Dossier PDFs/")
        print("4 étapes automatisées : Extraction → Tri → PDF → Organisation")
        print("="*60)
    
    def get_user_inputs(self):
        """Récupérer les paramètres de l'utilisateur"""
        print("\n📝 CHOIX DU MODE")
        print("-" * 30)
        print("Voulez-vous traiter un ou plusieurs documents ?")
        print("  [1] Un seul document (mode rapide)")
        print("  [2] Plusieurs documents (mode avancé)")
        
        while True:
            choice = input("\n➤ Votre choix (1 ou 2) : ").strip()
            
            if choice == '1':
                # Mode simple - un seul document
                return self._get_single_document_mode()
            elif choice == '2':
                # Mode multi-documents
                return self._get_multi_document_mode()
            else:
                print("❌ Veuillez choisir 1 ou 2 !")
    
    def _get_single_document_mode(self):
        """Mode simple pour un seul document"""
        print("\n📝 CONFIGURATION SIMPLE")
        print("-" * 30)
        
        # URL du document
        url = input("🌐 URL du document Scribd : ").strip()
        if not url:
            print("❌ URL requise !")
            return None
        
        # Validation basique de l'URL
        if 'scribd.com' not in url:
            print("⚠️ L'URL ne semble pas être un document Scribd")
            confirm = input("Continuer quand même ? (o/N) : ").strip().lower()
            if confirm not in ['o', 'oui', 'y', 'yes']:
                return None
        
        # Nom du PDF de sortie
        pdf_name = input("📄 Nom du PDF de sortie (ex: 'Mon Document.pdf') : ").strip()
        if not pdf_name:
            # Générer un nom par défaut basé sur l'URL
            pdf_name = self._generate_pdf_name_from_url(url)
            print(f"📄 Nom par défaut : {pdf_name}")
        
        # S'assurer que l'extension est .pdf
        if not pdf_name.lower().endswith('.pdf'):
            pdf_name += '.pdf'
        
        # Nombre maximum de pages à traiter
        max_pages_input = input("📊 Nombre max de pages à traiter (Entrée pour 100) : ").strip()
        try:
            max_pages = int(max_pages_input) if max_pages_input else 100
        except ValueError:
            max_pages = 100
        
        # Retourner sous forme de liste pour compatibilité
        return [{
            'url': url,
            'pdf_name': pdf_name,
            'max_pages': max_pages
        }]
    
    def _get_multi_document_mode(self):
        """Mode avancé pour plusieurs documents"""
        documents = self.get_multiple_documents()
        return documents
    
    def _generate_pdf_name_from_url(self, url):
        """Générer un nom de PDF à partir de l'URL"""
        try:
            # Extraire l'ID du document ou le titre depuis l'URL
            if '/document/' in url:
                parts = url.split('/document/')[-1].split('/')
                if len(parts) >= 2:
                    doc_name = parts[1].replace('-', ' ').title()
                    return f"{doc_name}.pdf"
            
            return "document_scribd.pdf"
        except:
            return "document_scribd.pdf"
    
    def get_multiple_documents(self):
        """Interface pour collecter plusieurs documents"""
        print("\n📚 CONFIGURATION MULTI-DOCUMENTS")
        print("=" * 50)
        print("Ajoutez autant de documents Scribd que vous voulez")
        print("Chaque document aura son propre PDF")
        print("=" * 50)
        
        documents = []
        
        while True:
            print(f"\n📋 DOCUMENTS CONFIGURÉS ({len(documents)})")
            print("-" * 30)
            
            # Afficher la liste actuelle
            if documents:
                for i, doc in enumerate(documents, 1):
                    print(f"  {i}. 📄 {doc['pdf_name']}")
                    print(f"     🌐 {doc['url'][:60]}{'...' if len(doc['url']) > 60 else ''}")
                    print(f"     📊 Max {doc['max_pages']} pages")
            else:
                print("  (Aucun document configuré)")
            
            print("\n🎛️  ACTIONS DISPONIBLES")
            print("  [a] Ajouter un document")
            if documents:
                print("  [s] Supprimer un document")
                print("  [m] Modifier un document")
                print("  [t] Terminer et lancer le traitement")
            print("  [q] Quitter")
            
            choice = input("\n➤ Votre choix : ").strip().lower()
            
            if choice == 'a':
                doc = self._get_single_document_config(len(documents) + 1)
                if doc:
                    documents.append(doc)
                    print(f"✅ Document '{doc['pdf_name']}' ajouté !")
            
            elif choice == 's' and documents:
                self._remove_document(documents)
            
            elif choice == 'm' and documents:
                self._modify_document(documents)
            
            elif choice == 't' and documents:
                return documents
            
            elif choice == 'q':
                confirm = input("❓ Êtes-vous sûr de vouloir quitter ? (o/N) : ").strip().lower()
                if confirm in ['o', 'oui', 'y', 'yes']:
                    return None
            
            else:
                print("❌ Choix invalide !")
    
    def _get_single_document_config(self, doc_number):
        """Configurer un seul document"""
        print(f"\n📄 DOCUMENT #{doc_number}")
        print("-" * 25)
        
        # URL du document
        url = input("🌐 URL du document Scribd : ").strip()
        if not url:
            print("❌ URL requise !")
            return None
        
        # Validation basique de l'URL
        if 'scribd.com' not in url:
            print("⚠️ L'URL ne semble pas être un document Scribd")
            confirm = input("Continuer quand même ? (o/N) : ").strip().lower()
            if confirm not in ['o', 'oui', 'y', 'yes']:
                return None
        
        # Nom du PDF de sortie
        pdf_name = input("📄 Nom du PDF de sortie (ex: 'Mon Document.pdf') : ").strip()
        if not pdf_name:
            # Générer un nom par défaut basé sur l'URL
            pdf_name = self._generate_pdf_name_from_url(url)
            print(f"📄 Nom par défaut : {pdf_name}")
        
        # S'assurer que l'extension est .pdf
        if not pdf_name.lower().endswith('.pdf'):
            pdf_name += '.pdf'
        
        # Nombre maximum de pages à traiter
        max_pages_input = input("📊 Nombre max de pages à traiter (Entrée pour 100) : ").strip()
        try:
            max_pages = int(max_pages_input) if max_pages_input else 100
        except ValueError:
            max_pages = 100
        
        return {
            'url': url,
            'pdf_name': pdf_name,
            'max_pages': max_pages
        }
    
    def _remove_document(self, documents):
        """Supprimer un document de la liste"""
        print("\n🗑️  SUPPRIMER UN DOCUMENT")
        print("-" * 25)
        
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc['pdf_name']}")
        
        try:
            choice = int(input("\n➤ Numéro du document à supprimer : ").strip())
            if 1 <= choice <= len(documents):
                removed = documents.pop(choice - 1)
                print(f"✅ Document '{removed['pdf_name']}' supprimé !")
            else:
                print("❌ Numéro invalide !")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide !")
    
    def _modify_document(self, documents):
        """Modifier un document de la liste"""
        print("\n✏️  MODIFIER UN DOCUMENT")
        print("-" * 25)
        
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc['pdf_name']}")
        
        try:
            choice = int(input("\n➤ Numéro du document à modifier : ").strip())
            if 1 <= choice <= len(documents):
                print(f"\n📝 Modification du document #{choice}")
                new_doc = self._get_single_document_config(choice)
                if new_doc:
                    documents[choice - 1] = new_doc
                    print(f"✅ Document modifié !")
            else:
                print("❌ Numéro invalide !")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide !")
    
    def run_complete_workflow(self, documents_list):
        """Exécuter le workflow complet pour un ou plusieurs documents"""
        if not documents_list:
            print("❌ Aucun document à traiter !")
            return False
        
        # S'assurer que le dossier PDFs existe
        self._ensure_pdfs_directory()
        
        total_docs = len(documents_list)
        successful_docs = []
        failed_docs = []
        
        print(f"\n🚀 DÉBUT DU WORKFLOW MULTI-DOCUMENTS")
        print(f"📊 Nombre de documents à traiter : {total_docs}")
        print("="*60)
        
        start_time = time.time()
        
        for doc_index, config in enumerate(documents_list, 1):
            print(f"\n📄 DOCUMENT {doc_index}/{total_docs}")
            print(f"🎯 {config['pdf_name']}")
            print("-" * 50)
            
            doc_start_time = time.time()
            success = self._process_single_document(config, doc_index, total_docs)
            doc_end_time = time.time()
            
            if success:
                successful_docs.append(config['pdf_name'])
                doc_time = doc_end_time - doc_start_time
                print(f"✅ Document {doc_index} terminé en {doc_time:.1f}s")
            else:
                failed_docs.append(config['pdf_name'])
                print(f"❌ Échec du document {doc_index}")
        
        # Nettoyage final
        print(f"\n🧹 NETTOYAGE FINAL DES FICHIERS TEMPORAIRES")
        self._cleanup_json_files()
        
        # Résumé final
        total_time = time.time() - start_time
        self._display_final_summary(successful_docs, failed_docs, total_time)
        
        return len(successful_docs) > 0
    
    def _process_single_document(self, config, doc_index, total_docs):
        """Traiter un seul document"""
        try:
            # ÉTAPE 1: Extraction des liens
            print(f"📥 ÉTAPE 1/3 : EXTRACTION DES LIENS")
            print(f"🌐 URL : {config['url'][:60]}{'...' if len(config['url']) > 60 else ''}")
            
            # Reset des liens pour chaque document
            self.all_links = set()
            
            links = self._extract_links(config['url'], config['max_pages'])
            if not links:
                print("❌ Aucun lien extrait !")
                return False
            
            print(f"✅ {len(links)} liens extraits")
            
            # ÉTAPE 2: Tri des liens
            print(f"🔢 ÉTAPE 2/3 : TRI DES LIENS")
            sorted_links = self._sort_links(links)
            print(f"✅ {len(sorted_links)} liens triés")
            
            # ÉTAPE 3: Création du PDF dans le dossier PDFs/
            print(f"📄 ÉTAPE 3/3 : CRÉATION DU PDF")
            pdf_path = os.path.join("PDFs", config['pdf_name'])
            success = self._create_pdf(sorted_links, pdf_path)
            
            if success:
                # Afficher la taille du fichier
                try:
                    file_size = os.path.getsize(pdf_path)
                    size_mb = file_size / (1024 * 1024)
                    print(f"📁 PDF créé : PDFs/{config['pdf_name']}")
                    print(f"📏 Taille : {size_mb:.1f} MB")
                except:
                    print(f"📁 PDF créé : PDFs/{config['pdf_name']}")
                
                return True
            else:
                print("❌ Erreur lors de la création du PDF")
                return False
                
        except Exception as e:
            print(f"❌ Erreur document : {e}")
            return False
    
    def _display_final_summary(self, successful_docs, failed_docs, total_time):
        """Afficher le résumé final"""
        print("\n" + "="*60)
        print("🎉 RÉSUMÉ FINAL DU TRAITEMENT")
        print("="*60)
        
        print(f"⏱️  Temps total : {total_time:.1f}s")
        print(f"✅ Documents réussis : {len(successful_docs)}")
        print(f"❌ Documents échoués : {len(failed_docs)}")
        
        if successful_docs:
            print(f"\n📁 PDFs créés dans le dossier 'PDFs/' :")
            for pdf_name in successful_docs:
                print(f"   📄 {pdf_name}")
                
        if failed_docs:
            print(f"\n❌ Documents échoués :")
            for pdf_name in failed_docs:
                print(f"   ⚠️  {pdf_name}")
        
        if successful_docs:
            # Calculer la taille totale
            total_size = 0
            for pdf_name in successful_docs:
                try:
                    pdf_path = os.path.join("PDFs", pdf_name)
                    total_size += os.path.getsize(pdf_path)
                except:
                    pass
            
            if total_size > 0:
                total_size_mb = total_size / (1024 * 1024)
                print(f"\n📊 Taille totale des PDFs : {total_size_mb:.1f} MB")
        
        print("="*60)
    
    def _ensure_pdfs_directory(self):
        """S'assurer que le dossier PDFs existe"""
        pdfs_dir = "PDFs"
        
        if not os.path.exists(pdfs_dir):
            try:
                os.makedirs(pdfs_dir)
                print(f"📁 Dossier '{pdfs_dir}/' créé")
            except OSError as e:
                print(f"❌ Impossible de créer le dossier '{pdfs_dir}/' : {e}")
                return False
        else:
            print(f"📁 Dossier '{pdfs_dir}/' déjà existant")
        
        return True
    
    def _extract_links(self, url, max_pages):
        """Extraire les liens depuis Scribd"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            print("🌐 Chargement de la page...")
            driver.get(url)
            time.sleep(5)
            
            print("🔄 Scroll dynamique pour charger toutes les pages...")
            self._dynamic_scroll_and_extract(driver, max_pages)
            
            # Convertir le set en liste triée
            final_links = sorted(list(self.all_links))
            return final_links
            
        except Exception as e:
            print(f"❌ Erreur extraction : {e}")
            return []
        finally:
            driver.quit()
    
    def _dynamic_scroll_and_extract(self, driver, max_attempts):
        """Scroll dynamique et extraction"""
        attempt = 0
        consecutive_no_new_pages = 0
        last_page_count = 0
        
        while attempt < max_attempts and consecutive_no_new_pages < 10:
            attempt += 1
            
            # Compter les pages actuelles
            current_page_count = driver.execute_script("return document.querySelectorAll('.newpage').length;")
            
            # Si on a de nouvelles pages, les traiter
            if current_page_count > last_page_count:
                if attempt % 10 == 0 or current_page_count > last_page_count + 5:
                    print(f"   📄 {current_page_count} pages détectées (tentative {attempt})")
                
                # Traiter les nouvelles pages
                for page_index in range(last_page_count, current_page_count):
                    self._process_single_page(driver, page_index)
                
                last_page_count = current_page_count
                consecutive_no_new_pages = 0
            else:
                consecutive_no_new_pages += 1
            
            # Scroll pour charger plus de contenu
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll plus agressif si besoin
            if consecutive_no_new_pages > 3:
                for _ in range(2):
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(0.5)
        
        print(f"✅ Scroll terminé : {last_page_count} pages trouvées")
    
    def _process_single_page(self, driver, page_index):
        """Traiter une page spécifique"""
        try:
            # Scroll vers cette page
            scroll_script = f"""
                var newpages = document.querySelectorAll('.newpage');
                if (newpages[{page_index}]) {{
                    newpages[{page_index}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    return true;
                }}
                return false;
            """
            
            scrolled = driver.execute_script(scroll_script)
            if not scrolled:
                return
            
            time.sleep(1)  # Attente réduite
            
            # Extraire les liens
            links = self._extract_links_from_page(driver, page_index)
            if links:
                self.all_links.update(links)
                
        except Exception as e:
            pass  # Ignorer les erreurs silencieusement pour l'interface
    
    def _extract_links_from_page(self, driver, page_index):
        """Extraire les liens d'une page"""
        try:
            extract_script = f"""
                var newpages = document.querySelectorAll('.newpage');
                var links = [];
                
                if (newpages[{page_index}]) {{
                    var page = newpages[{page_index}];
                    var images = page.querySelectorAll('.absimg');
                    
                    for (var i = 0; i < images.length; i++) {{
                        var img = images[i];
                        var src = img.src;
                        
                        if (src && 
                            !src.startsWith('data:') && 
                            src.startsWith('http')) {{
                            links.push(src);
                        }}
                    }}
                }}
                
                return links;
            """
            
            return driver.execute_script(extract_script)
            
        except Exception:
            return []
    
    def _sort_links(self, links):
        """Trier les liens par numéro de page"""
        print("🔢 Tri des liens par numéro de page...")
        
        valid_links = []
        pattern = r'/images/(\d{1,2})-'
        
        for link in links:
            match = re.search(pattern, link)
            if match:
                page_number = int(match.group(1))
                valid_links.append({
                    'page_number': page_number,
                    'url': link
                })
        
        # Trier par numéro de page
        valid_links.sort(key=lambda x: x['page_number'])
        
        # Extraire juste les URLs triées
        sorted_urls = [item['url'] for item in valid_links]
        
        if valid_links:
            first_page = valid_links[0]['page_number']
            last_page = valid_links[-1]['page_number']
            print(f"📄 Pages {first_page} à {last_page}")
        
        return sorted_urls
    
    def _create_pdf(self, links, pdf_name):
        """Créer le PDF"""
        if not links:
            print("❌ Aucun lien à traiter")
            return False
        
        print(f"📥 Téléchargement de {len(links)} images...")
        
        # Créer dossier temporaire
        temp_dir = "temp_images_interface"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Télécharger les images
            downloaded_files = []
            
            for i, url in enumerate(links):
                filename = f"page_{i+1:03d}.jpg"
                filepath = os.path.join(temp_dir, filename)
                
                if self._download_single_image(url, filepath):
                    downloaded_files.append(filepath)
                    
                    # Afficher le progrès tous les 10 téléchargements
                    if (i + 1) % 10 == 0 or i + 1 == len(links):
                        print(f"   📥 {i+1}/{len(links)} images téléchargées")
                
                time.sleep(0.1)  # Délai réduit
            
            if not downloaded_files:
                print("❌ Aucune image téléchargée")
                return False
            
            print(f"📄 Création du PDF avec {len(downloaded_files)} pages...")
            
            # Créer le PDF
            success = self._create_pdf_from_images(downloaded_files, pdf_name)
            
            # Nettoyer les fichiers temporaires
            print("🧹 Nettoyage...")
            for file_path in downloaded_files:
                try:
                    os.remove(file_path)
                except:
                    pass
            
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur création PDF : {e}")
            return False
    
    def _download_single_image(self, url, filepath):
        """Télécharger une image"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except Exception:
            return False
    
    def _create_pdf_from_images(self, image_files, output_pdf):
        """Créer un PDF à partir des images"""
        try:
            if not image_files:
                return False
            
            # Trier les fichiers par nom
            image_files.sort()
            
            # Ouvrir toutes les images
            images = []
            for img_path in image_files:
                try:
                    with Image.open(img_path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        images.append(img.copy())
                except Exception:
                    continue
            
            if not images:
                return False
            
            # Créer le PDF
            first_image = images[0]
            other_images = images[1:] if len(images) > 1 else []
            
            first_image.save(
                output_pdf,
                save_all=True,
                append_images=other_images,
                format='PDF',
                quality=95,
                optimize=True
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur création PDF : {e}")
            return False
    
    def _cleanup_json_files(self):
        """Supprimer les fichiers JSON temporaires"""
        json_files_to_remove = [
            'scribd_all_links.json',
            'scribd_sorted_links.json',
            'scribd_fast_links.json',
            'scribd_clean_links.json',
            'scribd_links.json'
        ]
        
        removed_count = 0
        for json_file in json_files_to_remove:
            try:
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"   🗑️  Supprimé : {json_file}")
                    removed_count += 1
            except Exception as e:
                print(f"   ⚠️  Impossible de supprimer {json_file}: {e}")
        
        if removed_count == 0:
            print("   ✅ Aucun fichier JSON temporaire à supprimer")
        else:
            print(f"   ✅ {removed_count} fichier(s) JSON supprimé(s)")

def main():
    """Interface principale"""
    interface = ScribdInterface()
    
    # Vérifier que Pillow est installé
    try:
        import PIL
    except ImportError:
        print("❌ Pillow requis ! Installez avec : pip3 install Pillow")
        return
    
    while True:
        interface.print_header()
        
        # Récupérer les paramètres (maintenant une liste de documents)
        documents_list = interface.get_user_inputs()
        if not documents_list:
            print("❌ Configuration annulée")
            break
        
        # Confirmation avec résumé des documents
        print(f"\n📋 RÉSUMÉ DES DOCUMENTS")
        print("-" * 40)
        for i, config in enumerate(documents_list, 1):
            print(f"📄 Document {i}")
            print(f"   🌐 URL : {config['url'][:50]}{'...' if len(config['url']) > 50 else ''}")
            print(f"   📁 PDF : {config['pdf_name']}")
            print(f"   📊 Max pages : {config['max_pages']}")
            if i < len(documents_list):
                print()
        
        print(f"\n📊 Total : {len(documents_list)} document(s) à traiter")
        print(f"📁 Destination : Dossier PDFs/")
        
        confirm = input("\n🚀 Lancer le traitement ? (O/n) : ").strip().lower()
        if confirm in ['', 'o', 'oui', 'y', 'yes']:
            
            start_time = time.time()
            success = interface.run_complete_workflow(documents_list)
            end_time = time.time()
            
            duration = end_time - start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            if success:
                print(f"\n✅ TRAITEMENT TERMINÉ en {minutes}m {seconds}s !")
                print(f"📁 Vos PDFs sont dans le dossier 'PDFs/'")
            else:
                print(f"\n❌ Échec du traitement après {minutes}m {seconds}s")
        
        # Demander si on veut continuer
        print(f"\n" + "="*60)
        continue_choice = input("🔄 Traiter d'autres documents ? (o/N) : ").strip().lower()
        if continue_choice not in ['o', 'oui', 'y', 'yes']:
            break
    
    print(f"\n👋 Au revoir ! Merci d'avoir utilisé l'interface Scribd")

if __name__ == "__main__":
    main()