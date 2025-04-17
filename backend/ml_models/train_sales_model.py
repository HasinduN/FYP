import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
import lightgbm as lgb


#LOAD DATA AND PREPROCESSING
data_path = "./cleaned_restaurant_sales_with_closed_dates.csv"
data = pd.read_csv(data_path, parse_dates=["Date"])

#FEATURES
features = ["Day_of_Week", "Month", "Weekend", "Unit_Price", "Restaurant_Closed"]
X = data[features]
y = data["Sales"]

#TRAIN/TEST SPLIT
split_index = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]


#SET UP BASE MODELS WITH IMPROVED HYPERPARAMETERS

# Base model 1: LightGBM (gradient boosting)
lgb_model = lgb.LGBMRegressor( n_estimators=500, learning_rate=0.03, num_leaves=31, random_state=42 )

# Base model 2: Gradient Boosting Regressor
gbr_model = GradientBoostingRegressor( n_estimators=500, learning_rate=0.03, max_depth=4, random_state=42 )

# Base model 3: MLP Regressor (a neural network)
mlp_model = MLPRegressor( hidden_layer_sizes=(100, 100), activation='relu', solver='adam', max_iter=1000, random_state=42 )

estimators = [ ('lgb', lgb_model), ('gbr', gbr_model), ('mlp', mlp_model) ]

# Meta-model to combine the base learners
meta_model = Ridge(alpha=1.0)

stacking_regressor = StackingRegressor( estimators=estimators, final_estimator=meta_model, cv=5, passthrough=True, n_jobs=-1 )


# BUILD A PIPELINE WITH SCALING, POLYNOMIAL FEATURES, AND THE STACKING ENSEMBLE

pipeline = make_pipeline(
    StandardScaler(),
    # PolynomialFeatures creates interaction and quadratic terms.
    # With include_bias=False the constant term is not added (since StandardScaler already centers the data).
    PolynomialFeatures(degree=2, include_bias=False),
    stacking_regressor
)

# TRAIN THE MODEL

pipeline.fit(X_train, y_train)

# EVALUATE THE MODEL ON THE HOLD‑OUT SET
y_pred = pipeline.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("Stacking Ensemble with Polynomial Features Evaluation:")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"R-squared (R^2): {r2:.4f}")


# SAVE THE FINAL MODEL

model_path = "sales_prediction_model.pkl"
joblib.dump(pipeline, model_path)
print(f"Model saved to: {model_path}")
