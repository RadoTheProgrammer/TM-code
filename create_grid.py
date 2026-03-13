"""
Crée la matrice d envie
"""

N_TM = 33

import pandas as pd
import numpy as np
df = pd.read_excel("Donnees_TMs/Année 2/TM année 2_voeux élèves.xlsx",index_col=0)

df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,N_TM+1))
data_duo = []
duo_repr = []
for nom_eleve,eleve in df.iterrows():

    for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
        choix = eleve[f"Choix {nchoix}"]
        
        if choix==0:
            df_grid.drop(nom_eleve, inplace=True)
            break
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]
        if ind_ou_duo=="Duo":
            
            nom_eleve2 = eleve[f"Choix {nchoix} en duo avec Nom Prénom (si case cochée précédemment)"]
            if nom_eleve2 in duo_repr:
                # déjà traité en tant que Eleve2
                assert (nom_eleve2, nom_eleve, choix) in data_duo
                continue
            assert not pd.isna(nom_eleve2)
            data_duo.append((nom_eleve, nom_eleve2, choix))
            duo_repr.append(nom_eleve)
        else:
            assert ind_ou_duo=="Individuel"
        
        choix = int(choix[2:])
        if choix==N_TM: # TM libre
            continue

        df_grid.at[nom_eleve,choix] = 4-nchoix

df_duo = pd.DataFrame(data_duo, columns=["Eleve1","Eleve2","Choix"])
df_duo.to_csv("duo.csv",index=False)
df_grid.to_csv("grid.csv")