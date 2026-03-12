import uuid
from datetime import datetime, date
from zoneinfo import ZoneInfo
from extensions import db
from flask_security import UserMixin, RoleMixin

IST = ZoneInfo("Asia/Kolkata")

def now_ist():
    return datetime.now(IST)

# ── Auth Models ───────────────────────────────────────────────────────────────

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(255), unique=True, nullable=False)
    email         = db.Column(db.String(255), nullable=True)
    password      = db.Column(db.String(255), nullable=False)
    phone         = db.Column(db.String(20), nullable=False)
    active        = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(
        db.String(64), unique=True, nullable=False,
        default=lambda: uuid.uuid4().hex
    )
    roles = db.relationship(
        "Role", secondary=roles_users,
        backref=db.backref("users", lazy="dynamic")
    )


class Admin(db.Model):
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name        = db.Column(db.String(255), nullable=False)
    designation = db.Column(db.String(255), nullable=False)
    user        = db.relationship("User", backref="admin_profile")


class Member(db.Model):
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name            = db.Column(db.String(255), nullable=False)
    join_date       = db.Column(db.DateTime, default=now_ist)
    streak          = db.Column(db.Integer, default=0)
    height_cm       = db.Column(db.Float, nullable=True)
    weight_kg       = db.Column(db.Float, nullable=True)
    profession      = db.Column(db.String(255), nullable=True)
    dob             = db.Column(db.Date, nullable=True)

    user            = db.relationship("User", backref="member_profile")
    subscriptions   = db.relationship("Subscription", backref="member", lazy="dynamic", foreign_keys="Subscription.member_id")
    transactions    = db.relationship("Transaction", backref="member", lazy="dynamic", foreign_keys="Transaction.member_id")
    attendances     = db.relationship("Attendance", backref="member", lazy="dynamic")

    @property
    def active_subscription(self):
        """Return the current active (approved + not expired) subscription."""
        from sqlalchemy import and_
        return (
            Subscription.query
            .filter(
                Subscription.member_id == self.user_id,
                Subscription.status == "active",
                Subscription.end_date >= date.today(),
            )
            .order_by(Subscription.end_date.desc())
            .first()
        )

    @property
    def pending_subscription(self):
        """Return subscription awaiting admin approval."""
        return (
            Subscription.query
            .filter_by(member_id=self.user_id, status="pending")
            .order_by(Subscription.created_at.desc())
            .first()
        )


class Lead(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name    = db.Column(db.String(255), nullable=False)
    user    = db.relationship("User", backref="lead_profile")


# ── Business Models ────────────────────────────────────────────────────────────

class Plan(db.Model):
    """Reusable plan templates defined by admin."""
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(255), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    duration_days = db.Column(db.Integer, nullable=False)
    price         = db.Column(db.Float, nullable=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=now_ist)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration_days": self.duration_days,
            "price": self.price,
            "is_active": self.is_active,
        }


class Subscription(db.Model):
    """
    One subscription record per purchase.
    status: pending → active → expired
            pending → rejected
    """
    id           = db.Column(db.Integer, primary_key=True)
    member_id    = db.Column(db.Integer, db.ForeignKey("member.user_id"), nullable=False)
    plan_id      = db.Column(db.Integer, db.ForeignKey("plan.id"), nullable=False)

    # Snapshot of plan at purchase time
    plan_name    = db.Column(db.String(255), nullable=False)
    duration_days= db.Column(db.Integer, nullable=False)
    amount       = db.Column(db.Float, nullable=False)

    status       = db.Column(db.String(30), default="pending")   # pending | active | expired | rejected
    payment_mode = db.Column(db.String(50), default="cash")       # cash | upi | card
    start_date   = db.Column(db.Date, nullable=True)              # set on approval
    end_date     = db.Column(db.Date, nullable=True)              # set on approval
    created_at   = db.Column(db.DateTime, default=now_ist)
    approved_at  = db.Column(db.DateTime, nullable=True)
    approved_by  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    notes        = db.Column(db.Text, nullable=True)

    plan         = db.relationship("Plan")
    approver     = db.relationship("User", foreign_keys=[approved_by])

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "duration_days": self.duration_days,
            "amount": self.amount,
            "status": self.status,
            "payment_mode": self.payment_mode,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "notes": self.notes,
        }


class Transaction(db.Model):
    """Financial transaction record — always created alongside a Subscription."""
    id               = db.Column(db.Integer, primary_key=True)
    member_id        = db.Column(db.Integer, db.ForeignKey("member.user_id"), nullable=False)
    subscription_id  = db.Column(db.Integer, db.ForeignKey("subscription.id"), nullable=True)
    amount           = db.Column(db.Float, nullable=False)
    mode             = db.Column(db.String(50), nullable=False)   # cash | upi | card
    status           = db.Column(db.String(30), default="pending") # pending | completed | refunded
    transaction_date = db.Column(db.DateTime, default=now_ist)
    description      = db.Column(db.String(255), nullable=True)
    recorded_by      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    subscription     = db.relationship("Subscription", backref="transaction")
    recorder         = db.relationship("User", foreign_keys=[recorded_by])

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "subscription_id": self.subscription_id,
            "amount": self.amount,
            "mode": self.mode,
            "status": self.status,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "description": self.description,
        }


class Attendance(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    member_id      = db.Column(db.Integer, db.ForeignKey("member.user_id"), nullable=False)
    check_in_time  = db.Column(db.DateTime, default=now_ist)
    check_out_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
        }