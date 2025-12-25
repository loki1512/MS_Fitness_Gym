from flask import Blueprint, request, jsonify
from extensions import db
from models import Item
from sqlalchemy import func
import pandas as pd

items_bp = Blueprint("items", __name__)

@items_bp.route("/api/items/search")
def search_items():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    items = (
        Item.query
        .filter(Item.name.ilike(f"%{q}%"))
        .limit(5)
        .all()
    )

    return jsonify([
        {"id": i.id, "name": i.name, "price": i.default_price}
        for i in items
    ])


@items_bp.route("/api/items", methods=["GET"])
def get_items():
    items = Item.query.order_by(Item.name).all()
    return jsonify([
        {"id": i.id, "name": i.name, "default_price": i.default_price}
        for i in items
    ])


@items_bp.route("/api/items", methods=["POST"])
def add_item():
    data = request.json
    name = data.get("name", "").strip()
    price = data.get("price")

    if not name or not isinstance(price, (int, float)):
        return {"error": "Invalid input"}, 400

    if Item.query.filter_by(name=name).first():
        return {"error": "Item already exists"}, 400

    item = Item(name=name, default_price=price)
    db.session.add(item)
    db.session.commit()

    return {"id": item.id}


@items_bp.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.json

    name = data.get("name", "").strip()
    price = data.get("price")

    if not name or not isinstance(price, (int, float)):
        return {"error": "Invalid input"}, 400

    item.name = name
    item.default_price = price
    db.session.commit()

    return {"success": True}


@items_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return {"success": True}


@items_bp.route("/api/items/import", methods=["POST"])
def import_items():
    file = request.files.get("file")
    if not file:
        return {"error": "No file uploaded"}, 400

    df = pd.read_excel(file)
    added = updated = skipped = 0

    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        price = row.get("price")

        if not name or not isinstance(price, (int, float)):
            skipped += 1
            continue

        item = Item.query.filter(
            func.lower(Item.name) == name.lower()
        ).first()

        if item:
            item.default_price = price
            updated += 1
        else:
            db.session.add(Item(name=name, default_price=price))
            added += 1

    db.session.commit()

    return {"added": added, "updated": updated, "skipped": skipped}
