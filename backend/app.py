from flask import Flask, jsonify, request, session
from models import session as db_session, User, MenuItem, InventoryItem, Order, OrderItem
from flask_cors import CORS
from functools import wraps
import bcrypt

app = Flask(__name__)
CORS(app)
app.secret_key = "ed"

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = db_session.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        # Use bcrypt to verify the password
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return jsonify({"error": "Invalid username or password"}), 401

        # Save user details to session
        session["username"] = user.username
        session["role"] = user.role

        return jsonify({"message": "Login successful", "role": user.role}), 200
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully!"}), 200

# Home route
@app.route('/')
def home():
    return "Welcome to the POS System!"

def role_required(allowed_roles):
    """
    Decorator to restrict access based on roles.
    :param allowed_roles: List of roles that can access the route.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user's role from the session
            user_role = session.get("role")
            if user_role not in allowed_roles:
                return jsonify({"error": "Access forbidden: Insufficient permissions"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Route to fetch all users (Manager-only access)
@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = db_session.query(User).all()
        result = [
            {"id": user.id, "username": user.username, "role": user.role}
            for user in users
        ]
        return jsonify(result), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to add a new user (Manager-only access)
@app.route("/users", methods=["POST"])
def add_user():
    try:
        data = request.json
        username = data["username"]
        password = data["password"]
        role = data["role"]

        # Check if the user already exists
        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Create a new user
        new_user = User(username=username, password_hash=hashed_password, role=role)
        db_session.add(new_user)
        db_session.commit()

        return jsonify({"message": "User added successfully!"}), 201
    except Exception as e:
        db_session.rollback()
        print(f"Error adding user: {e}")  # Log the actual error
        return jsonify({"error": str(e)}), 500

# Route to edit a user (Manager-only access)
@app.route("/users/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    try:
        data = request.json
        user = db_session.query(User).get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.username = data.get("username", user.username)
        user.role = data.get("role", user.role)
        db_session.commit()

        return jsonify({"message": "User updated successfully!"}), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to delete a user (Manager-only access)
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = db_session.query(User).get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db_session.delete(user)
        db_session.commit()

        return jsonify({"message": "User deleted successfully!"}), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

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
        session.add(new_item)
        session.commit()
        return jsonify({"message": "Menu item added successfully!"}), 201
    except Exception as e:
        session.rollback()
        print(f"Error adding menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to update menu item
@app.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    try:
        data = request.json
        item = session.query(MenuItem).get(item_id)
        if not item:
            return jsonify({"error": "Menu item not found"}), 404

        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.description = data.get('description', item.description)
        session.commit()
        return jsonify({"message": "Menu item updated successfully!"})
    except Exception as e:
        session.rollback()
        print(f"Error updating menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to delete menu item
@app.route('/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    try:
        item = session.query(MenuItem).get(item_id)
        if not item:
            return jsonify({"error": "Menu item not found"}), 404

        # Check if the item is part of any ongoing order
        ongoing_order = session.query(OrderItem).join(Order).filter(
            OrderItem.menu_item_id == item_id,
            Order.status == False  # Ongoing orders only
        ).first()

        if ongoing_order:
            return jsonify({"error": "Menu item cannot be deleted as it is part of an ongoing order."}), 400

        session.delete(item)
        session.commit()
        return jsonify({"message": "Menu item deleted successfully!"}), 200
    except Exception as e:
        session.rollback()
        print(f"Error deleting menu item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to fetch all inventory items
@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        inventory_items = session.query(InventoryItem).all()
        result = [
            {"id": item.id, "name": item.name, "quantity": item.quantity}
            for item in inventory_items
        ]
        return jsonify(result)
    except Exception as e:
        session.rollback()
        print(f"Error fetching inventory items: {e}")
        return jsonify({"error": str(e)}), 500

# Route to add a new inventory item
@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    try:
        data = request.json
        new_item = InventoryItem(name=data['name'], quantity=data['quantity'])
        session.add(new_item)
        session.commit()
        return jsonify({"message": "Inventory item added successfully!"}), 201
    except Exception as e:
        session.rollback()
        print(f"Error adding inventory item: {e}")
        return jsonify({"error": str(e)}), 500

# Route to fetch all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = session.query(Order).all()
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
        session.rollback()
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
        session.add(new_order)
        session.commit()

        # Add order items
        for item in items:
            new_order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['menu_item_id'],
                quantity=item['quantity']
            )
            session.add(new_order_item)
        session.commit()

        # Return the new order ID
        return jsonify({"message": "Order added successfully!", "order_id": new_order.id}), 201
    except Exception as e:
        session.rollback()
        print(f"Error adding order: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders/ongoing', methods=['GET'])
def get_ongoing_orders():
    try:
        # Fetch ongoing orders
        orders = session.query(Order).filter_by(status=False).all()
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
        session.rollback()
        print(f"Error fetching ongoing orders: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json
        items = data['items']

        # Fetch the existing order
        order = session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        if order.status:
            return jsonify({"error": "Cannot update a completed order"}), 400

        # Add new items to the order
        for item in items:
            existing_item = session.query(OrderItem).filter_by(
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
                session.add(new_order_item)

        # Update the total price
        for item in items:
            menu_item = session.query(MenuItem).get(item['menu_item_id'])
            order.total_price += menu_item.price * item['quantity']

        session.commit()
        return jsonify({"message": "Order updated successfully!"}), 200
    except Exception as e:
        session.rollback()
        print(f"Error updating order: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/orders/<int:order_id>/payment', methods=['POST'])
def process_payment(order_id):
    try:
        data = request.json
        payment_method = data.get('payment_method')

        if not payment_method or payment_method not in ['cash', 'card']:
            return jsonify({"error": "Invalid payment method"}), 400

        order = session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Update order status
        order.status = True
        session.commit()

        return jsonify({"message": f"Payment successful using {payment_method}!"}), 200
    except Exception as e:
        session.rollback()
        print(f"Error processing payment: {e}")
        return jsonify({"error": str(e)}), 500

# Route to update order status
@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        order = session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Mark the order as completed
        order.status = True
        session.commit()
        return jsonify({"message": "Order status updated to completed!"}), 200
    except Exception as e:
        session.rollback()
        print(f"Error updating order status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/orders/<int:order_id>/kot', methods=['POST'])
def print_kot(order_id):
    try:
        order = session.query(Order).get(order_id)
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
        session.commit()

        return jsonify({"message": "KOT printed successfully!"}), 200
    except Exception as e:
        session.rollback()
        print(f"Error printing KOT: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)