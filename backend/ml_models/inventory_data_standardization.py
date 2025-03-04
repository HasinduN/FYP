import pandas as pd

# Load cleaned data
data = pd.read_csv("E:/PROJECT/backend/data/cleaned_inventory_combined_data.csv")

# Define unit conversions to standard units (kg for weight, L for volume)
unit_conversions = {
    "g": 0.001, "kg": 1, "ml": 0.001, "L": 1, "nos": 1  # 1000g = 1kg, 1000ml = 1L
}

# Apply conversions
for col in data.columns:
    if "(Unit)" in col:
        item_col = col.replace(" (Unit)", "")  # Get corresponding amount column
        conversion_factor = data[col].map(lambda x: unit_conversions.get(x, 1))  # Get conversion factor
        data[item_col] = data[item_col] * conversion_factor  # Convert to base unit

# Drop unit columns after conversion
data = data.drop(columns=[col for col in data.columns if "(Unit)" in col])

print("\nStandardized Inventory Data (First 5 Rows):")
print(data.head())

# Save standardized data
#data.to_csv("E:/PROJECT/backend/data/standardized_inventory_data.csv", index=False)
#print("Standardized data saved successfully.")