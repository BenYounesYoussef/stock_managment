import datetime
from enum import Enum

class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"

class PaymentStatus(Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    REFUNDED = "REFUNDED"

class DeliveryStatus(Enum):
    NOT_SHIPPED = "NOT_SHIPPED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    RETURNED = "RETURNED"

class ProductStatus(Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class Product:
    def __init__(self, code_prod, nom_prod, description, quantite, prix_unit, status=ProductStatus.ACTIVE):
        self.code_prod = code_prod
        self.nom_prod = nom_prod
        self.description = description
        self.quantite = quantite
        self.prix_unit = prix_unit
        self.status = status if isinstance(status, ProductStatus) else ProductStatus(status)

    def to_dict(self):
        return {
            "code_prod": self.code_prod,
            "nom_prod": self.nom_prod,
            "description": self.description,
            "quantite": self.quantite,
            "prix_unit": self.prix_unit,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["code_prod"],
            data["nom_prod"],
            data["description"],
            data["quantite"],
            data["prix_unit"],
            data.get("status", "ACTIVE")
        )

    def __str__(self):
        status_str = " [ARCHIVED]" if self.status == ProductStatus.ARCHIVED else ""
        return f"[{self.code_prod}] {self.nom_prod} - {self.quantite} en stock - {self.prix_unit}€{status_str}"

class OrderLine:
    def __init__(self, code_prod, quantity, price_at_order_time):
        self.code_prod = code_prod
        self.quantity = quantity
        self.price_at_order_time = price_at_order_time

    @property
    def total(self):
        return self.quantity * self.price_at_order_time

    def to_dict(self):
        return {
            "code_prod": self.code_prod,
            "quantity": self.quantity,
            "price_at_order_time": self.price_at_order_time
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["code_prod"],
            data["quantity"],
            data["price_at_order_time"]
        )

class Order:
    def __init__(self, code_cmd, lines=None, status=OrderStatus.DRAFT, 
                 payment_status=PaymentStatus.UNPAID, delivery_status=DeliveryStatus.NOT_SHIPPED,
                 created_at=None, paid_at=None, delivered_at=None, paid_amount=0.0, updated_at=None):
        self.code_cmd = code_cmd
        self.lines = lines if lines else []
        self.status = status if isinstance(status, OrderStatus) else OrderStatus(status)
        self.payment_status = payment_status if isinstance(payment_status, PaymentStatus) else PaymentStatus(payment_status)
        self.delivery_status = delivery_status if isinstance(delivery_status, DeliveryStatus) else DeliveryStatus(delivery_status)
        self.created_at = self._parse_date(created_at) if created_at else datetime.datetime.now()
        self.updated_at = self._parse_date(updated_at) if updated_at else datetime.datetime.now()
        self.paid_at = self._parse_date(paid_at)
        self.delivered_at = self._parse_date(delivered_at)
        self.paid_amount = paid_amount

    def _parse_date(self, date_obj):
        if isinstance(date_obj, str):
            try:
                # Try full format, otherwise simple date
                if len(date_obj) > 10:
                    return datetime.datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")
                else:
                    return datetime.datetime.strptime(date_obj, "%Y-%m-%d")
            except ValueError:
                return None
        return date_obj

    @property
    def total_amount(self):
        return sum(line.total for line in self.lines)

    @property
    def paid_amount(self):
        return self._paid_amount
    
    @paid_amount.setter
    def paid_amount(self, value):
        self._paid_amount = value

    def to_dict(self):
        return {
            "code_cmd": self.code_cmd,
            "lines": [line.to_dict() for line in self.lines],
            "status": self.status.value,
            "payment_status": self.payment_status.value,
            "delivery_status": self.delivery_status.value,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "paid_at": self.paid_at.strftime("%Y-%m-%d %H:%M:%S") if self.paid_at else None,
            "delivered_at": self.delivered_at.strftime("%Y-%m-%d %H:%M:%S") if self.delivered_at else None,
            "paid_amount": self.paid_amount
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["code_cmd"],
            [OrderLine.from_dict(line) for line in data.get("lines", [])],
            data.get("status", "DRAFT"),
            data.get("payment_status", "UNPAID"),
            data.get("delivery_status", "NOT_SHIPPED"),
            data.get("created_at"),
            data.get("paid_at"),
            data.get("delivered_at"),
            data.get("paid_amount", 0.0),
            data.get("updated_at")
        )

    def __str__(self):
        return f"CMD#{self.code_cmd} [{self.status.value}] - {len(self.lines)} lines - Total: {self.total_amount:.2f}€"
