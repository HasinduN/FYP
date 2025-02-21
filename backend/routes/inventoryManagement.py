from flask import Blueprint, jsonify, request
from models import session as db_session, InventoryItem, InventoryLog
from datetime import datetime

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
        unit = data.get("unit", "nos").strip().lower()

        # Check if item already exists
        existing_item = db_session.query(InventoryItem).filter(InventoryItem.name == item_name).first()

        if existing_item:
            # Update quantity
            existing_item.quantity += quantity_to_add
            existing_item.unit = unit
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
    
@inventorymanagement_bp.route('/inventory-management/update', methods=['PUT'])
def update_inventory_item():
    try:
        data = request.json
        item_id = data.get("id")
        item_name = data.get("name")  # Check if Name is provided
        added_quantity = float(data["quantity"])
        unit = data.get("unit", "nos").strip().lower()

        if not item_id and not item_name:
            return jsonify({"error": "Provide either an 'id' or 'name' to update inventory"}), 400

        # Fetch inventory item based on ID or Name
        if item_id:
            inventory_item = db_session.query(InventoryItem).filter_by(id=item_id).first()
        else:
            inventory_item = db_session.query(InventoryItem).filter(InventoryItem.name.ilike(item_name)).first()

        if not inventory_item:
            return jsonify({"error": "Inventory item not found"}), 404

        # Ensure unit consistency
        if inventory_item.unit != unit:
            return jsonify({"error": f"Unit mismatch! Expected {inventory_item.unit}, but got {unit}"}), 400

        # Update stock quantity
        inventory_item.quantity += added_quantity

        # Log the stock addition
        new_log = InventoryLog(
            inventory_item_id=inventory_item.id,
            added_quantity=added_quantity,
            unit=unit,
            added_date=datetime.utcnow(),
            action="Stock Updated"
        )
        db_session.add(new_log)

        db_session.commit()
        return jsonify({"message": "Inventory updated successfully!", "item_id": inventory_item.id}), 200

    except Exception as e:
        db_session.rollback()
        print(f"Error updating inventory: {e}")
        return jsonify({"error": str(e)}), 500