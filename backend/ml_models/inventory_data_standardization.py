import pandas as pd

# Load cleaned data
data = pd.read_csv("E:/PROJECT/backend/data/cleaned_inventory_combined_data.csv")

# Define unit conversions to standard units (kg for weight, L for volume)
unit_conversions = {
    "g": 0.001, "kg": 1, "ml": 0.001, "L": 1, "nos": 1,  
    "": 1  # Default to 1 if unit is missing (assumes pieces/nos)
}

# Apply conversions
for col in data.columns:
    if "(Unit)" in col:
        item_col = col.replace(" (Unit)", "")  # Get corresponding amount column
        data[col] = data[col].fillna("")  # Ensure no NaN values in unit column
        conversion_factor = data[col].map(lambda x: unit_conversions.get(x, 1))  # Get conversion factor
        data[item_col] = data[item_col] * conversion_factor  # Convert to base unit

# Drop unit columns after conversion
data = data.drop(columns=[col for col in data.columns if "(Unit)" in col])

# Save the standardized data
data.to_csv("E:/PROJECT/backend/data/standardized_inventory_data.csv", index=False)

print("\nStandardized Data Processing Completed!")
print(data.head())  # Show first few rows