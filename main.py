INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "tm.csv"



import random
import pandas as pd


df_input = pd.read_csv(INPUT_FILE)
df_tm = pd.read_csv(TM_FILE)
print(df_input)
df_input["Choice"] = 0
print(df_input["Choice"] == 0)
N_TRIES = 1000
def generate():
    # Génère une répartition aléatoire, erreur si ça échoue
    for _,tm in df_tm.sample(frac=1).iterrows():
        print(tm)
        mask = (
                (df_input["Choice1"] == tm.id) |
                (df_input["Choice2"] == tm.id) |
                (df_input["Choice3"] == tm.id)
        ) & (df_input["Choice"] == 0)
        print(mask)

        print(mask)
        result = df_input[mask]
        eleve = result.sample(1)
        print(eleve)
        df_input.loc[eleve.id]
        pass
for _ in range(N_TRIES):
    generate()