"""
Crée la matrice d envie
"""
print("hello")
import pandas as pd

df = pd.read_excel("Donnees_TMs/Année 1/TM année 1_voeux élèves.xlsx",index_col=0)

df_grid = pd.DataFrame(0,index=df.index,columns=range(1,36))
gen_col = [0]*35
data = {}
for nom_eleve,eleve in df.iterrows():

    for nchoix in (1,2,3):
        choix = eleve[f"Choix {nchoix}"]
        if choix==0:
            continue
        df_grid.at[nom_eleve,int(choix[2:])] = 4-nchoix

df_grid.to_csv("grid.csv")