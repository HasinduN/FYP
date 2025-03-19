import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import numpy as np
import os

# Load standardized inventory data
data_path = "E:/PROJECT/backend/data/standardized_inventory_data.csv"
data = pd.read_csv(data_path)

# Convert "Date" to datetime and extract features
data["Date"] = pd.to_datetime(data["Date"])
data["Day_of_Week"] = data["Date"].dt.dayofweek
data["Month"] = data["Date"].dt.month
data["Weekend"] = data["Day_of_Week"].isin([5, 6]).astype(int)

# Drop Date column since it's not a numerical feature
data = data.drop(columns=["Date"])

# Define features (X) and target variables (y)
features = ["Day_of_Week", "Month", "Weekend"]
X = data[features]  # Only use date-related features for prediction
y = data.drop(columns=features)  # Predict all inventory items at once

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Multi-Output Random Forest model
rf_model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
rf_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_model.predict(X_test)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred, multioutput="uniform_average")
rmse = np.sqrt(mean_squared_error(y_test, y_pred, multioutput="uniform_average"))
r2 = r2_score(y_test, y_pred, multioutput="uniform_average")

print("\nModel Performance:")
print(f"   - MAE: {mae:.4f}")
print(f"   - RMSE: {rmse:.4f}")
print(f"   - R² Score: {r2:.4f}")

# Save the trained model
model_path = "E:/PROJECT/backend/ml_models/inventory_prediction_model.pkl"
joblib.dump(rf_model, model_path)
print(f"\nModel saved successfully at: {model_path}")