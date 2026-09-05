import pandas as pd

df = pd.DataFrame({"weight":[11,0.25,0,1,0,1,0.5,0.5,0.5,2.4]},index=[14,85,91,107,108,158,160,189,210,217])
print(4*max(df["weight"])/(df["weight"].sum()))
print(df.sample(4,weights=df["weight"],random_state=42))
# 14     11.00
# 85      0.25
# 91      0.00
# 107     1.00
# 108     0.00
# 158     1.00
# 160     0.50
# 189     0.50
# 210     0.50
# 217     2.40
# dtype: float64