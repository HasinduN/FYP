import pandas as pd

# Load past inventory data
df = pd.read_csv("stock_data.csv")  # Replace with your actual file
df["sale_date"] = pd.to_datetime(df["sale_date"])  # Convert to datetime
df.set_index("sale_date", inplace=True)  # Set date as index

print(df.head())  # Check data format
