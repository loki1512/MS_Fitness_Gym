from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user, hash_password
from extensions import db
from models import User, Role, Member, Plan, Subscription, Transaction, Attendance
from .auth_utils import admin_required
import uuid

admin_bp = Blueprint("admin", __name__)


# ── Members ───────────────────────────────────────────────────────────────────

@admin_bp.route("/members", methods=["GET"])
@login_required
@admin_required
def list_members():
    search = request.args.get("q", "").strip()
    page   = int(request.args.get("page", 1))
    per    = int(request.args.get("per_page", 20))

    q = Member.query.join(User, Member.user_id == User.id)
    if search:
        q = q.filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                Member.name.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
            )
        )
    paginated = q.order_by(Member.join_date.desc()).paginate(page=page, per_page=per, error_out=False)

    members = []
    for m in paginated.items:
        sub = m.active_subscription
        members.append({
            "user_id":      m.user_id,
            "name":         m.name,
            "username":     m.user.username,
            "phone":        m.user.phone,
            "email":        m.user.email,
            "join_date":    m.join_date.isoformat() if m.join_date else None,
            "streak":       m.streak,
            "active_subscription": sub.to_dict() if sub else None,
            "has_pending":  m.pending_subscription is not None,
        })

    return jsonify({
        "members": members,
        "total":   paginated.total,
        "pages":   paginated.pages,
        "page":    page,
    })


@admin_bp.route("/members/<int:member_id>", methods=["GET"])
@login_required
@admin_required
def get_member(member_id):
    m = Member.query.get_or_404(member_id)
    subs = (
        Subscription.query
        .filter_by(member_id=member_id)
        .order_by(Subscription.created_at.desc())
        .all()
    )
    return jsonify({
        "user_id":       m.user_id,
        "name":          m.name,
        "username":      m.user.username,
        "phone":         m.user.phone,
        "email":         m.user.email,
        "profession":    m.profession,
        "height_cm":     m.height_cm,
        "weight_kg":     m.weight_kg,
        "dob":           m.dob.isoformat() if m.dob else None,
        "join_date":     m.join_date.isoformat() if m.join_date else None,
        "streak":        m.streak,
        "subscriptions": [s.to_dict() for s in subs],
    })



@admin_bp.route("/members/<int:member_id>", methods=["PATCH"])
@login_required
@admin_required
def update_member(member_id):
    m    = Member.query.get_or_404(member_id)
    data = request.get_json(silent=True) or {}
    for field in ["name", "profession"]:
        if field in data:
            setattr(m, field, data[field])
    for field in ["height_cm", "weight_kg"]:
        if field in data:
            setattr(m, field, float(data[field]) if data[field] else None)
    if "phone" in data:
        m.user.phone = data["phone"]
    if "email" in data:
        m.user.email = data["email"] or None
    if "active" in data:
        m.user.active = bool(data["active"])
    db.session.commit()
    return jsonify({"message": "Member updated"})


@admin_bp.route("/members", methods=["POST"])
@login_required
@admin_required
def create_member():
    """Admin manually creates a member account."""
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    phone    = data.get("phone", "").strip()
    password = data.get("password", "ms@123")
    email  = data.get("email")

    
    if not email:
        email = f"{username}@msfitness.com"
    
    email = email.strip()
    if not all([username, phone]):
        return jsonify({"error": "username and phone are required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(
        username=username,
        email=data.get("email") or None,
        password=hash_password(password),
        phone=phone,
        fs_uniquifier=uuid.uuid4().hex,
    )
    db.session.add(user)
    db.session.flush()

    member_role = Role.query.filter_by(name="member").first()
    if member_role:
        user.roles.append(member_role)

    member = Member(
        user_id=user.id,
        name=data.get("name", username),
        profession=data.get("profession") or None,
        height_cm=data.get("height_cm") or None,
        weight_kg=data.get("weight_kg") or None,
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Member created", "user_id": user.id}), 201


# ── Plans ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/plans", methods=["GET"])
@login_required
@admin_required
def list_plans():
    plans = Plan.query.order_by(Plan.price).all()
    return jsonify([p.to_dict() for p in plans])


@admin_bp.route("/plans", methods=["POST"])
@login_required
@admin_required
def create_plan():
    data = request.get_json(silent=True) or {}
    name          = data.get("name", "").strip()
    duration_days = data.get("duration_days")
    price         = data.get("price")

    if not all([name, duration_days, price]):
        return jsonify({"error": "name, duration_days and price are required"}), 400

    plan = Plan(
        name=name,
        description=data.get("description"),
        duration_days=int(duration_days),
        price=float(price),
        is_active=data.get("is_active", True),
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@admin_bp.route("/plans/<int:plan_id>", methods=["PATCH"])
@login_required
@admin_required
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}
    for field in ["name", "description"]:
        if field in data:
            setattr(plan, field, data[field])
    if "duration_days" in data:
        plan.duration_days = int(data["duration_days"])
    if "price" in data:
        plan.price = float(data["price"])
    if "is_active" in data:
        plan.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(plan.to_dict())


@admin_bp.route("/plans/<int:plan_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = False   # soft delete
    db.session.commit()
    return jsonify({"message": "Plan deactivated"})


# ── Dashboard stats ────────────────────────────────────────────────────────────

@admin_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def dashboard_stats():
    from sqlalchemy import func
    from datetime import date, datetime

    today = date.today()
    month_start = today.replace(day=1)

    total_members = Member.query.count()
    active_subs   = (
        Subscription.query
        .filter_by(status="active")
        .filter(Subscription.end_date >= today)
        .count()
    )
    pending_approvals = Subscription.query.filter_by(status="pending").count()
    total_revenue = (
        db.session.query(func.sum(Transaction.amount))
        .filter_by(status="completed")
        .scalar() or 0
    )
    month_revenue = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.status == "completed",
            Transaction.transaction_date >= datetime.combine(month_start, datetime.min.time()),
        )
        .scalar() or 0
    )
    # Expiring within 7 days
    from datetime import timedelta
    expiring_soon = (
        Subscription.query
        .filter_by(status="active")
        .filter(
            Subscription.end_date >= today,
            Subscription.end_date <= today + timedelta(days=7),
        )
        .count()
    )

    return jsonify({
        "total_members":      total_members,
        "active_subscriptions": active_subs,
        "pending_approvals":  pending_approvals,
        "total_revenue":      round(float(total_revenue), 2),
        "month_revenue":      round(float(month_revenue), 2),
        "expiring_soon":      expiring_soon,
    })

@admin_bp.route("/api/admin/members/<int:id>/reset_password", methods=["POST"])
@login_required
@admin_required
def reset_password(id):
    member = Member.query.get_or_404(id)
    new_password = "member@ms4u"
    member.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"new_password": new_password})



