from functools import wraps
from flask import jsonify
from flask_security import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        roles = {r.name for r in current_user.roles}
        if not (roles & {"admin", "super_admin"}):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


def member_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        roles = {r.name for r in current_user.roles}
        if "member" not in roles and not (roles & {"admin", "super_admin"}):
            return jsonify({"error": "Member access required"}), 403
        return f(*args, **kwargs)
    return decorated