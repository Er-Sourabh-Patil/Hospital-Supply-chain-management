from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    status = db.Column(db.String(30), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inventory_batches = db.relationship('InventoryBatch', backref='supplier', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)


class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    minimum_stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inventory_batches = db.relationship('InventoryBatch', backref='supply', lazy=True, cascade='all, delete-orphan')
    purchase_items = db.relationship('PurchaseOrderItem', backref='supply', lazy=True)
    request_items = db.relationship('SupplyRequestItem', backref='supply', lazy=True)

    @property
    def current_stock(self):
        return sum(b.quantity for b in self.inventory_batches)


class InventoryBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supply_id = db.Column(db.Integer, db.ForeignKey('supply.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    batch_number = db.Column(db.String(80), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    manufacturing_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date, nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    unit_price = db.Column(db.Float, nullable=False, default=0)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(120))
    requests = db.relationship('SupplyRequest', backref='department', lazy=True)


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_date = db.Column(db.Date)
    status = db.Column(db.String(30), default='Pending')
    total_amount = db.Column(db.Float, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])


class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey('supply.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


class SupplyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(30), default='Normal')
    status = db.Column(db.String(30), default='Pending')
    items = db.relationship('SupplyRequestItem', backref='request', lazy=True, cascade='all, delete-orphan')
    requester = db.relationship('User', foreign_keys=[requested_by])


class SupplyRequestItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('supply_request.id'), nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey('supply.id'), nullable=False)
    quantity_requested = db.Column(db.Integer, nullable=False)
    quantity_approved = db.Column(db.Integer, default=0)
    quantity_issued = db.Column(db.Integer, default=0)
