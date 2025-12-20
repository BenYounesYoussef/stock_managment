import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QComboBox, QHeaderView, QGroupBox, QFormLayout, QProgressBar, QCheckBox, QSplitter, QScrollArea)
from PyQt6.QtCore import Qt
from manager import StockManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de Stock")
        self.setGeometry(100, 100, 1000, 700)
        
        # --- STYLESHEET ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background: #323232;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #3d3d3d;
                color: #b0b0b0;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #323232;
                color: #00d4ff; /* Bright Cyan accent */
                border-bottom: 2px solid #00d4ff;
            }
            QGroupBox {
                border: 1px solid #4d4d4d;
                margin-top: 1.5em;
                border-radius: 6px;
                font-weight: bold;
                color: #00d4ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
            QPushButton:pressed {
                background-color: #005c99;
            }
            /* Specific Button Styles */
            QPushButton#deleteBtn {
                background-color: #d32f2f;
            }
            QPushButton#deleteBtn:hover {
                background-color: #f44336;
            }
            QPushButton#clearBtn {
                background-color: #555;
            }
            QPushButton#clearBtn:hover {
                background-color: #777;
            }
            QTableWidget {
                background-color: #323232;
                gridline-color: #4d4d4d;
                border: none;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #00d4ff;
                color: #000000;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                padding-right: 25px; /* Space for the arrow */
                color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border: none;
                background: transparent;
                image: none; /* Ensure no default image */
            }
            QComboBox::down-arrow {
                image: url(arrow_down_hover.svg); /* Blue arrow by default */
                width: 14px;
                height: 14px;
                background: none;
                border: none; /* No CSS triangle borders */
            }

            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: white;
                selection-background-color: #00d4ff;
                selection-color: black;
                border: 1px solid #555;
                outline: none;
            }
            
            /* Nav Menu Hover Effects */
            QTabBar::tab:hover {
                background: #4d4d4d;
                color: white;
            }
            QHeaderView {
                background-color: #3d3d3d;
            }
            QTableCornerButton::section {
                background-color: #3d3d3d;
                border: none;
            }
        """)

        self.manager = StockManager()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Status Bar for feedback
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Prêt")
        
        self.product_tab = ProductTab(self.manager, self.status_bar)
        self.order_tab = OrderTab(self.manager, self.status_bar)
        self.stats_tab = StatsTab(self.manager)
        
        self.tabs.addTab(self.product_tab, "Produits")
        self.tabs.addTab(self.order_tab, "Commandes")
        self.tabs.addTab(self.stats_tab, "Statistiques")
        
        # Refresh other tabs when changed
        self.tabs.currentChanged.connect(self.on_tab_change)

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
        self.btn_add.clicked.connect(self.add_product)
        self.btn_update = QPushButton("Modifier")
        self.btn_update.clicked.connect(self.update_product)
        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.setObjectName("deleteBtn")
        self.btn_delete.clicked.connect(self.delete_product)
        self.btn_clear = QPushButton("Vider")
        self.btn_clear.setObjectName("clearBtn")
        self.btn_clear.clicked.connect(self.clear_inputs)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        
        self.form_layout.addRow(btn_layout)
        self.form_group.setLayout(self.form_layout)
        self.layout.addWidget(self.form_group)
        
        self.chk_show_archived = QCheckBox("Afficher les archives")
        self.chk_show_archived.stateChanged.connect(self.load_products)
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

    def clear_inputs(self):
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
                 self.clear_inputs()
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
            nom = self.input_nom.text()
            desc = self.input_desc.text()
            qty = int(self.input_qty.text())
            price = float(self.input_price.text())
            
            res = self.manager.update_product(code, nom, desc, qty, price)
            if res is True:
                self.load_products()
                self.clear_inputs()
                self.status_bar.showMessage(f"Produit '{nom}' modifié.", 3000)
            elif isinstance(res, str):
                QMessageBox.warning(self, "Erreur", res)
            else:
                QMessageBox.warning(self, "Erreur", "Produit introuvable.")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Vérifiez les données saisies.")

    def delete_product(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return
            
        code = int(self.table.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment Archiver ce produit ?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.manager.delete_product(code):
                self.load_products()
                self.clear_inputs()
                self.status_bar.showMessage("Produit archivé.", 3000)

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
        
        self.splitter.addWidget(self.left_widget)

        # --- RIGHT: Details (Scrollable) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.right_widget = QWidget()
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
        self.btn_confirm.clicked.connect(self.confirm_order)
        self.btn_pay = QPushButton("Payer Commande")
        self.btn_pay.clicked.connect(self.pay_order)
        self.btn_cancel = QPushButton("Annuler Commande")
        self.btn_cancel.clicked.connect(self.cancel_order)
        
        self.layout_actions.addWidget(self.btn_confirm)
        self.layout_actions.addWidget(self.btn_pay)
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
        self.group_add_line.setVisible(is_draft)
        
        # Buttons logic
        self.btn_confirm.setEnabled(is_draft)
        # Pay only if Confirmed and UNPAID/PARTIAL
        self.btn_pay.setEnabled(order.status.value == "CONFIRMED" and order.payment_status.value != "PAID")
        self.btn_cancel.setEnabled(order.status.value != "CANCELLED" and order.status.value != "ARCHIVED")

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

class StatsTab(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QLabel("Produits les plus commandés")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4ff; margin-bottom: 10px;")
        self.layout.addWidget(self.label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Produit", "Total Commandé", "Visualisation"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)
        
        self.load_stats()

    def load_stats(self):
        self.table.setRowCount(0)
        stats = self.manager.get_most_ordered_products()
        
        # Find max for scaling
        max_qty = 1
        if stats:
             max_qty = max(s[1] for s in stats)
        
        for name, qty in stats:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(qty)))
            
            # Visual Bar
            pbar = QProgressBar()
            pbar.setRange(0, max_qty)
            pbar.setValue(qty)
            pbar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #555;
                    border-radius: 3px;
                    text-align: center;
                    background: #3d3d3d;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: #00d4ff;
                }
            """)
            self.table.setCellWidget(row, 2, pbar)
