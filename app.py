from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---- Register Blueprints ----
    from routes.pages import pages_bp
    from routes.items import items_bp
    from routes.bills import bills_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(bills_bp)

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
