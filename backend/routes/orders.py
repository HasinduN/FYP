from flask import Blueprint, jsonify, request
from models import session as db_session, MenuItem, Order, OrderItem, InventoryItem, Recipe
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import func

orders_bp = Blueprint("orders", __name__)

def convert_units(recipe_unit, inventory_unit, quantity):
    unit_conversion = {
        "kg": 1000,
        "g": 1,
        "l": 1000,
        "ml": 1,
        "nos": 1
    }

    if recipe_unit in unit_conversion and inventory_unit in unit_conversion:
        return quantity * (unit_conversion[recipe_unit] / unit_conversion[inventory_unit])
    return None  # Return None if unit mismatch

# Route to fetch all orders
@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = db_session.query(Order)

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(func.date(Order.timestamp) >= start_date)

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(func.date(Order.timestamp) <= end_date)

        orders = query.order_by(Order.timestamp.desc()).all()  # Sort orders by latest first

        result = [
            {
                "id": order.id,
                "type": order.type,
                "total_price": order.total_price,
                "status": "Completed" if order.status else "Ongoing",
                "timestamp": order.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Ensure timestamp is formatted correctly
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

    except Exception as e:
        db_session.rollback()
        print(f"Error fetching orders: {e}")
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/orders', methods=['POST'])
def add_order():
    try:
        data = request.json
        order_type = data['type']
        items = data['items']
        table_number = data.get('table_number')

        if not order_type or not items:
            return jsonify({"error": "Order type and items are required"}), 400

        if order_type == "Dine-In" and not table_number:
            return jsonify({"error": "Table number is required for Dine-In orders"}), 400

        # Calculate total price
        total_price = sum(
            db_session.query(MenuItem).get(item['menu_item_id']).price * item['quantity']
            for item in items
        )

        # Create a new order
        new_order = Order(type=order_type, total_price=total_price, status=False)
        db_session.add(new_order)
        db_session.commit()

        # Process each item in the order
        for item in items:
            menu_item_id = item['menu_item_id']
            quantity = item['quantity']

            new_order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=menu_item_id,
                quantity=quantity
            )
            db_session.add(new_order_item)

            # Deduct ingredients from inventory based on the recipe
            recipe_items = db_session.query(Recipe).filter_by(menu_item_id=menu_item_id).all()
            for recipe in recipe_items:
                inventory_item = db_session.query(InventoryItem).get(recipe.ingredient_id)
                if inventory_item:
                    # Convert units if needed
                    required_quantity = convert_units(recipe.unit, inventory_item.unit, recipe.quantity_needed * quantity)

                    if required_quantity is None:
                        return jsonify({"error": f"Unit mismatch for {inventory_item.name}"}), 400

                    if inventory_item.quantity >= required_quantity:
                        inventory_item.quantity -= required_quantity
                    else:
                        return jsonify({"error": f"Not enough stock for {inventory_item.name}"}), 400

        db_session.commit()

        return jsonify({"message": "Order added successfully!", "order_id": new_order.id}), 201

    except Exception as e:
        db_session.rollback()
        print(f"Error adding order: {e}")
        return jsonify({"error": str(e)}), 500
    
@orders_bp.route("/orders/ongoing", methods=["GET"])
def get_ongoing_orders():
    """Fetch ongoing orders with their items"""
    try:
        orders = db_session.query(Order).filter_by(status=False).all()

        orders_data = []
        for order in orders:
            order_items = db_session.query(OrderItem, MenuItem).join(MenuItem).filter(OrderItem.order_id == order.id).all()
            
            items_list = [
                {"menu_item_id": oi.OrderItem.menu_item_id, "name": oi.MenuItem.name, "quantity": oi.OrderItem.quantity, "price": oi.MenuItem.price}
                for oi in order_items
            ]

            orders_data.append({
                "id": order.id,
                "type": order.type,
                "table_number": order.table_number,
                "total_price": order.total_price,
                "timestamp": order.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "items": items_list
            })

        return jsonify(orders_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@orders_bp.route("/orders/update/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """Update an existing order by adding new items"""
    try:
        data = request.json
        order = db_session.query(Order).filter_by(id=order_id).first()

        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Clear existing items
        db_session.query(OrderItem).filter_by(order_id=order_id).delete()

        # Add new items to the order
        for item in data["items"]:
            new_item = OrderItem(order_id=order_id, menu_item_id=item["menu_item_id"], quantity=item["quantity"])
            db_session.add(new_item)

        # Update total price
        total_price = sum(item["quantity"] * item["price"] for item in data["items"])
        order.total_price = total_price
        db_session.commit()

        return jsonify({"message": "Order updated successfully!"}), 200

    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    
@orders_bp.route('/orders/<int:order_id>/payment', methods=['POST'])
def process_payment(order_id):
    try:
        data = request.json
        payment_method = data.get('payment_method')

        if not payment_method or payment_method not in ['cash', 'card']:
            return jsonify({"error": "Invalid payment method"}), 400

        order = db_session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Update order status
        order.status = True
        db_session.commit()

        return jsonify({"message": f"Payment successful using {payment_method}!"}), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error processing payment: {e}")
        return jsonify({"error": str(e)}), 500

# Route to update order status
@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        order = db_session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Mark the order as completed
        order.status = True
        db_session.commit()
        return jsonify({"message": "Order status updated to completed!"}), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error updating order status: {e}")
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/orders/<int:order_id>/kot', methods=['POST'])
def print_kot(order_id):
    try:
        order = db_session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        if order.kot_printed:
            return jsonify({"message": "KOT has already been printed for this order."}), 200

        # Simulate KOT printing (e.g., save to file, send to printer, etc.)
        kot_details = {
            "order_id": order.id,
            "type": order.type,
            "items": [
                {
                    "name": item.menu_item.name,
                    "quantity": item.quantity
                }
                for item in order.order_items
            ]
        }
        print(f"KOT Printed: {kot_details}")  # Placeholder for actual printing logic

        # Mark KOT as printed
        order.kot_printed = True
        db_session.commit()

        return jsonify({"message": "KOT printed successfully!"}), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error printing KOT: {e}")
        return jsonify({"error": str(e)}), 500