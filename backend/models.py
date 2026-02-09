"""
MS Power Fitness - Database Models
SQLAlchemy models for gym management system
"""
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, verify_and_update_password
from datetime import datetime, timedelta

db = SQLAlchemy()

# Association table for many-to-many relationship between users and roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Role model for Flask-Security"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin):
    """User model with Flask-Security integration"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))
    memberships = db.relationship('Membership', backref='user', lazy='dynamic',
                                 cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    def verify_password(self, password):
        """Verify the password using Flask-Security's built-in utility"""
        return verify_and_update_password(password, self)
    @property
    def display_name(self):
        """Return name with phone number for consistent identity display"""
        return f"{self.name} - {self.phone}"
    
    @property
    def current_membership(self):
        """Get the current active membership"""
        return self.memberships.filter_by(status='Active').order_by(
            Membership.end_date.desc()
        ).first()
    
    @property
    def is_expired(self):
        """Check if user's membership has expired"""
        membership = self.current_membership
        if not membership:
            return True
        return membership.end_date < datetime.utcnow().date()
    
    @property
    def days_until_expiry(self):
        """Calculate days until membership expires"""
        membership = self.current_membership
        if not membership:
            return None
        delta = membership.end_date - datetime.utcnow().date()
        return delta.days
    
    def __repr__(self):
        return f'<User {self.display_name}>'

class Plan(db.Model):
    """Membership plan model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Plan {self.name} - ₹{self.price} for {self.duration_days} days>'

class Membership(db.Model):
    """Membership records linking users to plans"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active', index=True)  # Active, Expiring, Expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def user_display_name(self):
        """Return user's display name with phone"""
        return self.user.display_name
    
    @property
    def is_expiring_soon(self):
        """Check if membership expires within 7 days"""
        if self.status == 'Expired':
            return False
        delta = self.end_date - datetime.utcnow().date()
        return 0 <= delta.days <= 7
    
    def update_status(self):
        """Update membership status based on dates"""
        today = datetime.utcnow().date()
        if self.end_date < today:
            self.status = 'Expired'
        elif (self.end_date - today).days <= 7:
            self.status = 'Expiring'
        else:
            self.status = 'Active'
    
    def __repr__(self):
        return f'<Membership {self.user_display_name} - {self.plan.name} until {self.end_date}>'

class Payment(db.Model):
    """Payment records with UPI tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    txn_ref = db.Column(db.String(12), nullable=True, index=True)  # 12-digit UTR
    payment_method = db.Column(db.String(20), default='UPI')  # UPI or Cash
    status = db.Column(db.String(20), default='Pending', index=True)  # Pending, Approved, Rejected
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    plan = db.relationship('Plan', backref='payments')
    
    @property
    def user_display_name(self):
        """Return user's display name with phone"""
        return self.user.display_name
    
    def __repr__(self):
        return f'<Payment ₹{self.amount} by {self.user_display_name} - {self.status}>'
