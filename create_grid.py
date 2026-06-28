"""
Crée la matrice d'envie, un tableau avec les élèves comme lignes et les TMs comme colonnes, 
qui indique donc pour chaque élève à quel point il a envie de ce TM
"""


DUO_SEP = " + "
DIR = "Donnees_TMs/Annee_2"
TM_FILE = f"{DIR}/liste_sujets.csv" # tableau avec les TMs, leurs langues et le nombre de places

COLUMN_IGI = "Individuel/groupe/ indifférent"  # Colonne indiquant les préférences de groupe/individuel
IGI_INDIVIDUEL ="individuel"
IGI_GROUPE = "groupe"
IGI_INDIFFERENT = "indifférent"


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
tm_libre = df_tm[df_tm["Langue"]=="Libre"]
df.index = df.index.astype(str)

# Vérifier que toutes les valeurs de la colonne IGI sont parmi les valeurs autorisées
allowed_igi = {IGI_INDIVIDUEL, IGI_GROUPE, IGI_INDIFFERENT}
if COLUMN_IGI not in df_tm.columns:
    raise ValueError(f"Colonne attendue manquante: {COLUMN_IGI}")
df_tm["Langue"] = df_tm["Langue"].str.split("/")
df_tm[COLUMN_IGI] = df_tm[COLUMN_IGI].str.lower()
unique_igi = set(df_tm[COLUMN_IGI].dropna().unique())
invalid_igi = unique_igi - allowed_igi
if invalid_igi:
    raise ValueError(f"Valeurs invalides dans la colonne '{COLUMN_IGI}': {sorted(invalid_igi)}")


df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,n_tm+1))
df_duo = pd.DataFrame(columns=["Eleves","Choix","ElevesAccord","Envies"])
duo_repr = [] # liste des représentants de duos, pour vérifier que les représentants sont bien dans les duos accordés

for nom_eleve,eleve in df.iterrows():
    n_tm_libre = 0
    for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
        choix = eleve[f"Choix {nchoix}"]
        envie = 4 - nchoix
        if choix=="0":
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix in tm_libre.index: # TM libre
            n_tm_libre+=1
            continue
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]
        langue = eleve[f"Langue (si choix proposé){indice}"]
        langue_tm = df_tm.at[choix,"Langue"]
        if langue!="0" and langue not in langue_tm:
            if choix==35:
                print(tm_libre.index)
                pass
            print(f"Attention: élève {nom_eleve} a choisi le TM {choix} avec langue '{langue}' qui ne correspond pas à la langue du TM '{langue_tm}'")
        igi = df_tm.at[choix,COLUMN_IGI]
        if igi==IGI_INDIVIDUEL:
            if ind_ou_duo!="Individuel":
                print(f"TM {choix} est marqué comme individuel mais l'élève {nom_eleve} a indiqué '{ind_ou_duo}'")
        elif igi==IGI_GROUPE:
            if ind_ou_duo!="Duo":
                print(f"TM {choix} est marqué comme groupe mais l'élève {nom_eleve} a indiqué '{ind_ou_duo}'")
        if ind_ou_duo=="Duo":

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
                duo["Envies"].add(envie)

            else:
                df_duo.loc[len(df_duo)]=[eleves,choix,{nom_eleve},{envie}]

        else:
            assert ind_ou_duo=="Individuel"
        


        df_grid.at[nom_eleve,choix] = envie

    if n_tm_libre>1:
        print(f"Eleve {nom_eleve} a {n_tm_libre} tm libre")
for _,duo in df_duo.iterrows():
    if duo["Eleves"]!=duo["ElevesAccord"]:
        print(f"Problème duo: {duo}")

df_duo["Eleves"] = df_duo["Eleves"].apply(lambda x: " + ".join(x))
df_duo["ElevesAccord"] = df_duo["ElevesAccord"].apply(lambda x: " + ".join(x))
df_duo.to_csv(f"{DIR}/duo.csv",index=False)

df_grid.to_csv(f"{DIR}/grid.csv")