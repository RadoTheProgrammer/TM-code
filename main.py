
DIR = "Donnees_TMs/Annee_1"
INPUT_FILE = f"{DIR}/grid.csv"
OUTPUT_DIR = f"{DIR}/results-none"
OUTPUT_FILE = f"{DIR}/results.csv"
TM_FILE = f"{DIR}/liste_sujets.csv"
DUO_FILE = f"{DIR}/duo.csv"
N_TRIES = 256


import os
import random
from statistics import mean
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
else:
    os.mkdir(OUTPUT_DIR)
def generate():
    global max_l2,best_mean,best_std
    # Génère une répartition aléatoire, erreur si ça échoue
    df_grid = df_grid_orig.copy()
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}
    problems = []
    for i_tm,tm in df_tm.sample(frac=1).iterrows():
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
        if len(duos):
            # Handle duo assignments
            pass
        #print(result.drop(columns=[str(i_tm)]).mean(axis=1))
        #print(result[str(i_tm)])

        weights = a/b
        n = int(tm["Nombre maximal travaux"])

        # gérer le poids des duos
        # for i_duo, duo in duos.iterrows():
        #     #print(duo)
        #     eleves = duo["Eleves"]
        #     duo_weight = 1
        #     for eleve in eleves:
        #         try:
        #             duo_weight *= weights[eleve]
        #             weights[eleve] = 0
        #         except KeyError as e: # élève déjà assigné à un TM précédent
        #             duo_weight = 0
        #             pass
        #     l-=len(duo["Eleves"])
        #     if duo_weight:
        #         l+=1
        #         weights[duo["Repr"]] = duo_weight

        #if l<tm["Nmin"]
        #n = random.randrange(int(tm["Nombre maximal travaux"])+1)
        

        
        m = tm["Nombre minimal travaux"]
        if not pd.isna(m) and l<m:
            #problems.append((i_tm,f"Not enough: {l}<{m}"))
            pass
        #print(pd.isna(m))
        if n<l:
            forced_bool = b==0

            forced = result[forced_bool]
            if len(forced):
                pass
            #print(weights)
            weights[forced_bool] = 0 
            #print(b)
            #print(b.isna())# Ceux qui n'ont pas d'autres choix
            n_to_assign = n-len(forced)

            if n_to_assign>=0:

                selected2 = result.sample(n-len(forced),weights=weights)
                selected = pd.concat([forced,selected2])
            else: # PROBLEM !!!!
                problems.append((i_tm,f"Too many: {len(forced)}>{n}"))
                selected = forced
        else:
            selected = result
        #for eleve in result:
        #print(selected)
        #print(result)
        for i_eleve,eleve in result.iterrows():
            if i_eleve==51:
                pass
            if i_eleve in selected.index:
                if i_eleve in duos["Repr"]:
                    pass
                choice_weight = eleve[str(i_tm)]
                decision_data["Id"].append(i_eleve)
                decision_data["Choice"].append(i_tm)
                decision_data["ChoiceWeight"].append(choice_weight)
                df_grid.loc[i_eleve] = np.nan # type: ignore
                df_grid.at[i_eleve,str(i_tm)] = choice_weight
            else:
                df_grid.at[i_eleve,str(i_tm)] = np.nan
                pass
            pass
        #df_grid.drop(selected.index,inplace=True)
        pass


    df_decision_data = pd.DataFrame(decision_data)
    for nom_eleve in df_grid.index:
        if nom_eleve not in decision_data["Id"]:
            print(df_grid[nom_eleve])
            print(f"Nom eleve: {nom_eleve}")

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
