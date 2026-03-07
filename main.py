INPUT_FILE = "grid.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "Donnees_TMs/Année 1/Liste sujets TM + jauge_année 1.xlsx"



import random
from statistics import mean
import pandas as pd


df_grid_orig = pd.read_csv(INPUT_FILE,index_col=0)

df_tm = pd.read_excel(TM_FILE,index_col=0)
df_tm = df_tm.iloc[:-1] # enlever TM libre

best_mean = 0
best_std = 0
N_TRIES = 1000
results = {"Id":[],"Mean":[],"Std":[]}
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
        print(result.mean())
        weights = result[str(i_tm)] / result.mean()
        #if l<tm["Nmin"]
        #n = random.randrange(int(tm["Nombre maximal travaux"])+1)
        n = int(tm["Nombre maximal travaux"])
        if n<l:
            selected = result.sample(n)
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
                df_grid.loc[i_eleve] = 0
                df_grid.at[i_eleve,str(i_tm)] = choice_weight
            else:
                df_grid.at[i_eleve,str(i_tm)] = 0
                pass
            pass
        #df_grid.drop(selected.index,inplace=True)
        pass


    df_decision_data = pd.DataFrame(decision_data)
    if len(df_grid)==len(df_decision_data): # Succès
        df_decision_data.to_csv(f"results/{i_try}.csv",index=False)
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
    l2 = generate()

df_results = pd.DataFrame(results)
df_results.to_csv("results.csv",index=False)
