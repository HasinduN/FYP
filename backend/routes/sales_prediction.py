from flask import Blueprint, jsonify
import joblib
import pandas as pd
from datetime import datetime, timedelta
from models import session as db_session, MenuItem

# Create Blueprint
sales_prediction_bp = Blueprint("sales_prediction", __name__)

# Load trained model (ensure this path matches where your model is saved)
model_path = "ml_models/sales_prediction_model.pkl"
model = joblib.load(model_path)

# Function to generate future features for each menu item
def generate_future_features(menu_items, days=3):
    today = datetime.today()
    future_dates = [today + timedelta(days=i) for i in range(days)]
    
    # Create list to accumulate feature dictionaries
    future_data = []

    # For each menu item and for each future date, create a feature dictionary
    for menu_item in menu_items:
        for date in future_dates:
            future_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "menu_item_id": menu_item.id,
                "item_name": menu_item.name,
                "Day_of_Week": date.weekday(),
                "Month": date.month,
                "Weekend": 1 if date.weekday() in [5, 6] else 0,
                "Unit_Price": menu_item.price,
                "Restaurant_Closed": 0
            })

    return pd.DataFrame(future_data)

# API endpoint to predict sales per menu item
@sales_prediction_bp.route("/predict-sales", methods=["GET"])
def predict_sales():
    try:
        # Fetch all menu items from the database
        menu_items = db_session.query(MenuItem).all()
        
        # Generate future features for the specified number of days (here, 3 days into the future)
        future_features = generate_future_features(menu_items)

        # Explicitly select and order the features expected by the model.
        # The order here should match what was used in training: 
        # "Day_of_Week", "Month", "Weekend", "Unit_Price", "Restaurant_Closed"
        input_features = future_features[['Day_of_Week', 'Month', 'Weekend', 'Unit_Price', 'Restaurant_Closed']]

        # Make predictions with the loaded model
        predictions = model.predict(input_features)
        
        # Format the predictions to be sent as a JSON response
        prediction_results = []
        for i, pred in enumerate(predictions):
            prediction_results.append({
                "date": future_features.iloc[i]["date"],
                "menu_item_id": int(future_features.iloc[i]["menu_item_id"]),
                "item_name": future_features.iloc[i]["item_name"],
                "predicted_sales": round(float(pred))
            })

        return jsonify(prediction_results)
    
    except Exception as e:
        # Catch any exceptions, log or print them if needed, and return a JSON error response
        return jsonify({"error": str(e)}), 500
