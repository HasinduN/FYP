from flask import Blueprint, jsonify, request
from sqlalchemy import func, and_
from models import session as db_session, MenuItem, Order, OrderItem
from datetime import datetime

sales_bp = Blueprint("sales", __name__)

@sales_bp.route('/sales-report', methods=['GET'])
def get_sales_report():
    try:
        # Get date range from query parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            # Default to today if no range is provided
            today = datetime.today().date()
            start_date = end_date = today

        # Filtered query range condition
        date_range_filter = and_(
            func.date(Order.timestamp) >= start_date,
            func.date(Order.timestamp) <= end_date
        )

        # Item-wise sales within range
        daily_item_sales = (
            db_session.query(
                MenuItem.name,
                func.sum(OrderItem.quantity).label("total_sold"),
                (func.sum(OrderItem.quantity) * MenuItem.price).label("total_revenue")
            )
            .join(OrderItem, MenuItem.id == OrderItem.menu_item_id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(date_range_filter)
            .group_by(MenuItem.name, MenuItem.price)
            .order_by(func.sum(OrderItem.quantity).desc())
            .all()
        )
        daily_item_sales_list = [
            {"item_name": row.name, "total_sold": row.total_sold, "total_revenue": row.total_revenue}
            for row in daily_item_sales
        ]

        # Daily sales summary within range
        daily_sales = (
            db_session.query(
                func.date(Order.timestamp).label("date"),
                func.sum(Order.total_price).label("total_sales"),
                func.count(Order.id).label("total_orders"),
                (func.sum(Order.total_price) / func.count(Order.id)).label("avg_order_value"),
            )
            .filter(date_range_filter)
            .group_by(func.date(Order.timestamp))
            .order_by(func.date(Order.timestamp).desc())
            .all()
        )
        daily_sales_list = [
            {"date": row.date, "total_sales": row.total_sales, "total_orders": row.total_orders, "avg_order_value": row.avg_order_value}
            for row in daily_sales
        ]

        # Order summary within range
        order_details = (
            db_session.query(
                Order.id,
                func.date(Order.timestamp).label("date"),
                Order.total_price
            )
            .filter(date_range_filter)
            .order_by(Order.timestamp.desc())
            .all()
        )
        order_list = [
            {"order_id": row.id, "date": row.date, "total_sale": row.total_price}
            for row in order_details
        ]

        # Top items (all time)
        top_items = (
            db_session.query(
                MenuItem.name,
                MenuItem.price,
                func.sum(OrderItem.quantity).label("total_sold"),
                (func.sum(OrderItem.quantity) * MenuItem.price).label("revenue_generated"),
            )
            .join(OrderItem, MenuItem.id == OrderItem.menu_item_id)
            .group_by(MenuItem.name, MenuItem.price)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(5)
            .all()
        )
        top_items_list = [
            {"item_name": row.name, "unit_price": row.price, "total_sold": row.total_sold, "revenue_generated": row.revenue_generated}
            for row in top_items
        ]

        # Sales trends (last 7 days - fixed)
        sales_trends = (
            db_session.query(
                func.date(Order.timestamp).label("date"),
                func.sum(Order.total_price).label("sales_amount"),
            )
            .group_by(func.date(Order.timestamp))
            .order_by(func.date(Order.timestamp).desc())
            .limit(7)
            .all()
        )
        sales_trends_list = [{"date": row.date, "sales_amount": row.sales_amount} for row in sales_trends]

        # Sales by order type (filtered)
        order_type_sales = (
            db_session.query(
                Order.type,
                func.sum(Order.total_price).label("total_sales"),
            )
            .filter(date_range_filter)
            .group_by(Order.type)
            .all()
        )
        order_type_sales_list = [{"order_type": row.type, "total_sales": row.total_sales} for row in order_type_sales]

        # Compile report
        report_data = {
            "daily_item_sales": daily_item_sales_list,
            "daily_sales": daily_sales_list,
            "top_items": top_items_list,
            "sales_trends": sales_trends_list,
            "order_type_sales": order_type_sales_list,
            "order_details": order_list
        }

        return jsonify(report_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
