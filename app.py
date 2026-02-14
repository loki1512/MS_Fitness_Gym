import os
from flask import Flask, request, jsonify, redirect, url_for
from extensions import db
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Render sets DATABASE_URL; fix postgres:// → postgresql:// for SQLAlchemy
    db_url = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Security config
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT", "dev-salt-change-me")
    app.config["SECURITY_LOGIN_URL"] = "/login"
    app.config["SECURITY_LOGOUT_URL"] = "/logout"
    app.config["SECURITY_POST_LOGIN_VIEW"] = "/"
    app.config["SECURITY_POST_LOGOUT_VIEW"] = "/login"
    app.config["SECURITY_REGISTERABLE"] = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_SEND_PASSWORD_CHANGE_EMAIL"] = False
    app.config["SECURITY_SEND_PASSWORD_RESET_EMAIL"] = False
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = ""
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = []

    db.init_app(app)

    # ---- Flask-Security Setup ----
    from models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Return JSON 401 for API routes, redirect for pages
    @security.unauthn_handler
    def unauthorized(mechanisms, headers=None):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Authentication required"}), 401
        return redirect(url_for("security.login"))

    # ---- Register Blueprints ----
    from routes.pages import pages_bp
    from routes.items import items_bp
    from routes.bills import bills_bp
    from routes.invoice import invoice_bp
    from dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(invoice_bp)

    # ---- Create tables & seed admin ----
    with app.app_context():
        db.create_all()

        # Auto-migrate SQLite → PostgreSQL on first deploy
        if db_url.startswith("postgresql"):
            _auto_migrate_sqlite_to_pg(app)

        if not user_datastore.find_user(email="admin@ksa.com"):
            admin_role = user_datastore.find_or_create_role(name="admin", description="Administrator")
            user_datastore.create_user(email="admin@ksa.com", password=hash_password("admin@123"), roles=[admin_role])
            db.session.commit()
    migrate = Migrate(app, db)
    return app


def _auto_migrate_sqlite_to_pg(app):
    """One-time auto-migration: copies data from SQLite to PostgreSQL if PG is empty and SQLite has data."""
    import sqlite3

    sqlite_path = os.path.join(app.instance_path, "db.sqlite3")
    if not os.path.exists(sqlite_path):
        return

    # Check if PostgreSQL already has data (bills table)
    from models import Bill
    pg_count = Bill.query.count()
    if pg_count > 0:
        return  # Already migrated

    # Check if SQLite has data
    try:
        src = sqlite3.connect(sqlite_path)
        src.row_factory = sqlite3.Row
        sqlite_bills = src.execute("SELECT COUNT(*) FROM bill").fetchone()[0]
        if sqlite_bills == 0:
            src.close()
            return  # Nothing to migrate
    except Exception:
        return

    # Migrate tables in order (respecting foreign keys)
    tables = ["item", "bill", "bill_item"]
    from sqlalchemy import text

    app.logger.info(f"Auto-migrating {sqlite_bills} bills from SQLite to PostgreSQL...")

    for table in tables:
        try:
            rows = src.execute(f"SELECT * FROM {table}").fetchall()
        except Exception:
            continue

        if not rows:
            continue

        col_names = rows[0].keys()
        placeholders = ", ".join(f":{c}" for c in col_names)
        col_list = ", ".join(col_names)
        insert_sql = text(
            f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        )

        for row in rows:
            db.session.execute(insert_sql, dict(row))

        db.session.commit()
        app.logger.info(f"  Migrated {table}: {len(rows)} rows")

    src.close()
    app.logger.info("SQLite → PostgreSQL migration complete!")


app = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
