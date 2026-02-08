from flask import Blueprint, render_template, request
from datetime import datetime, date, timedelta
from calendar import monthrange
from sqlalchemy import func
from models import Bill, BillItem
from extensions import db
from sqlalchemy import distinct, and_

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def daily_dashboard():
    date_param = request.args.get("date")
    if date_param:
        today = datetime.strptime(date_param, "%Y-%m-%d").date()
    else:
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
        selected_date=today.isoformat(),
        today_iso=date.today().isoformat(),
    )


# ---- Helper: period dashboard data ----
def _period_dashboard_data(start_date, end_date):
    date_filter = and_(
        func.date(Bill.timestamp) >= start_date,
        func.date(Bill.timestamp) <= end_date,
    )

    # KPIs
    total_sales = db.session.query(func.sum(Bill.final_amount))\
        .filter(date_filter).scalar() or 0
    total_bills = db.session.query(func.count(Bill.id))\
        .filter(date_filter).scalar() or 0
    avg_bill = round(total_sales / total_bills, 2) if total_bills else 0
    total_units = db.session.query(func.sum(BillItem.qty))\
        .join(Bill, Bill.id == BillItem.bill_id)\
        .filter(date_filter).scalar() or 0

    # Top 10 customers by number of bills
    top_customers_by_count = db.session.query(
        Bill.customer_name,
        Bill.customer_phone,
        func.count(Bill.id).label("bill_count"),
        func.sum(Bill.final_amount).label("total_spent"),
    ).filter(date_filter)\
     .group_by(Bill.customer_phone)\
     .order_by(func.count(Bill.id).desc())\
     .limit(10).all()

    # Top 10 customers by revenue
    top_customers_by_revenue = db.session.query(
        Bill.customer_name,
        Bill.customer_phone,
        func.count(Bill.id).label("bill_count"),
        func.sum(Bill.final_amount).label("total_spent"),
    ).filter(date_filter)\
     .group_by(Bill.customer_phone)\
     .order_by(func.sum(Bill.final_amount).desc())\
     .limit(10).all()

    # Top 10 products by quantity
    top_products_by_qty = db.session.query(
        BillItem.item_name,
        func.sum(BillItem.qty).label("qty"),
        func.sum(BillItem.final_item_amount).label("revenue"),
    ).join(Bill)\
     .filter(date_filter)\
     .group_by(BillItem.item_name)\
     .order_by(func.sum(BillItem.qty).desc())\
     .limit(10).all()

    # Top 10 products by revenue
    top_products_by_revenue = db.session.query(
        BillItem.item_name,
        func.sum(BillItem.qty).label("qty"),
        func.sum(BillItem.final_item_amount).label("revenue"),
    ).join(Bill)\
     .filter(date_filter)\
     .group_by(BillItem.item_name)\
     .order_by(func.sum(BillItem.final_item_amount).desc())\
     .limit(10).all()

    # Day-wise sales for line chart
    daily_sales = db.session.query(
        func.date(Bill.timestamp).label("day"),
        func.sum(Bill.final_amount).label("sales"),
    ).filter(date_filter)\
     .group_by(func.date(Bill.timestamp))\
     .order_by(func.date(Bill.timestamp)).all()

    days = [str(d.day) for d in daily_sales]
    day_sales = [float(d.sales) for d in daily_sales]

    return dict(
        total_sales=round(total_sales, 2),
        total_bills=total_bills,
        avg_bill=avg_bill,
        total_units=total_units,
        top_customers_by_count=top_customers_by_count,
        top_customers_by_revenue=top_customers_by_revenue,
        top_products_by_qty=top_products_by_qty,
        top_products_by_revenue=top_products_by_revenue,
        days=days,
        day_sales=day_sales,
    )


@dashboard_bp.route("/dashboard/monthly")
def monthly_dashboard():
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    data = _period_dashboard_data(start_date, end_date)
    label = start_date.strftime("%B %Y")

    # Previous / Next month
    prev_month = (start_date - timedelta(days=1))
    next_month = end_date + timedelta(days=1)

    return render_template(
        "period_dashboard.html",
        period="monthly",
        period_label=label,
        prev_url=f"/dashboard/monthly?year={prev_month.year}&month={prev_month.month}",
        next_url=f"/dashboard/monthly?year={next_month.year}&month={next_month.month}",
        **data,
    )


@dashboard_bp.route("/dashboard/quarterly")
def quarterly_dashboard():
    year = request.args.get("year", date.today().year, type=int)
    quarter = request.args.get("quarter", (date.today().month - 1) // 3 + 1, type=int)
    start_month = (quarter - 1) * 3 + 1
    start_date = date(year, start_month, 1)
    end_month = start_month + 2
    end_date = date(year, end_month, monthrange(year, end_month)[1])

    data = _period_dashboard_data(start_date, end_date)
    label = f"Q{quarter} {year}"

    # Previous / Next quarter
    prev_q = quarter - 1
    prev_year = year
    if prev_q < 1:
        prev_q = 4
        prev_year = year - 1
    next_q = quarter + 1
    next_year = year
    if next_q > 4:
        next_q = 1
        next_year = year + 1

    return render_template(
        "period_dashboard.html",
        period="quarterly",
        period_label=label,
        prev_url=f"/dashboard/quarterly?year={prev_year}&quarter={prev_q}",
        next_url=f"/dashboard/quarterly?year={next_year}&quarter={next_q}",
        **data,
    )


@dashboard_bp.route("/dashboard/yearly")
def yearly_dashboard():
    year = request.args.get("year", date.today().year, type=int)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    data = _period_dashboard_data(start_date, end_date)
    label = str(year)

    return render_template(
        "period_dashboard.html",
        period="yearly",
        period_label=label,
        prev_url=f"/dashboard/yearly?year={year - 1}",
        next_url=f"/dashboard/yearly?year={year + 1}",
        **data,
    )
