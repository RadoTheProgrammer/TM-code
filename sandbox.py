import pandas as pd

df = pd.DataFrame({"a":[],"b":[]})
c = df["a"]/df["b"]
mean = df["b"].mean()
print(mean)
print(c[0])
print(type(c[0]))
df = pd.read_csv("tm.csv",dtype={"A":str})
df = df.astype({"A":str})
print(df)
print(df.dtypes)