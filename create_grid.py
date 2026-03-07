"""
Crée la matrice d envie
"""

N_TM = 35
print("hello")
import pandas as pd
import numpy as np
df = pd.read_excel("Donnees_TMs/Année 1/TM année 1_voeux élèves.xlsx",index_col=0)

df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,N_TM+1))
gen_col = [0]*N_TM
data = {}
for nom_eleve,eleve in df.iterrows():

    for nchoix in (1,2,3):
        choix = eleve[f"Choix {nchoix}"]
        if choix==0:
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix==N_TM: # TM libre
            continue

        df_grid.at[nom_eleve,choix] = 4-nchoix

df_grid.to_csv("grid.csv")