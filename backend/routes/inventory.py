from flask import Blueprint, jsonify
from models import InventoryItem, InventoryLog
from models import session as db_session
from datetime import datetime, timedelta

inventory_bp = Blueprint("inventory", __name__)

# Get Inventory Report
@inventory_bp.route("/inventory-report", methods=["GET"])
def get_inventory_report():
    try:
        # Get Current Stock Levels
        inventory = db_session.query(InventoryItem).all()
        stock_levels = [
            {"id": item.id, "name": item.name, "quantity": item.quantity, "unit": item.unit}
            for item in inventory
        ]

        # Find Low Stock Items (Threshold: 10)
        LOW_STOCK_THRESHOLD = 10
        low_stock = [
            {"id": item.id, "name": item.name, "quantity": item.quantity, "unit": item.unit}
            for item in inventory if item.quantity < LOW_STOCK_THRESHOLD
        ]

        # Fetch Stock Additions (Last 7 Days)
        last_7_days = datetime.utcnow() - timedelta(days=7)
        stock_additions = (
            db_session.query(InventoryLog)
            .filter(InventoryLog.added_date >= last_7_days)
            .order_by(InventoryLog.added_date.desc())
            .all()
        )

        stock_trends = [
            {
                "id": log.id,
                "item_name": log.inventory_item.name,
                "added_quantity": log.added_quantity,
                "unit": log.inventory_item.unit,
                "added_date": log.added_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            for log in stock_additions
        ]

        # Generate Report
        report_data = {
            "current_stock": stock_levels,
            "low_stock_alerts": low_stock,
            "stock_additions": stock_trends  # Shows stock updates in the last 7 days
        }

        return jsonify(report_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500