import pandas as pd
import numpy as np
import re
import os
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import joblib
import lightgbm as lgb

def parse_amount(value_str):
    """Extract numeric value from strings like '120kg' or '20L'."""
    if pd.isna(value_str):
        return 0.0
    match = re.search(r'(\d+(\.\d+)?)', str(value_str))
    if match:
        return float(match.group(1))
    return 0.0

def create_date_features(df, date_col="Date"):
    """Create date-based features: Day_of_Week, Month, Weekend, Quarter."""
    df["Day_of_Week"] = df[date_col].dt.dayofweek
    df["Month"] = df[date_col].dt.month
    df["Weekend"] = df["Day_of_Week"].isin([5, 6]).astype(int)
    df["Quarter"] = df[date_col].dt.quarter
    return df

def train_and_evaluate_improved(df, product_col, results_list):
    """
    For a given product column:
      - Filter out rows with zero values.
      - Create features from the Date.
      - Train a stacking ensemble (with log transformation on target)
        using a pipeline with scaling and polynomial features.
      - Use RandomizedSearchCV to tune hyperparameters.
      - Evaluate and save the model.
    """
    # Filter non-zero rows for the target product
    prod_df = df[df[product_col] != 0].copy()
    if len(prod_df) < 10:
        print(f"[WARNING] Not enough non-zero data points for {product_col}, skipping.")
        return

    # Feature columns (you can add more if available)
    feature_cols = ["Day_of_Week", "Month", "Weekend", "Quarter"]
    X = prod_df[feature_cols]
    # We'll log-transform the target (using log1p) to reduce skewness.
    y = prod_df[product_col]

    # Use a time-ordered split (or random split if time order is less critical)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # --- Define base models ---
    lgb_model = lgb.LGBMRegressor(
        n_estimators=500,
        learning_rate=0.03,
        num_leaves=31,
        random_state=42
    )
    gbr_model = GradientBoostingRegressor(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=4,
        random_state=42
    )
    rf_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        random_state=42
    )
    mlp_model = MLPRegressor(
        hidden_layer_sizes=(100, 100),
        max_iter=1500,
        random_state=42
    )

    # Stacking ensemble with these base models and Ridge as meta-model.
    base_estimators = [
        ('lgb', lgb_model),
        ('gbr', gbr_model),
        ('rf', rf_model),
        ('mlp', mlp_model)
    ]
    meta_model = Ridge(alpha=1.0)
    stacking_estimator = StackingRegressor(
        estimators=base_estimators,
        final_estimator=meta_model,
        cv=5,
        passthrough=True,
        n_jobs=-1
    )

    # --- Build a pipeline ---
    # The pipeline applies scaling and polynomial feature expansion before the regressor.
    # We wrap the stacking ensemble with a TransformedTargetRegressor to apply log1p transformation.
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('stack', TransformedTargetRegressor(
            regressor=stacking_estimator,
            func=np.log1p,
            inverse_func=np.expm1
        ))
    ])

    # --- Hyperparameter tuning ---
    # Define parameter distributions for tuning the stacking regressor's base estimators.
    param_dist = {
        # You can tune parameters for the base estimators via the pipeline.
        # Note: Parameters are referenced using the estimator names.
        'stack__regressor__lgb__n_estimators': [500, 700, 1000],
        'stack__regressor__lgb__learning_rate': [0.01, 0.03, 0.05],
        'stack__regressor__gbr__n_estimators': [500, 700, 1000],
        'stack__regressor__gbr__learning_rate': [0.01, 0.03, 0.05],
        'stack__regressor__rf__n_estimators': [300, 500, 700],
        'poly__degree': [1, 2, 3]  # also let polynomial degree vary
    }

    search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=30,
        scoring="neg_mean_absolute_error",
        cv=3,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )

    print(f"Training model for {product_col} with {len(X_train)} training samples...")
    search.fit(X_train, y_train)
    best_model = search.best_estimator_

    # --- Evaluation ---
    y_pred = best_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"Product: {product_col}")
    print(f"  Best Params: {search.best_params_}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R^2:  {r2:.4f}\n")

    # Save model (naming file by product column)
    safe_col = product_col.replace(" ", "_").replace("/", "_")
    model_filename = f"monthly_model_{safe_col}.pkl"
    joblib.dump(best_model, model_filename)

    # Append results to the list
    results_list.append({
        "product": product_col,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    })

def main():
    # Load monthly restocked products data (update the file path as needed)
    data_path = "monthly_products.xlsx"
    df = pd.read_excel(data_path)
    
    # Convert the Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d", errors="coerce")
    
    # List of product columns to model
    product_columns = [
        "Salt Amount",
        "Pepper Amount",
        "Chilie flakes Amount",
        "Cheese Amount",
        "Fresh milk Amount",
        "Sesame oil Amount",
        "Tomato ketchup Amount",
        "Dark sauce Amount",
        "Oyster sauce Amount"
    ]
    
    # Parse the product amount strings into numeric values
    for col in product_columns:
        df[col] = df[col].apply(parse_amount)
    
    # Create date features
    df = create_date_features(df, date_col="Date")
    
    results = []
    for product in product_columns:
        train_and_evaluate_improved(df, product, results)
    
    # Save a summary of model metrics
    results_df = pd.DataFrame(results)
    summary_filename = "monthly_products_model_summary.csv"
    results_df.to_csv(summary_filename, index=False)
    print("\nSummary of model evaluations:")
    print(results_df)

if __name__ == "__main__":
    main()
