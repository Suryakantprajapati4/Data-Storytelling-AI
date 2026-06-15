import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np

np.random.seed(42)
n = 500

dates = pd.date_range("2023-01-01", periods=n, freq="D")
regions = np.random.choice(["North", "South", "East", "West"], n, p=[0.38, 0.22, 0.25, 0.15])
categories = np.random.choice(["Electronics", "Clothing", "Food", "Furniture", "Sports"], n, p=[0.30, 0.25, 0.20, 0.15, 0.10])
orders = np.random.randint(1, 50, n)
revenue = orders * np.random.uniform(20, 200, n) * np.where(categories == "Electronics", 2.5, 1)
profit = revenue * np.random.uniform(0.05, 0.35, n)
customers = np.random.randint(1, 30, n)

df = pd.DataFrame({
    "Date": dates,
    "Region": regions,
    "Category": categories,
    "Orders": orders,
    "Revenue": np.round(revenue, 2),
    "Profit": np.round(profit, 2),
    "Customers": customers,
})

df.to_csv(os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv"), index=False)
print(f"Created sample_sales.csv with {len(df)} rows")
