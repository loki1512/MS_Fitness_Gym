from flask import Blueprint, render_template, redirect, url_for
from flask_security import login_required, current_user

pages_bp = Blueprint("pages", __name__)


def _role(name):
    return any(r.name == name for r in current_user.roles)


@pages_bp.route("/")
@login_required
def index():
    if _role("admin") or _role("super_admin"):
        return redirect(url_for("pages.admin_dashboard"))
    return redirect(url_for("pages.member_dashboard"))


@pages_bp.route("/dashboard")
@login_required
def member_dashboard():
    if _role("admin") or _role("super_admin"):
        return redirect(url_for("pages.admin_dashboard"))
    return render_template("member/dashboard.html")


@pages_bp.route("/admin")
@login_required
def admin_dashboard():
    if not (_role("admin") or _role("super_admin")):
        return redirect(url_for("pages.member_dashboard"))
    return render_template("admin/dashboard.html")


@pages_bp.route("/admin/members")
@login_required
def admin_members():
    if not (_role("admin") or _role("super_admin")):
        return redirect(url_for("pages.member_dashboard"))
    return render_template("admin/members.html")


@pages_bp.route("/admin/payments")
@login_required
def admin_payments():
    if not (_role("admin") or _role("super_admin")):
        return redirect(url_for("pages.member_dashboard"))
    return render_template("admin/payments.html")


@pages_bp.route("/admin/plans")
@login_required
def admin_plans():
    # if not (_role("admin") or _role("super_admin")):
    #     return redirect(url_for("pages.member_dashboard"))
    return render_template("admin/plans.html")


@pages_bp.route("/member/subscription")
@login_required
def member_subscription():
    return render_template("member/subscription.html")


@pages_bp.route("/register")
def register_page():
    return render_template("register.html")