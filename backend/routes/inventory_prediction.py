from flask import Blueprint, jsonify, request
import joblib
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime, timedelta

# Create blueprint for inventory predictions
inventory_prediction_bp = Blueprint("inventory_prediction", __name__)

#Dictionaries Mapping Product Names to Their Corresponding Model Files

monthly_models = {
    "Salt": "ml_models/monthly_model_Salt_Amount.pkl",
    "Pepper": "ml_models/monthly_model_Pepper_Amount.pkl",
    "Chilie flakes": "ml_models/monthly_model_Chilie_flakes_Amount.pkl",
    "Cheese": "ml_models/monthly_model_Cheese_Amount.pkl",
    "Fresh milk": "ml_models/monthly_model_Fresh_milk_Amount.pkl",
    "Sesame oil": "ml_models/monthly_model_Sesame_oil_Amount.pkl",
    "Tomato ketchup": "ml_models/monthly_model_Tomato_ketchup_Amount.pkl",
    "Dark sauce": "ml_models/monthly_model_Dark_sauce_Amount.pkl",
    "Oyster sauce": "ml_models/monthly_model_Oyster_sauce_Amount.pkl"
}

weekly_models = {
    "Basmathi rice": "ml_models/weekly_model_Basmathi_rice_Amount.pkl",
    "Samba rice": "ml_models/weekly_model_Samba_rice_Amount.pkl",
    "Cooking oil": "ml_models/weekly_model_Cooking_oil_Amount.pkl",
    "Chicken": "ml_models/weekly_model_Chicken_Amount.pkl",
    "Fish": "ml_models/weekly_model_Fish_Amount.pkl",
    "Prawns": "ml_models/weekly_model_Prawns_Amount.pkl",
    "Cuttlefish": "ml_models/weekly_model_Cuttlefish_Amount.pkl",
    "Egg": "ml_models/weekly_model_Egg_Amount.pkl",
    "Sausage": "ml_models/weekly_model_Sausage_Amount.pkl",
    "Carrot": "ml_models/weekly_model_Carrot_Amount.pkl",
    "Leeks": "ml_models/weekly_model_Leeks_Amount.pkl",
    "Cabage": "ml_models/weekly_model_Cabage_Amount.pkl",
    "Pinnaple": "ml_models/weekly_model_Pinnaple_Amount.pkl"
}

frequent_models = {
    "Roti": "ml_models/frequent_restock_roti_model.pkl"
}


# Helper Functions for Preprocessing and Feature Engineering


def create_date_features(df, date_col="Date"):
    """
    Add basic date features to the DataFrame.
    """
    df["Day_of_Week"] = df[date_col].dt.dayofweek
    df["Month"] = df[date_col].dt.month
    df["Weekend"] = df["Day_of_Week"].isin([5, 6]).astype(int)
    df["Quarter"] = df[date_col].dt.quarter
    return df

def is_last_day_of_month(dt):
    """Return True if dt is the last day of its month."""
    return (dt + timedelta(days=1)).month != dt.month

def is_sunday(dt):
    """Return True if dt is a Sunday (weekday() == 6)."""
    return dt.weekday() == 6

def generate_features_for_date_range(date_list):
    """
    Given a list of datetime objects, create a DataFrame with features 
    needed for monthly and frequent models.
    """
    df = pd.DataFrame({"Date": date_list})
    df = create_date_features(df, "Date")
    X = df[["Day_of_Week", "Month", "Weekend", "Quarter"]]
    return X

def generate_weekly_features_for_date(product, target_date):
    """
    Generate one feature row for a weekly model for the given product for the
    specified target_date.
    
    This function loads historical data from the Excel file
    "ml_models/weekly_products.xlsx" (instead of CSV files) and expects that
    the column name is "<product> Amount" (e.g. "Basmathi rice Amount").
    
    Before computing lags and rolling statistics, it filters out rows with zero values.
    
    Returns:
      - X_new: A one-row DataFrame with features ready for prediction.
      - predicted_date: The target_date formatted as string.
    """
    file_path = os.path.join("ml_models", "weekly_products.xlsx")
    if not os.path.exists(file_path):
        return None, None

    # Load the historical weekly data
    df = pd.read_excel(file_path, parse_dates=["Date"])
    df.sort_values("Date", inplace=True)

    # Construct the column name as in the Excel file
    col_name = f"{product} Amount"
    if col_name not in df.columns:
        return None, None

    # Convert values to numeric (extracting numeric parts) and fill missing with 0
    df[col_name] = df[col_name].astype(str).str.extract(r'(\d+\.?\d*)')[0]
    df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0)

    # Filter out rows with zero values for this product
    df = df[df[col_name] != 0].copy()
    if len(df) < 5:
        return None, None  # Not enough data to compute lags

    # Create a sequential time index
    df["TimeIndex"] = np.arange(len(df))

    # Create lag features for lags 1 to 4
    for lag in range(1, 5):
        df[f"lag_{lag}"] = df[col_name].shift(lag)

    # Create rolling statistics based on lag_1 with window sizes 3 and 5
    df["roll_mean_3"] = df["lag_1"].rolling(window=3).mean()
    df["roll_std_3"] = df["lag_1"].rolling(window=3).std()
    df["roll_mean_5"] = df["lag_1"].rolling(window=5).mean()
    df["roll_std_5"] = df["lag_1"].rolling(window=5).std()

    df.dropna(inplace=True)
    if df.empty:
        return None, None

    # Use the last row of the filtered data to compute lag values for prediction.
    last_row = df.iloc[-1].copy()
    next_time_index = last_row["TimeIndex"] + 1

    # Build the feature row for the given target_date.
    new_features = {
        "TimeIndex": [next_time_index],
        "Year": [target_date.year],
        "Month": [target_date.month],
        "Week": [target_date.isocalendar().week],
        "DayOfWeek": [target_date.weekday()],
        "lag_1": [last_row[col_name]],
        "lag_2": [last_row["lag_1"]],
        "lag_3": [last_row["lag_2"]],
        "lag_4": [last_row["lag_3"]],
        "roll_mean_3": [last_row["roll_mean_3"]],
        "roll_std_3": [last_row["roll_std_3"]],
        "roll_mean_5": [last_row["roll_mean_5"]],
        "roll_std_5": [last_row["roll_std_5"]]
    }
    X_new = pd.DataFrame(new_features)
    return X_new, target_date.strftime("%Y-%m-%d")

def generate_frequent_features(date_list):
    """
    Generate future features for frequent restock models using the same method as monthly models.
    """
    return generate_features_for_date_range(date_list)


# Prediction Route: Return All Predictions for a Given Date Range

@inventory_prediction_bp.route("/predict-inventory", methods=["GET"])
def predict_inventory():
    """
    This endpoint generates inventory predictions for all products across the three categories 
    (monthly, weekly, and frequent) over a user-specified date range.
    
    Query parameters:
       - start_date (YYYY-MM-DD)
       - end_date (YYYY-MM-DD)
       
    For monthly products:
      - A prediction is returned only for dates that are the last day of the month; otherwise, predicted_quantity = 0.
    
    For weekly products:
      - For each date in the range, if the date is a Sunday then the model prediction is generated based on historical nonzero data; otherwise, predicted_quantity = 0.
    
    For frequent products:
      - Predictions are provided for every date in the range.
    
    All predicted quantities are rounded to whole numbers.
    """
    try:
        # Read query parameters; if not provided, default to next 7 days starting today.
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            start_date = datetime.today().date()
            end_date = start_date + timedelta(days=6)
        
        # Generate a list of dates within the specified range.
        date_range = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
        
        predictions_all = []
        
        # --- Monthly Models ---
        for product, model_file in monthly_models.items():
            if not os.path.exists(model_file):
                continue
            model = joblib.load(model_file)
            X_features = generate_features_for_date_range(date_range)
            preds = model.predict(X_features)
            # For each date in the range, only return a prediction if it is the last day of that month.
            for dt, pred in zip(date_range, preds):
                actual_pred = int(round(float(pred))) if is_last_day_of_month(dt) else 0
                predictions_all.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "product": product,
                    "predicted_quantity": actual_pred
                })
        
        # --- Frequent Models ---
        for product, model_file in frequent_models.items():
            if not os.path.exists(model_file):
                continue
            model = joblib.load(model_file)
            X_features = generate_frequent_features(date_range)
            preds = model.predict(X_features)
            for dt, pred in zip(date_range, preds):
                actual_pred = int(round(float(pred)))
                predictions_all.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "product": product,
                    "predicted_quantity": actual_pred
                })
        
        # --- Weekly Models ---
        for product, model_file in weekly_models.items():
            if not os.path.exists(model_file):
                continue
            model = joblib.load(model_file)
            for dt in date_range:
                # For weekly products, only generate a prediction on Sundays.
                if is_sunday(dt):
                    X_features, predicted_date_str = generate_weekly_features_for_date(product, dt)
                    if X_features is not None:
                        weekly_pred = int(round(float(model.predict(X_features)[0])))
                    else:
                        weekly_pred = 0
                else:
                    weekly_pred = 0
                predictions_all.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "product": product,
                    "predicted_quantity": weekly_pred
                })
        
        # Sort predictions by date then by product.
        predictions_all.sort(key=lambda x: (x["date"], x["product"]))
        
        return jsonify(predictions_all)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
