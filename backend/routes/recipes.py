from flask import Blueprint, jsonify, request
from models import session as db_session, Recipe

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.route('/recipes', methods=['POST'])
def add_recipe():
    try:
        data = request.json
        menu_item_id = data.get('menu_item_id')
        ingredients = data.get('ingredients')  # List of {ingredient_id, quantity_needed}

        if not menu_item_id or not ingredients:
            return jsonify({"error": "Menu item ID and ingredients are required"}), 400

        for ingredient in ingredients:
            new_recipe = Recipe(
                menu_item_id=menu_item_id,
                ingredient_id=ingredient["ingredient_id"],
                quantity_needed=ingredient["quantity_needed"],
                unit=ingredient["unit"]
            )
            db_session.add(new_recipe)

        db_session.commit()
        return jsonify({"message": "Recipe added successfully!"}), 201

    except Exception as e:
        db_session.rollback()
        print(f"Error adding recipe: {e}")
        return jsonify({"error": str(e)}), 500
    
@recipes_bp.route('/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    try:
        data = request.json
        menu_item_id = data.get("menu_item_id")
        ingredients = data.get("ingredients")

        if not menu_item_id or not ingredients:
            return jsonify({"error": "Menu item ID and ingredients are required"}), 400

        # Delete existing recipe entries for this menu item
        db_session.query(Recipe).filter(Recipe.menu_item_id == menu_item_id).delete()

        # Add the new updated ingredients
        for ingredient in ingredients:
            updated_recipe = Recipe(
                menu_item_id=menu_item_id,
                ingredient_id=ingredient["ingredient_id"],
                quantity_needed=ingredient["quantity_needed"],
                unit=ingredient["unit"]
            )
            db_session.add(updated_recipe)

        db_session.commit()
        return jsonify({"message": "Recipe updated successfully!"}), 200

    except Exception as e:
        db_session.rollback()
        print(f"Error updating recipe: {e}")
        return jsonify({"error": str(e)}), 500