
DIR = "Donnees_TMs/Annee_1"
INPUT_FILE = f"{DIR}/grid.csv"
OUTPUT_DIR = f"{DIR}/results"
OUTPUT_FILE = f"{DIR}/results.csv"
TM_FILE = f"{DIR}/liste_sujets.csv"
DUO_FILE = f"{DIR}/duo.csv"
N_TRIES = 256

RANDOM_STATE = 0

import os
import random
import pandas as pd
import shutil
import numpy as np

df_grid_orig = pd.read_csv(INPUT_FILE,index_col=0)
df_grid_orig.index = df_grid_orig.index.astype(str)
df_tm = pd.read_csv(TM_FILE,index_col=0)
df_tm = df_tm.iloc[:-1] # enlever TM libre

df_duo = pd.read_csv(DUO_FILE)
df_duo["Eleves"] = df_duo["Eleves"].str.split(r" \+ ")
df_duo["Repr"] = df_duo["Eleves"].str[0]
results = {"Id":[],"Mean":[],"Std":[],"Problems":[]}
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR,ignore_errors=True)

os.mkdir(OUTPUT_DIR)
def generate():
    global max_l2,best_mean,best_std
    # Génère une répartition aléatoire, erreur si ça échoue
    df_grid = df_grid_orig.copy()
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}
    problems = []
    for i_tm,tm in df_tm.sample(frac=1,random_state=RANDOM_STATE).iterrows():
        #print(i_tm)
        col = df_grid[str(i_tm)]
        mask = df_grid[str(i_tm)] > 0

        result = df_grid[mask]
        #result.choic
        l = len(result)
        
        a = result[str(i_tm)]
        result1 = result.drop(columns=[str(i_tm)])

        b = result1.sum(axis=1)
        duos = df_duo[df_duo["Choix"]==i_tm]
        #print("l",len(result),len(duos))
        if len(duos):
            # Handle duo assignments
            pass
        #print(result.drop(columns=[str(i_tm)]).mean(axis=1))
        #print(result[str(i_tm)])

        weights = a/b
        n = int(tm["Nombre maximal travaux"])

        #gérer le poids des duos
        problem = False
        eleves_duos = set()
        for i_duo, duo in duos.iterrows():
            #print(duo)
            eleves = duo["Eleves"]
            duo_weight = 1
            for eleve in eleves:
                eleves_duos.add(eleve)
                if eleve=="119":
                    problem = True
                    eleve_data = df_grid.loc[eleve]
                    print(eleve_data[eleve_data>0])
                    pass
                try:
                    #print(duo_weight,weights[eleve])
                    if duo_weight==0 and weights[eleve]==np.inf:
                        problems.append(f"{eleve} non attribué")
                        print(problems[-1])
                        decision_data["Id"].append(eleve)
                        decision_data["Choice"].append(0)
                        decision_data["ChoiceWeight"].append(0)
                        duo_weight = 0
                    else:
                        duo_weight *= weights[eleve]

                        
                    weights[eleve] = 0
                except KeyError as e: # élève déjà assigné à un TM précédent
                    # attention avec l<n
                    if duo_weight==np.inf:
                        # WARNING !!!
                        duo_weight = 0
                        pass
                    duo_weight *= 0
                    pass


            if duo_weight:

                weights[duo["Repr"]] = duo_weight

        l = len(weights[weights!=0]) 

        #if l<tm["Nmin"]
        #n = random.randrange(int(tm["Nombre maximal travaux"])+1)
        

        
        m = tm["Nombre minimal travaux"]
        if not pd.isna(m) and l<m:
            #problems.append((i_tm,f"Not enough: {l}<{m}"))
            pass
        #print(pd.isna(m))
        if n<l:
            forced_bool = weights==np.inf

            forced = result[forced_bool]
            if i_tm==4:
                pass
            if len(forced):
                pass
            #print(weights)
            weights[forced_bool] = 0 
            #print(b)
            #print(b.isna())# Ceux qui n'ont pas d'autres choix
            n_to_assign = n-len(forced)

            if n_to_assign>=0:

                selected2 = result.sample(n-len(forced),weights=weights,random_state=RANDOM_STATE)
                selected = pd.concat([forced,selected2])
            else: # PROBLEM !!!!
                problems.append((i_tm,f"Too many: {len(forced)}>{n}"))
                selected = forced
        else:
            if i_tm==4:
                pass
            selected = result[weights!=0]
        #for eleve in result:
        #print(selected)
        #print(result)
        repr = duos["Repr"].values
        for nom_eleve_repr,eleve in result.iterrows():
            if nom_eleve_repr in eleves_duos and nom_eleve_repr not in repr:
                if nom_eleve_repr in duos["Repr"]:
                    pass
                if nom_eleve_repr=="119":
                    print(duos["Repr"].values)
                    pass
                continue
                pass

            sel_duos = duos[duos["Repr"]==nom_eleve_repr]
            if sel_duos.empty:
                eleves = [nom_eleve_repr]
            else:
                assert len(sel_duos)==1,f"{len(sel_duos)} duos pour {nom_eleve_repr} TM {i_tm}"
                duo = sel_duos.iloc[0]
                eleves = duo["Eleves"]
            is_selected = nom_eleve_repr in selected.index.values
            print(selected.index)
            for nom_eleve in eleves:
                if (nom_eleve=="33") and (i_tm==7):
                    pass
                if is_selected:
                    choice_weight = eleve[str(i_tm)]
                    #assert nom_eleve not in decision_data["Id"]
                    decision_data["Id"].append(nom_eleve)
                    decision_data["Choice"].append(i_tm)
                    decision_data["ChoiceWeight"].append(choice_weight)
                    df_grid.loc[nom_eleve] = np.nan # type: ignore
                    df_grid.at[nom_eleve,str(i_tm)] = choice_weight
                else:
                    df_grid.at[nom_eleve,str(i_tm)] = np.nan
                pass
            pass
        #df_grid.drop(selected.index,inplace=True)
        pass


    df_decision_data = pd.DataFrame(decision_data)
    for nom_eleve in df_grid.index:
        if nom_eleve not in decision_data["Id"]:
            #print(df_grid.loc[nom_eleve])
            print(f"Nom eleve: {nom_eleve}")
    df_decision_data.to_csv("decision-data.csv")
    print(df_decision_data["Id"].value_counts())
            # 119 91
    #print(df_decision_data)
    if len(df_grid)==len(df_decision_data): # Succès
        df_decision_data.to_csv(f"{OUTPUT_DIR}/r{i_try}.csv",index=False)
        mean = df_decision_data["ChoiceWeight"].mean()
        std = df_decision_data["ChoiceWeight"].std()
        results["Id"].append(i_try)
        results["Mean"].append(mean)
        results["Std"].append(std)
        results["Problems"].append(problems)
        print(f"Try {i_try}: mean={mean}, std={std}, problems={problems}")

        pass
    else:
        print(len(df_grid))
        print(len(df_decision_data))
    if len(df_grid)>0:
        return False # échec
    return True
    pass

max_l2 = 0
for i_try in range(N_TRIES):
    print(i_try)
    l2 = generate()

df_results = pd.DataFrame(results)
df_results.to_csv(OUTPUT_FILE,index=False)
