#!/usr/bin/env python3
"""
Script pour télécharger les images depuis le JSON trié et créer un PDF
"""

import json
import os
import requests
import time
import logging
import sys
import argparse
from typing import List, Dict
from PIL import Image
import io

class PDFCreator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def create_pdf_from_json(self, json_file: str, output_pdf: str = "scribd_document.pdf", temp_dir: str = "temp_images"):
        """
        Télécharge les images depuis le JSON et crée un PDF
        
        Args:
            json_file: Fichier JSON avec les liens triés
            output_pdf: Nom du fichier PDF de sortie
            temp_dir: Dossier temporaire pour les images
        """
        try:
            # Charger le JSON
            self.logger.info(f"📂 Chargement du JSON: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'links' not in data:
                self.logger.error("❌ Clé 'links' non trouvée dans le JSON")
                return {'success': False, 'error': 'Clé links manquante'}
            
            links = data['links']
            self.logger.info(f"📊 {len(links)} images à télécharger")
            
            # Créer le dossier temporaire
            os.makedirs(temp_dir, exist_ok=True)
            
            # Télécharger toutes les images
            self.logger.info("📥 Téléchargement des images...")
            downloaded_files = self._download_all_images(links, temp_dir)
            
            if not downloaded_files:
                self.logger.error("❌ Aucune image téléchargée")
                return {'success': False, 'error': 'Aucune image téléchargée'}
            
            # Créer le PDF
            self.logger.info("📄 Création du PDF...")
            pdf_success = self._create_pdf_from_images(downloaded_files, output_pdf)
            
            if pdf_success:
                # Nettoyer les fichiers temporaires
                self.logger.info("🧹 Nettoyage des fichiers temporaires...")
                self._cleanup_temp_files(downloaded_files)
                
                # Supprimer le dossier temporaire s'il est vide
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass  # Dossier non vide, on le laisse
                
                return {
                    'success': True,
                    'pdf_file': output_pdf,
                    'images_downloaded': len(downloaded_files),
                    'total_links': len(links)
                }
            else:
                return {'success': False, 'error': 'Erreur création PDF'}
            
        except FileNotFoundError:
            self.logger.error(f"❌ Fichier non trouvé: {json_file}")
            return {'success': False, 'error': f'Fichier {json_file} non trouvé'}
        except Exception as e:
            self.logger.error(f"❌ Erreur: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_all_images(self, links: List[str], temp_dir: str) -> List[str]:
        """Télécharger toutes les images"""
        downloaded_files = []
        
        for i, url in enumerate(links):
            try:
                # Générer un nom de fichier avec numéro de page
                page_num = i + 1
                filename = f"page_{page_num:03d}.jpg"
                filepath = os.path.join(temp_dir, filename)
                
                # Télécharger l'image
                if self._download_single_image(url, filepath):
                    downloaded_files.append(filepath)
                    self.logger.info(f"✅ {page_num:03d}/{len(links)} - {filename}")
                else:
                    self.logger.error(f"❌ {page_num:03d}/{len(links)} - Échec téléchargement")
                
                # Petit délai pour éviter de surcharger le serveur
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"💥 Erreur image {i+1}: {e}")
                continue
        
        self.logger.info(f"📊 {len(downloaded_files)}/{len(links)} images téléchargées")
        return downloaded_files
    
    def _download_single_image(self, url: str, filepath: str) -> bool:
        """Télécharger une image"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erreur téléchargement {url}: {e}")
            return False
    
    def _create_pdf_from_images(self, image_files: List[str], output_pdf: str) -> bool:
        """Créer un PDF à partir des images"""
        try:
            if not image_files:
                self.logger.error("❌ Aucune image à convertir")
                return False
            
            # Trier les fichiers par nom pour s'assurer de l'ordre
            image_files.sort()
            
            # Ouvrir toutes les images et les convertir en RGB si nécessaire
            images = []
            for img_path in image_files:
                try:
                    with Image.open(img_path) as img:
                        # Convertir en RGB si nécessaire (pour éviter les problèmes avec les PNG)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Copier l'image en mémoire
                        img_copy = img.copy()
                        images.append(img_copy)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Impossible d'ouvrir {img_path}: {e}")
                    continue
            
            if not images:
                self.logger.error("❌ Aucune image valide trouvée")
                return False
            
            # Créer le PDF
            self.logger.info(f"📄 Création du PDF avec {len(images)} pages...")
            
            # La première image sera la première page
            first_image = images[0]
            other_images = images[1:] if len(images) > 1 else []
            
            # Sauvegarder en PDF
            first_image.save(
                output_pdf,
                save_all=True,
                append_images=other_images,
                format='PDF',
                quality=95,
                optimize=True
            )
            
            self.logger.info(f"✅ PDF créé avec succès: {output_pdf}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création PDF: {e}")
            return False
    
    def _cleanup_temp_files(self, file_list: List[str]):
        """Nettoyer les fichiers temporaires"""
        for file_path in file_list:
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.warning(f"⚠️ Impossible de supprimer {file_path}: {e}")

def main():
    """Script principal avec support des arguments de ligne de commande"""
    
    # Configuration des arguments
    parser = argparse.ArgumentParser(
        description='Créateur de PDF Scribd - Télécharge les images depuis un JSON trié et crée un PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 pdf_creator.py
  python3 pdf_creator.py --pdf "Mon Document.pdf"
  python3 pdf_creator.py --json liens.json --pdf document.pdf
  python3 pdf_creator.py -j liens.json -p "Livre Complet.pdf"
        """
    )
    
    parser.add_argument(
        '-j', '--json',
        default='scribd_sorted_links.json',
        help='Fichier JSON avec les liens triés (défaut: scribd_sorted_links.json)'
    )
    
    parser.add_argument(
        '-p', '--pdf',
        default='scribd_document.pdf',
        help='Nom du fichier PDF de sortie (défaut: scribd_document.pdf)'
    )
    
    parser.add_argument(
        '--temp-dir',
        default='temp_images',
        help='Dossier temporaire pour les images (défaut: temp_images)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Mode interactif (demande les paramètres)'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Supprimer les fichiers JSON temporaires après création du PDF'
    )
    
    # Si aucun argument n'est fourni, utiliser le mode interactif
    if len(sys.argv) == 1:
        args = parser.parse_args(['--interactive'])
    else:
        args = parser.parse_args()
    
    creator = PDFCreator()
    
    print("=== CRÉATEUR DE PDF SCRIBD ===")
    print("Télécharge les images depuis le JSON trié et crée un PDF")
    print()
    
    # Mode interactif ou paramètres
    if args.interactive:
        # Mode interactif classique
        json_file = input(f"Fichier JSON avec les liens (appuyez sur Entrée pour '{args.json}'): ").strip()
        if not json_file:
            json_file = args.json
        
        pdf_file = input(f"Nom du fichier PDF de sortie (appuyez sur Entrée pour '{args.pdf}'): ").strip()
        if not pdf_file:
            pdf_file = args.pdf
        
        temp_dir = args.temp_dir
    else:
        # Utiliser les arguments de ligne de commande
        json_file = args.json
        pdf_file = args.pdf
        temp_dir = args.temp_dir
        
        print(f"📂 JSON source: {json_file}")
        print(f"📄 PDF de sortie: {pdf_file}")
    
    print(f"\n🚀 Création du PDF depuis {json_file}...")
    print(f"📄 Fichier de sortie: {pdf_file}\n")
    
    result = creator.create_pdf_from_json(json_file, pdf_file, temp_dir)
    
    if result['success']:
        print(f"\n🎉 PDF CRÉÉ AVEC SUCCÈS!")
        print(f"📁 Fichier PDF: {result['pdf_file']}")
        print(f"📊 {result['images_downloaded']}/{result['total_links']} images incluses")
        
        # Afficher la taille du fichier
        try:
            file_size = os.path.getsize(result['pdf_file'])
            size_mb = file_size / (1024 * 1024)
            print(f"📏 Taille du PDF: {size_mb:.1f} MB")
        except:
            pass
        
        print(f"\n✅ Le document Scribd a été converti en PDF!")
        
        # Nettoyage optionnel des fichiers JSON
        if args.cleanup:
            print(f"\n🧹 Nettoyage des fichiers JSON temporaires...")
            cleanup_json_files()
        
    else:
        print(f"❌ Erreur: {result['error']}")

def cleanup_json_files():
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

if __name__ == "__main__":
    main()