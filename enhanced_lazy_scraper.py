#!/usr/bin/env python3
"""
Scraper amélioré qui continue à scroller pour charger toutes les pages .newpage
et gère le lazy loading dynamique
"""

import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class EnhancedLazyScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.all_links = set()  # Utiliser un set pour éviter automatiquement les doublons
    
    def scrape_all_pages_dynamic(self, url: str, output_file: str = "scribd_all_links.json", max_attempts: int = 100):
        """
        Scroll dynamiquement pour charger toutes les pages .newpage
        et extraire tous les liens des images .absimg
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            self.logger.info(f"🌐 Chargement de: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Commencer par le scroll dynamique
            self.logger.info("🔄 Début du scroll dynamique pour charger toutes les pages...")
            total_pages_found = self._dynamic_scroll_and_extract(driver, max_attempts)
            
            # Convertir le set en liste triée
            final_links = sorted(list(self.all_links))
            
            self.logger.info(f"🎉 Extraction terminée!")
            self.logger.info(f"📄 {total_pages_found} pages .newpage traitées")
            self.logger.info(f"🔗 {len(final_links)} liens uniques extraits")
            
            # Sauvegarder le JSON clean
            self._save_final_json(final_links, output_file)
            
            return {
                'success': True,
                'file': output_file,
                'total_links': len(final_links),
                'pages_found': total_pages_found
            }
            
        except Exception as e:
            self.logger.error(f"💥 Erreur: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            driver.quit()
    
    def _dynamic_scroll_and_extract(self, driver, max_attempts):
        """Scroll dynamique pour charger et traiter toutes les pages"""
        
        attempt = 0
        consecutive_no_new_pages = 0
        last_page_count = 0
        
        while attempt < max_attempts and consecutive_no_new_pages < 10:
            attempt += 1
            
            # Compter les pages actuelles
            current_page_count = driver.execute_script("return document.querySelectorAll('.newpage').length;")
            
            # Si on a de nouvelles pages, les traiter
            if current_page_count > last_page_count:
                self.logger.info(f"🔍 Tentative {attempt}: {current_page_count} pages .newpage trouvées")
                
                # Traiter les nouvelles pages
                for page_index in range(last_page_count, current_page_count):
                    self._process_single_page(driver, page_index)
                
                last_page_count = current_page_count
                consecutive_no_new_pages = 0
            else:
                consecutive_no_new_pages += 1
                if consecutive_no_new_pages <= 5:
                    self.logger.info(f"🔄 Tentative {attempt}: Aucune nouvelle page, scroll pour en charger...")
            
            # Scroll vers le bas pour charger plus de contenu
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Scroll vers la fin du document
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight + 1000);")
            time.sleep(1)
            
            # Parfois, il faut scroller plus agressivement
            if consecutive_no_new_pages > 3:
                self.logger.info("   🚀 Scroll agressif pour débloquer plus de contenu...")
                for _ in range(3):
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(1)
        
        return last_page_count
    
    def _process_single_page(self, driver, page_index):
        """Traiter une page .newpage spécifique"""
        try:
            self.logger.info(f"📄 Traitement page {page_index + 1}")
            
            # Scroll vers cette page spécifique
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
                self.logger.warning(f"   ⚠️ Page {page_index + 1} introuvable")
                return
            
            # Attendre le chargement des images
            time.sleep(3)
            
            # Extraire les liens
            links = self._extract_links_from_page(driver, page_index)
            
            if links:
                before_count = len(self.all_links)
                self.all_links.update(links)  # Ajouter au set (dédoublonnage automatique)
                new_links = len(self.all_links) - before_count
                
                if new_links > 0:
                    self.logger.info(f"   ✅ {new_links} nouveaux liens (+{len(links)} trouvés, total unique: {len(self.all_links)})")
                else:
                    self.logger.info(f"   📭 {len(links)} liens trouvés (déjà connus)")
            else:
                self.logger.info(f"   📭 Aucun lien sur cette page")
                
        except Exception as e:
            self.logger.error(f"   💥 Erreur page {page_index + 1}: {e}")
    
    def _extract_links_from_page(self, driver, page_index):
        """Extraire les liens src des images .absimg d'une page"""
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
                        
                        // Vérifier que le src est valide
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
            
        except Exception as e:
            self.logger.error(f"Erreur extraction page {page_index}: {e}")
            return []
    
    def _save_final_json(self, links, output_file):
        """Sauvegarder le JSON final clean"""
        
        data = {
            "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_links": len(links),
            "links": links
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 JSON final sauvegardé: {output_file}")
        
        # Afficher quelques exemples
        self.logger.info("📋 Exemples de liens extraits:")
        for i, link in enumerate(links[:10]):
            filename = link.split('/')[-1]
            self.logger.info(f"   {i+1:2d}. {filename}")
        
        if len(links) > 10:
            self.logger.info(f"   ... et {len(links) - 10} autres liens")

def main():
    """Script principal"""
    scraper = EnhancedLazyScraper()
    
    url = "https://www.scribd.com/document/845261765/Progressions-Classics-Vol-1-1"
    
    print("=== SCRAPER LAZY LOADING AMÉLIORÉ ===")
    print("Scroll dynamique pour charger TOUTES les pages .newpage")
    print("Gestion automatique du lazy loading")
    print("JSON clean avec seulement les liens\n")
    
    # Demander le nombre max de tentatives
    try:
        max_attempts = int(input("Nombre max de tentatives de scroll (appuyez sur Entrée pour 50): ") or "50")
    except ValueError:
        max_attempts = 50
    
    result = scraper.scrape_all_pages_dynamic(url, "scribd_all_links.json", max_attempts)
    
    if result['success']:
        print(f"\n✅ EXTRACTION COMPLÈTE RÉUSSIE!")
        print(f"📁 Fichier JSON: {result['file']}")
        print(f"📊 {result['total_links']} liens uniques extraits")
        print(f"📄 {result['pages_found']} pages .newpage traitées")
        
        if result['total_links'] >= 80:
            print("🎉 Excellent! Probablement toutes les images récupérées!")
        elif result['total_links'] >= 10:
            print("👍 Bon résultat! Peut-être essayer avec plus de tentatives.")
        else:
            print("🤔 Peu de liens trouvés, vérifiez la structure de la page.")
            
    else:
        print(f"❌ Erreur: {result.get('error')}")

if __name__ == "__main__":
    main()