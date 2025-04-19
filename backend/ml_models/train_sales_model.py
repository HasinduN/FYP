import os
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb

# 1. Load data
data_path = "../data/cleaned_restaurant_sales_with_closed_dates.csv"
df = pd.read_csv(data_path, parse_dates=["Date"])

# 2. Create date features
df["Day_of_Week"] = df["Date"].dt.dayofweek
df["Month"]       = df["Date"].dt.month
df["Weekend"]     = df["Day_of_Week"].isin([5,6]).astype(int)
# (If you want Quarter or cyclic transforms you can add here.)

# 3. Prepare output directory
os.makedirs("ml_models/sales_by_item", exist_ok=True)

# 4. Loop over each unique Item
results = []
for item in df["Item"].unique():
    # a) Filter
    item_df = df[df["Item"] == item].sort_values("Date")
    if len(item_df) < 20:
        print(f"Skipping {item!r}: only {len(item_df)} records.")
        continue

    X = item_df[["Day_of_Week", "Month", "Weekend", "Unit_Price", "Restaurant_Closed"]]
    y = item_df["Sales"]

    # b) Time‑ordered split
    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # c) Build stacking pipeline
    lgb_model = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.03,
                                  num_leaves=31, random_state=42)
    gbr_model = GradientBoostingRegressor(n_estimators=500, learning_rate=0.03,
                                          max_depth=4, random_state=42)
    mlp_model = MLPRegressor(hidden_layer_sizes=(100,100),
                             max_iter=1000, random_state=42)
    estimators = [("lgb", lgb_model), ("gbr", gbr_model), ("mlp", mlp_model)]
    meta = Ridge(alpha=1.0)

    stack = StackingRegressor(estimators=estimators,
                              final_estimator=meta,
                              passthrough=True, cv=5, n_jobs=-1)

    pipeline = make_pipeline(
        StandardScaler(),
        PolynomialFeatures(degree=2, include_bias=False),
        stack
    )

    # d) Train
    pipeline.fit(X_train, y_train)

    # e) Evaluate
    y_pred = pipeline.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print(f"{item!r} → MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")

    # f) Save model
    safe = re.sub(r"\W+", "_", item).strip("_")
    mdl_path = f"ml_models/sales_by_item/sales_model_{safe}.pkl"
    joblib.dump(pipeline, mdl_path)

    # g) Record metrics
    results.append({
        "Item": item,
        "records": len(item_df),
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "model_file": mdl_path
    })

# 5. Write out summary CSV
summary = pd.DataFrame(results).sort_values("r2", ascending=False)
summary.to_csv("ml_models/sales_by_item/sales_models_summary.csv", index=False)
print("\nAll done! Summary written to sales_models_summary.csv")
