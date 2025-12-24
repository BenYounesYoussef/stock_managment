from manager import StockManager
import os

class ConsoleInterface:
    def __init__(self):
        self.manager = StockManager()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        print("\n" + "="*40)
        print(f" {title.center(38)} ")
        print("="*40)

    def main_menu(self):
        while True:
            self.print_header("GESTION DE STOCK")
            print("1. Gestion des Produits")
            print("2. Gestion des Commandes")
            print("3. Quitter")
            
            choice = input("\nVotre choix: ")
            
            if choice == '1':
                self.product_menu()
            elif choice == '2':
                self.order_menu()
            elif choice == '3':
                print("Au revoir!")
                break
            else:
                print("Choix invalide.")

    # --- Product Views ---
    def product_menu(self):
        while True:
            self.print_header("GESTION DES PRODUITS")
            print("1. Ajouter un produit")
            print("2. Modifier un produit")
            print("3. Archiver un produit")
            print("4. Lister les produits (A-Z)")
            print("5. Retour")

            choice = input("\nVotre choix: ")

            if choice == '1':
                self.add_product_view()
            elif choice == '2':
                self.update_product_view()
            elif choice == '3':
                self.delete_product_view()
            elif choice == '4':
                self.list_products_view()
            elif choice == '5':
                break
            else:
                print("Choix invalide.")

    def add_product_view(self):
        self.print_header("AJOUTER PRODUIT")
        nom = input("Nom du produit: ")
        desc = input("Description: ")
        try:
            qty = int(input("Quantité: "))
            price = float(input("Prix unitaire: "))
            prod = self.manager.add_product(nom, desc, qty, price)
            print(f"\nProduit ajouté avec succès: {prod}")
        except ValueError:
            print("\nErreur: Veuillez entrer des nombres valides pour la quantité et le prix.")
        input("\nAppuyez sur Entrée pour continuer...")

    def list_products_view(self):
        self.print_header("LISTE DES PRODUITS")
        products = self.manager.get_all_products_sorted()
        if not products:
            print("Aucun produit en stock.")
        else:
            print(f"{'Code':<5} {'Nom':<20} {'Qté':<5} {'Prix':<10} {'Description'}")
            print("-" * 60)
            for p in products:
                print(f"{p.code_prod:<5} {p.nom_prod:<20} {p.quantite:<5} {p.prix_unit:<10} {p.description}")
        input("\nAppuyez sur Entrée pour continuer...")

    def update_product_view(self):
        self.print_header("MODIFIER PRODUIT")
        try:
            code = int(input("Code du produit à modifier: "))
            prod = self.manager.get_product(code)
            if not prod:
                print("Produit introuvable.")
            else:
                print(f"Modification de: {prod.nom_prod}")
                nom = input(f"Nouveau nom ({prod.nom_prod}): ") or prod.nom_prod
                desc = input(f"Nouvelle description ({prod.description}): ") or prod.description
                
                qty_str = input(f"Nouvelle quantité ({prod.quantite}): ")
                qty = int(qty_str) if qty_str else prod.quantite
                
                price_str = input(f"Nouveau prix ({prod.prix_unit}): ")
                price = float(price_str) if price_str else prod.prix_unit
                
                self.manager.update_product(code, nom, desc, qty, price)
                print("Produit mis à jour.")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def delete_product_view(self):
        self.print_header("SUPPRIMER PRODUIT")
        try:
            code = int(input("Code du produit à supprimer: "))
            if self.manager.delete_product(code):
                print("Produit supprimé.")
            else:
                print("Produit introuvable.")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    # --- Order Views ---
    def order_menu(self):
        while True:
            self.print_header("GESTION DES COMMANDES")
            print("1. Créer une commande")
            print("2. Archiver une commande")
            print("3. Afficher Statistiques")
            print("4. Historique des commandes")
            print("5. Retour")

            choice = input("\nVotre choix: ")

            if choice == '1':
                self.create_order_view()
            elif choice == '2':
                self.delete_order_view()
            elif choice == '3':
                self.stats_view()
            elif choice == '4':
                self.history_view()
            elif choice == '5':
                break
            else:
                print("Choix invalide.")

    def create_order_view(self):
        self.print_header("NOUVELLE COMMANDE")
        try:
            code_prod = int(input("Code du produit: "))
            qty = int(input("Quantité commandée: "))
            result = self.manager.create_order(code_prod, qty)
            if isinstance(result, str): # Error message
                print(f"Erreur: {result}")
            else:
                print(f"Commande créée: {result}")
                # Generate Invoice
                print("\n--- FACTURE ---")
                prod = self.manager.get_product(code_prod)
                total = prod.prix_unit * qty
                print(f"Produit: {prod.nom_prod}")
                print(f"Quantité: {qty}")
                print(f"Prix Unitaire: {prod.prix_unit}€")
                print(f"Total à payer: {total}€")
                print("---------------")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def delete_order_view(self):
        self.print_header("SUPPRIMER COMMANDE")
        try:
            code = int(input("Code de la commande à supprimer: "))
            if self.manager.delete_order(code):
                print("Commande supprimée (archivée dans l'historique).")
            else:
                print("Commande introuvable.")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def stats_view(self):
        self.print_header("STATISTIQUES")
        stats = self.manager.get_most_ordered_products()
        if not stats:
            print("Aucune donnée.")
        else:
            print("Produits les plus commandés:")
            for name, qty in stats:
                print(f"- {name}: {qty} unités")
        input("\nAppuyez sur Entrée pour continuer...")

    def history_view(self):
        self.print_header("HISTORIQUE DES COMMANDES")
        orders = self.manager.get_all_orders_history()
        if not orders:
            print("Aucune commande.")
        else:
            for o in orders:
                print(o)
        input("\nAppuyez sur Entrée pour continuer...")
