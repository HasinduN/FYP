from flask import Flask, jsonify
from flask_cors import CORS
from routes.menu import menu_bp
from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.orders import orders_bp
from routes.sales import sales_bp
from routes.inventoryManagement import inventorymanagement_bp
from models import session as db_session, MenuItem
import joblib
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "ed"

app.register_blueprint(menu_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(inventorymanagement_bp)


# Load trained model
model_path = "E:/PROJECT/backend/data/sales_prediction_model.pkl"
model = joblib.load(model_path)

# Function to generate future features for each item
def generate_future_features(menu_items, days=3):
    today = datetime.today()
    future_dates = [today + timedelta(days=i) for i in range(days)]
    
    # Create an empty DataFrame
    future_data = []

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

# API to predict sales per item
@app.route("/predict-sales", methods=["GET"])
def predict_sales():
    try:
        # Fetch all menu items from the database
        menu_items = db_session.query(MenuItem).all()
        
        # Generate future features
        future_features = generate_future_features(menu_items)
        input_features = future_features.drop(columns=["date", "menu_item_id", "item_name"])

        # Make predictions
        predictions = model.predict(input_features)
        
        # Prepare the response
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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)