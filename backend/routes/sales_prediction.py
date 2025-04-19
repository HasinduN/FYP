from flask import Blueprint, jsonify, request
import joblib
import pandas as pd
import re
from datetime import datetime, timedelta
from models import session as db_session, MenuItem

sales_prediction_bp = Blueprint("sales_prediction", __name__)

# cache loaded models in memory to avoid repeated disk I/O
_models_cache = {}

def _safe_name(name: str) -> str:
    """Convert an arbitrary item name into a filesystem‑safe basename."""
    return re.sub(r'\W+', '_', name).strip('_')

def _get_model(item_name: str):
    """
    Load (and cache) the trained model for a given item.
    Expects the file ml_models/sales_by_item/sales_model_<safe>.pkl to exist.
    """
    if item_name in _models_cache:
        return _models_cache[item_name]
    safe = _safe_name(item_name)
    path = f"ml_models/sales_models/sales_by_item/sales_model_{safe}.pkl"
    model = joblib.load(path)
    _models_cache[item_name] = model
    return model

def _generate_dates(days: int):
    """Generate a list of datetime.date for today + next days-1."""
    today = datetime.today().date()
    return [today + timedelta(days=i) for i in range(days)]

@sales_prediction_bp.route("/predict-sales", methods=["GET"])
def predict_sales():
    """
    Returns a list of:
      { date, menu_item_id, item_name, predicted_sales }
    for each menu item and for each of the next N days (default N=3).
    
    Optional query parameter:
      ?days=5   <-- to predict 5 days instead of 3
    """
    try:
        days = int(request.args.get("days", 3))
        future_dates = _generate_dates(days)

        # pull all menu items once
        menu_items = db_session.query(MenuItem).all()
        results = []

        for mi in menu_items:
            # attempt to load the item‑specific model
            try:
                model = _get_model(mi.name)
            except FileNotFoundError:
                # no model for this item, skip
                continue

            # for each date, build the exact 5‑column input and predict
            for dt in future_dates:
                feat = pd.DataFrame([{
                    "Day_of_Week": dt.weekday(),
                    "Month":       dt.month,
                    "Weekend":     1 if dt.weekday() in (5, 6) else 0,
                    "Unit_Price":  mi.price,
                    "Restaurant_Closed": 0
                }])

                pred = model.predict(feat)[0]
                results.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "menu_item_id": mi.id,
                    "item_name": mi.name,
                    "predicted_sales": int(round(pred))
                })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
