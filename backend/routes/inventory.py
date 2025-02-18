from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models import InventoryItem
from models import session as db_session

inventory_bp = Blueprint("inventory", __name__)

#Get Inventory Report
@inventory_bp.route("/inventory-report", methods=["GET"])
def get_inventory_report():
    try:
        #Get Current Stock Levels
        inventory = db_session.query(InventoryItem).all()
        stock_levels = [
            {"id": item.id, "name": item.name, "quantity": item.quantity}
            for item in inventory
        ]

        #Find Low Stock Items (Threshold: 10)
        low_stock = [
            {"id": item.id, "name": item.name, "quantity": item.quantity}
            for item in inventory if item.quantity < 10
        ]

        #Sample Usage Trends (Future Enhancement)
        stock_trends = []  # This can be implemented using historical stock data

        #Generate Report
        report_data = {
            "current_stock": stock_levels,
            "low_stock_alerts": low_stock,
            "stock_trends": stock_trends
        }

        return jsonify(report_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500