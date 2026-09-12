import pandas as pd

OUTPUT_FILE = r"Donnees_TMs\Annee_2\resultslearned2\o.csv"

df = pd.read_csv(OUTPUT_FILE)
sum_mean = df["Mean"].sum()
sum_std = df["Std"].sum()
print(sum_mean/sum_std)
df["Value"] = (df["Mean"]/sum_mean - df["Std"]/sum_std)

df.to_csv(OUTPUT_FILE,index=False)
pass
# fréquence relative