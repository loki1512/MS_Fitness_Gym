import uuid
from datetime import date
from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user, hash_password
from extensions import db
from models import User, Role, Member, Subscription, Transaction, Attendance, Plan

member_bp = Blueprint("member", __name__)


# ── Registration ──────────────────────────────────────────────────────────────

@member_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip() or None
    password = data.get("password", "")
    phone    = data.get("phone", "").strip()

    if not all([username, password, phone]):
        return jsonify({"error": "username, password and phone are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        username=username,
        email=email,
        password=hash_password(password),
        phone=phone,
        fs_uniquifier=uuid.uuid4().hex,
    )
    db.session.add(user)
    db.session.flush()   # get user.id before commit

    member_role = Role.query.filter_by(name="member").first()
    if member_role:
        user.roles.append(member_role)

    member = Member(
        user_id=user.id,
        name=data.get("name", username),
        profession=data.get("profession") or None,
        height_cm=data.get("height_cm") or None,
        weight_kg=data.get("weight_kg") or None,
        dob=_parse_date(data.get("dob")),
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Registration successful", "user_id": user.id}), 201


def _parse_date(val):
    if not val:
        return None
    try:
        return date.fromisoformat(val)
    except Exception:
        return None


# ── Profile ───────────────────────────────────────────────────────────────────

@member_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    m = Member.query.get(current_user.id)
    if not m:
        return jsonify({"error": "Member profile not found"}), 404
    sub = m.active_subscription
    pending = m.pending_subscription
    return jsonify({
        "user_id":       m.user_id,
        "name":          m.name,
        "username":      current_user.username,
        "email":         current_user.email,
        "phone":         current_user.phone,
        "profession":    m.profession,
        "height_cm":     m.height_cm,
        "weight_kg":     m.weight_kg,
        "dob":           m.dob.isoformat() if m.dob else None,
        "join_date":     m.join_date.isoformat() if m.join_date else None,
        "streak":        m.streak,
        "active_subscription": sub.to_dict() if sub else None,
        "pending_subscription": pending.to_dict() if pending else None,
    })


@member_bp.route("/profile", methods=["PATCH"])
@login_required
def update_profile():
    data = request.get_json(silent=True) or {}
    m = Member.query.get(current_user.id)
    if not m:
        return jsonify({"error": "Member profile not found"}), 404

    for field in ["name", "profession"]:
        if field in data:
            setattr(m, field, data[field])
    for field in ["height_cm", "weight_kg"]:
        if field in data:
            setattr(m, field, float(data[field]) if data[field] else None)
    if "dob" in data:
        m.dob = _parse_date(data["dob"])
    if "phone" in data and data["phone"]:
        current_user.phone = data["phone"]
    if "email" in data:
        current_user.email = data["email"] or None

    db.session.commit()
    return jsonify({"message": "Profile updated"})


# ── Subscription ──────────────────────────────────────────────────────────────

@member_bp.route("/subscriptions", methods=["GET"])
@login_required
def get_subscriptions():
    m = Member.query.get(current_user.id)
    if not m:
        return jsonify({"error": "Member not found"}), 404
    subs = (
        Subscription.query
        .filter_by(member_id=current_user.id)
        .order_by(Subscription.created_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in subs])


@member_bp.route("/subscription/request", methods=["POST"])
@login_required
def request_subscription():
    """Member selects a plan and initialises a payment request (status=pending)."""
    data = request.get_json(silent=True) or {}
    plan_id      = data.get("plan_id")
    payment_mode = data.get("payment_mode", "cash")

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    plan = Plan.query.get(plan_id)
    if not plan or not plan.is_active:
        return jsonify({"error": "Plan not found or inactive"}), 404

    m = Member.query.get(current_user.id)
    if not m:
        return jsonify({"error": "Member profile not found"}), 404

    # Block duplicate pending requests
    if m.pending_subscription:
        return jsonify({"error": "You already have a pending payment request. Wait for admin approval."}), 409

    sub = Subscription(
        member_id=current_user.id,
        plan_id=plan.id,
        plan_name=plan.name,
        duration_days=plan.duration_days,
        amount=plan.price,
        status="pending",
        payment_mode=payment_mode,
        notes=data.get("notes"),
    )
    db.session.add(sub)
    db.session.flush()

    txn = Transaction(
        member_id=current_user.id,
        subscription_id=sub.id,
        amount=plan.price,
        mode=payment_mode,
        status="pending",
        description=f"Payment for {plan.name} plan",
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Payment request submitted. Waiting for admin approval.",
        "subscription": sub.to_dict(),
    }), 201


@member_bp.route("/subscription/cancel-pending", methods=["POST"])
@login_required
def cancel_pending():
    """Member cancels their own pending request before admin acts."""
    m = Member.query.get(current_user.id)
    if not m:
        return jsonify({"error": "Member not found"}), 404
    pending = m.pending_subscription
    if not pending:
        return jsonify({"error": "No pending subscription found"}), 404
    pending.status = "rejected"
    if pending.transaction:
        pending.transaction.status = "refunded"
    db.session.commit()
    return jsonify({"message": "Pending request cancelled"})


# ── Attendance ────────────────────────────────────────────────────────────────

@member_bp.route("/attendance/checkin", methods=["POST"])
@login_required
def check_in():
    from models import now_ist
    existing = (
        Attendance.query
        .filter_by(member_id=current_user.id, check_out_time=None)
        .first()
    )
    if existing:
        return jsonify({"error": "Already checked in"}), 409
    att = Attendance(member_id=current_user.id)
    db.session.add(att)
    db.session.commit()
    return jsonify({"message": "Checked in", "attendance": att.to_dict()}), 201


@member_bp.route("/attendance/checkout", methods=["POST"])
@login_required
def check_out():
    from models import now_ist
    att = (
        Attendance.query
        .filter_by(member_id=current_user.id, check_out_time=None)
        .first()
    )
    if not att:
        return jsonify({"error": "No active check-in found"}), 404
    att.check_out_time = now_ist()
    # Update streak
    m = Member.query.get(current_user.id)
    if m:
        last = (
            Attendance.query
            .filter(
                Attendance.member_id == current_user.id,
                Attendance.check_out_time.isnot(None),
                Attendance.id != att.id,
            )
            .order_by(Attendance.check_in_time.desc())
            .first()
        )
        if last and last.check_in_time:
            delta = (att.check_in_time.date() - last.check_in_time.date()).days
            m.streak = m.streak + 1 if delta == 1 else 1
        else:
            m.streak = 1
    db.session.commit()
    return jsonify({"message": "Checked out", "attendance": att.to_dict()})


@member_bp.route("/attendance/history", methods=["GET"])
@login_required
def attendance_history():
    records = (
        Attendance.query
        .filter_by(member_id=current_user.id)
        .order_by(Attendance.check_in_time.desc())
        .limit(30)
        .all()
    )
    return jsonify([r.to_dict() for r in records])


# ── Plans (public listing) ────────────────────────────────────────────────────

@member_bp.route("/plans", methods=["GET"])
@login_required
def list_plans():
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.price).all()
    return jsonify([p.to_dict() for p in plans])


# ── Password management ───────────────────────────────────────────────────────

@member_bp.route("/profile/update_password", methods=["POST"])
@login_required
def update_password():
    """Change password — requires current password for verification."""
    import bcrypt
    data             = request.get_json(silent=True) or {}
    current_password = data.get("current_password", "")
    new_password     = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({"error": "Current and new passwords are required"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters"}), 400

    if len(new_password.encode()) > 72:
        return jsonify({"error": "Password must be 72 characters or fewer"}), 400

    try:
        match = bcrypt.checkpw(
            current_password.encode("utf-8"),
            current_user.password.encode("utf-8"),
        )
    except Exception:
        match = False

    if not match:
        return jsonify({"error": "Current password is incorrect"}), 401

    current_user.password = hash_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated successfully"})