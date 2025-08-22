import pandas as pd

# Load CSV as dataframe
df = pd.read_csv("example.csv")
print(df)

# Peek into raw structure
with open("example.csv", "r") as f:
    print(f.read())
