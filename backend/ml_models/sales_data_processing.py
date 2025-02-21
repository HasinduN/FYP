import pandas as pd

# Load dataset (ensure we are reading column names correctly)
file_path = "E:/PROJECT/backend/data/sales_data.xlsx"
df = pd.read_excel(file_path, skiprows=0)

# Print first few rows for debugging
print("Raw Data Preview:\n", df.head())

# Fix column names by removing extra spaces and newlines
df.columns = [col.replace("\nAmount", "").strip() for col in df.columns]

# Rename 'Unit price' column correctly
df.rename(columns={"Unit price": "Unit_Price"}, inplace=True)

# Debug: Print new column names
print("Cleaned Column Names:", df.columns.tolist())

# Check if "Item" and "Unit_Price" exist
if "Item" not in df.columns or "Unit_Price" not in df.columns:
    print("Error: 'Item' or 'Unit_Price' columns are missing!")
    exit()

# Melt the DataFrame to convert dates into rows
df_melted = df.melt(id_vars=["Item", "Unit_Price"], var_name="Date", value_name="Amount_Sold")

# Convert "Date" column to datetime format
df_melted["Date"] = pd.to_datetime(df_melted["Date"], errors='coerce')

# Convert "Amount_Sold" to numeric
df_melted["Amount_Sold"] = pd.to_numeric(df_melted["Amount_Sold"], errors='coerce')

# Drop missing values
df_melted.dropna(inplace=True)

# Save cleaned data
df_melted.to_csv("E:/PROJECT/backend/data/cleaned_sales_data.csv", index=False)

# Print success message
print("Data Cleaning Completed! Cleaned dataset saved.")
print(df_melted.head())
