import pandas as pd
import matplotlib.pyplot as plt

# Load the cleaned inventory data
data_path = "E:/PROJECT/backend/data/standardized_inventory_data.csv"
data = pd.read_csv(data_path)

# Convert "Date" column to datetime
data["Date"] = pd.to_datetime(data["Date"])

# Set the date as the index
data.set_index("Date", inplace=True)

# **Check and Fix Non-Numeric Columns**
for column in data.columns:
    if "(Unit)" not in column:  # Ignore unit columns
        data[column] = pd.to_numeric(data[column], errors="coerce")  # Convert to numeric

# **Check for any remaining non-numeric columns**
non_numeric_cols = data.select_dtypes(exclude=["number"]).columns
if len(non_numeric_cols) > 0:
    print("⚠️ Warning: These columns are still non-numeric:", list(non_numeric_cols))

# **Plot Inventory Purchase Trends**
plt.figure(figsize=(12, 6))
for column in data.columns:
    if "(Unit)" not in column:  # Ignore unit columns
        plt.plot(data.index, data[column], label=column)

plt.xlabel("Date")
plt.ylabel("Quantity Purchased")
plt.title("Inventory Purchase Trends Over Time")
plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
plt.xticks(rotation=45)
plt.grid()
plt.show()

# **Calculate Estimated Daily Consumption**
numeric_data = data.select_dtypes(include=["number"])  # Select only numeric columns
daily_consumption = numeric_data.diff().abs().mean()  # Compute absolute daily differences

# **Remove NaN values (first row of diff() will be NaN)**
daily_consumption = daily_consumption.dropna()

# **Display estimated daily usage**
print("\n✅ Estimated Daily Consumption Rate (Avg per day):")
print(daily_consumption)
