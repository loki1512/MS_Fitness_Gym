import uuid
from datetime import datetime
from extensions import db
from flask_security import UserMixin, RoleMixin

# ---- Auth Models ----
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# ---- Business Models ----

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    default_price = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    subtotal = db.Column(db.Float, nullable=False)
    bill_discount_type = db.Column(db.String(10))
    bill_discount_value = db.Column(db.Float)
    final_amount = db.Column(db.Float, nullable=False)

    customer_name = db.Column(db.String(200))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.Text)

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bill.id"), nullable=False)

    item_name = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    physical_units = db.Column(db.Enum('pcs', 'kg', 'liter', 'meter'), default='pcs')
    item_discount_type = db.Column(db.String(10))
    item_discount_value = db.Column(db.Float)
    final_item_amount = db.Column(db.Float, nullable=False)

