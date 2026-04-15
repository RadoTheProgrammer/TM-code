import pandas as pd
import numpy as np
import random
random.seed("hello world")
print(random.randrange(7))
print(random.randrange(7))
random.seed("hello world")
print(random.randrange(7))
print(random.randrange(7))
df = pd.DataFrame({"a":list("ABCDEFGH"),"b":list("12345678")})
a = df["a"]
a[a.index.intersection([1,3])] = 0
print(a)
print(1 in df["a"])
rng = np.random.default_rng(42)
print(type(rng))
print(df.sample(n=8,random_state=rng))
print(df.sample(n=8,random_state=rng))
print(df.sample(n=8,random_state=rng))
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
"""
Changement de plan: df_grid 0 everywhere ? weights>=0, might take even more time
-> solve duo inf*0 problem
yes:
* might be simpler for preselection
* no need of default thing, reindex and whats not

no:
* don't have to rechange everything

which is faster?
"""