import pandas as pd


for d in ["Donnees_TMs/Annee_2/results"]:
    df = pd.read_csv(d+"/o.csv")
    df1 = df[df["Old"]==1].sort_values("NbEnvie1")
    df2 = df[df["Old"]==0].sort_values("NbEnvie1")
    
    for idx,value in df1.head(20).iterrows():
        with open(".gitignore","a") as f:
            f.write(f"\n!{d}/r{idx}.csv")
        pass
    for idx,value in df2.head(20).iterrows():
        with open(".gitignore","a") as f:
            f.write(f"\n!{d}/r{idx}.csv")
        pass