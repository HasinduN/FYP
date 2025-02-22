import pandas as pd

# Load the data
data = pd.read_excel("E:/PROJECT/backend/data/sales_data.xlsx")

data.columns = data.columns.str.replace(r"\s*Amount\s*", "", regex=True).str.strip()

# Reshape the data to long format
long_data = data.melt(id_vars=["Item", "Unit_Price"], var_name="Date", value_name="Sales")

long_data["Date"] = pd.to_datetime(long_data["Date"], format="%m/%d/%Y", errors="coerce")

# Group by date and check if all sales are 0
closed_dates = long_data.groupby("Date")["Sales"].sum() == 0
closed_dates = closed_dates[closed_dates].index.tolist()

# Add a "Restaurant_Closed" column to mark closed dates
long_data["Restaurant_Closed"] = long_data["Date"].isin(closed_dates).astype(int)

# Extract day of the week and month
long_data["Day_of_Week"] = long_data["Date"].dt.dayofweek
long_data["Month"] = long_data["Date"].dt.month

long_data["Weekend"] = long_data["Day_of_Week"].isin([5, 6]).astype(int)

print(long_data.head())

# Save the cleaned data to the specified directory
#output_path = "E:/PROJECT/backend/data/cleaned_restaurant_sales_with_closed_dates.csv"
#long_data.to_csv(output_path, index=False)

#print(f"Cleaned data saved")