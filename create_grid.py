"""
Crée la matrice d envie
"""


DUO_SEP = " + "
DIR = "Donnees_TMs/Annee_2"
TM_FILE = f"{DIR}/liste_sujets.csv"
import os
import time

import pandas as pd
import numpy as np
df = pd.read_csv(f"{DIR}/voeux_eleves.csv",index_col=0,dtype={
    "Elève":str,
    "Choix 1 en duo avec Nom Prénom (si case cochée précédemment)":str,
    "Choix 2 en duo avec Nom Prénom (si case cochée précédemment)":str,
    "Choix 3 en duo avec Nom Prénom (si case cochée précédemment)":str})
df_tm = pd.read_csv(TM_FILE,index_col=0)
n_tm = len(df_tm)
df.index = df.index.astype(str)
print(df.dtypes)
df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,n_tm+1))
df_duo = pd.DataFrame(columns=["Eleves","Choix","ElevesAccord"])
duo_repr = []
for nom_eleve,eleve in df.iterrows():

    for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
        choix = eleve[f"Choix {nchoix}"]
        
        if choix=="0":
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix>=n_tm: # TM libre
            assert choix==n_tm
            break
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]

        if ind_ou_duo=="Duo":
            if nom_eleve=="187":
                pass
            nom_eleve2 = str(eleve[f"Choix {nchoix} en duo avec Nom Prénom (si case cochée précédemment)"])
            assert not pd.isna(nom_eleve2)

            eleves = {str(nom_eleve)}
            for nom_eleve2 in nom_eleve2.split(DUO_SEP):
                if nom_eleve2 not in df.index:
                    print(f"Nom eleve: {nom_eleve2}")
                eleves.add(nom_eleve2)
            if eleves=={"117","280"}:
                pass
            #eleves.sort() # type: ignore
            #eleves = DUO_SEP.join(eleves)
            duo_bool = (df_duo["Eleves"]==eleves) & (df_duo["Choix"]==choix)
            if duo_bool.any():
                duo = df_duo[duo_bool]
                assert len(duo)==1
                duo = duo.iloc[0]

                duo["ElevesAccord"].add(nom_eleve)

            else:
                df_duo.loc[len(df_duo)]=[eleves,choix,{nom_eleve}]

        else:
            assert ind_ou_duo=="Individuel"
        


        df_grid.at[nom_eleve,choix] = 4-nchoix
for _,duo in df_duo.iterrows():
    if duo["Eleves"]!=duo["ElevesAccord"]:
        print(f"Problème duo: {duo}")

df_duo["Eleves"] = df_duo["Eleves"].apply(lambda x: " + ".join(x))
df_duo["ElevesAccord"] = df_duo["ElevesAccord"].apply(lambda x: " + ".join(x))
df_duo.to_csv(f"{DIR}/duo.csv",index=False)

df_duo.to_parquet(f"{DIR}/duo.parquet")
df_grid.to_csv(f"{DIR}/grid.csv")