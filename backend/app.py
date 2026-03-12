"""
MS Power Fitness - Flask Backend Application
Complete REST API with Flask-Security-Too integration
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, current_user, hash_password
from datetime import datetime, timedelta, date
from models import db, User, Role, Plan, Membership, Payment
import os
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ms_power_fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'

# Initialize extensions
db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


from flask_security import hash_password

# ... after your security = Security(app, user_datastore) ...

with app.app_context():
    db.create_all()
    
    # Ensure the role exists
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    
    # Check if admin exists
    if not user_datastore.find_user(email="admin@msfitness.com"):
        user_datastore.create_user(
            email="admin@msfitness.com",
            password=hash_password("admin123"),
            name="System Admin",        # <--- ADD THIS
            phone="0000000000",         # <--- AND THIS (if required)
            roles=['admin'],
            active=True
        )
        db.session.commit()
        print("Admin user created successfully!")
# Custom decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    @auth_required()
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# INITIALIZATION & SETUP
# ============================================================================

@app.before_request
def before_first_request():
    """Create tables and initialize data if needed"""
    db.create_all()
    
    # Create roles if they don't exist
    if not Role.query.first():
        user_datastore.create_role(name='admin', description='Super Administrator')
        user_datastore.create_role(name='manager', description='Gym Manager')
        user_datastore.create_role(name='member', description='Gym Member')
        db.session.commit()

@app.route('/api/init-admin', methods=['POST'])
def init_admin():
    """Initialize admin user (use once during setup)"""
    data = request.json
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Admin already exists'}), 400
    
    admin_role = Role.query.filter_by(name='admin').first()
    
    admin_user = user_datastore.create_user(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        password=hash_password(data.get('password')),
        active=True,
        roles=[admin_role]
    )
    db.session.commit()
    
    return jsonify({
        'message': 'Admin user created successfully',
        'user': {
            'id': admin_user.id,
            'name': admin_user.display_name,
            'email': admin_user.email
        }
    }), 201

# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new member"""
    data = request.json
    
    # Validate phone number
    phone = data.get('phone', '').strip()
    if len(phone) != 10 or not phone.isdigit():
        return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400
    
    # Check if user exists
    if User.query.filter_by(phone=phone).first():
        return jsonify({'error': 'Phone number already registered'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Parse date of birth
    dob = None
    if data.get('date_of_birth'):
        try:
            dob = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date of birth format. Use YYYY-MM-DD'}), 400
    
    member_role = user_datastore.find_or_create_role(
        name='member', 
        description='Standard gym member'
    )
    
    user = user_datastore.create_user(
        name=data.get('name'),
        phone=phone,
        email=data.get('email'),
        password=hash_password(data.get('password')),
        date_of_birth=dob,
        gender=data.get('gender'),
        active=True,
        roles=[member_role]
    )
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'name': user.display_name,
            'email': user.email,
            'phone': user.phone
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Login user and return token"""
    data = request.json
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.verify_password(data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update membership statuses before login
    for membership in user.memberships:
        membership.update_status()
    db.session.commit()
    
    token = user.get_auth_token()
    is_admin = user.has_role('admin')
    is_manager = user.has_role('manager')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.display_name,
            'email': user.email,
            'phone': user.phone,
            'is_admin': is_admin,
            'is_manager': is_manager,
            'role': 'admin' if is_admin else ('manager' if is_manager else 'member')
        }
    }), 200

@app.route('/api/me', methods=['GET'])
@auth_required()
def get_current_user():
    """Get current user info"""
    # Update membership status
    for membership in current_user.memberships:
        membership.update_status()
    db.session.commit()
    
    membership = current_user.current_membership
    is_admin = current_user.has_role('admin')
    is_manager = current_user.has_role('manager')
    
    return jsonify({
        'id': current_user.id,
        'name': current_user.display_name,
        'email': current_user.email,
        'phone': current_user.phone,
        'date_of_birth': current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
        'gender': current_user.gender,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'role': 'admin' if is_admin else ('manager' if is_manager else 'member'),
        'membership': {
            'active': membership is not None and not current_user.is_expired,
            'plan': membership.plan.name if membership else None,
            'end_date': membership.end_date.isoformat() if membership else None,
            'days_remaining': current_user.days_until_expiry if membership else None,
            'status': membership.status if membership else 'No Membership'
        } if membership else None
    }), 200

# Custom decorator for manager or admin access
def manager_required(f):
    @wraps(f)
    @auth_required()
    def decorated_function(*args, **kwargs):
        if not (current_user.has_role('admin') or current_user.has_role('manager')):
            return jsonify({'error': 'Manager or Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# PROFILE MANAGEMENT
# ============================================================================

@app.route('/api/profile', methods=['GET'])
@auth_required()
def get_profile():
    """Get user's own profile"""
    user = current_user
    
    # Update membership status
    for membership in user.memberships:
        membership.update_status()
    db.session.commit()
    
    membership = user.current_membership
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'gender': user.gender,
        'membership': {
            'active': membership is not None and not user.is_expired,
            'plan': membership.plan.name if membership else None,
            'end_date': membership.end_date.isoformat() if membership else None,
            'days_remaining': user.days_until_expiry if membership else None,
            'status': membership.status if membership else 'No Membership'
        } if membership else None
    }), 200

@app.route('/api/profile', methods=['PUT'])
@auth_required()
def update_profile():
    """Update user's own profile (members can update name, email, phone, password)"""
    data = request.json
    user = current_user
    
    # Members can update these fields
    if 'name' in data:
        user.name = data['name']
    
    if 'email' in data:
        # Check if email is already taken by another user
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'phone' in data:
        phone = data['phone'].strip()
        if len(phone) != 10 or not phone.isdigit():
            return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400
        # Check if phone is already taken by another user
        existing = User.query.filter_by(phone=phone).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Phone number already in use'}), 400
        user.phone = phone
    
    if 'password' in data and data['password']:
        user.password = hash_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@manager_required
def get_user_details(user_id):
    """Get user details (Admin/Manager can view any user)"""
    user = User.query.get_or_404(user_id)
    
    # Update membership status
    for membership in user.memberships:
        membership.update_status()
    db.session.commit()
    
    membership = user.current_membership
    
    # Get all memberships history
    memberships_history = [{
        'id': m.id,
        'plan': m.plan.name,
        'start_date': m.start_date.isoformat(),
        'end_date': m.end_date.isoformat(),
        'status': m.status
    } for m in user.memberships.order_by(Membership.created_at.desc()).all()]
    
    # Get payment history
    payments_history = [{
        'id': p.id,
        'amount': p.amount,
        'plan': p.plan.name if p.plan else 'N/A',
        'payment_method': p.payment_method,
        'txn_ref': p.txn_ref,
        'status': p.status,
        'date': p.date.isoformat()
    } for p in user.payments.order_by(Payment.date.desc()).all()]
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'gender': user.gender,
        'active': user.active,
        'created_at': user.created_at.isoformat(),
        'roles': [role.name for role in user.roles],
        'current_membership': {
            'active': membership is not None and not user.is_expired,
            'plan': membership.plan.name if membership else None,
            'start_date': membership.start_date.isoformat() if membership else None,
            'end_date': membership.end_date.isoformat() if membership else None,
            'days_remaining': user.days_until_expiry if membership else None,
            'status': membership.status if membership else 'No Membership'
        } if membership else None,
        'memberships_history': memberships_history,
        'payments_history': payments_history
    }), 200

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_details(user_id):
    """Update user details (Admin only - can update all fields)"""
    data = request.json
    user = User.query.get_or_404(user_id)
    
    # Admin can update all fields
    if 'name' in data:
        user.name = data['name']
    
    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'phone' in data:
        phone = data['phone'].strip()
        if len(phone) != 10 or not phone.isdigit():
            return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400
        existing = User.query.filter_by(phone=phone).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Phone number already in use'}), 400
        user.phone = phone
    
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if 'gender' in data:
        user.gender = data['gender']
    
    if 'password' in data and data['password']:
        user.password = hash_password(data['password'])
    
    if 'active' in data:
        user.active = data['active']
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/api/admin/members', methods=['GET'])
@manager_required
def get_all_members():
    """Get all members with filters (Admin/Manager)"""
    # Get query parameters
    search = request.args.get('search', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    plan_filter = request.args.get('plan', '').strip()
    dob_from = request.args.get('dob_from', '').strip()
    dob_to = request.args.get('dob_to', '').strip()
    
    # Base query - only members
    member_role = Role.query.filter_by(name='member').first()
    query = User.query.filter(User.roles.contains(member_role))
    
    # Search by name, email, or phone
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.phone.ilike(search_pattern)
            )
        )
    
    # Filter by gender
    if gender_filter:
        query = query.filter(User.gender == gender_filter)
    
    # Filter by date of birth range
    if dob_from:
        try:
            dob_from_date = datetime.strptime(dob_from, '%Y-%m-%d').date()
            query = query.filter(User.date_of_birth >= dob_from_date)
        except ValueError:
            pass
    
    if dob_to:
        try:
            dob_to_date = datetime.strptime(dob_to, '%Y-%m-%d').date()
            query = query.filter(User.date_of_birth <= dob_to_date)
        except ValueError:
            pass
    
    # Get users
    users = query.order_by(User.created_at.desc()).all()
    
    # Filter by plan if specified
    if plan_filter:
        filtered_users = []
        for user in users:
            membership = user.current_membership
            if membership and membership.plan.name == plan_filter:
                filtered_users.append(user)
        users = filtered_users
    
    # Build response
    members_list = []
    for user in users:
        membership = user.current_membership
        members_list.append({
            'id': user.id,
            'name': user.name,
            'display_name': user.display_name,
            'email': user.email,
            'phone': user.phone,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'gender': user.gender,
            'current_plan': membership.plan.name if membership else 'No Plan',
            'membership_status': membership.status if membership else 'Expired',
            'end_date': membership.end_date.isoformat() if membership else None,
            'days_remaining': user.days_until_expiry if membership else None,
            'created_at': user.created_at.isoformat()
        })
    
    return jsonify({
        'members': members_list,
        'count': len(members_list)
    }), 200

@app.route('/api/admin/managers', methods=['POST'])
@admin_required
def create_manager():
    """Create a new manager (Admin only)"""
    data = request.json
    
    # Validate phone number
    phone = data.get('phone', '').strip()
    if len(phone) != 10 or not phone.isdigit():
        return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400
    
    # Check if user exists
    if User.query.filter_by(phone=phone).first():
        return jsonify({'error': 'Phone number already registered'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Parse date of birth
    dob = None
    if data.get('date_of_birth'):
        try:
            dob = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date of birth format. Use YYYY-MM-DD'}), 400
    
    manager_role = Role.query.filter_by(name='manager').first()
    
    manager = user_datastore.create_user(
        name=data.get('name'),
        phone=phone,
        email=data.get('email'),
        password=hash_password(data.get('password')),
        date_of_birth=dob,
        gender=data.get('gender'),
        active=True,
        roles=[manager_role]
    )
    db.session.commit()
    
    return jsonify({
        'message': 'Manager created successfully',
        'user': {
            'id': manager.id,
            'name': manager.display_name,
            'email': manager.email,
            'phone': manager.phone
        }
    }), 201

@app.route('/api/admin/managers', methods=['GET'])
@admin_required
def get_all_managers():
    """Get all managers (Admin only)"""
    manager_role = Role.query.filter_by(name='manager').first()
    managers = User.query.filter(User.roles.contains(manager_role)).all()
    
    return jsonify([{
        'id': m.id,
        'name': m.display_name,
        'email': m.email,
        'phone': m.phone,
        'date_of_birth': m.date_of_birth.isoformat() if m.date_of_birth else None,
        'gender': m.gender,
        'active': m.active,
        'created_at': m.created_at.isoformat()
    } for m in managers]), 200

# ============================================================================
# PLAN MANAGEMENT (Admin)
# ============================================================================

@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get all active plans"""
    plans = Plan.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'duration_days': p.duration_days
    } for p in plans]), 200

@app.route('/api/admin/plans', methods=['GET'])
@admin_required
def get_all_plans():
    """Get all plans including inactive (Admin)"""
    plans = Plan.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'duration_days': p.duration_days,
        'is_active': p.is_active
    } for p in plans]), 200

@app.route('/api/admin/plans', methods=['POST'])
@admin_required
def create_plan():
    """Create new plan (Admin)"""
    data = request.json
    
    plan = Plan(
        name=data.get('name'),
        price=float(data.get('price')),
        duration_days=int(data.get('duration_days')),
        is_active=True
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'message': 'Plan created successfully',
        'plan': {
            'id': plan.id,
            'name': plan.name,
            'price': plan.price,
            'duration_days': plan.duration_days
        }
    }), 201

@app.route('/api/admin/plans/<int:plan_id>', methods=['PUT'])
@admin_required
def update_plan(plan_id):
    """Update plan (Admin)"""
    plan = Plan.query.get_or_404(plan_id)
    data = request.json
    
    plan.name = data.get('name', plan.name)
    plan.price = float(data.get('price', plan.price))
    plan.duration_days = int(data.get('duration_days', plan.duration_days))
    plan.is_active = data.get('is_active', plan.is_active)
    
    db.session.commit()
    
    return jsonify({'message': 'Plan updated successfully'}), 200

@app.route('/api/admin/plans/<int:plan_id>', methods=['DELETE'])
@admin_required
def delete_plan(plan_id):
    """Soft delete plan (Admin)"""
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Plan deleted successfully'}), 200

# ============================================================================
# PAYMENT MANAGEMENT
# ============================================================================

@app.route('/api/payments/submit', methods=['POST'])
@auth_required()
def submit_payment():
    """Submit payment for approval"""
    data = request.json
    
    # Validate UTR if UPI payment
    if data.get('payment_method') == 'UPI':
        txn_ref = data.get('txn_ref', '').strip()
        if len(txn_ref) != 12 or not txn_ref.isdigit():
            return jsonify({'error': 'UTR must be exactly 12 digits'}), 400
    else:
        txn_ref = None
    
    payment = Payment(
        user_id=current_user.id,
        plan_id=data.get('plan_id'),
        amount=float(data.get('amount')),
        txn_ref=txn_ref,
        payment_method=data.get('payment_method', 'UPI'),
        status='Pending',
        notes=data.get('notes')
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment submitted for approval',
        'payment_id': payment.id
    }), 201
    
@app.route('/api/payments/history', methods=['GET'])
@auth_required()
def payment_history():
    """Get payment history for current user"""
    payments = current_user.payments.order_by(Payment.date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'amount': p.amount,
        'plan': p.plan.name if p.plan else 'N/A',
        'payment_method': p.payment_method,
        'txn_ref': p.txn_ref,
        'status': p.status,
        'date': p.date.isoformat(),
        'notes': p.notes
    } for p in payments]), 200

@app.route('/api/admin/payments/pending', methods=['GET'])
@admin_required
def get_pending_payments():
    """Get all pending payments (Admin)"""
    payments = Payment.query.filter_by(status='Pending').order_by(Payment.date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'user_name': p.user_display_name,
        'user_id': p.user_id,
        'plan': p.plan.name if p.plan else 'N/A',
        'amount': p.amount,
        'txn_ref': p.txn_ref,
        'payment_method': p.payment_method,
        'date': p.date.isoformat(),
        'notes': p.notes
    } for p in payments]), 200

@app.route('/api/admin/payments/<int:payment_id>/approve', methods=['POST'])
@admin_required
def approve_payment(payment_id):
    """Approve payment and create/extend membership (Admin)"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'Pending':
        return jsonify({'error': 'Payment already processed'}), 400
    
    # Get plan
    plan = Plan.query.get(payment.plan_id)
    if not plan:
        return jsonify({'error': 'Invalid plan'}), 400
    
    # Get user's current membership
    current_membership = payment.user.current_membership
    
    # Calculate start and end dates
    if current_membership and current_membership.end_date >= date.today():
        # Extend from current end date
        start_date = current_membership.end_date + timedelta(days=1)
    else:
        # Start from today
        start_date = date.today()
    
    end_date = start_date + timedelta(days=plan.duration_days)
    
    # Mark old memberships as expired
    if current_membership:
        current_membership.status = 'Expired'
    
    # Create new membership
    membership = Membership(
        user_id=payment.user_id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status='Active'
    )
    
    # Update payment status
    payment.status = 'Approved'
    payment.approved_at = datetime.utcnow()
    
    db.session.add(membership)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment approved and membership activated',
        'membership': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    }), 200

@app.route('/api/admin/payments/<int:payment_id>/reject', methods=['POST'])
@admin_required
def reject_payment(payment_id):
    """Reject payment (Admin)"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'Pending':
        return jsonify({'error': 'Payment already processed'}), 400
    
    payment.status = 'Rejected'
    db.session.commit()
    
    return jsonify({'message': 'Payment rejected'}), 200


@app.route('/api/admin/transactions/all', methods=['GET'])
@manager_required
def get_all_transactions():
    """Get all transactions with optional date filters (Admin/Manager)"""
    # Get query parameters
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    query = Payment.query.filter_by(status='Approved')
    
    # Apply date filters if provided
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Payment.date) >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Payment.date) <= end)
        except ValueError:
            pass
    
    payments = query.order_by(Payment.date.desc()).all()
    
    return jsonify({
        'transactions': [{
            'id': p.id,
            'user_name': p.user_display_name,
            'user_email': p.user.email,
            'user_phone': p.user.phone,
            'plan': p.plan.name if p.plan else 'N/A',
            'amount': p.amount,
            'txn_ref': p.txn_ref,
            'payment_method': p.payment_method,
            'status': p.status,
            'date': p.date.isoformat(),
            'approved_at': p.approved_at.isoformat() if p.approved_at else None,
            'notes': p.notes
        } for p in payments],
        'count': len(payments)
    }), 200
    
    
@app.route('/api/admin/transactions', methods=['GET'])
@admin_required
def get_transactions():
    """Get transactions with filters (Admin)"""
    # Get filter parameters
    filter_type = request.args.get('filter', 'last_7_days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Payment.query.filter(Payment.status.in_(['Approved', 'Pending', 'Rejected']))
    
    # Apply date filters
    today = date.today()
    if filter_type == 'this_month':
        start = date(today.year, today.month, 1)
        query = query.filter(Payment.date >= start)
    elif filter_type == 'last_month':
        first_this_month = date(today.year, today.month, 1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)
        query = query.filter(Payment.date >= last_month_start, Payment.date <= last_month_end)
    elif filter_type == 'custom' and start_date and end_date:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        query = query.filter(Payment.date >= start, Payment.date <= end)
    else:  # last_30_days
        thirty_days_ago = today - timedelta(days=30)
        query = query.filter(Payment.date >= thirty_days_ago)
    
    payments = query.order_by(Payment.date.desc()).all()
    
    total_revenue = sum(p.amount for p in payments)
    
    return jsonify({
        'transactions': [{
            'id': p.id,
            'user_name': p.user_display_name,
            'plan': p.plan.name if p.plan else 'N/A',
            'amount': p.amount,
            'txn_ref': p.txn_ref,
            'payment_method': p.payment_method,
            'date': p.date.isoformat()
        } for p in payments],
        'total_revenue': total_revenue,
        'count': len(payments)
    }), 200

# ============================================================================
# MEMBERSHIP MANAGEMENT (Admin)
# ============================================================================

@app.route('/api/admin/priority-list', methods=['GET'])
@admin_required
def get_priority_list():
    """Get members expiring within 7 days (Admin)"""
    today = date.today()
    seven_days_later = today + timedelta(days=7)
    
    memberships = Membership.query.filter(
        Membership.status.in_(['Active', 'Expiring']),
        Membership.end_date >= today,
        Membership.end_date <= seven_days_later
    ).order_by(Membership.end_date).all()
    
    return jsonify([{
        'id': m.id,
        'user_name': m.user_display_name,
        'user_id': m.user_id,
        'phone': m.user.phone,
        'plan': m.plan.name,
        'end_date': m.end_date.isoformat(),
        'days_remaining': (m.end_date - today).days
    } for m in memberships]), 200

@app.route('/api/admin/expired-members', methods=['GET'])
@admin_required
def get_expired_members():
    """Get all expired members (Admin)"""
    today = date.today()
    
    memberships = Membership.query.filter(
        Membership.end_date < today
    ).order_by(Membership.end_date.desc()).all()
    
    # Get unique users with expired memberships
    expired_users = {}
    for m in memberships:
        if m.user_id not in expired_users:
            expired_users[m.user_id] = {
                'user_id': m.user_id,
                'user_name': m.user_display_name,
                'phone': m.user.phone,
                'last_plan': m.plan.name,
                'expired_on': m.end_date.isoformat(),
                'days_expired': (today - m.end_date).days
            }
    
    return jsonify(list(expired_users.values())), 200

@app.route('/api/admin/memberships/<int:user_id>/renew', methods=['POST'])
@admin_required
def admin_renew_membership(user_id):
    """Manually renew/approve membership (Admin - Digital Gatekeeper)"""
    data = request.json
    user = User.query.get_or_404(user_id)
    plan = Plan.query.get_or_404(data.get('plan_id'))
    
    # Get current membership
    current_membership = user.current_membership
    
    # Calculate dates
    if current_membership and current_membership.end_date >= date.today():
        start_date = current_membership.end_date + timedelta(days=1)
    else:
        start_date = date.today()
    buffer_days = user.days_until_expiry if current_membership else 0
    end_date = start_date + timedelta(days=plan.duration_days+buffer_days)
    
    # Mark old membership as expired
    if current_membership:
        current_membership.status = 'Expired'
    
    # Create new membership
    membership = Membership(
        user_id=user_id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status='Active'
    )
    
    # Create payment record
    payment = Payment(
        user_id=user_id,
        plan_id=plan.id,
        amount=plan.price,
        payment_method='Cash',
        status='Approved',
        approved_at=datetime.utcnow(),
        notes='Admin approved - Cash payment'
    )
    
    db.session.add(membership)
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'message': 'Membership renewed successfully',
        'membership': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    }), 200

# ============================================================================
# BUSINESS PROJECTIONS (Admin)
# ============================================================================

@app.route('/api/admin/projections', methods=['GET'])
@admin_required
def get_business_projections():
    """Calculate business projections (Admin)"""
    today = date.today()
    
    # Next 30 days expiring
    thirty_days_later = today + timedelta(days=30)
    expiring_memberships = Membership.query.filter(
        Membership.status.in_(['Active', 'Expiring']),
        Membership.end_date >= today,
        Membership.end_date <= thirty_days_later
    ).all()
    
    expected_revenue = sum(m.plan.price for m in expiring_memberships)
    
    # Last 30 days actual revenue
    thirty_days_ago = today - timedelta(days=30)
    last_month_payments = Payment.query.filter(
        Payment.status == 'Approved',
        Payment.date >= thirty_days_ago
    ).all()
    
    last_month_revenue = sum(p.amount for p in last_month_payments)
    
    # Calculate quarterly and annual projections
    monthly_avg = last_month_revenue
    
    scenarios = {
        'pessimistic': {
            'growth_rate': -0.05,
            'quarterly': monthly_avg * 3 * 0.95,
            'annual': monthly_avg * 12 * 0.95
        },
        'status_quo': {
            'growth_rate': 0.0,
            'quarterly': monthly_avg * 3,
            'annual': monthly_avg * 12
        },
        'optimistic': {
            'growth_rate': 0.10,
            'quarterly': monthly_avg * 3 * 1.10,
            'annual': monthly_avg * 12 * 1.10
        }
    }
    
    return jsonify({
        'next_month_expected': expected_revenue,
        'expiring_count': len(expiring_memberships),
        'last_month_actual': last_month_revenue,
        'monthly_average': monthly_avg,
        'scenarios': scenarios
    }), 200

# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic system statistics"""
    total_members = User.query.filter(User.roles.any(Role.name == 'member')).count()
    active_memberships = Membership.query.filter_by(status='Active').count()
    total_plans = Plan.query.filter_by(is_active=True).count()
    
    return jsonify({
        'total_members': total_members,
        'active_memberships': active_memberships,
        'total_plans': total_plans
    }), 200

# Background task to update membership statuses
@app.cli.command('update-statuses')
def update_membership_statuses():
    """CLI command to update all membership statuses"""
    memberships = Membership.query.all()
    for membership in memberships:
        membership.update_status()
    db.session.commit()
    print(f"Updated {len(memberships)} membership statuses")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
