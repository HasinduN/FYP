import pandas as pd

# Load the data
data = pd.read_excel("E:/PROJECT/backend/data/stock_data.xlsx")

# Replace ArrayFormula objects with NaN or 0
data = data.apply(lambda col: col.map(lambda x: 0 if isinstance(x, object) and "ArrayFormula" in str(x) else x))

# Fill missing values with 0
data = data.fillna(0)

# Convert the "Date" column to datetime format
data["Date"] = pd.to_datetime(data["Date"])

# function to extract numeric values and units
import re

def extract_numeric_and_unit(x):
    if isinstance(x, str):
        match = re.match(r"([-+]?\d*\.?\d+)\s*([a-zA-Z]*)", x)  # Extract number and unit
        if match:
            numeric_value = float(match.group(1))  # Extracted number
            unit = match.group(2) if match.group(2) else None  # Extracted unit
            return numeric_value, unit
    return x, None

# Apply function to all columns except "Date"
numeric_data = data.copy()
unit_data = pd.DataFrame(index=data.index)

for col in data.columns:
    if col != "Date":
        numeric_data[col], unit_data[col] = zip(*data[col].map(extract_numeric_and_unit))

# Merge numeric data with unit data
for col in unit_data.columns:
    if col != "Date":
        numeric_data[col + " (Unit)"] = unit_data[col]

# Display the cleaned data
print("Combined Data:")
print(numeric_data.head())

# Save the cleaned data
numeric_data.to_csv("E:/PROJECT/backend/data/cleaned_inventory_combined_data.csv", index=False)
print("Combined data saved successfully.")
