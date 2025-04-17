import pandas as pd
import numpy as np
import re
import joblib
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor

# -------------------------------
# 1. Load and Clean the Weekly Data
# -------------------------------
data_path = "weekly_products.xlsx"  # Update this with the actual path to your Excel file
df = pd.read_excel(data_path, parse_dates=["Date"])

print("Shape before cleaning:", df.shape)

# Identify product columns (all columns except 'Date')
product_cols = df.columns.drop("Date")

# Convert product columns (e.g., "300kg", "100L") to numeric values by extracting the numeric part
for col in product_cols:
    df[col] = df[col].astype(str).str.extract(r'(\d+\.?\d*)')[0]
    df[col] = pd.to_numeric(df[col], errors='coerce')

print("Shape after cleaning:", df.shape)

# -------------------------------
# 2. Initialize a List to Store Evaluation Results
# -------------------------------
results = []

# -------------------------------
# 3. Loop Over Each Product Column to Train a Model
# -------------------------------
for product in product_cols:
    # Filter out rows where the product's value is zero or missing
    df_prod = df[df[product] != 0].dropna(subset=[product]).copy()
    if df_prod.empty:
        print(f"No non-zero data for {product}. Skipping...")
        continue

    # Sort by date (important for time‐series splits)
    df_prod.sort_values("Date", inplace=True)
    
    # -------------------------------
    # 3a. Create Time‐Based and Lag Features
    # -------------------------------
    df_prod["Year"] = df_prod["Date"].dt.year
    df_prod["Month"] = df_prod["Date"].dt.month
    df_prod["Week"] = df_prod["Date"].dt.isocalendar().week.astype(int)
    df_prod["DayOfWeek"] = df_prod["Date"].dt.dayofweek
    # Create a sequential time index
    df_prod["TimeIndex"] = np.arange(len(df_prod))
    
    # Create lag features (lags 1 to 4)
    for lag in range(1, 5):
        df_prod[f"lag_{lag}"] = df_prod[product].shift(lag)
    
    # Create rolling statistics on lag_1 (rolling mean and std with windows 3 and 5)
    df_prod["roll_mean_3"] = df_prod["lag_1"].rolling(window=3).mean()
    df_prod["roll_std_3"] = df_prod["lag_1"].rolling(window=3).std()
    df_prod["roll_mean_5"] = df_prod["lag_1"].rolling(window=5).mean()
    df_prod["roll_std_5"] = df_prod["lag_1"].rolling(window=5).std()
    
    # Drop rows with NaN values introduced by lags and rolling calculations
    df_prod.dropna(inplace=True)
    
    # -------------------------------
    # 3b. Define Features and Target
    # -------------------------------
    feature_cols = ["TimeIndex", "Year", "Month", "Week", "DayOfWeek", 
                    "lag_1", "lag_2", "lag_3", "lag_4", 
                    "roll_mean_3", "roll_std_3", "roll_mean_5", "roll_std_5"]
    X = df_prod[feature_cols]
    y = df_prod[product]
    
    # -------------------------------
    # 4. Time-Ordered Train/Test Split (80% train, 20% test)
    # -------------------------------
    split_index = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    
    # -------------------------------
    # 5. Extended Hyperparameter Tuning for GradientBoostingRegressor
    # -------------------------------
    param_grid = {
        "n_estimators": [200, 300, 500, 750, 1000, 1500, 2000],
        "max_depth": [2, 3, 4, 5, 6, 7, 8],
        "learning_rate": [0.005, 0.01, 0.03, 0.05, 0.1],
        "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
        "min_samples_split": [2, 3, 4, 5, 10],
        "min_samples_leaf": [1, 2, 3, 4, 5]
    }
    
    # Build a pipeline that scales features and trains the regressor
    pipeline = make_pipeline(
        StandardScaler(),
        GradientBoostingRegressor(random_state=42)
    )
    
    # Use TimeSeriesSplit for cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Use RandomizedSearchCV with 200 iterations for an exhaustive search
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions={"gradientboostingregressor__" + k: v for k, v in param_grid.items()},
        n_iter=200,
        cv=tscv,
        scoring="neg_mean_absolute_error",
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    print(f"\nTraining model for {product} with extended training...")
    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    
    # -------------------------------
    # 6. Evaluate the Model on the Hold-Out Set
    # -------------------------------
    y_pred = best_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Evaluation for {product}:")
    print(f"  MAE : {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R^2 : {r2:.4f}")
    
    results.append({
        "product": product,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    })
    
    # -------------------------------
    # 7. Save the Best Model for This Product
    # -------------------------------
    safe_product = re.sub(r'\s+', '_', product)  # Replace spaces with underscores
    model_filename = f"weekly_model_{safe_product}.pkl"
    joblib.dump(best_model, model_filename)
    print(f"Model saved to: {model_filename}")

# -------------------------------
# 8. Print Summary of Evaluation Metrics for All Products
# -------------------------------
results_df = pd.DataFrame(results)
print("\nSummary of model evaluations:")
print(results_df)
