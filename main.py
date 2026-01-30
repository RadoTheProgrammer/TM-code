INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "tm.csv"


a=[1,2,3,4,5]
for i in range(len(a)):
    print(next(iter(a)))


import pandas as pd

df_input = pd.read_csv(INPUT_FILE)
df_tm = pd.read_csv(TM_FILE)

N_TRIES = 1000
def generate():
    # Génère une répartition aléatoire, erreur si ça échoue
for _ in range(N_TRIES):pass