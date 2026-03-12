import os
from flask import Flask, request, jsonify, redirect, url_for
from extensions import db
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)

    # ── Core config ────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    db_url = os.environ.get("SUPABASE_DB_URL", "sqlite:///db.sqlite3")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 3,
        "max_overflow": 2,
    }

    # ── Flask-Security config ──────────────────────────────────────────────────
    app.config["SECURITY_PASSWORD_HASH"]              = "bcrypt"
    app.config["SECURITY_PASSWORD_SALT"]              = os.environ.get("SECURITY_PASSWORD_SALT", "dev-salt-change-me")
    app.config["SECURITY_LOGIN_URL"]                  = "/login"
    app.config["SECURITY_LOGOUT_URL"]                 = "/logout"
    app.config["SECURITY_POST_LOGIN_VIEW"]             = "/"
    app.config["SECURITY_POST_LOGOUT_VIEW"]            = "/login"
    app.config["SECURITY_REGISTERABLE"]               = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"]        = False
    app.config["SECURITY_SEND_PASSWORD_CHANGE_EMAIL"] = False
    app.config["SECURITY_SEND_PASSWORD_RESET_EMAIL"]  = False
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]= ""
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
    app.config["WTF_CSRF_ENABLED"]                    = False
    app.config["SECURITY_CSRF_PROTECT_MECHANISMS"]    = []

    # ── Extensions ─────────────────────────────────────────────────────────────
    db.init_app(app)
    Migrate(app, db)

    # ── Flask-Security setup ───────────────────────────────────────────────────
    from models import User, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    @security.unauthn_handler
    def unauthorized(mechanisms, headers=None):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Authentication required"}), 401
        return redirect(url_for("security.login"))

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from routes.pages           import pages_bp
    from routes.member_routes   import member_bp
    from routes.admin_routes    import admin_bp
    from routes.payment_routes  import payment_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(member_bp,  url_prefix="/api/member")
    app.register_blueprint(admin_bp,   url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")

    # ── DB init & seeding ──────────────────────────────────────────────────────
    with app.app_context():
        from sqlalchemy import inspect as sa_inspect

        inspector = sa_inspect(db.engine)
        if not inspector.get_table_names():
            print("No tables found — initialising database...")
            db.create_all()
        else:
            print("Database already initialised — skipping create_all()")

        roles_def = {
            "member":      "Basic member access",
            "lead":        "Team lead",
            "admin":       "Administrator",
            "super_admin": "Super administrator",
        }
        for role_name, description in roles_def.items():
            user_datastore.find_or_create_role(name=role_name, description=description)

        if not user_datastore.find_user(email="admin@msfitness.com"):
            admin_role = user_datastore.find_or_create_role(name="admin", description="Administrator")
            user_datastore.create_user(
                email="admin@msfitness.com",
                password=hash_password("admin@123"),
                roles=[admin_role],
                username="admin",
                phone="0000000000",
            )

        # Seed sample plans if none exist
        from models import Plan
        if Plan.query.count() == 0:
            plans = [
                Plan(name="Monthly",   duration_days=30,  price=999.0,  description="Full gym access for 1 month"),
                Plan(name="Quarterly", duration_days=90,  price=2499.0, description="Full gym access for 3 months"),
                Plan(name="Half Year", duration_days=180, price=4499.0, description="Full gym access for 6 months"),
                Plan(name="Annual",    duration_days=365, price=7999.0, description="Full gym access for 1 year"),
            ]
            db.session.add_all(plans)

        db.session.commit()

        if db_url.startswith("postgresql"):
            _auto_migrate_sqlite_to_pg(app)

    return app


def _auto_migrate_sqlite_to_pg(app):
    import sqlite3
    from sqlalchemy import text

    sqlite_path = os.path.join(app.instance_path, "db.sqlite3")
    if not os.path.exists(sqlite_path):
        return

    try:
        with db.engine.connect() as conn:
            pg_user_count = conn.execute(text('SELECT COUNT(*) FROM "user"')).scalar()
        if pg_user_count and pg_user_count > 0:
            app.logger.info("PostgreSQL already has data — skipping migration.")
            return
    except Exception as exc:
        app.logger.warning(f"Could not check PG user count: {exc}")
        return

    try:
        src = sqlite3.connect(sqlite_path)
        src.row_factory = sqlite3.Row
        sqlite_user_count = src.execute("SELECT COUNT(*) FROM user").fetchone()[0]
        if sqlite_user_count == 0:
            src.close()
            return
    except Exception as exc:
        app.logger.warning(f"Could not read SQLite source: {exc}")
        return

    tables = ["role","user","roles_users","admin","member","lead",
              "plan","subscription","attendance","transaction"]

    app.logger.info(f"Auto-migrating {sqlite_user_count} users SQLite → PostgreSQL...")
    for table in tables:
        try:
            rows = src.execute(f"SELECT * FROM [{table}]").fetchall()
        except Exception:
            continue
        if not rows:
            continue
        col_names   = list(rows[0].keys())
        placeholders= ", ".join(f":{c}" for c in col_names)
        col_list    = ", ".join(f'"{c}"' for c in col_names)
        insert_sql  = text(f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING')
        try:
            with db.engine.begin() as conn:
                for row in rows:
                    conn.execute(insert_sql, dict(row))
            app.logger.info(f"  ✓ {table}: {len(rows)} rows")
        except Exception as exc:
            app.logger.error(f"  ✗ {table}: {exc}")
    src.close()
    app.logger.info("Migration complete!")


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)