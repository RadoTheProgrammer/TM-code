import pandas as pd
import numpy as np
import random
random.seed("hello world")
print(random.randrange(7))
df = pd.DataFrame({"a":[1,2,3,4,5,6,7],"b":[0,1,2,3,4,5,6]})
print(df.sample(1,random_state=0))
c = df["a"]/df["b"]
print(c[0]*0)
mean = df["b"].mean()
print(mean)
print(c[0])
print(type(c[0]))
df = pd.read_csv("tm.csv",dtype={"A":str})
df = df.astype({"A":str})
print(df)
print(df.dtypes)