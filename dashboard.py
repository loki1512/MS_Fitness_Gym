from flask import Blueprint, render_template
from flask_security import auth_required
from datetime import datetime, date
from sqlalchemy import func
from models import Bill, BillItem
from extensions import db
from sqlalchemy import distinct, and_

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@auth_required()
def daily_dashboard():
    today = date.today()

    # Total Sales Today
    total_sales = db.session.query(func.sum(Bill.final_amount))\
        .filter(func.date(Bill.timestamp) == today).scalar() or 0

    # Total Bills
    total_bills = db.session.query(func.count(Bill.id))\
        .filter(func.date(Bill.timestamp) == today).scalar() or 0

    # Average Bill Value
    avg_bill = round(total_sales / total_bills, 2) if total_bills else 0

    # Units Sold
    total_units = db.session.query(func.sum(BillItem.qty))\
        .join(Bill, Bill.id == BillItem.bill_id)\
        .filter(func.date(Bill.timestamp) == today).scalar() or 0

    # Hourly Sales
    hourly = db.session.query(
        func.strftime('%H', Bill.timestamp).label("hour"),
        func.sum(Bill.final_amount)
    ).filter(func.date(Bill.timestamp) == today)\
     .group_by("hour").order_by("hour").all()

    hours = [h[0] for h in hourly]
    hour_sales = [float(h[1]) for h in hourly]

    # Top 10 Items Today
    top_items = db.session.query(
        BillItem.item_name,
        func.sum(BillItem.qty).label("qty"),
        func.sum(BillItem.final_item_amount).label("amount")
    ).join(Bill)\
     .filter(func.date(Bill.timestamp) == today)\
     .group_by(BillItem.item_name)\
     .order_by(func.sum(BillItem.final_item_amount).desc())\
     .limit(10).all()


    # Total customers today
    total_customers = db.session.query(func.count(distinct(Bill.customer_phone)))\
        .filter(func.date(Bill.timestamp) == today)\
        .scalar() or 0

    # New vs Repeat (simple logic: first time seen = new)
    subquery = db.session.query(
        Bill.customer_phone,
        func.min(func.date(Bill.timestamp)).label("first_visit")
    ).group_by(Bill.customer_phone).subquery()

    new_customers = db.session.query(func.count())\
        .select_from(subquery)\
        .filter(subquery.c.first_visit == today)\
        .scalar() or 0

    repeat_customers = total_customers - new_customers
    # New customers today (details)
    new_customer_details = db.session.query(
        Bill.customer_name,
        Bill.customer_phone,
        func.sum(Bill.final_amount).label("total_spent")
    ).filter(func.date(Bill.timestamp) == today)\
    .group_by(Bill.customer_phone)\
    .having(func.min(func.date(Bill.timestamp)) == today)\
    .all()

    # Repeat customers today (details)
    repeat_customer_details = db.session.query(
        Bill.customer_name,
        Bill.customer_phone,
        func.sum(Bill.final_amount).label("total_spent")
    ).filter(func.date(Bill.timestamp) == today)\
    .group_by(Bill.customer_phone)\
    .having(func.min(func.date(Bill.timestamp)) < today)\
    .all()

    
    return render_template(
        
        "daily_dashboard.html",
        total_sales=round(total_sales,2),
        total_bills=total_bills,
        avg_bill=avg_bill,
        total_units=total_units,
        hours=hours,
        hour_sales=hour_sales,
        top_items=top_items,
        total_customers=total_customers,
        new_customers=new_customers,
        customer_details=new_customer_details,
    )
