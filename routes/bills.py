from flask import Blueprint, request, jsonify
from extensions import db
from models import Bill, BillItem
from datetime import datetime

bills_bp = Blueprint("bills", __name__)

# -----------------------------
# CREATE BILL (EXISTING - UNCHANGED)
# -----------------------------
@bills_bp.route("/api/bills", methods=["POST"])
def save_bill():
    data = request.get_json(force=True)

    bill_discount = data.get("billDiscount") or {}

    bill = Bill(
        subtotal=data["subtotal"],
        final_amount=data["finalTotal"],
        bill_discount_type=bill_discount.get("type"),
        bill_discount_value=bill_discount.get("value"),

        customer_name=data.get("customer_name"),
        customer_phone=data.get("customer_phone"),
        customer_address=data.get("customer_address"),

        timestamp=datetime.utcnow()
    )

    db.session.add(bill)
    db.session.flush()  # get bill.id before commit

    for it in data["items"]:
        discount = it.get("discount") or {}

        db.session.add(
            BillItem(
                bill_id=bill.id,
                item_name=it["name"],
                qty=it["qty"],
                unit_price=it["rate"],
                item_discount_type=discount.get("type"),
                item_discount_value=discount.get("value"),
                final_item_amount=it["lineTotal"]
            )
        )

    db.session.commit()

    return jsonify({
        "bill_id": bill.id,
        "timestamp": bill.timestamp.isoformat()
    })


# -----------------------------
# LIST BILLS (NEW)
# -----------------------------
@bills_bp.route("/api/bills", methods=["GET"])
def list_bills():
    bills = (
        Bill.query
        .order_by(Bill.timestamp.desc())
        .all()
    )

    return jsonify([
        {
            "id": bill.id,
            "timestamp": bill.timestamp.isoformat(),
            "final_amount": bill.final_amount,
            "customer_name": bill.customer_name
        }
        for bill in bills
    ])


# -----------------------------
# BILL DETAILS (NEW)
# -----------------------------
@bills_bp.route("/api/bills/<int:bill_id>", methods=["GET"])
def get_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)

    items = (
        BillItem.query
        .filter_by(bill_id=bill.id)
        .all()
    )

    return jsonify({
        "id": bill.id,
        "timestamp": bill.timestamp.isoformat(),

        "subtotal": bill.subtotal,
        "bill_discount_type": bill.bill_discount_type,
        "bill_discount_value": bill.bill_discount_value,
        "final_amount": bill.final_amount,

        "customer": {
            "name": bill.customer_name,
            "phone": bill.customer_phone,
            "address": bill.customer_address
        },

        "items": [
            {
                "item_name": i.item_name,
                "qty": i.qty,
                "unit_price": i.unit_price,
                "item_discount_type": i.item_discount_type,
                "item_discount_value": i.item_discount_value,
                "final_item_amount": i.final_item_amount
            }
            for i in items
        ]
    })
