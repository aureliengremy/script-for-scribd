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
        print("🚀 INTERFACE SCRIBD - SCRAPER COMPLET")
        print("="*60)
        print("Extrait, trie et convertit en PDF les documents Scribd")
        print("3 étapes automatisées : Extraction → Tri → PDF")
        print("="*60)
    
    def get_user_inputs(self):
        """Récupérer les paramètres de l'utilisateur"""
        print("\n📝 CONFIGURATION")
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
        
        return {
            'url': url,
            'pdf_name': pdf_name,
            'max_pages': max_pages
        }
    
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
    
    def run_complete_workflow(self, config):
        """Exécuter le workflow complet"""
        print(f"\n🚀 DÉBUT DU WORKFLOW COMPLET")
        print(f"📄 URL : {config['url']}")
        print(f"📁 PDF : {config['pdf_name']}")
        print(f"📊 Max pages : {config['max_pages']}")
        
        try:
            # ÉTAPE 1: Extraction des liens
            print(f"\n" + "="*50)
            print("📥 ÉTAPE 1/3 : EXTRACTION DES LIENS")
            print("="*50)
            
            links = self._extract_links(config['url'], config['max_pages'])
            if not links:
                print("❌ Aucun lien extrait !")
                return False
            
            print(f"✅ {len(links)} liens extraits avec succès")
            
            # ÉTAPE 2: Tri des liens
            print(f"\n" + "="*50)
            print("🔢 ÉTAPE 2/3 : TRI DES LIENS")
            print("="*50)
            
            sorted_links = self._sort_links(links)
            print(f"✅ {len(sorted_links)} liens triés par numéro de page")
            
            # ÉTAPE 3: Création du PDF
            print(f"\n" + "="*50)
            print("📄 ÉTAPE 3/3 : CRÉATION DU PDF")
            print("="*50)
            
            success = self._create_pdf(sorted_links, config['pdf_name'])
            
            if success:
                # ÉTAPE 4: Nettoyage des fichiers temporaires
                print(f"\n🧹 NETTOYAGE DES FICHIERS TEMPORAIRES")
                self._cleanup_json_files()
                
                print(f"\n🎉 WORKFLOW TERMINÉ AVEC SUCCÈS !")
                print(f"📁 PDF créé : {config['pdf_name']}")
                
                # Afficher la taille du fichier
                try:
                    file_size = os.path.getsize(config['pdf_name'])
                    size_mb = file_size / (1024 * 1024)
                    print(f"📏 Taille : {size_mb:.1f} MB")
                except:
                    pass
                
                return True
            else:
                print("❌ Erreur lors de la création du PDF")
                return False
            
        except Exception as e:
            print(f"💥 Erreur workflow : {e}")
            return False
    
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
        
        # Récupérer les paramètres
        config = interface.get_user_inputs()
        if not config:
            print("❌ Configuration annulée")
            break
        
        # Confirmation
        print(f"\n📋 RÉSUMÉ")
        print(f"   🌐 URL : {config['url']}")
        print(f"   📄 PDF : {config['pdf_name']}")
        print(f"   📊 Max pages : {config['max_pages']}")
        
        confirm = input("\n🚀 Lancer le scraping ? (O/n) : ").strip().lower()
        if confirm in ['', 'o', 'oui', 'y', 'yes']:
            
            start_time = time.time()
            success = interface.run_complete_workflow(config)
            end_time = time.time()
            
            duration = end_time - start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            if success:
                print(f"\n✅ SUCCÈS TOTAL en {minutes}m {seconds}s !")
                print(f"📁 Votre PDF : {config['pdf_name']}")
            else:
                print(f"\n❌ Échec après {minutes}m {seconds}s")
        
        # Demander si on veut continuer
        print(f"\n" + "="*60)
        continue_choice = input("🔄 Scraper un autre document ? (o/N) : ").strip().lower()
        if continue_choice not in ['o', 'oui', 'y', 'yes']:
            break
    
    print(f"\n👋 Au revoir ! Merci d'avoir utilisé l'interface Scribd")

if __name__ == "__main__":
    main()