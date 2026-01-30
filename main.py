INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
TM_FILE = "tm.csv"

import pandas as pd

df_input = pd.read_csv(INPUT_FILE)
df_tm = pd.read_csv(TM_FILE)