"""
Crée la matrice d envie
"""

N_TM = 35
DUO_SEP = " + "
DIR = "Donnees_TMs/Annee_1"
import pandas as pd
import numpy as np
df = pd.read_csv(f"{DIR}/voeux_eleves.csv",index_col=0)
df.index = df.index.astype(str)
print(df.dtypes)
df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,N_TM+1))
data_duo = []
duo_repr = []
for nom_eleve,eleve in df.iterrows():

    for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
        choix = eleve[f"Choix {nchoix}"]
        
        if choix=="0":
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix>=N_TM: # TM libre
            continue
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]
        if ind_ou_duo=="Duo":
            if nom_eleve=="187":
                pass
            nom_eleve2 = str(eleve[f"Choix {nchoix} en duo avec Nom Prénom (si case cochée précédemment)"])
            assert not pd.isna(nom_eleve2)
            if isinstance(nom_eleve2,str):
                duo = [nom_eleve]
                for nom_eleve2 in nom_eleve2.split(DUO_SEP):
                    if nom_eleve2 not in df.index:
                        print(f"Nom eleve: {nom_eleve2}")
                    duo.append(nom_eleve2)
            if duo==["187","110"]:
                pass
            duo.sort() # type: ignore
            data_duo.append(((DUO_SEP.join(duo),choix))) # type: ignore
            duo_repr.append(nom_eleve)
        else:
            assert ind_ou_duo=="Individuel"
        


        df_grid.at[nom_eleve,choix] = 4-nchoix
# new_data_duo = []
# for duoc in data_duo: #duoc: duo, choix
#     if duoc in new_data_duo:
#         continue
#     new_data_duo.append(duoc)
#     count = data_duo.count(duoc)

#     assert count == duoc[0].count(DUO_SEP)+1
# df_duo = pd.DataFrame(data_duo, columns=["Duo","Choix"])
# df_duo.to_csv(f"{DIR}/duo.csv",index=False)

df_grid.to_csv(f"{DIR}/grid.csv")