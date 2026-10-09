import pandas as pd


for d in ["Donnees_TMs/Annee_1/results","Donnees_TMs/Annee_2/results","Annee_28/results"]:
    df = pd.read_csv(d+"/o.csv")
    df = df.sort_values("NbEnvie1")
    for idx,value in df.head(20).iterrows():
        with open(".gitignore","a") as f:
            f.write(f"\n!{d}/r{idx}.csv")
        pass