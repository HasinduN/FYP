from flask import Blueprint, jsonify
import pandas as pd
import joblib
from models import session as db_session, InventoryItem
from datetime import datetime, timedelta

#Correct blueprint name
inventory_prediction_bp = Blueprint("inventory_prediction", __name__)

# Load trained inventory model
model_path = "E:/PROJECT/backend/ml_models/inventory_prediction_model.pkl"
model = joblib.load(model_path)

# Function to generate future features
def generate_future_features(inventory_items, days=7):
    today = datetime.today()
    future_dates = [today + timedelta(days=i) for i in range(days)]
    
    future_data = []
    for inventory_item in inventory_items:
        for date in future_dates:
            future_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "item_id": inventory_item.id,
                "item_name": inventory_item.name,
                "Day_of_Week": date.weekday(),
                "Month": date.month,
                "Weekend": 1 if date.weekday() in [5, 6] else 0,
            })

    return pd.DataFrame(future_data)

# Route to predict inventory
@inventory_prediction_bp.route("/predict-inventory", methods=["GET"])
def predict_inventory():
    try:
        # Fetch inventory items
        inventory_items = db_session.query(InventoryItem).all()
        
        # Generate features
        future_features = generate_future_features(inventory_items)
        
        if future_features.empty:
            return jsonify({"error": "No inventory items found"}), 400

        # Drop non-numeric columns
        input_features = future_features.drop(columns=["date", "item_id", "item_name"])

        # Make predictions
        predictions = model.predict(input_features)

        print("Predictions type:", type(predictions))
        print("Predictions shape:", predictions.shape)
        print("Predictions content:", predictions)

        # Ensure predictions are properly formatted
        predictions = predictions.flatten().tolist()  # Convert NumPy array to Python list

        # Format predictions
        prediction_results = []
        for i in range(len(future_features)):
            prediction_results.append({
                "date": future_features.iloc[i]["date"],
                "item_id": int(future_features.iloc[i]["item_id"]),
                "item_name": future_features.iloc[i]["item_name"],
                "predicted_quantity": float(predictions[i])  # Ensure it's a Python float
            })

        return jsonify(prediction_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
