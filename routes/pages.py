from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/ping")
def ping():
    return "pong"

@pages_bp.route("/")
def index():
    return render_template("index.html")

@pages_bp.route("/catalog")
def catalog():
    return render_template("catalog.html")
