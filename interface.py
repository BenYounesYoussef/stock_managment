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
            print("2. Voir les détails d'une commande")
            print("3. Confirmer une commande")
            print("4. Payer une commande")
            print("5. Livrer une commande")
            print("6. Annuler une commande")
            print("7. Archiver une commande")
            print("8. Afficher Statistiques")
            print("9. Historique des commandes")
            print("10. Retour")

            choice = input("\nVotre choix: ")

            if choice == '1':
                self.create_order_view()
            elif choice == '2':
                self.view_order_details_view()
            elif choice == '3':
                self.confirm_order_view()
            elif choice == '4':
                self.pay_order_view()
            elif choice == '5':
                self.deliver_order_view()
            elif choice == '6':
                self.cancel_order_view()
            elif choice == '7':
                self.delete_order_view()
            elif choice == '8':
                self.stats_view()
            elif choice == '9':
                self.history_view()
            elif choice == '10':
                break
            else:
                print("Choix invalide.")

    def create_order_view(self):
        self.print_header("NOUVELLE COMMANDE")
        try:
            print("--- Premier Produit ---")
            code_prod = int(input("Code du produit: "))
            qty = int(input("Quantité commandée: "))
            order = self.manager.create_order(code_prod, qty)
            
            if isinstance(order, str): # Error message
                print(f"Erreur: {order}")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            print(f"Commande créée: {order.code_cmd}")
            
            # Additional lines loop
            while True:
                choice = input("\nAjouter un autre produit ? (o/n): ").lower()
                if choice != 'o':
                    break
                
                try:
                    code_prod = int(input("Code du produit: "))
                    qty = int(input("Quantité commandée: "))
                    res = self.manager.add_line_to_order(order.code_cmd, code_prod, qty)
                    if res is True:
                         print("Ligne ajoutée.")
                    else:
                         print(f"Erreur: {res}")
                except ValueError:
                    print("Erreur de saisie.")

            # Show Recap
            self.print_order_details(order.code_cmd)
                
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def view_order_details_view(self):
        self.print_header("DETAILS COMMANDE")
        try:
            code = int(input("Code de la commande: "))
            self.print_order_details(code)
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def print_order_details(self, code_cmd):
        order = self.manager.get_order(code_cmd)
        if not order:
            print("Commande introuvable.")
            return

        print("\n" + "="*30)
        print(f"COMMANDE #{order.code_cmd}")
        print(f"Status: {order.status.value}")
        print(f"Paiement: {order.payment_status.value}")
        print(f"Livraison: {order.delivery_status.value}")
        print("-" * 30)
        print(f"{'Produit':<20} {'Qté':<5} {'Total':<10}")
        print("-" * 30)
        
        for line in order.lines:
            prod = self.manager.get_product(line.code_prod)
            name = prod.nom_prod if prod else f"Unknown ({line.code_prod})"
            print(f"{name:<20} {line.quantity:<5} {line.total:<10.2f}")
            
        print("-" * 30)
        print(f"TOTAL: {order.total_amount:.2f}€")
        print("="*30)

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

    def confirm_order_view(self):
        self.print_header("CONFIRMER COMMANDE")
        try:
            code = int(input("Code de la commande: "))
            res = self.manager.confirm_order(code)
            if res is True:
                print("Commande confirmée avec succès.")
            else:
                print(f"Erreur: {res}")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def pay_order_view(self):
        self.print_header("PAYER COMMANDE")
        try:
            code = int(input("Code de la commande: "))
            amount_str = input("Montant (laisser vide pour tout payer): ")
            amount = float(amount_str) if amount_str else None
            
            res = self.manager.pay_order(code, amount)
            if res is True:
                print("Paiement enregistré.")
            else:
                print(f"Erreur: {res}")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def deliver_order_view(self):
        self.print_header("LIVRER COMMANDE")
        try:
            code = int(input("Code de la commande: "))
            res = self.manager.deliver_order(code)
            if res is True:
                print("Commande livrée avec succès.")
            else:
                print(f"Erreur: {res}")
        except ValueError:
            print("Erreur de saisie.")
        input("\nAppuyez sur Entrée pour continuer...")

    def cancel_order_view(self):
        self.print_header("ANNULER COMMANDE")
        try:
            code = int(input("Code de la commande: "))
            res = self.manager.cancel_order(code)
            if res is True:
                print("Commande annulée.")
            else:
                print(f"Erreur: {res}")
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
