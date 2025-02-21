import pandas as pd


df = pd.read_excel("stock_data.csv") 
df["sale_date"] = pd.to_datetime(df["sale_date"])
df.set_index("sale_date", inplace=True)

print(df.head())
