from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_security import login_required, current_user
from extensions import db
from models import Subscription, Transaction, Member
from .auth_utils import admin_required

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/pending", methods=["GET"])
@login_required
@admin_required
def list_pending():
    """All subscriptions awaiting admin approval."""
    subs = (
        Subscription.query
        .filter_by(status="pending")
        .order_by(Subscription.created_at.asc())
        .all()
    )
    result = []
    for s in subs:
        d = s.to_dict()
        m = Member.query.get(s.member_id)
        d["member_name"] = m.name if m else "Unknown"
        d["member_username"] = m.user.username if m else ""
        result.append(d)
    return jsonify(result)


@payment_bp.route("/approve/<int:sub_id>", methods=["POST"])
@login_required
@admin_required
def approve_payment(sub_id):
    """
    Admin approves a pending subscription.
    - Sets subscription status → active
    - Sets start_date and end_date
      * If member has an active unexpired subscription, extend from its end_date
      * Otherwise start from today
    - Marks transaction → completed
    """
    sub = Subscription.query.get_or_404(sub_id)
    if sub.status != "pending":
        return jsonify({"error": f"Subscription is already '{sub.status}'"}), 409

    data  = request.get_json(silent=True) or {}
    notes = data.get("notes", "")

    # Determine start date
    m = Member.query.get(sub.member_id)
    active_sub = m.active_subscription if m else None
    if active_sub and active_sub.end_date and active_sub.end_date >= date.today():
        start = active_sub.end_date + timedelta(days=1)   # stack on top of current
    else:
        start = date.today()

    end = start + timedelta(days=sub.duration_days - 1)

    from models import now_ist
    sub.status      = "active"
    sub.start_date  = start
    sub.end_date    = end
    sub.approved_at = now_ist()
    sub.approved_by = current_user.id
    if notes:
        sub.notes = notes

    # Update linked transaction
    if sub.transaction:
        sub.transaction.status      = "completed"
        sub.transaction.recorded_by = current_user.id

    db.session.commit()
    return jsonify({
        "message": f"Subscription approved. Active {start} → {end}.",
        "subscription": sub.to_dict(),
    })


@payment_bp.route("/reject/<int:sub_id>", methods=["POST"])
@login_required
@admin_required
def reject_payment(sub_id):
    """Admin rejects a pending subscription."""
    sub = Subscription.query.get_or_404(sub_id)
    if sub.status != "pending":
        return jsonify({"error": f"Subscription is already '{sub.status}'"}), 409

    data  = request.get_json(silent=True) or {}
    notes = data.get("notes", "Payment rejected by admin")

    sub.status = "rejected"
    sub.notes  = notes
    if sub.transaction:
        sub.transaction.status = "refunded"

    db.session.commit()
    return jsonify({"message": "Subscription rejected", "subscription": sub.to_dict()})


@payment_bp.route("/history", methods=["GET"])
@login_required
@admin_required
def payment_history():
    """All transactions for admin view with optional filters."""
    status  = request.args.get("status")
    page    = int(request.args.get("page", 1))
    per     = int(request.args.get("per_page", 20))

    q = Transaction.query.order_by(Transaction.transaction_date.desc())
    if status:
        q = q.filter_by(status=status)

    paginated = q.paginate(page=page, per_page=per, error_out=False)
    result = []
    for t in paginated.items:
        d = t.to_dict()
        m = Member.query.get(t.member_id)
        d["member_name"]     = m.name if m else "Unknown"
        d["member_username"] = m.user.username if m else ""
        result.append(d)

    return jsonify({
        "transactions": result,
        "total":  paginated.total,
        "pages":  paginated.pages,
        "page":   page,
    })


@payment_bp.route("/member/<int:member_id>", methods=["GET"])
@login_required
@admin_required
def member_payment_history(member_id):
    """Transaction history for a specific member."""
    txns = (
        Transaction.query
        .filter_by(member_id=member_id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )
    return jsonify([t.to_dict() for t in txns])


@payment_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def payment_stats():
    """Quick financial summary for admin dashboard."""
    from sqlalchemy import func
    from models import now_ist
    from datetime import datetime

    today     = date.today()
    month_start = today.replace(day=1)

    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status="completed").scalar() or 0
    month_revenue = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.status == "completed",
            Transaction.transaction_date >= datetime.combine(month_start, datetime.min.time()),
        )
        .scalar() or 0
    )
    pending_count  = Subscription.query.filter_by(status="pending").count()
    active_count   = (
        Subscription.query
        .filter_by(status="active")
        .filter(Subscription.end_date >= today)
        .count()
    )

    return jsonify({
        "total_revenue":   round(total_revenue, 2),
        "month_revenue":   round(month_revenue, 2),
        "pending_approvals": pending_count,
        "active_subscriptions": active_count,
    })