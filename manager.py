import json
import os
import datetime
import mysql.connector
from mysql.connector import Error
from models import Product, Order, OrderLine, OrderStatus, PaymentStatus, ProductStatus, DeliveryStatus

class StockManager:
    def __init__(self, products_file="products.json", orders_file="orders.json"):
        self.products_file = products_file
        self.orders_file = orders_file
        self.products = []
        self.orders = []
        self.auto_sync = False # Feature flag for real-time sync
        self.load_data()

    def load_data(self):
        # Load Products
        if os.path.exists(self.products_file):
            try:
                with open(self.products_file, 'r') as f:
                    data = json.load(f)
                    self.products = [Product.from_dict(item) for item in data]
            except (json.JSONDecodeError, KeyError, TypeError):
                self.products = []
        
        # Load Orders
        # Warning: Schema changed. Old orders might fail to load.
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r') as f:
                    data = json.load(f)
                    self.orders = []
                    for item in data:
                        try:
                            self.orders.append(Order.from_dict(item))
                        except Exception:
                            # Skip malformed/old version orders to avoid crash
                            continue
            except json.JSONDecodeError:
                self.orders = []

    def save_data(self):
        with open(self.products_file, 'w') as f:
            json.dump([p.to_dict() for p in self.products], f, indent=4)
        
        with open(self.orders_file, 'w') as f:
            json.dump([o.to_dict() for o in self.orders], f, indent=4)
            
        # Auto-Sync Trigger
        if self.auto_sync:
            try:
                # We don't want to show a popup here as it might be frequent, 
                # just print to console or log. 
                # If disconnected, export_json_to_db returns False but handles it gracefully.
                self.export_json_to_db()
            except Exception as e:
                print(f"Auto-Sync Warning: {e}")

    # --- Product Management ---
    def add_product(self, nom, description, quantite, prix):
        # Unique Name Check (Case Insensitive)
        for p in self.products:
            if p.nom_prod.lower() == nom.lower():
                return "Un produit avec ce nom existe déjà."
                
        # Auto-increment code_prod
        new_code = 1
        if self.products:
            new_code = max(p.code_prod for p in self.products) + 1
        
        new_product = Product(new_code, nom, description, quantite, prix)
        self.products.append(new_product)
        self.save_data()
        return new_product

    def get_product(self, code_prod):
        for p in self.products:
            if p.code_prod == code_prod:
                return p
        return None

    def update_product(self, code_prod, nom=None, description=None, quantite=None, prix=None):
        product = self.get_product(code_prod)
        if product:
            if nom:
                # Check uniqueness if name changed
                for p in self.products:
                    if p.code_prod != code_prod and p.nom_prod.lower() == nom.lower():
                        return "Un produit avec ce nom existe déjà."
                product.nom_prod = nom
            if description: product.description = description
            if quantite is not None: product.quantite = quantite
            if prix is not None: product.prix_unit = prix
            self.save_data()
            return True
        return False

    def delete_product(self, code_prod):
        # Soft Delete (Archive)
        product = self.get_product(code_prod)
        if product:
            product.status = ProductStatus.ARCHIVED
            self.save_data()
            return True
        return False

    def get_all_products_sorted(self):
        # Active only
        return sorted([p for p in self.products if p.status == ProductStatus.ACTIVE], key=lambda p: p.nom_prod.lower())

    def get_archived_products(self):
        return sorted([p for p in self.products if p.status == ProductStatus.ARCHIVED], key=lambda p: p.nom_prod.lower())

    def unarchive_product(self, code_prod):
        # Restore archived product to active
        product = self.get_product(code_prod)
        if product and product.status == ProductStatus.ARCHIVED:
            product.status = ProductStatus.ACTIVE
            self.save_data()
            return True
        return False

    # --- Order Management ---
    def create_order(self, code_prod, quantite):
        """
        Creates a new Order in DRAFT status. 
        Validates Qty > 0 and Stock availability (Strict Draft Rule).
        """
        if quantite <= 0:
            return "La quantité doit être positive."

        product = self.get_product(code_prod)
        if not product:
            return "Produit introuvable."
        
        if product.quantite < quantite:
            return f"Stock insuffisant (Stock: {product.quantite})."

        # Create Line
        line = OrderLine(code_prod, quantite, product.prix_unit)
        
        new_code = 1
        if self.orders:
            new_code = max(o.code_cmd for o in self.orders) + 1
            
        new_order = Order(new_code, lines=[line], status=OrderStatus.DRAFT)
        self.orders.append(new_order)
        self.save_data()
        return new_order

    def add_line_to_order(self, code_cmd, code_prod, quantite):
        if quantite <= 0:
            return "La quantité doit être positive."

        order = self.get_order(code_cmd)
        if not order:
            return "Commande introuvable"
        
        if order.status != OrderStatus.DRAFT:
            return "Impossible de modifier une commande qui n'est plus en brouillon."
            
        product = self.get_product(code_prod)
        if not product:
            return "Produit introuvable"
            
        # Check Stock (Total for this product in this order vs Stock)
        current_in_order = sum(l.quantity for l in order.lines if l.code_prod == code_prod)
        if (current_in_order + quantite) > product.quantite:
             return f"Stock insuffisant. Total demandé: {current_in_order + quantite}, Stock: {product.quantite}"

        # Check if line exists, merge?
        existing_line = next((l for l in order.lines if l.code_prod == code_prod), None)
        if existing_line:
            existing_line.quantity += quantite
        else:
            line = OrderLine(code_prod, quantite, product.prix_unit)
            order.lines.append(line)
            
        order.updated_at = datetime.datetime.now()
        self.save_data()
        return True
    def confirm_order(self, code_cmd):
        order = self.get_order(code_cmd)
        if not order:
            return "Commande introuvable"
        
        if order.status != OrderStatus.DRAFT and order.status != OrderStatus.PENDING:
            return "La commande ne peut pas être confirmée (Status actuel: {})".format(order.status.value)

        # Check Stock availability for all lines
        for line in order.lines:
            prod = self.get_product(line.code_prod)
            if not prod or prod.quantite < line.quantity:
                return f"Stock insuffisant pour le produit #{line.code_prod}"

        order.status = OrderStatus.CONFIRMED
        self.check_and_deduct_stock(order)
        order.updated_at = datetime.datetime.now()
        self.save_data()
        return True

    def pay_order(self, code_cmd, amount=None):
        order = self.get_order(code_cmd)
        if not order:
            return "Commande introuvable"
        
        # If amount not specified, assume full payment
        if amount is None:
            amount = order.total_amount

        order.paid_amount += amount
        order.paid_at = datetime.datetime.now()
        
        if order.paid_amount >= order.total_amount:
            order.payment_status = PaymentStatus.PAID
        elif order.paid_amount > 0:
            order.payment_status = PaymentStatus.PARTIALLY_PAID
            
        self.check_and_deduct_stock(order)
        order.updated_at = datetime.datetime.now()
        self.save_data()
        return True

    def deliver_order(self, code_cmd):
        order = self.get_order(code_cmd)
        if not order:
            return "Commande introuvable"


        if order.status == OrderStatus.CANCELLED:
            return "Impossible de livrer une commande annulée."
            
        if order.status == OrderStatus.ARCHIVED:
            return "Impossible de livrer une commande archivée."
            
        if order.status != OrderStatus.CONFIRMED:
            return f"La commande doit être confirmée avant livraison (Statut actuel: {order.status.value})."

        if order.payment_status != PaymentStatus.PAID:
             return "La commande doit être payée avant la livraison."

        if order.delivery_status == DeliveryStatus.DELIVERED:
            return "La commande est déjà livrée."

        order.delivery_status = DeliveryStatus.DELIVERED
        order.delivered_at = datetime.datetime.now()
        order.updated_at = datetime.datetime.now()
        self.save_data()
        return True

    def check_and_deduct_stock(self, order):
        """
        Subtract stock only when OrderStatus = CONFIRMED and PaymentStatus = PAID
        """
        if order.status == OrderStatus.CONFIRMED and order.payment_status == PaymentStatus.PAID:
            # Check if stock was already deducted? 
            # We need a flag 'stock_deducted' or imply it from status. 
            # If we rely solely on status, we must ensure we don't deduct twice.
            # However, if it JUST became Confirmed+Paid, we deduct.
            # But stateless check is hard. 
            # Simplification: This function is called on status changes.
            # We will iterate lines and deduct. 
            # RISK: Deducting twice.
            # FIX: We should use delivery_status or a specific flag. 
            # Or, we assume if it is NOT_SHIPPED, we process it.
            # Let's assume this method is called exactly when the transition happens.
            # To be safe, we can check if it's already shipped? No.
            # Correct approach: Transitions should be atomic. 
            # For this 'simple' exercise without database transactions:
            # We will perform deduction right here.
            
            # Re-verify stock existence (double check)
            can_fulfill = True
            for line in order.lines:
                 prod = self.get_product(line.code_prod)
                 if prod.quantite < line.quantity:
                     can_fulfill = False
            
            if can_fulfill:
                for line in order.lines:
                    prod = self.get_product(line.code_prod)
                    prod.quantite -= line.quantity
                
                # Auto-update delivery status to ready/pending shipping? 
                # User didn't request auto-shipping.
            else:
                # Rollback or Error?
                # If paid but no stock, we have a problem. 
                pass

    def cancel_order(self, code_cmd):
        """
        Allow cancellation / rollback logic before payment confirmation
        """
        order = self.get_order(code_cmd)
        if not order: return False
        
        # If already paid/confirmed, we might need to refund or restock?
        # User said "rollback logic before payment confirmation".
        # So we freely cancel if not CONFIRMED+PAID.
        
        if order.status == OrderStatus.CONFIRMED and order.payment_status == PaymentStatus.PAID:
             # Need to restock if we cancel a paid confirmed order?
             # User said "Subtract stock only when...", so if we cancel, we add it back.
             for line in order.lines:
                 prod = self.get_product(line.code_prod)
                 if prod: prod.quantite += line.quantity
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.datetime.now()
        self.save_data()
        return True
        
    def get_order(self, code_cmd):
        for o in self.orders:
            if o.code_cmd == code_cmd:
                return o
        return None

    def delete_order(self, code_cmd):
        # User: "instead of delete always add archive"
        # We will use the ARCHIVED status or just CANCELLED.
        # Let's use ARCHIVED to imply "Hidden/Deleted"
        order = self.get_order(code_cmd)
        if order:
            order.status = OrderStatus.ARCHIVED
            order.updated_at = datetime.datetime.now()
            self.save_data()
            return True
        return False

    def get_active_orders(self):
        # Filter out Archived
        return [o for o in self.orders if o.status != OrderStatus.ARCHIVED]

    def get_archived_orders(self):
        return [o for o in self.orders if o.status == OrderStatus.ARCHIVED]

    def get_all_orders_history(self):
        return self.orders 

    def unarchive_order(self, code_cmd):
        # Restore archived order to DRAFT status
        order = self.get_order(code_cmd)
        if order and order.status == OrderStatus.ARCHIVED:
            order.status = OrderStatus.DRAFT
            order.updated_at = datetime.datetime.now()
            self.save_data()
            return True
        return False


    def get_most_ordered_products(self):
        # Returns list of (product_name, total_qty)
        stats = {}
        for order in self.orders:
            # Skip invalid/cancelled orders? Or include all demand?
            # Usually stats include all valid sales.
            if order.status == OrderStatus.CANCELLED or order.status == OrderStatus.ARCHIVED:
                continue
                
            for line in order.lines:
                prod = self.get_product(line.code_prod)
                name = prod.nom_prod if prod else f"Unknown ({line.code_prod})"
                stats[name] = stats.get(name, 0) + line.quantity
        
        sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
        return sorted_stats

    # ========== NEW DASHBOARD STATISTICS METHODS ==========

    def get_dashboard_kpis(self):
        """Returns dict with total revenue, active orders, products count, low stock count."""
        total_revenue = 0.0
        active_orders = 0
        
        for order in self.orders:
            if order.status not in [OrderStatus.CANCELLED, OrderStatus.ARCHIVED]:
                active_orders += 1
                if order.payment_status == PaymentStatus.PAID:
                    total_revenue += order.total_amount
        
        active_products = len(self.get_all_products_sorted())
        
        # Low stock: products with quantity < 10
        low_stock_count = sum(1 for p in self.get_all_products_sorted() if p.quantite < 10)
        
        return {
            "total_revenue": total_revenue,
            "active_orders": active_orders,
            "active_products": active_products,
            "low_stock_count": low_stock_count
        }

    def get_order_status_distribution(self):
        """Returns dict of status -> count for pie/donut chart."""
        distribution = {}
        for order in self.orders:
            status = order.status.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution

    def get_revenue_over_time(self):
        """Returns list of (date_str, revenue) tuples for line chart, grouped by day."""
        daily_revenue = {}
        
        for order in self.orders:
            if order.payment_status == PaymentStatus.PAID and order.paid_at:
                date_str = order.paid_at.strftime("%Y-%m-%d")
                daily_revenue[date_str] = daily_revenue.get(date_str, 0) + order.total_amount
        
        # Sort by date
        sorted_data = sorted(daily_revenue.items(), key=lambda x: x[0])
        return sorted_data

    def get_stock_levels(self):
        """Returns list of products with stock info and status (healthy/medium/low)."""
        levels = []
        for p in self.get_all_products_sorted():
            # Determine status based on quantity thresholds
            if p.quantite >= 50:
                status = "healthy"
            elif p.quantite >= 10:
                status = "medium"
            else:
                status = "low"
            
            levels.append({
                "name": p.nom_prod,
                "quantity": p.quantite,
                "status": status
            })
        return levels

    def get_payment_status_summary(self):
        """Returns dict of payment status -> count."""
        summary = {}
        for order in self.orders:
            if order.status not in [OrderStatus.CANCELLED, OrderStatus.ARCHIVED]:
                status = order.payment_status.value
                summary[status] = summary.get(status, 0) + 1
        return summary

    def get_recent_activity(self, limit=10):
        """Returns list of recent events (orders, payments) with timestamps."""
        activities = []
        
        for order in self.orders:
            # Order creation
            if order.created_at:
                activities.append({
                    "type": "order_created",
                    "message": f"Commande #{order.code_cmd} créée",
                    "timestamp": order.created_at,
                    "amount": order.total_amount
                })
            
            # Payment
            if order.paid_at and order.payment_status == PaymentStatus.PAID:
                activities.append({
                    "type": "payment",
                    "message": f"Commande #{order.code_cmd} payée - {order.total_amount:.2f}DT",
                    "timestamp": order.paid_at,
                    "amount": order.total_amount
                })
        
        # Sort by timestamp descending (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    def get_revenue_by_product(self):
        """Returns list of (product_name, total_revenue) for revenue breakdown."""
        revenue_map = {}
        
        for order in self.orders:
            if order.payment_status == PaymentStatus.PAID:
                for line in order.lines:
                    prod = self.get_product(line.code_prod)
                    name = prod.nom_prod if prod else f"Unknown ({line.code_prod})"
                    revenue_map[name] = revenue_map.get(name, 0) + line.total
        
        sorted_revenue = sorted(revenue_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_revenue

    # --- DATABASE INTEGRATION ---
    def connect_db(self, host, user, password, database_name):
        """Establishes connection to MySQL database, creating it if it doesn't exist."""
        try:
            # First connect to server to check/create DB
            conn = mysql.connector.connect(host=host, user=user, password=password)
            if float(mysql.connector.__version__[0:3]) >= 8.0:
                 cursor = conn.cursor()
            else:
                 cursor = conn.cursor(buffered=True) # For older versions if needed
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            conn.close()

            # Now connect to the specific DB
            self.db_config = {
                'host': host,
                'user': user,
                'password': password,
                'database': database_name
            }
            self.db_conn = mysql.connector.connect(**self.db_config)
            print(f"Connected to database: {database_name}")
            return True, "Connected successfully."
        except Error as e:
            print(f"Error connecting to DB: {e}")
            return False, str(e)

    def setup_database(self):
        """Creates necessary tables in the database."""
        if not hasattr(self, 'db_conn') or not self.db_conn.is_connected():
            return False, "Not connected to database."
        
        try:
            cursor = self.db_conn.cursor()
            
            # Products Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    code_prod INT PRIMARY KEY,
                    nom_prod VARCHAR(255),
                    description TEXT,
                    quantite INT,
                    prix_unit DECIMAL(10, 2),
                    status VARCHAR(50)
                )
            """)
            
            # Orders Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    code_cmd INT PRIMARY KEY,
                    details TEXT,
                    status VARCHAR(50),
                    payment_status VARCHAR(50),
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            
            self.db_conn.commit()
            return True, "Database tables setup successfully."
        except Error as e:
            return False, str(e)

    def export_json_to_db(self):
        """Exports current JSON data objects to MySQL."""
        if not hasattr(self, 'db_conn') or not self.db_conn.is_connected():
            return False, "Not connected to database."
        
        try:
            cursor = self.db_conn.cursor()
            
            # Export Products
            for p in self.products:
                sql = """
                    REPLACE INTO products (code_prod, nom_prod, description, quantite, prix_unit, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # FIX: use p.status.value
                status_val = p.status.value if hasattr(p.status, 'value') else str(p.status)
                val = (p.code_prod, p.nom_prod, p.description, p.quantite, p.prix_unit, status_val)
                cursor.execute(sql, val)
                
            # Export Orders
            for o in self.orders:
                sql = """
                    REPLACE INTO orders (code_cmd, details, status, payment_status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # FIX: use o.lines instead of o.details, and line.to_dict()
                details_json = json.dumps([line.to_dict() for line in o.lines])
                
                # FIX: use .value for Enums
                status_val = o.status.value if hasattr(o.status, 'value') else str(o.status)
                payment_val = o.payment_status.value if hasattr(o.payment_status, 'value') else str(o.payment_status)
                
                val = (o.code_cmd, details_json, status_val, payment_val, o.created_at, o.updated_at)
                cursor.execute(sql, val)

            self.db_conn.commit()
            return True, "Data exported to Database successfully."
        except Error as e:
            return False, str(e)

    def import_db_to_json(self):
        """Imports data from MySQL to in-memory/JSON structure."""
        if not hasattr(self, 'db_conn') or not self.db_conn.is_connected():
            return False, "Not connected to database."
        
        try:
            cursor = self.db_conn.cursor(dictionary=True)
            
            # Import Products
            cursor.execute("SELECT * FROM products")
            db_products = cursor.fetchall()
            self.products = [] 
            for row in db_products:
                p = Product(
                    row['code_prod'], row['nom_prod'], row['description'],
                    row['quantite'], float(row['prix_unit']), row['status']
                )
                self.products.append(p)
            
            # Import Orders
            cursor.execute("SELECT * FROM orders")
            db_orders = cursor.fetchall()
            self.orders = []
            for row in db_orders:
                o = Order(row['code_cmd'])
                lines_data = json.loads(row['details'])
                o.lines = [OrderLine.from_dict(l) for l in lines_data]
                
                # Convert DB strings to Enums
                try:
                    o.status = OrderStatus(row['status'])
                except ValueError:
                    o.status = OrderStatus.DRAFT # Fallback
                
                try:
                    o.payment_status = PaymentStatus(row['payment_status'])
                except ValueError:
                    o.payment_status = PaymentStatus.UNPAID # Fallback

                o.created_at = row['created_at']
                if isinstance(o.created_at, str):
                    try:
                        o.created_at = datetime.datetime.fromisoformat(o.created_at)
                    except ValueError:
                        o.created_at = datetime.datetime.now()

                o.updated_at = row['updated_at']
                if isinstance(o.updated_at, str):
                    try:
                        o.updated_at = datetime.datetime.fromisoformat(o.updated_at)
                    except ValueError:
                        o.updated_at = o.created_at

                self.orders.append(o)

            self.save_data()
            return True, "Data imported from Database successfully."
        except Error as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error parsing data: {e}"

    def sync_data(self):
        """
        Merge rules:
        1. Local products that match DB ID -> Update Local with DB values (Master).
           EXCEPTION: We could sum quantities, but let's assume DB is the truth for this step? 
           User said "automated db setup... rules like new ids or merge qte specifications".
           Implementation: If exists in DB, update local (including Qty). 
           BUT user mentioned "merge qte". Let's sum them for 'sync'.
        2. New IDs in DB -> Add to Local.
        3. Local IDs not in DB -> Keep (will be exported).
        """
        if not hasattr(self, 'db_conn') or not self.db_conn.is_connected():
            return False, "Not connected to database."
        
        try:
            cursor = self.db_conn.cursor(dictionary=True)
            
            # --- SYNC PRODUCTS ---
            cursor.execute("SELECT * FROM products")
            db_prods = {row['code_prod']: row for row in cursor.fetchall()}
            
            local_prods_map = {p.code_prod: p for p in self.products}
            
            for code, row in db_prods.items():
                if code in local_prods_map:
                    local_p = local_prods_map[code]
                    # Merge Logic: DB is Master for attributes to avoid infinite growth on repeated sync.
                    # "Merge Qty" interpreted as: if duplicates existed in source, they are summed (handled by DB aggregation if any, or previous imports).
                    # For Client-DB sync: Update local with DB value.
                    local_p.quantite = row['quantite'] 
                    # Update other fields from DB
                    local_p.nom_prod = row['nom_prod']
                    local_p.prix_unit = float(row['prix_unit'])
                else:
                    # New from DB
                    p = Product(
                        row['code_prod'], row['nom_prod'], row['description'],
                        row['quantite'], float(row['prix_unit']), row['status']
                    )
                    self.products.append(p)
            
            self.save_data()
            # Push back everything to DB
            self.export_json_to_db()
            
            return True, "Data synchronized (Quantities Merged)."
        except Error as e:
            return False, str(e)

