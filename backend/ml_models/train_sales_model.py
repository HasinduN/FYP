import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import joblib

# Load the processed data
cleaned_data = pd.read_csv("E:/PROJECT/backend/data/cleaned_restaurant_sales_with_closed_dates.csv")

# Check for NaN values
print("NaN values in the data:")
print(cleaned_data.isnull().sum())

# Fill NaN values (or drop them)
cleaned_data = cleaned_data.fillna(0)  # Fill NaN with 0
# cleaned_data = cleaned_data.dropna()  # Alternatively, drop rows with NaN

# Feature selection
features = ["Day_of_Week", "Month", "Weekend", "Unit_Price", "Restaurant_Closed"]
X = cleaned_data[features]
y = cleaned_data["Sales"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
model_path = "E:/PROJECT/backend/data/sales_prediction_model.pkl"
joblib.dump(model, model_path)

print(f"Model saved to: {model_path}")

# Make predictions on the test set
y_pred = model.predict(X_test)

# Check for NaN values in y_test and y_pred
print("NaN values in y_test:", y_test.isnull().sum())
print("NaN values in y_pred:", pd.Series(y_pred).isnull().sum())

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)

print(f"Mean Absolute Error: {mae}")
print(f"Root Mean Squared Error: {rmse}")