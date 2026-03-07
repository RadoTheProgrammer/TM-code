INPUT_FILE = "grid.csv"
OUTPUT_DIR = "results2"
OUTPUT_FILE = f"{OUTPUT_DIR}/results.csv"
TM_FILE = "Donnees_TMs/Année 1/Liste sujets TM + jauge_année 1.xlsx"
N_TRIES = 1000


import os
import random
from statistics import mean
import pandas as pd
import shutil
import numpy as np

df_grid_orig = pd.read_csv(INPUT_FILE,index_col=0)

df_tm = pd.read_excel(TM_FILE,index_col=0)
df_tm = df_tm.iloc[:-1] # enlever TM libre

best_mean = 0
best_std = 0

results = {"Id":[],"Mean":[],"Std":[]}
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR,ignore_errors=True)
else:
    os.mkdir(OUTPUT_DIR)
def generate():
    global max_l2,best_mean,best_std
    # Génère une répartition aléatoire, erreur si ça échoue
    df_grid = df_grid_orig.copy()
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}
    for i_tm,tm in df_tm.sample(frac=1).iterrows():
        #print(i_tm)
        mask = df_grid[str(i_tm)] > 0

        result = df_grid[mask]
        #result.choic
        l = len(result)
        a = result[str(i_tm)]
        b = result.drop(columns=[str(i_tm)]).mean(axis=1)
        #print(result.drop(columns=[str(i_tm)]).mean(axis=1))
        #print(result[str(i_tm)])
        weights = a/b
        #if l<tm["Nmin"]
        #n = random.randrange(int(tm["Nombre maximal travaux"])+1)
        
        forced = result[b==0]
        n = int(tm["Nombre maximal travaux"])

        if n<l:
            forced = result[b.isna()]
            if len(forced):
                pass

            weights[b.isna()] = 0 
            #print(b)
            #print(b.isna())# Ceux qui n'ont pas d'autres choix
            n_to_assign = n-len(forced)
            if n_to_assign>0:
                selected2 = result.sample(n-len(forced),weights=weights)
                selected = pd.concat([forced,selected2])
            else:
                selected = forced
        else:
            selected = result
        #for eleve in result:
        #print(selected)
        #print(result)
        for i_eleve,eleve in result.iterrows():

            if i_eleve in selected.index:
                choice_weight = eleve[str(i_tm)]
                decision_data["Id"].append(i_eleve)
                decision_data["Choice"].append(i_tm)
                decision_data["ChoiceWeight"].append(choice_weight)
                df_grid.loc[i_eleve] = 0 # type: ignore
                df_grid.at[i_eleve,str(i_tm)] = choice_weight
            else:
                df_grid.at[i_eleve,str(i_tm)] = np.nan
                pass
            pass
        #df_grid.drop(selected.index,inplace=True)
        pass


    df_decision_data = pd.DataFrame(decision_data)
    if len(df_grid)==len(df_decision_data): # Succès
        df_decision_data.to_csv(f"{OUTPUT_DIR}/{i_try}.csv",index=False)
        mean = df_decision_data["ChoiceWeight"].mean()
        std = df_decision_data["ChoiceWeight"].std()
        results["Id"].append(i_try)
        results["Mean"].append(mean)
        results["Std"].append(std)
        print(f"Try {i_try}: mean={mean}, std={std}")

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
