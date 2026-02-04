import pandas as pd

df = pd.read_csv("input.csv",index_col=0)
gen_col = [0]*8
data = {}
for i,eleve in df.iterrows():
    col = gen_col.copy()
    col[eleve["Choice1"]] = 3
    col[eleve["Choice2"]] = 2
    col[eleve["Choice3"]] = 1
    data[i] = col

df_grid = pd.DataFrame(data)
df_grid.to_csv("grid.csv")