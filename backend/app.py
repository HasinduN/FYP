from flask import Flask, jsonify, request, session
from models import session as db_session, User, MenuItem, InventoryItem, Order, OrderItem
from flask_cors import CORS
from functools import wraps
import bcrypt

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS with credentials
app.secret_key = "ed"  # Use a strong secret key in production

# Route to fetch all menu items
@app.route('/menu', methods=['GET'])
def get_menu():
    try:
        menu_items = db_session.query(MenuItem).all()
        result = [
            {"id": item.id, "name": item.name, "price": item.price, "description": item.description}
            for item in menu_items
        ]
        return jsonify(result)
    except Exception as e:
        db_session.rollback()
        print(f"Error fetching menu items: {e}")
        return jsonify({"error": str(e)}), 500

# Route to add a new menu item
@app.route('/menu', methods=['POST'])
def add_menu_item():
    try:
        data = request.json
        new_item = MenuItem(name=data['name'], price=data['price'], description=data.get('description'))
        db_session.add(new_item)
        db_session.commit()
        return jsonify({"message": "Menu item added successfully!"}), 201
    except Exception as e:
        db_session.rollback()
        print(f"Error adding menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to update menu item
@app.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    try:
        data = request.json
        item = db_session.query(MenuItem).get(item_id)
        if not item:
            return jsonify({"error": "Menu item not found"}), 404

        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.description = data.get('description', item.description)
        db_session.commit()
        return jsonify({"message": "Menu item updated successfully!"})
    except Exception as e:
        db_session.rollback()
        print(f"Error updating menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to delete menu item
@app.route('/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    try:
        item = db_session.query(MenuItem).get(item_id)
        if not item:
            return jsonify({"error": "Menu item not found"}), 404

        # Check if the item is part of any ongoing order
        ongoing_order = db_session.query(OrderItem).join(Order).filter(
            OrderItem.menu_item_id == item_id,
            Order.status == False  # Ongoing orders only
        ).first()

        if ongoing_order:
            return jsonify({"error": "Menu item cannot be deleted as it is part of an ongoing order."}), 400

        db_session.delete(item)
        db_session.commit()
        return jsonify({"message": "Menu item deleted successfully!"}), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error deleting menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to fetch all inventory items
@app.route('/inventory-management', methods=['GET'])
def get_inventory():
    try:
        inventory_items = db_session.query(InventoryItem).all()
        result = [
            {"id": item.id, "name": item.name, "quantity": item.quantity, "added_date": item.added_date.strftime("%Y-%m-%d %H:%M:%S")}
            for item in inventory_items
        ]
        return jsonify(result)
    except Exception as e:
        db_session.rollback()
        print(f"Error fetching inventory items: {e}")
        return jsonify({"error": str(e)}), 500

# Route to add a new inventory item
@app.route('/inventory-management', methods=['POST'])
def add_inventory_item():
    try:
        data = request.json
        new_item = InventoryItem(name=data['name'], quantity=data['quantity'])
        db_session.add(new_item)
        db_session.commit()
        return jsonify({"message": "Inventory item added successfully!"}), 201
    except Exception as e:
        db_session.rollback()
        print(f"Error adding inventory item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to fetch all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = db_session.query(Order).all()
        result = [
            {
                "id": order.id,
                "type": order.type,
                "total_price": order.total_price,
                "status": "Completed" if order.status else "Ongoing",
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

@app.route('/orders', methods=['POST'])
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
            session.query(MenuItem).get(item['menu_item_id']).price * item['quantity']
            for item in items
        )

        # Create a new order
        new_order = Order(type=order_type, total_price=total_price, status=False)
        db_session.add(new_order)
        db_session.commit()

        # Add order items
        for item in items:
            new_order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['menu_item_id'],
                quantity=item['quantity']
            )
            db_session.add(new_order_item)
        db_session.commit()

        # Return the new order ID
        return jsonify({"message": "Order added successfully!", "order_id": new_order.id}), 201
    except Exception as e:
        db_session.rollback()
        print(f"Error adding order: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders/ongoing', methods=['GET'])
def get_ongoing_orders():
    try:
        # Fetch ongoing orders
        orders = db_session.query(Order).filter_by(status=False).all()
        result = [
            {
                "id": order.id,
                "type": order.type,
                "table_number": order.table_number,
                "table_number": order.type == "Dine-In" and order.table_number or None,
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
        return jsonify(result), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error fetching ongoing orders: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json
        items = data['items']

        # Fetch the existing order
        order = db_session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        if order.status:
            return jsonify({"error": "Cannot update a completed order"}), 400

        # Add new items to the order
        for item in items:
            existing_item = db_session.query(OrderItem).filter_by(
                order_id=order_id,
                menu_item_id=item['menu_item_id']
            ).first()
            if existing_item:
                # Update quantity if the item already exists in the order
                existing_item.quantity += item['quantity']
            else:
                # Add a new item
                new_order_item = OrderItem(
                    order_id=order_id,
                    menu_item_id=item['menu_item_id'],
                    quantity=item['quantity']
                )
                db_session.add(new_order_item)

        # Update the total price
        for item in items:
            menu_item = db_session.query(MenuItem).get(item['menu_item_id'])
            order.total_price += menu_item.price * item['quantity']

        db_session.commit()
        return jsonify({"message": "Order updated successfully!"}), 200
    except Exception as e:
        db_session.rollback()
        print(f"Error updating order: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/orders/<int:order_id>/payment', methods=['POST'])
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
@app.route('/orders/<int:order_id>/status', methods=['PUT'])
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

@app.route('/orders/<int:order_id>/kot', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)