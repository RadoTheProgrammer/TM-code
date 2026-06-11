import pandas as pd

df = pd.DataFrame({
    "Id": [1, 2, 3],
    "Mean": [0.5, 0.7, 0.3],
    "Std": [0.1, 0.2, 0.15],
    "Problems": [0, 1, 2],
    "TMnonouverts": [1, 0, 2]
})

print(df.to_dict(orient="dict"))