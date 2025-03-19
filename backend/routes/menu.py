from flask import Blueprint, jsonify, request
from models import session as db_session, MenuItem, Order,OrderItem
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required

menu_bp = Blueprint("menu", __name__)

#Fetch all menu items
@menu_bp.route('/menu', methods=['GET'])
def get_menu():
    try:
        menu_items = db_session.query(MenuItem).all()
        result = [{"id": item.id, "name": item.name, "price": item.price, "description": item.description} for item in menu_items]
        return jsonify(result)
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

#Add a new menu item
@menu_bp.route('/menu', methods=['POST'])
@jwt_required()
@role_required(["admin"])
def add_menu_item():
    try:
        data = request.json
        new_item = MenuItem(name=data['name'], price=data['price'], description=data.get('description'))
        db_session.add(new_item)
        db_session.commit()
        return jsonify({"message": "Menu item added successfully!"}), 201
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

#Update an existing menu item
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

        db_session.commit()
        return jsonify({"message": "Menu item updated successfully!"}), 200
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

#Delete a menu item
@menu_bp.route('/menu/<int:item_id>', methods=['DELETE'])
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
        return jsonify({"error": str(e)}), 500
