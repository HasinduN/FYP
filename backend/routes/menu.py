from flask import Blueprint, jsonify, request
from models import session as db_session, MenuItem, Order,OrderItem
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required

menu_bp = Blueprint("menu", __name__)

#Fetch all menu items
@menu_bp.route("/menu", methods=["GET"])
def get_menu():
    """Fetch all menu items categorized"""
    try:
        menu_items = db_session.query(MenuItem).all()
        categorized_menu = {}

        for item in menu_items:
            category = item.category if item.category else "Uncategorized"
            if category not in categorized_menu:
                categorized_menu[category] = []
            categorized_menu[category].append({
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "description": item.description,
                "category": item.category
            })

        return jsonify(categorized_menu), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@menu_bp.route('/menu', methods=['POST'])
def add_menu_item():
    try:
        data = request.json

        # Check if all required fields are provided
        if not all(k in data for k in ("name", "price", "description", "category")):
            return jsonify({"error": "Missing required fields"}), 400

        if data["category"] not in ["Fried Rice", "Noodles", "Kottu", "Cheese Kottu", "Nasigoreng", "Side Dishes", "Beverages", "Deserts"]:
            return jsonify({"error": "Invalid category"}), 400

        # Create new menu item
        new_item = MenuItem(name=data["name"], price=data["price"], description = data.get("description", ""), category=data["category"])
        db_session.add(new_item)
        db_session.commit()

        return jsonify({"message": "Menu item added successfully!"}), 201
    except Exception as e:
        db_session.rollback()
        print(f"Error adding menu item: {e}")  # Debugging
        return jsonify({"error": str(e)}), 500

@menu_bp.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    try:
        data = request.json
        item = db_session.query(MenuItem).get(item_id)

        if not item:
            return jsonify({"error": "Menu item not found"}), 404

        # Update fields only if provided in the request
        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.description = data.get('description', item.description)
        item.category = data.get('category', item.category)

        db_session.commit()
        return jsonify({"message": "Menu item updated successfully!"}), 200
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@menu_bp.route("/menu/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    try:
        # Check if the menu item is being used in orders
        order_item_exists = db_session.query(OrderItem).filter_by(menu_item_id=item_id).first()
        
        if order_item_exists:
            return jsonify({"error": "Cannot delete. Item is referenced in existing orders."}), 400

        # If not referenced, proceed with deletion
        menu_item = MenuItem.query.get(item_id)
        if menu_item:
            db_session.delete(menu_item)
            db_session.commit()
            return jsonify({"message": "Menu item deleted successfully!"}), 200
        else:
            return jsonify({"error": "Menu item not found."}), 404

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Database integrity error. Item may still be referenced in orders."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
