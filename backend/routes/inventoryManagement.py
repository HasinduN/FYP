from flask import Blueprint, jsonify, request
from models import session as db_session, InventoryItem, InventoryLog

inventorymanagement_bp = Blueprint("inventoryManagement", __name__)

# Route to fetch all inventory items
@inventorymanagement_bp.route('/inventory-management', methods=['GET'])
def get_inventory():
    try:
        inventory_items = db_session.query(InventoryItem).all()
        result = [
            {"id": item.id, "name": item.name, "quantity": item.quantity, "unit": item.unit}
            for item in inventory_items
        ]
        return jsonify(result)
    except Exception as e:
        db_session.rollback()
        print(f"Error fetching inventory items: {e}")
        return jsonify({"error": str(e)}), 500

# Route to add a new inventory item
@inventorymanagement_bp.route('/inventory-management', methods=['POST'])
def add_inventory_item():
    try:
        data = request.json
        item_name = data['name'].strip().lower()
        quantity_to_add = float(data['quantity'])
        unit = data.get("unit", "nos")

        # Check if item already exists
        existing_item = db_session.query(InventoryItem).filter(InventoryItem.name == item_name).first()

        if existing_item:
            # Update quantity
            existing_item.quantity += quantity_to_add
        else:
            # Create a new inventory item
            existing_item = InventoryItem(name=item_name, quantity=quantity_to_add, unit=unit)
            db_session.add(existing_item)
            db_session.flush()  # Get the newly created ID

        # Add an inventory log entry
        new_log = InventoryLog(inventory_item_id=existing_item.id, added_quantity=quantity_to_add, unit=unit)
        db_session.add(new_log)

        db_session.commit()
        return jsonify({"message": "Inventory updated successfully!"}), 201

    except Exception as e:
        db_session.rollback()
        print(f"Error updating inventory: {e}")
        return jsonify({"error": str(e)}), 500