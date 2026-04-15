import pandas as pd

DIR = "Donnees_TMs/Annee_1"
GRID_FILE = f"{DIR}/grid.csv"
TM_FILE = f"{DIR}/liste_sujets.csv"
DUO_FILE = f"{DIR}/duo.csv"

RESULT_FILE = "Donnees_TMs/Annee_1/results/r0.csv"

df_grid = pd.read_csv(GRID_FILE,index_col=0)
df_grid.index = df_grid.index.astype(str)

df_tm = pd.read_csv(TM_FILE,index_col=0)
df_tm = df_tm.iloc[:-1] # enlever TM libre

df_result = pd.read_csv(RESULT_FILE,index_col=0)
df_result.index = df_result.index.astype(str)

df_duo = pd.read_csv(DUO_FILE)
df_duo["Eleves"] = df_duo["Eleves"].str.split(r" \+ ")
df_duo["Repr"] = df_duo["Eleves"].str[0]

for nom_eleve,eleve in df_grid.iterrows():
    eleve_result = df_result.loc[nom_eleve]

    if not isinstance(eleve_result,pd.Series):
        print(f"{nom_eleve} a {len(eleve_result)} TMs")
        if not l:
            continue
        eleve_result = eleve_result.iloc[0]
    envie = eleve_result["ChoiceWeight"]
    if envie<=0:
        print(f"{nom_eleve} a {envie} envie")
    tm = int(eleve_result["Choice"])
    #print(eleve)
    envie_attendu = eleve[str(tm)]
    if envie!=envie_attendu:
        print(f"{nom_eleve} a {envie_attendu} envie pour {tm}, pas {envie}")

for i_tm,tm in df_tm.iterrows():
    maximum = int(tm["Nombre maximal travaux"])
    minimum = tm["Nombre minimal travaux"]
    eleves = df_result[df_result["Choice"]==i_tm]
    duos = df_duo[df_duo["Choix"]==i_tm]
    #print(duos)
    #duos = duos[duos["Repr"] in eleves.index]
    n = len(eleves)
    for _,duo in duos.iterrows():
        if duo["Repr"] not in eleves.index:
            continue
        duo:pd.DataFrame
        selected = pd.Series(duo["Eleves"]).isin(eleves.index)
        if selected.all():
            if i_tm==4:
                print(len(selected))
                pass
            n-=len(selected)-1
        elif not ~selected.all():
            print(f"Duo inaccuracy: {selected}")
        

    
    
    if n>maximum:
        print(f"Trop d'élèves pour {i_tm}: {n}>{maximum}")
    elif not pd.isna(minimum) and n<minimum:
        if n==0:
            print(f"(TM non ouvert: {i_tm})")
        else:
            print(f"Pas assez d'élèves pour {i_tm}: {n}<{minimum}")