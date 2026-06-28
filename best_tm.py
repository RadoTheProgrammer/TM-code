DIR = "Donnees_TMs/Annee_2"
INPUT_FILE = f"{DIR}/grid.csv" 

import pandas as pd

df_grid = pd.read_csv(INPUT_FILE, index_col=0)  # Charger la grille originale
df_grid.index = df_grid.index.astype(str)  # Convertir les indices en chaînes

print(df_grid.sum(axis=0).sort_values(ascending=False))