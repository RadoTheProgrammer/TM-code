INPUT_FILE = "grid.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "Donnees_TMs/Année 1/Liste sujets TM + jauge_année 1.xlsx"



import random
import pandas as pd


df_grid_orig = pd.read_csv(INPUT_FILE,index_col=0)

df_tm = pd.read_excel(TM_FILE,index_col=0)
df_tm = df_tm.iloc[:-1] # enlever TM libre

N_TRIES = 1000
def generate():
    # Génère une répartition aléatoire, erreur si ça échoue
    df_grid = df_grid_orig.copy()
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}
    for i_tm,tm in df_tm.sample(frac=1).iterrows():
        #print(i_tm)
        mask = df_grid[str(i_tm)] > 0

        result = df_grid[mask]
        result.choic
        l = len(result)
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
                #df_grid.loc[i_eleve] = 0
                #df_grid.at[i_eleve,i_tm] = choice_weight
            else:
                df_grid.at[i_eleve,str(i_tm)] = 0
                pass
            pass
        df_grid.drop(selected.index,inplace=True)
        pass
    l1,l2 = len(df_grid), len(decision_data["Choice"])
    #print(l1,l2,l1+l2)
    df_decision_data = pd.DataFrame(decision_data)
    df_decision_data.sort_values(by=["Id"],inplace=True)
    return l2
    if len(df_grid)>0:
        return False # échec
    return True
    pass
generate()
max_l2 = 0
for i_try in range(N_TRIES):
    l2 = generate()
    print(l2)
    if l2>max_l2:
        max_l2 = l2
