from flask import Blueprint, render_template
from flask_security import auth_required
from models import Bill, BillItem

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/ping")
def ping():
    return "pong"

@pages_bp.route("/billing")
@auth_required()
def index():
    return render_template("index.html")

@pages_bp.route("/catalog")
@auth_required()
def catalog():
    return render_template("catalog.html")

@pages_bp.route("/bills")
@auth_required()
def bills_page():
    bills = (
        Bill.query
        .order_by(Bill.timestamp.desc())
        .all()
    )
    return render_template("bills.html", bills=bills)

@pages_bp.route("/bills/<int:bill_id>")
@auth_required()
def bill_detail_page(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill.id).all()

    return render_template(
        "bill_detail.html",
        bill=bill,
        items=items
    )

@pages_bp.route("/bills/edit/<int:bill_id>")
@auth_required()
def update_bill_page(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill.id).all()

    items_data = [
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

    return render_template(
        "update_bill.html",
        bill=bill,
        items=items,
        items_json=items_data
    )