from flask import Blueprint, request, jsonify
from extensions import db
from models import Bill, BillItem
from datetime import datetime

bills_bp = Blueprint("bills", __name__)

@bills_bp.route("/api/bills", methods=["POST"])
def save_bill():
    data = request.get_json(force=True)

    bill_discount = data.get("billDiscount") or {}
    customer = data.get("customer") or {}

    bill = Bill(
        subtotal=data["subtotal"],
        final_amount=data["finalTotal"],
        bill_discount_type=bill_discount.get("type"),
        bill_discount_value=bill_discount.get("value"),

        customer_name=data["customer_name"],
        customer_phone=data["customer_phone"],
        customer_address=data["customer_address"],

        timestamp=datetime.utcnow()
    )

    db.session.add(bill)
    db.session.flush()

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
