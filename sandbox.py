import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"Donnees_TMs\Annee_1\results2\o2.csv")

def is_empty_problems(value):
    if value == []:
        return True
    if isinstance(value, str):
        b = value.strip() == "[]"
        if b:
            pass
        return b
    return False

problem_success = df['Problems'].apply(is_empty_problems)
df['SuccessRate'] = problem_success.rolling(100).mean()

plt.plot(df['Id'], df['SuccessRate'])

plt.show()