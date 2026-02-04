INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "tm.csv"



import random
import pandas as pd


df_grid = pd.read_csv("grid.csv",index_col=0).transpose()

df_tm = pd.read_csv(TM_FILE,index_col=0)
decision_data = {"Id":[], "Choice":[], "ChoiceWeight":[]}
N_TRIES = 1000
def generate():
    # Génère une répartition aléatoire, erreur si ça échoue
    for i_tm,tm in df_tm.sample(frac=1).iterrows():
        #print(i_tm)
        mask = df_grid[i_tm] > 0

        result = df_grid[mask]

        l = len(result)
        #if l<tm["Nmin"]
        n = random.randrange(tm["Nmax"]+1)
        if n<l:
            selected = result.sample(n)
        else:
            selected = result
        #for eleve in result:
        #print(selected)
        #print(result)
        for i_eleve,eleve in result.iterrows():

            if i_eleve in selected.index:
                decision_data["Id"].append(i_eleve)
                decision_data["Choice"].append(i_tm)
                decision_data["ChoiceWeight"].append(eleve[i_tm])

            else:
                df_grid.loc[i_eleve,i_tm] = 0
            pass
        df_grid.drop(selected.index,inplace=True)
        pass
    print(df_grid)
    return len(df_grid)
    if len(df_grid)>0:
        return False # échec
    return True
    pass
generate()
for i_try in range(N_TRIES):
    print(i_try,generate())
