import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor
)
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
import joblib

def parse_amount(value):
    """
    Extract numeric value from strings like '210kg'.
    Returns 0.0 if the value is missing or no number is found.
    """
    if pd.isna(value):
        return 0.0
    match = re.search(r'(\d+(\.\d+)?)', str(value))
    if match:
        return float(match.group(1))
    return 0.0

def create_date_features(df, date_col="Date"):
    """Create date-based features in the dataframe."""
    df["Day_of_Week"] = df[date_col].dt.dayofweek
    df["Month"] = df[date_col].dt.month
    df["Weekend"] = df["Day_of_Week"].isin([5, 6]).astype(int)
    df["Quarter"] = df[date_col].dt.quarter
    return df

def main():
    # 1. Load the data (update the path/filename as needed)
    data_path = "roti.xlsx"
    df = pd.read_excel(data_path)
    
    # 2. Convert date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d", errors="coerce")
    
    # 3. Parse numeric values from the "Roti Amount" column
    df["Roti_Amount"] = df["Roti Amount"].apply(parse_amount)
    
    # 4. Create date-based features
    df = create_date_features(df, date_col="Date")
    
    # 5. Define features (time-based) and target
    feature_cols = ["Day_of_Week", "Month", "Weekend", "Quarter"]
    X = df[feature_cols]
    y = df["Roti_Amount"]
    
    # 6. Time-ordered train/test split (no shuffle)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 7. Define base estimators for stacking
    lgb_model = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.03, num_leaves=31, random_state=42)
    gbr_model = GradientBoostingRegressor(n_estimators=500, learning_rate=0.03, max_depth=4, random_state=42)
    rf_model  = RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42)
    mlp_model = MLPRegressor(hidden_layer_sizes=(100, 100), max_iter=2000, random_state=42)
    
    base_estimators = [
        ('lgb', lgb_model),
        ('gbr', gbr_model),
        ('rf', rf_model),
        ('mlp', mlp_model)
    ]
    
    meta_model = Ridge(alpha=1.0)
    stacking_regressor = StackingRegressor(
        estimators=base_estimators,
        final_estimator=meta_model,
        cv=5,
        passthrough=True,
        n_jobs=-1
    )
    
    # 8. Build pipeline: scale -> polynomial -> stacked regressor (with log transform on target)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('stack', TransformedTargetRegressor(
            regressor=stacking_regressor,
            func=np.log1p,
            inverse_func=np.expm1
        ))
    ])
    
    # 9. Define hyperparameter search space for an intensive search
    param_dist = {
        'stack__regressor__lgb__n_estimators': [500, 700, 1000],
        'stack__regressor__lgb__learning_rate': [0.01, 0.03, 0.05],
        'stack__regressor__gbr__n_estimators': [500, 700, 1000],
        'stack__regressor__gbr__learning_rate': [0.01, 0.03, 0.05],
        'stack__regressor__rf__n_estimators': [300, 500, 700],
        'poly__degree': [1, 2, 3]
    }
    
    # Increase n_iter for a more exhaustive search
    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=50,  # Increase to 100+ for even more exhaustive search
        scoring="neg_mean_absolute_error",
        cv=5,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")
    random_search.fit(X_train, y_train)
    
    # 10. Evaluate best model
    best_model = random_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print("Best Hyperparameters:", random_search.best_params_)
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R^2:  {r2:.4f}")
    
    # 11. Save the final model
    model_filename = "frequent_restock_roti_model.pkl"
    joblib.dump(best_model, model_filename)
    print(f"Model saved to: {model_filename}")

if __name__ == "__main__":
    main()
