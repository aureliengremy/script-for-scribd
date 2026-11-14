#!/usr/bin/env python3
"""
Interface graphique Tkinter pour le scraper Scribd
Utilise la logique de scribd_interface.py avec une interface moderne
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import time
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# Import de notre interface CLI existante
from scribd_interface import ScribdInterface

class ScribdGUI:
    def __init__(self):
        """Initialiser l'interface graphique"""
        self.root = tk.Tk()
        self.setup_window()
        
        # Interface CLI pour la logique métier
        self.scribd_interface = ScribdInterface()
        
        # Variables pour le threading
        self.processing_thread = None
        self.processing_queue = queue.Queue()
        self.is_processing = False
        
        # Données de l'interface
        self.documents_list = []
        self.current_document_index = 0
        
        # Variables Tkinter
        self.setup_variables()
        
        # Créer l'interface
        self.create_widgets()
        self.setup_menu()
        
        # Timer pour vérifier la queue
        self.root.after(100, self.check_queue)
    
    def setup_window(self):
        """Configurer la fenêtre principale"""
        self.root.title("🚀 Scribd Scraper - Interface Graphique")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Icône (si disponible)
        try:
            # On peut ajouter une icône plus tard
            pass
        except:
            pass
        
        # Style moderne
        style = ttk.Style()
        # Utiliser un thème moderne si disponible
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
    
    def setup_variables(self):
        """Initialiser les variables Tkinter"""
        # Variables pour le mode simple
        self.simple_url = tk.StringVar()
        self.simple_pdf_name = tk.StringVar()
        self.simple_max_pages = tk.IntVar(value=100)
        
        # Variables pour les progress bars
        self.global_progress = tk.DoubleVar()
        self.current_progress = tk.DoubleVar()
        
        # Variables pour les statuts
        self.status_text = tk.StringVar(value="Prêt")
        self.global_status_text = tk.StringVar(value="Aucun traitement en cours")
    
    def setup_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir dossier PDFs", command=self.open_pdfs_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Effacer l'historique", command=self.clear_history)
        tools_menu.add_command(label="Interface CLI", command=self.launch_cli)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def create_widgets(self):
        """Créer tous les widgets de l'interface"""
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Titre principal
        title_label = ttk.Label(
            main_frame, 
            text="🚀 Scribd Scraper - Interface Graphique",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Créer les onglets
        self.create_simple_tab()
        self.create_multi_tab()
        self.create_logs_tab()
        
        # Frame de statut en bas
        self.create_status_frame(main_frame)
    
    def create_simple_tab(self):
        """Créer l'onglet pour le mode simple"""
        # Frame de l'onglet
        simple_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(simple_frame, text="📄 Document simple")
        
        # Configuration du grid
        simple_frame.columnconfigure(1, weight=1)
        
        # Section URL
        ttk.Label(simple_frame, text="🌐 URL du document Scribd:", 
                 font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        url_frame = ttk.Frame(simple_frame)
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.simple_url, font=('TkDefaultFont', 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        
        self.validate_btn = ttk.Button(url_frame, text="Valider", command=self.validate_url)
        self.validate_btn.grid(row=0, column=1)
        
        # Section nom du PDF
        ttk.Label(simple_frame, text="📄 Nom du PDF de sortie:", 
                 font=('TkDefaultFont', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        pdf_frame = ttk.Frame(simple_frame)
        pdf_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        pdf_frame.columnconfigure(0, weight=1)
        
        self.pdf_entry = ttk.Entry(pdf_frame, textvariable=self.simple_pdf_name, font=('TkDefaultFont', 10))
        self.pdf_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(pdf_frame, text=".pdf").grid(row=0, column=1)
        
        # Section nombre de pages
        ttk.Label(simple_frame, text="📊 Nombre maximum de pages:", 
                 font=('TkDefaultFont', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        pages_frame = ttk.Frame(simple_frame)
        pages_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        self.pages_spinbox = ttk.Spinbox(pages_frame, from_=1, to=500, width=10,
                                        textvariable=self.simple_max_pages, font=('TkDefaultFont', 10))
        self.pages_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(pages_frame, text="pages maximum").grid(row=0, column=1)
        
        # Section résumé
        self.create_simple_preview(simple_frame)
        
        # Bouton de traitement
        self.simple_process_btn = ttk.Button(
            simple_frame, 
            text="🚀 Lancer le traitement", 
            command=self.start_simple_processing,
            style='Accent.TButton'
        )
        self.simple_process_btn.grid(row=8, column=0, columnspan=2, pady=20)
    
    def create_simple_preview(self, parent):
        """Créer la section de prévisualisation pour le mode simple"""
        # Frame de prévisualisation
        preview_frame = ttk.LabelFrame(parent, text="📋 Résumé", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        preview_frame.columnconfigure(1, weight=1)
        
        # Labels de résumé
        ttk.Label(preview_frame, text="URL:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.preview_url = ttk.Label(preview_frame, text="(Aucune URL)", foreground='gray')
        self.preview_url.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(preview_frame, text="PDF:", font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=0, sticky=tk.W)
        self.preview_pdf = ttk.Label(preview_frame, text="(Aucun nom)", foreground='gray')
        self.preview_pdf.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(preview_frame, text="Pages:", font=('TkDefaultFont', 9, 'bold')).grid(row=2, column=0, sticky=tk.W)
        self.preview_pages = ttk.Label(preview_frame, text="100 pages max")
        self.preview_pages.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Lier les variables pour mise à jour automatique
        self.simple_url.trace('w', self.update_simple_preview)
        self.simple_pdf_name.trace('w', self.update_simple_preview)
        self.simple_max_pages.trace('w', self.update_simple_preview)
    
    def create_multi_tab(self):
        """Créer l'onglet pour le mode multi-documents"""
        # Frame de l'onglet
        multi_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(multi_frame, text="📚 Multi-documents")
        
        # Configuration du grid
        multi_frame.columnconfigure(0, weight=1)
        multi_frame.rowconfigure(1, weight=1)
        
        # Instructions
        instruction_label = ttk.Label(
            multi_frame, 
            text="Gérez plusieurs documents Scribd à traiter en lot:",
            font=('TkDefaultFont', 10, 'bold')
        )
        instruction_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Treeview pour la liste des documents
        self.create_documents_tree(multi_frame)
        
        # Boutons de gestion
        self.create_multi_buttons(multi_frame)
        
        # Bouton de traitement multi
        self.multi_process_btn = ttk.Button(
            multi_frame, 
            text="🚀 Traiter tous les documents", 
            command=self.start_multi_processing,
            style='Accent.TButton'
        )
        self.multi_process_btn.grid(row=3, column=0, pady=20)
    
    def create_documents_tree(self, parent):
        """Créer le Treeview pour les documents"""
        # Frame pour le treeview avec scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('url', 'pdf_name', 'max_pages', 'status')
        self.documents_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=8)
        
        # Configuration des colonnes
        self.documents_tree.heading('#0', text='#')
        self.documents_tree.heading('url', text='URL')
        self.documents_tree.heading('pdf_name', text='Nom PDF')
        self.documents_tree.heading('max_pages', text='Pages max')
        self.documents_tree.heading('status', text='Statut')
        
        # Largeur des colonnes
        self.documents_tree.column('#0', width=50, minwidth=30)
        self.documents_tree.column('url', width=250, minwidth=150)
        self.documents_tree.column('pdf_name', width=200, minwidth=150)
        self.documents_tree.column('max_pages', width=80, minwidth=60)
        self.documents_tree.column('status', width=100, minwidth=80)
        
        # Placement du treeview
        self.documents_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.documents_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.documents_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.documents_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.documents_tree.configure(xscrollcommand=h_scrollbar.set)
    
    def create_multi_buttons(self, parent):
        """Créer les boutons de gestion multi-documents"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, pady=10)
        
        # Boutons principaux
        ttk.Button(buttons_frame, text="➕ Ajouter", command=self.add_document).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="✏️ Modifier", command=self.edit_document).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Supprimer", command=self.remove_document).grid(row=0, column=2, padx=5)
        
        # Boutons d'ordre
        ttk.Button(buttons_frame, text="⬆️ Monter", command=self.move_document_up).grid(row=0, column=3, padx=5)
        ttk.Button(buttons_frame, text="⬇️ Descendre", command=self.move_document_down).grid(row=0, column=4, padx=5)
        
        # Bouton de nettoyage
        ttk.Button(buttons_frame, text="🧹 Vider", command=self.clear_documents).grid(row=0, column=5, padx=5)
    
    def create_logs_tab(self):
        """Créer l'onglet pour les logs et l'historique"""
        # Frame de l'onglet
        logs_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(logs_frame, text="📝 Logs & Historique")
        
        # Configuration du grid
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(1, weight=1)
        
        # Titre
        ttk.Label(
            logs_frame, 
            text="Suivi en temps réel et historique des traitements:",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Zone de logs avec scrolling
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            height=15, 
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.logs_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons de gestion des logs
        logs_buttons_frame = ttk.Frame(logs_frame)
        logs_buttons_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(logs_buttons_frame, text="🧹 Effacer", command=self.clear_logs).grid(row=0, column=0, padx=5)
        ttk.Button(logs_buttons_frame, text="💾 Sauvegarder", command=self.save_logs).grid(row=0, column=1, padx=5)
        ttk.Button(logs_buttons_frame, text="📁 Ouvrir dossier PDFs", command=self.open_pdfs_folder).grid(row=0, column=2, padx=5)
    
    def create_status_frame(self, parent):
        """Créer la barre de statut en bas"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Progress bars
        ttk.Label(status_frame, text="Progression globale:").grid(row=0, column=0, sticky=tk.W)
        self.global_progressbar = ttk.Progressbar(status_frame, variable=self.global_progress, length=200)
        self.global_progressbar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        self.global_status_label = ttk.Label(status_frame, textvariable=self.global_status_text)
        self.global_status_label.grid(row=0, column=2, sticky=tk.E)
        
        # Progress bar du document actuel
        ttk.Label(status_frame, text="Document actuel:").grid(row=1, column=0, sticky=tk.W)
        self.current_progressbar = ttk.Progressbar(status_frame, variable=self.current_progress, length=200)
        self.current_progressbar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text)
        self.status_label.grid(row=1, column=2, sticky=tk.E)
    
    # Méthodes d'événements et de callbacks
    def on_url_change(self, event=None):
        """Appelé quand l'URL change"""
        url = self.simple_url.get().strip()
        if url and 'scribd.com' in url:
            # Générer automatiquement le nom du PDF
            pdf_name = self.scribd_interface._generate_pdf_name_from_url(url)
            if pdf_name and pdf_name != "document_scribd.pdf":
                # Retirer l'extension .pdf pour l'affichage
                pdf_name = pdf_name.replace('.pdf', '')
                self.simple_pdf_name.set(pdf_name)
    
    def validate_url(self):
        """Valider l'URL saisie"""
        url = self.simple_url.get().strip()
        if not url:
            messagebox.showwarning("URL vide", "Veuillez saisir une URL")
            return
        
        if 'scribd.com' not in url:
            result = messagebox.askyesno(
                "URL non-Scribd", 
                "L'URL ne semble pas être un document Scribd.\nContinuer quand même ?"
            )
            if not result:
                return
        
        messagebox.showinfo("URL valide", "✅ URL validée avec succès")
        self.on_url_change()  # Mettre à jour le nom du PDF
    
    def update_simple_preview(self, *args):
        """Mettre à jour l'aperçu du mode simple"""
        url = self.simple_url.get().strip()
        pdf_name = self.simple_pdf_name.get().strip()
        max_pages = self.simple_max_pages.get()
        
        # URL
        if url:
            display_url = url[:50] + "..." if len(url) > 50 else url
            self.preview_url.config(text=display_url, foreground='black')
        else:
            self.preview_url.config(text="(Aucune URL)", foreground='gray')
        
        # PDF
        if pdf_name:
            self.preview_pdf.config(text=f"{pdf_name}.pdf", foreground='black')
        else:
            self.preview_pdf.config(text="(Aucun nom)", foreground='gray')
        
        # Pages
        self.preview_pages.config(text=f"{max_pages} pages max")
    
    def log_message(self, message: str, level: str = "INFO"):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"[{timestamp}] {level}: {message}\n"
        
        self.logs_text.insert(tk.END, colored_message)
        self.logs_text.see(tk.END)  # Scroll automatique vers le bas
        
        # Rafraîchir l'interface
        self.root.update_idletasks()
    
    # Méthodes de traitement
    def start_simple_processing(self):
        """Démarrer le traitement en mode simple"""
        if self.is_processing:
            messagebox.showwarning("Traitement en cours", "Un traitement est déjà en cours")
            return
        
        # Valider les champs
        url = self.simple_url.get().strip()
        pdf_name = self.simple_pdf_name.get().strip()
        
        if not url:
            messagebox.showwarning("URL manquante", "Veuillez saisir une URL")
            return
        
        if not pdf_name:
            messagebox.showwarning("Nom PDF manquant", "Veuillez saisir un nom pour le PDF")
            return
        
        # Créer le document
        document = {
            'url': url,
            'pdf_name': pdf_name + '.pdf' if not pdf_name.endswith('.pdf') else pdf_name,
            'max_pages': self.simple_max_pages.get()
        }
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirmer le traitement",
            f"Traiter le document :\n\n"
            f"URL: {url}\n"
            f"PDF: {document['pdf_name']}\n"
            f"Pages max: {document['max_pages']}\n\n"
            f"Le PDF sera sauvé dans le dossier PDFs/"
        )
        
        if result:
            self.start_processing([document])
    
    def start_multi_processing(self):
        """Démarrer le traitement en mode multi-documents"""
        if self.is_processing:
            messagebox.showwarning("Traitement en cours", "Un traitement est déjà en cours")
            return
        
        if not self.documents_list:
            messagebox.showwarning("Aucun document", "Ajoutez au moins un document à traiter")
            return
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirmer le traitement",
            f"Traiter {len(self.documents_list)} document(s) ?\n\n"
            f"Les PDFs seront sauvés dans le dossier PDFs/"
        )
        
        if result:
            self.start_processing(self.documents_list.copy())
    
    def start_processing(self, documents: List[Dict]):
        """Démarrer le traitement (threading)"""
        self.is_processing = True
        self.global_progress.set(0)
        self.current_progress.set(0)
        
        # Désactiver les boutons
        self.simple_process_btn.config(state='disabled')
        self.multi_process_btn.config(state='disabled')
        
        # Démarrer le thread de traitement
        self.processing_thread = threading.Thread(
            target=self.processing_worker,
            args=(documents,),
            daemon=True
        )
        self.processing_thread.start()
        
        self.log_message(f"🚀 Début du traitement de {len(documents)} document(s)")
    
    def processing_worker(self, documents: List[Dict]):
        """Worker thread pour le traitement"""
        try:
            # Simuler le traitement avec progress
            total_docs = len(documents)
            
            for i, doc in enumerate(documents):
                if not self.is_processing:  # Vérifier si annulé
                    break
                
                # Mettre à jour le statut global
                self.processing_queue.put(('global_status', f"Document {i+1}/{total_docs}: {doc['pdf_name']}"))
                self.processing_queue.put(('global_progress', (i / total_docs) * 100))
                
                # Simuler les étapes du traitement
                steps = ["Extraction des liens", "Tri des liens", "Création du PDF", "Finalisation"]
                
                for j, step in enumerate(steps):
                    if not self.is_processing:
                        break
                    
                    self.processing_queue.put(('current_status', f"{step}..."))
                    self.processing_queue.put(('current_progress', (j / len(steps)) * 100))
                    self.processing_queue.put(('log', f"📄 Document {i+1}: {step}"))
                    
                    # Simuler le temps de traitement
                    time.sleep(1)
                
                # Document terminé
                self.processing_queue.put(('current_progress', 100))
                self.processing_queue.put(('log', f"✅ Document {i+1} terminé: {doc['pdf_name']}"))
            
            # Traitement terminé
            self.processing_queue.put(('global_progress', 100))
            self.processing_queue.put(('global_status', f"Terminé: {total_docs} document(s) traités"))
            self.processing_queue.put(('log', f"🎉 Traitement terminé avec succès !"))
            self.processing_queue.put(('log', f"📁 PDFs disponibles dans le dossier PDFs/"))
            
        except Exception as e:
            self.processing_queue.put(('log', f"❌ Erreur: {str(e)}"))
        finally:
            self.processing_queue.put(('finished', None))
    
    def check_queue(self):
        """Vérifier la queue de communication avec le thread"""
        try:
            while True:
                message_type, data = self.processing_queue.get_nowait()
                
                if message_type == 'global_status':
                    self.global_status_text.set(data)
                elif message_type == 'global_progress':
                    self.global_progress.set(data)
                elif message_type == 'current_status':
                    self.status_text.set(data)
                elif message_type == 'current_progress':
                    self.current_progress.set(data)
                elif message_type == 'log':
                    self.log_message(data)
                elif message_type == 'finished':
                    self.processing_finished()
                
        except queue.Empty:
            pass
        
        # Programmer la prochaine vérification
        self.root.after(100, self.check_queue)
    
    def processing_finished(self):
        """Appelé quand le traitement est terminé"""
        self.is_processing = False
        
        # Réactiver les boutons
        self.simple_process_btn.config(state='normal')
        self.multi_process_btn.config(state='normal')
        
        # Reset des progress bars après quelques secondes
        self.root.after(3000, self.reset_progress_bars)
        
        messagebox.showinfo("Traitement terminé", "Le traitement s'est terminé avec succès !")
    
    def reset_progress_bars(self):
        """Remettre à zéro les barres de progression"""
        self.global_progress.set(0)
        self.current_progress.set(0)
        self.global_status_text.set("Aucun traitement en cours")
        self.status_text.set("Prêt")
    
    # Méthodes de gestion des documents (multi-documents)
    def add_document(self):
        """Ajouter un document à la liste"""
        self.open_document_dialog()
    
    def edit_document(self):
        """Modifier le document sélectionné"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un document à modifier")
            return
        
        # Récupérer l'index du document
        item = selection[0]
        index = int(self.documents_tree.item(item, 'text')) - 1
        
        if 0 <= index < len(self.documents_list):
            self.open_document_dialog(self.documents_list[index], index)
    
    def remove_document(self):
        """Supprimer le document sélectionné"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un document à supprimer")
            return
        
        result = messagebox.askyesno("Confirmer", "Supprimer le document sélectionné ?")
        if result:
            item = selection[0]
            index = int(self.documents_tree.item(item, 'text')) - 1
            
            if 0 <= index < len(self.documents_list):
                del self.documents_list[index]
                self.refresh_documents_tree()
    
    def move_document_up(self):
        """Monter le document sélectionné"""
        selection = self.documents_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.documents_tree.item(item, 'text')) - 1
        
        if index > 0:
            # Échanger avec le précédent
            self.documents_list[index], self.documents_list[index-1] = \
                self.documents_list[index-1], self.documents_list[index]
            self.refresh_documents_tree()
            
            # Resélectionner l'item
            new_item = self.documents_tree.get_children()[index-1]
            self.documents_tree.selection_set(new_item)
    
    def move_document_down(self):
        """Descendre le document sélectionné"""
        selection = self.documents_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.documents_tree.item(item, 'text')) - 1
        
        if index < len(self.documents_list) - 1:
            # Échanger avec le suivant
            self.documents_list[index], self.documents_list[index+1] = \
                self.documents_list[index+1], self.documents_list[index]
            self.refresh_documents_tree()
            
            # Resélectionner l'item
            new_item = self.documents_tree.get_children()[index+1]
            self.documents_tree.selection_set(new_item)
    
    def clear_documents(self):
        """Vider la liste des documents"""
        if self.documents_list:
            result = messagebox.askyesno("Confirmer", "Vider toute la liste des documents ?")
            if result:
                self.documents_list.clear()
                self.refresh_documents_tree()
    
    def open_document_dialog(self, document: Optional[Dict] = None, index: Optional[int] = None):
        """Ouvrir la fenêtre de dialogue pour ajouter/modifier un document"""
        dialog = DocumentDialog(self.root, document)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if index is not None:
                # Modification
                self.documents_list[index] = dialog.result
            else:
                # Ajout
                self.documents_list.append(dialog.result)
            
            self.refresh_documents_tree()
    
    def refresh_documents_tree(self):
        """Rafraîchir l'affichage du Treeview"""
        # Vider le treeview
        for item in self.documents_tree.get_children():
            self.documents_tree.delete(item)
        
        # Ajouter les documents
        for i, doc in enumerate(self.documents_list):
            url_display = doc['url'][:40] + "..." if len(doc['url']) > 40 else doc['url']
            
            self.documents_tree.insert('', 'end', 
                text=str(i+1),
                values=(url_display, doc['pdf_name'], doc['max_pages'], 'En attente')
            )
    
    # Méthodes utilitaires
    def clear_logs(self):
        """Effacer les logs"""
        self.logs_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Sauvegarder les logs"""
        content = self.logs_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Logs vides", "Aucun log à sauvegarder")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder les logs",
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Succès", f"Logs sauvegardés dans {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder : {e}")
    
    def open_pdfs_folder(self):
        """Ouvrir le dossier PDFs"""
        pdfs_path = os.path.join(os.getcwd(), "PDFs")
        
        try:
            if os.path.exists(pdfs_path):
                if os.name == 'nt':  # Windows
                    os.startfile(pdfs_path)
                elif os.name == 'posix':  # macOS/Linux
                    os.system(f'open "{pdfs_path}"')
            else:
                messagebox.showinfo("Dossier PDFs", "Le dossier PDFs n'existe pas encore")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier : {e}")
    
    def clear_history(self):
        """Effacer l'historique"""
        result = messagebox.askyesno("Confirmer", "Effacer tout l'historique et les logs ?")
        if result:
            self.clear_logs()
            messagebox.showinfo("Succès", "Historique effacé")
    
    def launch_cli(self):
        """Lancer l'interface en ligne de commande"""
        messagebox.showinfo("Interface CLI", 
                           "Pour lancer l'interface en ligne de commande :\n\n"
                           "python3 scribd_interface.py")
    
    def show_help(self):
        """Afficher l'aide"""
        help_text = """
🚀 Guide d'utilisation de l'interface Scribd

📄 MODE SIMPLE :
1. Saisissez l'URL du document Scribd
2. Choisissez un nom pour le PDF
3. Définissez le nombre max de pages
4. Lancez le traitement

📚 MODE MULTI-DOCUMENTS :
1. Ajoutez plusieurs documents avec le bouton ➕
2. Gérez la liste (modifier, supprimer, réorganiser)
3. Lancez le traitement en lot

📁 ORGANISATION :
- Tous les PDFs sont sauvés dans le dossier PDFs/
- L'historique est affiché dans l'onglet Logs
- Utilisez le menu Fichier pour ouvrir le dossier de sortie

💡 CONSEILS :
- Les URLs Scribd sont automatiquement détectées
- Les noms de PDF sont générés automatiquement depuis l'URL
- Le traitement peut prendre plusieurs minutes selon la taille
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Guide d'utilisation")
        help_window.geometry("500x400")
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('TkDefaultFont', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state='disabled')
    
    def show_about(self):
        """Afficher les informations sur l'application"""
        messagebox.showinfo("À propos", 
                           "🚀 Scribd Scraper - Interface Graphique\n\n"
                           "Version: 2.0 GUI\n"
                           "Interface graphique moderne pour extraire et\n"
                           "convertir des documents Scribd en PDF.\n\n"
                           "Fonctionnalités:\n"
                           "• Mode simple et multi-documents\n"
                           "• Organisation automatique dans PDFs/\n"
                           "• Suivi en temps réel\n"
                           "• Interface intuitive\n\n"
                           "Développé avec Python + Tkinter")
    
    def on_closing(self):
        """Gérer la fermeture de l'application"""
        if self.is_processing:
            result = messagebox.askyesno("Traitement en cours", 
                                       "Un traitement est en cours. Quitter quand même ?")
            if not result:
                return
            
            self.is_processing = False
        
        self.root.destroy()
    
    def run(self):
        """Démarrer l'interface graphique"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.log_message("🚀 Interface graphique Scribd prête")
        self.root.mainloop()


class DocumentDialog:
    """Fenêtre de dialogue pour ajouter/modifier un document"""
    
    def __init__(self, parent, document: Optional[Dict] = None):
        self.result = None
        
        # Créer la fenêtre modale
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📄 Configuration du document")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Variables
        self.url_var = tk.StringVar()
        self.pdf_name_var = tk.StringVar()
        self.max_pages_var = tk.IntVar(value=100)
        
        # Remplir avec les données existantes si modification
        if document:
            self.url_var.set(document['url'])
            pdf_name = document['pdf_name']
            if pdf_name.endswith('.pdf'):
                pdf_name = pdf_name[:-4]  # Retirer .pdf
            self.pdf_name_var.set(pdf_name)
            self.max_pages_var.set(document['max_pages'])
        
        self.create_widgets()
    
    def create_widgets(self):
        """Créer les widgets de la fenêtre"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL
        ttk.Label(main_frame, text="🌐 URL du document Scribd:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('TkDefaultFont', 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        
        ttk.Button(url_frame, text="Valider", command=self.validate_url).pack(side=tk.RIGHT)
        
        # Nom PDF
        ttk.Label(main_frame, text="📄 Nom du PDF de sortie:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        pdf_frame = ttk.Frame(main_frame)
        pdf_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_name_var, font=('TkDefaultFont', 10))
        self.pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(pdf_frame, text=".pdf").pack(side=tk.RIGHT)
        
        # Pages max
        ttk.Label(main_frame, text="📊 Nombre maximum de pages:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        pages_frame = ttk.Frame(main_frame)
        pages_frame.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Spinbox(pages_frame, from_=1, to=500, width=10,
                   textvariable=self.max_pages_var, font=('TkDefaultFont', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(pages_frame, text="pages maximum").pack(side=tk.LEFT)
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(buttons_frame, text="Annuler", command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="OK", command=self.ok, style='Accent.TButton').pack(side=tk.RIGHT)
    
    def on_url_change(self, event=None):
        """Générer automatiquement le nom du PDF depuis l'URL"""
        url = self.url_var.get().strip()
        if url and 'scribd.com' in url and not self.pdf_name_var.get().strip():
            # Utiliser la même logique que l'interface principale
            from scribd_interface import ScribdInterface
            scribd = ScribdInterface()
            pdf_name = scribd._generate_pdf_name_from_url(url)
            if pdf_name and pdf_name != "document_scribd.pdf":
                pdf_name = pdf_name.replace('.pdf', '')
                self.pdf_name_var.set(pdf_name)
    
    def validate_url(self):
        """Valider l'URL"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL vide", "Veuillez saisir une URL")
            return
        
        if 'scribd.com' not in url:
            result = messagebox.askyesno("URL non-Scribd", 
                                       "L'URL ne semble pas être un document Scribd.\nContinuer quand même ?")
            if not result:
                return
        
        messagebox.showinfo("URL valide", "✅ URL validée avec succès")
        self.on_url_change()
    
    def ok(self):
        """Valider et fermer"""
        url = self.url_var.get().strip()
        pdf_name = self.pdf_name_var.get().strip()
        
        if not url:
            messagebox.showwarning("URL manquante", "Veuillez saisir une URL")
            return
        
        if not pdf_name:
            messagebox.showwarning("Nom PDF manquant", "Veuillez saisir un nom pour le PDF")
            return
        
        # Créer le résultat
        self.result = {
            'url': url,
            'pdf_name': pdf_name + '.pdf' if not pdf_name.endswith('.pdf') else pdf_name,
            'max_pages': self.max_pages_var.get()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Annuler et fermer"""
        self.dialog.destroy()


def main():
    """Fonction principale pour l'interface graphique"""
    try:
        app = ScribdGUI()
        app.run()
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'interface graphique : {e}")
        print("💡 Essayez de lancer l'interface en ligne de commande avec : python3 scribd_interface.py")


if __name__ == "__main__":
    main()