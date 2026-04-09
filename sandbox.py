import pandas as pd

df = pd.read_csv("tm.csv",dtype={"A":str})
df = df.astype({"A":str})
print(df)
print(df.dtypes)