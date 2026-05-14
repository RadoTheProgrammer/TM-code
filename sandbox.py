import pandas as pd
import mplcursors
import matplotlib.pyplot as plt
df = pd.read_csv(r"Donnees_TMs\Annee_1\results.csv")

plt.scatter(df["Mean"],df["Std"])
# Assuming the scatter plot is created as plt.scatter(df["Mean"], df["Std"])
# Add hover functionality
cursor = mplcursors.cursor(hover=True)

@cursor.connect("add")
def on_add(sel):
    # Get the index of the hovered point
    index = sel.index
    # Display the Id
    sel.annotation.set_text(f'Id: {df.iloc[index]["Id"]}')

plt.show()
