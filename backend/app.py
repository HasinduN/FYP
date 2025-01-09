from flask import Flask, jsonify, request, Response
from models import session, MenuItem, Order, OrderItem
from flask_cors import CORS
from sqlalchemy import func
import csv
from io import StringIO
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the POS System!"

@app.route('/menu', methods=['GET'])
def get_menu():
    menu_items = session.query(MenuItem).all()
    result = [{"id": item.id, "name": item.name, "price": item.price, "description": item.description} for item in menu_items]
    return jsonify(result)

@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    new_item = MenuItem(name=data['name'], price=data['price'], description=data.get('description'))
    session.add(new_item)
    session.commit()
    return jsonify({"message": "Menu item added successfully!"}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = session.query(Order).all()
    result = [
        {
            "id": order.id,
            "type": order.type,
            "total_price": order.total_price,
            "items": [
                {
                    "menu_item_id": item.menu_item_id,
                    "name": item.menu_item.name,
                    "price": item.menu_item.price,
                    "quantity": item.quantity
                }
                for item in order.order_items
            ]
        }
        for order in orders
    ]
    return jsonify(result)

@app.route('/orders', methods=['POST'])
def add_order():
    try:
        data = request.json
        order_type = data.get('type')
        table_number = data.get('table_number')
        items = data.get('items', [])

        # Validate payload
        if not order_type or not items:
            return jsonify({"error": "Order type and items are required"}), 400
        if order_type == "Dine-In" and not table_number:
            return jsonify({"error": "Table number is required for Dine-In orders"}), 400

        # Calculate total price
        total_price = 0
        for item in items:
            menu_item = session.query(MenuItem).get(item['menu_item_id'])
            if not menu_item:
                return jsonify({"error": f"Menu item with id {item['menu_item_id']} not found"}), 404
            total_price += menu_item.price * item['quantity']

        # Create order
        new_order = Order(type=order_type, total_price=total_price)
        session.add(new_order)
        session.commit()

        # Create order items
        for item in items:
            new_order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['menu_item_id'],
                quantity=item['quantity']
            )
            session.add(new_order_item)
        session.commit()

        return jsonify({"message": "Order added successfully!"}), 201

    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")  # Log the error for debugging
        return jsonify({"error": "An error occurred while placing the order."}), 500

@app.route('/reports/sales', methods=['GET'])
def generate_sales_report():
    try:
        # Ensure there is data in the orders table
        total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0
        total_orders = session.query(func.count(Order.id)).scalar() or 0

        revenue_by_type = session.query(
            Order.type, func.sum(Order.total_price)
        ).group_by(Order.type).all()

        if not revenue_by_type:
            return jsonify({"error": "No sales data available"}), 404

        report = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "revenue_by_type": [
                {"type": r[0], "revenue": r[1]} for r in revenue_by_type
            ]
        }
        return jsonify(report)
    except Exception as e:
        print(f"Error generating sales report: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/reports/sales/download', methods=['GET'])
def download_sales_report():
    try:
        # Fetch sales data
        total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0
        total_orders = session.query(func.count(Order.id)).scalar() or 0
        revenue_by_type = session.query(
            Order.type, func.sum(Order.total_price)
        ).group_by(Order.type).all()

        # Prepare CSV content
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Revenue", total_revenue])
        writer.writerow(["Total Orders", total_orders])

        writer.writerow([])
        writer.writerow(["Order Type", "Revenue"])
        for r in revenue_by_type:
            writer.writerow([r[0], r[1]])

        # Create response
        output.seek(0)
        response = Response(output, mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=sales_report.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/reports/inventory/download', methods=['GET'])
def download_inventory_report():
    try:
        # Fetch inventory data
        inventory_items = session.query(InventoryItem).all()

        # Prepare CSV content
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item Name", "Quantity", "Status"])
        for item in inventory_items:
            status = "Low Stock" if item.quantity < 10 else "Sufficient"
            writer.writerow([item.name, item.quantity, status])

        # Create response
        output.seek(0)
        response = Response(output, mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=inventory_report.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)