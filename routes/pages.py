from flask import Blueprint, render_template
from models import Bill, BillItem

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/ping")
def ping():
    return "pong"

@pages_bp.route("/billing")
def index():
    return render_template("index.html")

@pages_bp.route("/catalog")
def catalog():
    return render_template("catalog.html")

# ✅ FIXED: Bill History Page
@pages_bp.route("/bills")
def bills_page():
    bills = (
        Bill.query
        .order_by(Bill.timestamp.desc())
        .all()
    )
    return render_template("bills.html", bills=bills)

# ✅ FIXED: Bill Detail Page
@pages_bp.route("/bills/<int:bill_id>")
def bill_detail_page(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill.id).all()

    return render_template(
        "bill_detail.html",
        bill=bill,
        items=items
    )
