import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned data
df = pd.read_csv("E:/PROJECT/backend/data/cleaned_sales_data.csv")

# Convert 'Date' column to datetime format
#df["Date"] = pd.to_datetime(df["Date"])

# Sort data by date
df = df.sort_values(by="Date")

#Plot overall sales trends
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x="Date", y="Amount_Sold", hue="Item", legend=False)
plt.title("Daily Sales Trend")
plt.xlabel("Date")
plt.ylabel("Amount Sold")
plt.xticks(rotation=45)
plt.show()

#Check summary statistics
print(df.describe())
