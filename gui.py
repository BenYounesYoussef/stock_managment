import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QComboBox, QHeaderView, QGroupBox, QFormLayout, QProgressBar, QCheckBox, QSplitter, QScrollArea, QFrame, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPainterPath
from manager import StockManager

class WelcomeTab(QWidget):
    def __init__(self, manager, status_bar, refresh_callback=None):
        super().__init__()
        self.manager = manager
        self.status_bar = status_bar
        self.refresh_callback = refresh_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(layout)

        # Title
        title = QLabel("Bienvenue dans Stock Manager")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00d4ff; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description / Objective
        desc_box = QGroupBox("Objectif & Flux des Opérations")
        desc_box.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; color: #e0e0e0; border: 1px solid #404040; border-radius: 8px; margin-top: 20px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        desc_layout = QVBoxLayout()
        
        info_text = """
        <b>Objectif:</b>
        Cette application permet de gérer efficacement le stock de produits et les commandes clients.
        
        <b>Flux des Opérations:</b>
        1. <b>Gestion des Produits:</b> Ajoutez, modifiez ou archivez vos produits.
        2. <b>Gestion des Commandes:</b> Créez des paniers, validez des commandes et générez des factures.
        3. <b>Suivi & Statistiques:</b> Visualisez vos revenus et l'état des stocks en temps réel.
        4. <b>Base de Données:</b> Synchronisez vos données locales (JSON) avec une base de données MySQL.
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 14px; color: #cccccc; line-height: 1.4;")
        desc_layout.addWidget(info_label)
        desc_box.setLayout(desc_layout)
        layout.addWidget(desc_box)

        # Database Integration Section
        db_group = QGroupBox("Intégration Base de Données (MySQL)")
        db_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; color: #00d4ff; border: 1px solid #00d4ff; border-radius: 8px; margin-top: 20px; }")
        db_layout = QVBoxLayout()
        db_layout.setSpacing(15)

        # Connection Form
        form_layout = QFormLayout()
        self.db_host = QLineEdit("localhost")
        self.db_user = QLineEdit("root")
        self.db_pass = QLineEdit("")
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name = QLineEdit("stock_db")
        
        # Styling inputs
        for w in [self.db_host, self.db_user, self.db_pass, self.db_name]:
            w.setStyleSheet("padding: 8px; border-radius: 4px; background-color: #2b2b2b; color: white; border: 1px solid #555;")

        form_layout.addRow("Hôte:", self.db_host)
        form_layout.addRow("Utilisateur:", self.db_user)
        form_layout.addRow("Mot de passe:", self.db_pass)
        form_layout.addRow("Nom de la BDD:", self.db_name)
        
        db_layout.addLayout(form_layout)
        
        # Auto-Sync Checkbox
        self.chk_auto_sync = QCheckBox("Auto-Sync (JSON -> DB)")
        self.chk_auto_sync.setStyleSheet("color: #00d4ff; font-weight: bold; margin-left: 5px;")
        self.chk_auto_sync.stateChanged.connect(self.toggle_auto_sync)
        db_layout.addWidget(self.chk_auto_sync)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("1. Connexion / Setup Auto")
        self.btn_connect.clicked.connect(self.connect_and_setup)
        
        self.btn_export = QPushButton("2. Exporter JSON -> DB")
        self.btn_export.clicked.connect(self.export_to_db)
        self.btn_export.setEnabled(False)

        self.btn_import = QPushButton("3. Importer DB -> JSON")
        self.btn_import.clicked.connect(self.import_from_db)
        self.btn_import.setEnabled(False)
        
        self.btn_sync = QPushButton("4. Sync / Merge Data")
        self.btn_sync.clicked.connect(self.sync_data)
        self.btn_sync.setEnabled(False)

        # Button Styles
        for btn in [self.btn_connect, self.btn_export, self.btn_import, self.btn_sync]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border: 1px solid #00d4ff;
                    color: #00d4ff;
                }
                QPushButton:disabled {
                    color: #555;
                    border-color: #333;
                }
            """)
        
        # Highlight Connect button
        self.btn_connect.setStyleSheet(self.btn_connect.styleSheet().replace("border: 1px solid #555;", "border: 1px solid #00d4ff;"))

        btn_layout.addWidget(self.btn_connect)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_sync)
        
        db_layout.addLayout(btn_layout)
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        layout.addStretch()

    def connect_and_setup(self):
        host = self.db_host.text()
        user = self.db_user.text()
        pwd = self.db_pass.text()
        db_name = self.db_name.text()
        
        success, msg = self.manager.connect_db(host, user, pwd, db_name)
        if success:
            # Setup tables
            s2, m2 = self.manager.setup_database()
            if s2:
                QMessageBox.information(self, "Succès", f"Connecté et BDD configurée!\n{m2}")
                self.btn_export.setEnabled(True)
                self.btn_import.setEnabled(True)
                self.btn_sync.setEnabled(True)
                self.status_bar.showMessage(f"Connecté à la BDD: {db_name}")
            else:
                QMessageBox.warning(self, "Attention", f"Connecté mais erreur setup: {m2}")
        else:
            QMessageBox.critical(self, "Erreur Connexion", msg)

    def export_to_db(self):
        success, msg = self.manager.export_json_to_db()
        if success:
            QMessageBox.information(self, "Succès", msg)
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def toggle_auto_sync(self):
        self.manager.auto_sync = self.chk_auto_sync.isChecked()
        state = "activée" if self.manager.auto_sync else "désactivée"
        self.status_bar.showMessage(f"Synchro Auto {state}")

    def sync_data(self):
        success, msg = self.manager.sync_data()
        if success:
            QMessageBox.information(self, "Succès", msg)
            if self.refresh_callback:
                self.refresh_callback()
        else:
            QMessageBox.warning(self, "Erreur", msg)

    def import_from_db(self):
        reply = QMessageBox.question(self, "Confirmation", 
                                     "Cela va écraser vos données locales actuelles avec celles de la base de données. Continuer?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.manager.import_db_to_json()
            if success:
                QMessageBox.information(self, "Succès", msg)
                if self.refresh_callback:
                    self.refresh_callback()
                    self.status_bar.showMessage("Données rechargées avec succès.", 3000)
            else:
                QMessageBox.warning(self, "Erreur", msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de Stock")
        self.setGeometry(100, 100, 1000, 700)
        
        # --- STYLESHEET ---
        # Get absolute path for arrow icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arrow_path = os.path.join(script_dir, "arrow_down_hover.svg").replace("\\", "/")
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #2b2b2b;
            }}
            QWidget {{
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            QTabWidget::pane {{
                border: 1px solid #3d3d3d;
                background: #323232;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: #3d3d3d;
                color: #b0b0b0;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: #323232;
                color: #00d4ff; /* Bright Cyan accent */
                border-bottom: 2px solid #00d4ff;
            }}
            QGroupBox {{
                border: 1px solid #4d4d4d;
                margin-top: 1.5em;
                border-radius: 6px;
                font-weight: bold;
                color: #00d4ff;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QLineEdit {{
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid #00d4ff;
            }}
            /* Futuristic Glassmorphism Button Style */
            QPushButton {{
                background-color: rgba(60, 60, 70, 0.6);
                color: rgba(200, 210, 220, 0.95);
                border: 1px solid rgba(100, 120, 140, 0.3);
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(80, 100, 120, 0.5);
                color: rgba(220, 235, 255, 1);
                border: 1px solid rgba(100, 180, 255, 0.5);
            }}
            QPushButton:pressed {{
                background-color: rgba(50, 60, 70, 0.7);
                color: rgba(180, 200, 220, 0.9);
            }}
            QPushButton:disabled {{
                background-color: rgba(40, 40, 45, 0.4);
                color: rgba(120, 120, 130, 0.6);
                border: 1px solid rgba(60, 60, 70, 0.3);
            }}
            
            /* Primary/Action Button - Soft Cyan Glow */
            QPushButton#primaryBtn {{
                background-color: rgba(0, 100, 140, 0.45);
                color: rgba(180, 230, 255, 0.95);
                border: 1px solid rgba(0, 180, 220, 0.4);
                padding: 10px 20px;
            }}
            QPushButton#primaryBtn:hover {{
                background-color: rgba(0, 140, 180, 0.55);
                color: rgba(220, 250, 255, 1);
                border: 1px solid rgba(0, 210, 255, 0.6);
            }}
            QPushButton#primaryBtn:pressed {{
                background-color: rgba(0, 80, 110, 0.6);
            }}

            /* Delete Button - Subtle Warm Red */
            QPushButton#deleteBtn {{
                background-color: rgba(140, 50, 50, 0.45);
                color: rgba(255, 200, 200, 0.95);
                border: 1px solid rgba(180, 80, 80, 0.4);
            }}
            QPushButton#deleteBtn:hover {{
                background-color: rgba(170, 60, 60, 0.55);
                color: rgba(255, 230, 230, 1);
                border: 1px solid rgba(220, 100, 100, 0.6);
            }}
            
            /* Clear/Secondary Button - Neutral */
            QPushButton#clearBtn {{
                background-color: rgba(70, 70, 80, 0.5);
                color: rgba(180, 180, 190, 0.9);
                border: 1px solid rgba(90, 90, 100, 0.35);
            }}
            QPushButton#clearBtn:hover {{
                background-color: rgba(90, 90, 100, 0.55);
                color: rgba(210, 210, 220, 1);
                border: 1px solid rgba(120, 130, 150, 0.5);
            }}
            QTableWidget {{
                background-color: #323232;
                gridline-color: #4d4d4d;
                border: none;
            }}
            QHeaderView::section {{
                background-color: #3d3d3d;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #e0e0e0;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: #00d4ff;
                color: #000000;
            }}
            QComboBox {{
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                padding-right: 25px; /* Space for the arrow */
                color: white;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border: none;
                background: transparent;
                image: none; /* Ensure no default image */
            }}
            QComboBox::down-arrow {{
                image: url({arrow_path}); /* Blue arrow by default */
                width: 14px;
                height: 14px;
                background: none;
                border: none; /* No CSS triangle borders */
            }}

            QComboBox QAbstractItemView {{
                background-color: #3d3d3d;
                color: white;
                selection-background-color: #00d4ff;
                selection-color: black;
                border: 1px solid #555;
                outline: none;
            }}
            
            /* Nav Menu Hover Effects */
            QTabBar::tab:hover {{
                background: #4d4d4d;
                color: white;
            }}
            QHeaderView {{
                background-color: #3d3d3d;
            }}
            QTableCornerButton::section {{
                background-color: #3d3d3d;
                border: none;
            }}
            QScrollArea {{
                background-color: #2b2b2b;
                border: none;
            }}
            QLabel {{
                color: #e0e0e0;
                background-color: transparent;
            }}
            QSplitter::handle {{
                background-color: #4d4d4d;
            }}
        """)

        self.manager = StockManager()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Status Bar for feedback
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Prêt")
        
        self.welcome_tab = WelcomeTab(self.manager, self.status_bar, self.refresh_app_data)
        self.product_tab = ProductTab(self.manager, self.status_bar)
        self.order_tab = OrderTab(self.manager, self.status_bar)
        self.stats_tab = StatsTab(self.manager)
        
        self.tabs.addTab(self.welcome_tab, "Accueil")
        self.tabs.addTab(self.product_tab, "Produits")
        self.tabs.addTab(self.order_tab, "Commandes")
        self.tabs.addTab(self.stats_tab, "Statistiques")
        
        # Refresh other tabs when changed
        self.tabs.currentChanged.connect(self.on_tab_change)

    def refresh_app_data(self):
        """Reloads data in all tabs."""
        self.product_tab.load_products()
        self.order_tab.refresh_products() # Refresh combo box
        self.order_tab.load_orders()
        self.stats_tab.load_stats()
        self.status_bar.showMessage("Application rechargée.", 3000)

    def on_tab_change(self, index):
        if index == 1: # Order Tab
            self.order_tab.refresh_products()
            self.order_tab.load_orders()
        elif index == 2: # Stats Tab
            self.stats_tab.load_stats()
        elif index == 0: # Product Tab
            self.product_tab.load_products()

class ProductTab(QWidget):
    def __init__(self, manager, status_bar):
        super().__init__()
        self.manager = manager
        self.status_bar = status_bar
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # --- Form ---
        self.form_group = QGroupBox("Détails du Produit")
        self.form_layout = QFormLayout()
        
        self.input_nom = QLineEdit()
        self.input_desc = QLineEdit()
        self.input_qty = QLineEdit()
        self.input_price = QLineEdit()
        
        self.form_layout.addRow("Nom:", self.input_nom)
        self.form_layout.addRow("Description:", self.input_desc)
        self.form_layout.addRow("Quantité:", self.input_qty)
        self.form_layout.addRow("Prix:", self.input_price)
        
        self.btn_add = QPushButton("Ajouter")
        self.btn_add.setObjectName("primaryBtn")
        self.btn_add.clicked.connect(self.add_product)
        self.btn_update = QPushButton("Modifier")
        self.btn_update.clicked.connect(self.update_product)
        self.btn_delete = QPushButton("Archiver")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.clicked.connect(self.toggle_archive_selected)
        self.btn_clear = QPushButton("Archiver tous")
        self.btn_clear.setObjectName("clearBtn")
        self.btn_clear.clicked.connect(self.toggle_archive_all)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        
        self.form_layout.addRow(btn_layout)
        self.form_group.setLayout(self.form_layout)
        self.layout.addWidget(self.form_group)
        
        self.chk_show_archived = QCheckBox("Afficher les archives")
        self.chk_show_archived.stateChanged.connect(self.on_archive_mode_changed)
        self.layout.addWidget(self.chk_show_archived)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Description", "Quantité", "Prix"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.fill_form_from_selection)
        self.layout.addWidget(self.table)
        
        self.load_products()

    def on_archive_mode_changed(self):
        """Toggle button text and load appropriate products based on archive mode."""
        is_archive_mode = self.chk_show_archived.isChecked()
        
        if is_archive_mode:
            self.btn_delete.setText("Désarchiver")
            self.btn_clear.setText("Désarchiver tous")
            # Disable add/update in archive view
            self.btn_add.setEnabled(False)
            self.btn_update.setEnabled(False)
        else:
            self.btn_delete.setText("Archiver")
            self.btn_clear.setText("Archiver tous")
            self.btn_add.setEnabled(True)
            self.btn_update.setEnabled(True)
        
        self.load_products()
        self.clear_form_inputs()

    def load_products(self):
        self.table.setRowCount(0)
        
        if self.chk_show_archived.isChecked():
            products = self.manager.get_archived_products()
        else:
            products = self.manager.get_all_products_sorted()
            
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.code_prod)))
            self.table.setItem(row, 1, QTableWidgetItem(p.nom_prod))
            self.table.setItem(row, 2, QTableWidgetItem(p.description))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.quantite)))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.prix_unit)))
            
            if hasattr(p, 'status') and p.status.value == "ARCHIVED":
                 for i in range(5):
                     self.table.item(row, i).setForeground(Qt.GlobalColor.gray)

    def clear_form_inputs(self):
        """Clear form fields and table selection."""
        self.input_nom.clear()
        self.input_desc.clear()
        self.input_qty.clear()
        self.input_price.clear()
        self.table.clearSelection()

    def fill_form_from_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self.input_nom.setText(self.table.item(row, 1).text())
            self.input_desc.setText(self.table.item(row, 2).text())
            self.input_qty.setText(self.table.item(row, 3).text())
            self.input_price.setText(self.table.item(row, 4).text())

    def add_product(self):
        try:
            nom = self.input_nom.text()
            desc = self.input_desc.text()
            qty = int(self.input_qty.text())
            price = float(self.input_price.text())
            
            if not nom:
                QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
                return

            res = self.manager.add_product(nom, desc, qty, price)
            if isinstance(res, str):
                 QMessageBox.warning(self, "Erreur", res)
            else:
                 self.load_products()
                 self.clear_form_inputs()
                 self.status_bar.showMessage(f"Produit '{nom}' ajouté avec succès.", 3000)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Quantité et Prix doivent être des nombres.")

    def update_product(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return
            
        try:
            code = int(self.table.item(row, 0).text())
            
            # Check if product is archived
            product = self.manager.get_product(code)
            if product and hasattr(product, 'status') and product.status.value == "ARCHIVED":
                QMessageBox.warning(self, "Erreur", "Impossible de modifier un produit archivé.")
                return
            
            nom = self.input_nom.text()
            desc = self.input_desc.text()
            qty = int(self.input_qty.text())
            price = float(self.input_price.text())
            
            res = self.manager.update_product(code, nom, desc, qty, price)
            if res is True:
                self.load_products()
                self.clear_form_inputs()
                self.status_bar.showMessage(f"Produit '{nom}' modifié.", 3000)
            elif isinstance(res, str):
                QMessageBox.warning(self, "Erreur", res)
            else:
                QMessageBox.warning(self, "Erreur", "Produit introuvable.")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Vérifiez les données saisies.")

    def toggle_archive_selected(self):
        """Archive or unarchive a single selected product based on current mode."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return
            
        code = int(self.table.item(row, 0).text())
        is_archive_mode = self.chk_show_archived.isChecked()
        
        if is_archive_mode:
            # Unarchive mode
            confirm = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment désarchiver ce produit ?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                if self.manager.unarchive_product(code):
                    self.load_products()
                    self.clear_form_inputs()
                    self.status_bar.showMessage("Produit désarchivé.", 3000)
        else:
            # Archive mode
            confirm = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment archiver ce produit ?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                if self.manager.delete_product(code):
                    self.load_products()
                    self.clear_form_inputs()
                    self.status_bar.showMessage("Produit archivé.", 3000)

    def toggle_archive_all(self):
        """Archive or unarchive all visible products based on current mode."""
        is_archive_mode = self.chk_show_archived.isChecked()
        
        if is_archive_mode:
            # Unarchive all archived products
            products = self.manager.get_archived_products()
            if not products:
                QMessageBox.information(self, "Info", "Aucun produit archivé.")
                return
            confirm = QMessageBox.question(self, "Confirmation", 
                                         f"Voulez-vous vraiment désarchiver {len(products)} produits ?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                count = 0
                for p in products:
                    if self.manager.unarchive_product(p.code_prod):
                        count += 1
                self.load_products()
                self.clear_form_inputs()
                self.status_bar.showMessage(f"{count} produits désarchivés.", 3000)
        else:
            # Archive all active products
            products = self.manager.get_all_products_sorted()
            if not products:
                QMessageBox.information(self, "Info", "Aucun produit actif.")
                return
            confirm = QMessageBox.question(self, "Confirmation", 
                                         f"Voulez-vous vraiment archiver {len(products)} produits ?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                count = 0
                for p in products:
                    if self.manager.delete_product(p.code_prod):
                        count += 1
                self.load_products()
                self.clear_form_inputs()
                self.status_bar.showMessage(f"{count} produits archivés.", 3000)

class OrderTab(QWidget):
    def __init__(self, manager, status_bar):
        super().__init__()
        self.manager = manager
        self.status_bar = status_bar
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Top Controls
        top_layout = QHBoxLayout()
        self.btn_create = QPushButton("Nouvelle Commande (Brouillon)")
        self.btn_create.setObjectName("primaryBtn")
        self.btn_create.clicked.connect(self.create_draft)
        self.chk_archived = QCheckBox("Voir les archives")
        self.chk_archived.stateChanged.connect(self.load_orders)
        
        top_layout.addWidget(self.btn_create)
        top_layout.addWidget(self.chk_archived)
        top_layout.addStretch()
        self.layout.addLayout(top_layout)

        # Splitter for Left/Right panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        # --- LEFT: List ---
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet("background-color: #2b2b2b;")
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)

        self.table_orders = QTableWidget()
        self.table_orders.setColumnCount(6)
        self.table_orders.setHorizontalHeaderLabels(["ID", "Status", "Paiement", "Livraison", "Total", "Date"])
        self.table_orders.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_orders.itemSelectionChanged.connect(self.on_order_selected)
        self.left_layout.addWidget(self.table_orders)

        self.btn_archive = QPushButton("Archiver / Supprimer")
        self.btn_archive.clicked.connect(self.archive_order)
        self.btn_archive.setStyleSheet("background-color: #d32f2f;")
        self.left_layout.addWidget(self.btn_archive)
        
        self.btn_unarchive = QPushButton("Désarchiver")
        self.btn_unarchive.clicked.connect(self.unarchive_order)
        self.btn_unarchive.setStyleSheet("background-color: #28a745;")
        self.btn_unarchive.setVisible(False)  # Hidden by default
        self.left_layout.addWidget(self.btn_unarchive)
        
        self.splitter.addWidget(self.left_widget)

        # --- RIGHT: Details (Scrollable) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("background-color: #2b2b2b;")
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        self.lbl_order_info = QLabel("Sélectionnez une commande")
        self.lbl_order_info.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        self.right_layout.addWidget(self.lbl_order_info)

        # Lines Table
        self.table_lines = QTableWidget()
        self.table_lines.setMinimumHeight(150)
        self.table_lines.setColumnCount(4)
        self.table_lines.setHorizontalHeaderLabels(["Produit", "Qté", "Prix Unit.", "Total Ligne"])
        self.table_lines.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.right_layout.addWidget(self.table_lines)

        # Add Product Form (Only visible for Draft)
        self.group_add_line = QGroupBox("Ajouter un produit")
        self.form_add_line = QFormLayout()
        self.combo_prod = QComboBox()
        self.input_qty = QLineEdit()
        self.btn_add_line = QPushButton("Ajouter")
        self.btn_add_line.setObjectName("primaryBtn")
        self.btn_add_line.clicked.connect(self.add_line)
        
        self.form_add_line.addRow("Produit:", self.combo_prod)
        self.form_add_line.addRow("Qté:", self.input_qty)
        self.form_add_line.addRow(self.btn_add_line)
        self.group_add_line.setLayout(self.form_add_line)
        self.right_layout.addWidget(self.group_add_line)

        # Actions
        self.group_actions = QGroupBox("Actions")
        self.layout_actions = QVBoxLayout()
        self.btn_confirm = QPushButton("Confirmer Commande")
        self.btn_confirm.setObjectName("primaryBtn")
        self.btn_confirm.clicked.connect(self.confirm_order)
        self.btn_pay = QPushButton("Payer Commande")
        self.btn_pay.setObjectName("primaryBtn")
        self.btn_pay.clicked.connect(self.pay_order)
        self.btn_deliver = QPushButton("Livrer Commande")
        self.btn_deliver.setObjectName("primaryBtn")
        self.btn_deliver.clicked.connect(self.deliver_order)
        self.btn_cancel = QPushButton("Annuler Commande")
        self.btn_cancel.setObjectName("primaryBtn")
        self.btn_cancel.clicked.connect(self.cancel_order)
        
        self.layout_actions.addWidget(self.btn_confirm)
        self.layout_actions.addWidget(self.btn_pay)
        self.layout_actions.addWidget(self.btn_deliver)
        self.layout_actions.addWidget(self.btn_cancel)
        self.group_actions.setLayout(self.layout_actions)
        self.right_layout.addWidget(self.group_actions)
        
        self.right_layout.addStretch() # Push everything up

        self.scroll_area.setWidget(self.right_widget)
        self.splitter.addWidget(self.scroll_area)
        self.splitter.setSizes([600, 400]) # Initial sizes

        self.load_orders()
        self.refresh_products()

    def refresh_products(self):
        self.combo_prod.clear()
        # active products only usually, maybe we allow active only for new lines
        products = self.manager.get_all_products_sorted()
        for p in products:
            self.combo_prod.addItem(f"{p.nom_prod} (Stock: {p.quantite}) - {p.prix_unit}€", p.code_prod)

    def load_orders(self):
        self.table_orders.setRowCount(0)
        
        if self.chk_archived.isChecked():
            orders_arch = self.manager.get_archived_orders()
            orders_active = self.manager.get_active_orders()
            orders = orders_active + orders_arch
        else:
            orders = self.manager.get_active_orders()
            
        orders.sort(key=lambda x: x.code_cmd, reverse=True)
        
        for o in orders:
            row = self.table_orders.rowCount()
            self.table_orders.insertRow(row)
            self.table_orders.setItem(row, 0, QTableWidgetItem(str(o.code_cmd)))
            self.table_orders.setItem(row, 1, QTableWidgetItem(o.status.value))
            self.table_orders.setItem(row, 2, QTableWidgetItem(o.payment_status.value))
            self.table_orders.setItem(row, 3, QTableWidgetItem(o.delivery_status.value))
            self.table_orders.setItem(row, 4, QTableWidgetItem(f"{o.total_amount:.2f} €"))
            self.table_orders.setItem(row, 5, QTableWidgetItem(o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else ""))
            
            if o.status.value == "ARCHIVED" or o.status.value == "CANCELLED":
                 for i in range(6):
                     self.table_orders.item(row, i).setForeground(Qt.GlobalColor.gray)

    def on_order_selected(self):
        row = self.table_orders.currentRow()
        if row < 0:
            self.right_widget.setEnabled(False)
            return
        
        self.right_widget.setEnabled(True)
        code_cmd = int(self.table_orders.item(row, 0).text())
        order = self.manager.get_order(code_cmd)
        if not order: return

        self.selected_order = order
        self.lbl_order_info.setText(f"Commande #{order.code_cmd} - {order.status.value}")
        
        # Load Lines
        self.table_lines.setRowCount(0)
        for line in order.lines:
            prod = self.manager.get_product(line.code_prod)
            prod_name = prod.nom_prod if prod else f"Unknown ({line.code_prod})"
            
            r = self.table_lines.rowCount()
            self.table_lines.insertRow(r)
            self.table_lines.setItem(r, 0, QTableWidgetItem(prod_name))
            self.table_lines.setItem(r, 1, QTableWidgetItem(str(line.quantity)))
            self.table_lines.setItem(r, 2, QTableWidgetItem(f"{line.price_at_order_time:.2f}"))
            self.table_lines.setItem(r, 3, QTableWidgetItem(f"{line.total:.2f}"))

        # Enable/Disable controls based on status
        is_draft = (order.status.value == "DRAFT")
        is_archived = (order.status.value == "ARCHIVED")
        self.group_add_line.setVisible(is_draft)
        
        # Buttons logic
        self.btn_confirm.setEnabled(is_draft)
        # Pay only if Confirmed and UNPAID/PARTIAL
        self.btn_pay.setEnabled(order.status.value == "CONFIRMED" and order.payment_status.value != "PAID")
        self.btn_cancel.setEnabled(order.status.value != "CANCELLED" and order.status.value != "ARCHIVED")
        
        # Show/hide archive/unarchive buttons
        self.btn_archive.setVisible(not is_archived)
        self.btn_unarchive.setVisible(is_archived)

    def create_draft(self):
        # Allow creating empty draft
        # Manager.create_order currently requires product.
        # We need to change Manager or just instantiate with first product?
        # User said "add button won't work". 
        # I'll rely on add_line for populating.
        # But I need to create the container first.
        # Use selection from combo?
        
        idx = self.combo_prod.currentIndex()
        if idx < 0: 
             QMessageBox.warning(self, "Info", "Veuillez sélectionner un produit pour commencer")
             return

        code_prod = self.combo_prod.itemData(idx)
        # We prompt for Qty or default 1
        res = self.manager.create_order(code_prod, 1) # Default 1, can edit later
        if isinstance(res, str):
             QMessageBox.warning(self, "Erreur", res)
        else:
             self.load_orders()
             self.status_bar.showMessage(f"Commande #{res.code_cmd} créée.", 3000)

    def add_line(self):
        if not hasattr(self, 'selected_order'): return
        try:
            qty_text = self.input_qty.text()
            if not qty_text: 
                 QMessageBox.warning(self, "Erreur", "Quantité requise")
                 return
            qty = int(qty_text)
            
            idx = self.combo_prod.currentIndex()
            if idx < 0: return
            code_prod = self.combo_prod.itemData(idx)
            
            res = self.manager.add_line_to_order(self.selected_order.code_cmd, code_prod, qty)
            if res is True:
                self.on_order_selected() # refresh details
                self.load_orders() # refresh total (in list)
                self.status_bar.showMessage("Produit ajouté.", 2000)
            else:
                 QMessageBox.warning(self, "Erreur", str(res))
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Quantité invalide")

    def confirm_order(self):
        if not hasattr(self, 'selected_order'): return
        res = self.manager.confirm_order(self.selected_order.code_cmd)
        if res is True:
            self.load_orders()
            self.on_order_selected()
            self.status_bar.showMessage("Commande CONFIRMÉE.", 3000)
        else:
            QMessageBox.warning(self, "Erreur", str(res))

    def pay_order(self):
        if not hasattr(self, 'selected_order'): return
        res = self.manager.pay_order(self.selected_order.code_cmd)
        if res is True:
            self.load_orders()
            self.on_order_selected()
            self.status_bar.showMessage("Commande PAYÉE (Stock déduit).", 3000)
        else:
            QMessageBox.warning(self, "Erreur", str(res))

    def deliver_order(self):
        if not hasattr(self, 'selected_order'): return
        res = self.manager.deliver_order(self.selected_order.code_cmd)
        if res is True:
            self.load_orders()
            self.on_order_selected()
            self.status_bar.showMessage("Commande LIVRÉE.", 3000)
        else:
            QMessageBox.warning(self, "Erreur", str(res))

    def cancel_order(self):
        if not hasattr(self, 'selected_order'): return
        if self.manager.cancel_order(self.selected_order.code_cmd):
            self.load_orders()
            self.on_order_selected()
            self.status_bar.showMessage("Commande ANNULÉE.", 3000)

    def archive_order(self):
        row = self.table_orders.currentRow()
        if row < 0: return
        code_cmd = int(self.table_orders.item(row, 0).text())
        if self.manager.delete_order(code_cmd):
            self.load_orders()
            self.status_bar.showMessage("Commande Archivée.", 3000)

    def unarchive_order(self):
        row = self.table_orders.currentRow()
        if row < 0: return
        code_cmd = int(self.table_orders.item(row, 0).text())
        if self.manager.unarchive_order(code_cmd):
            self.load_orders()
            self.status_bar.showMessage("Commande Désarchivée.", 3000)

# --- CUSTOM DASHBOARD WIDGETS ---

class KPICard(QFrame):
    def __init__(self, title, value, color="#00d4ff"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumSize(200, 100)
        self.setStyleSheet(f"""
            KPICard {{
                background-color: rgba(60, 60, 70, 0.4);
                border: 1px solid rgba(100, 120, 140, 0.2);
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title Label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #b0b0b0; font-size: 13px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Value Label
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 800; margin-top: 5px;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)


    def update_value(self, value):
        self.value_label.setText(value)

class PieChartWidget(QWidget):
    def __init__(self, data=None):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.data = data or {}
        self.colors = ["#00d4ff", "#ff4b2b", "#ffb400", "#28a745", "#9b59b6"]

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        if not self.data: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center the pie chart
        side = min(self.width(), self.height())
        rect = QRectF((self.width() - side) / 2 + 20, (self.height() - side) / 2 + 20, side - 40, side - 40)
        
        total = sum(self.data.values())
        if total == 0: return
        
        start_angle = 90 * 16
        for i, (name, value) in enumerate(self.data.items()):
            span_angle = -int((value / total) * 360 * 16)
            
            color = QColor(self.colors[i % len(self.colors)])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(rect, start_angle, span_angle)
            
            start_angle += span_angle

class BarChartWidget(QWidget):
    def __init__(self, data=None, color="#00d4ff"):
        super().__init__()
        self.setMinimumHeight(200)
        self.data = data or [] # List of (name, value)
        self.color = color

    def set_data(self, data):
        self.data = data[:5] # Top 5 only
        self.update()

    def paintEvent(self, event):
        if not self.data: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        max_val = max(v for _, v in self.data) if self.data else 1
        bar_height = 20
        spacing = 30
        
        for i, (name, value) in enumerate(self.data):
            y = 20 + i * (bar_height + spacing)
            w = (value / max_val) * (self.width() - 100)
            
            # Label
            painter.setPen(QPen(QColor("#b0b0b0")))
            painter.drawText(0, y - 5, name)
            
            # Bar
            gradient = QLinearGradient(0, y, w, y)
            gradient.setColorAt(0, QColor(self.color))
            gradient.setColorAt(1, QColor(self.color).darker(150))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(0, y, w, bar_height), 4, 4)
            
            # Value
            painter.setPen(QPen(QColor("white")))
            painter.drawText(int(w) + 5, y + 15, str(value))

class LineChartWidget(QWidget):
    def __init__(self, data=None):
        super().__init__()
        self.setMinimumHeight(200)
        self.data = data or [] # List of (date, value)

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        if not self.data: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        values = [v for _, v in self.data]
        if not values: return
        max_val = max(values) if values else 1
        min_val = min(values) if values else 1
        if max_val == min_val: max_val += 1
        
        padding = 40
        w = self.width() - (padding * 2)
        h = self.height() - (padding * 2)
        step_x = w / (len(self.data) - 1) if len(self.data) > 1 else w
        
        path = QPainterPath()
        for i, (_, v) in enumerate(self.data):
            x = padding + i * step_x
            y = self.height() - padding - ((v / max_val) * h)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        # Stroke
        pen = QPen(QColor("#00d4ff"), 3)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Fill
        fill_path = QPainterPath(path)
        fill_path.lineTo(self.width() - padding, self.height() - padding)
        fill_path.lineTo(padding, self.height() - padding)
        fill_path.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 212, 255, 60))
        gradient.setColorAt(1, QColor(0, 212, 255, 0))
        painter.fillPath(fill_path, QBrush(gradient))

class StatsTab(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Main layout is scrollable
        self.main_layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #2b2b2b;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. KPI Cards Row
        self.kpi_layout = QHBoxLayout()
        self.card_revenue = KPICard("REVENU TOTAL", "0.00 DT")
        self.card_orders = KPICard("COMMANDES", "0", color="#ffb400")
        self.card_products = KPICard("PRODUITS", "0", color="#28a745")
        self.card_low_stock = KPICard("STOCK FAIBLE", "0", color="#ff4b2b")
        
        self.kpi_layout.addWidget(self.card_revenue)
        self.kpi_layout.addWidget(self.card_orders)
        self.kpi_layout.addWidget(self.card_products)
        self.kpi_layout.addWidget(self.card_low_stock)
        self.layout.addLayout(self.kpi_layout)
        
        # 2. Charts Grid
        charts_layout = QHBoxLayout()
        
        # Order Status (Pie)
        pie_group = QGroupBox("Répartition des Commandes")
        pie_layout = QVBoxLayout()
        self.pie_chart = PieChartWidget()
        pie_layout.addWidget(self.pie_chart)
        pie_group.setLayout(pie_layout)

        
        # Top Products (Bar)
        top_prod_group = QGroupBox("Top 5 Produits (Quantité)")
        top_prod_layout = QVBoxLayout()
        self.top_prod_chart = BarChartWidget()
        top_prod_layout.addWidget(self.top_prod_chart)
        top_prod_group.setLayout(top_prod_layout)
        
        charts_layout.addWidget(pie_group, 1)
        charts_layout.addWidget(top_prod_group, 2)
        self.layout.addLayout(charts_layout)
        
        # 3. Middle Row: Stock & Revenue by Product
        middle_layout = QHBoxLayout()
        
        # Stock Levels
        stock_group = QGroupBox("État du Stock")
        stock_layout = QVBoxLayout()
        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(3)
        self.table_stock.setHorizontalHeaderLabels(["Produit", "Stock", "État"])
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stock.setMaximumHeight(250)
        stock_layout.addWidget(self.table_stock)
        stock_group.setLayout(stock_layout)
        
        # Revenue by Product (Bar)
        rev_prod_group = QGroupBox("Revenu par Produit")
        rev_prod_layout = QVBoxLayout()
        self.rev_prod_chart = BarChartWidget(color="#28a745")
        rev_prod_layout.addWidget(self.rev_prod_chart)
        rev_prod_group.setLayout(rev_prod_layout)
        
        middle_layout.addWidget(stock_group, 1)
        middle_layout.addWidget(rev_prod_group, 1)
        self.layout.addLayout(middle_layout)
        
        # 4. Bottom Row: Revenue Trend & Activity
        bottom_layout = QHBoxLayout()
        
        # Revenue Over Time
        line_group = QGroupBox("Évolution du Revenu (Paiements)")
        line_layout = QVBoxLayout()
        self.line_chart = LineChartWidget()
        line_layout.addWidget(self.line_chart)
        line_group.setLayout(line_layout)
        
        # Recent Activity
        activity_group = QGroupBox("Activité Récente")
        activity_layout = QVBoxLayout()
        self.list_activity = QListWidget()
        self.list_activity.setMaximumHeight(250)
        self.list_activity.setStyleSheet("""
            QListWidget {
                background: rgba(60, 60, 70, 0.4);
                border: 1px solid rgba(100, 120, 140, 0.2);
                border-radius: 8px;
            }
        """)
        activity_layout.addWidget(self.list_activity)
        activity_group.setLayout(activity_layout)
        
        bottom_layout.addWidget(line_group, 2)
        bottom_layout.addWidget(activity_group, 1)
        self.layout.addLayout(bottom_layout)
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)
        
        self.load_stats()

    def load_stats(self):
        # 1. Update KPIs
        kpis = self.manager.get_dashboard_kpis()
        self.card_revenue.update_value(f"{kpis['total_revenue']:.2f} DT")
        self.card_orders.update_value(str(kpis['active_orders']))
        self.card_products.update_value(str(kpis['active_products']))
        self.card_low_stock.update_value(str(kpis['low_stock_count']))
        
        # 2. Update Charts
        self.pie_chart.set_data(self.manager.get_order_status_distribution())
        self.top_prod_chart.set_data(self.manager.get_most_ordered_products())
        self.rev_prod_chart.set_data(self.manager.get_revenue_by_product())
        self.line_chart.set_data(self.manager.get_revenue_over_time())
        
        # 3. Update Stock Table
        self.table_stock.setRowCount(0)
        stock_levels = self.manager.get_stock_levels()
        for s in stock_levels:
            r = self.table_stock.rowCount()
            self.table_stock.insertRow(r)
            self.table_stock.setItem(r, 0, QTableWidgetItem(s['name']))
            self.table_stock.setItem(r, 1, QTableWidgetItem(str(s['quantity'])))
            
            # Badge for status
            status_item = QTableWidgetItem(s['status'].upper())
            if s['status'] == 'low': status_item.setForeground(QColor("#ff4b2b"))
            elif s['status'] == 'medium': status_item.setForeground(QColor("#ffb400"))
            else: status_item.setForeground(QColor("#28a745"))
            self.table_stock.setItem(r, 2, status_item)
            
        # 4. Update Activity Feed
        self.list_activity.clear()
        activities = self.manager.get_recent_activity()
        for act in activities:
            item_text = f"[{act['timestamp'].strftime('%H:%M')}] {act['message']}"
            item = QListWidgetItem(item_text)
            if act['type'] == 'payment':
                item.setForeground(QColor("#28a745"))
            elif act['type'] == 'order_created':
                item.setForeground(QColor("#00d4ff"))
            self.list_activity.addItem(item)

