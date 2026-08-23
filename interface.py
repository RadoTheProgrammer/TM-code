import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import algorithme
import json


settings_description = {
    "GRID_FILE": "Fichier CSV contenant la grille des élèves.",
    "TM_FILE": "Fichier CSV contenant les travaux de maturité.",
    "DUO_FILE": "Fichier CSV contenant les binômes d'élèves.",
    "NPROBLEMS_ELEVES_FILE": "Fichier CSV contenant le nombre de problèmes par élève.",
    "NPROBLEMS_TM_FILE": "Fichier CSV contenant le nombre de problèmes par TM.",
    "OUTPUT_DIR": "Répertoire où seront enregistrés les résultats.",
    "OUTPUT_FILE": "Fichier CSV où seront enregistrés les résultats.",
    "RANDOM_SEED": "Graine pour le générateur aléatoire (entier).",
}

class SettingsEditor:
    def __init__(self, master:tk.Tk):
        self.master = master
        self.master.title("TM Settings")
        self.master.geometry("760x520")
        self.master.minsize(700, 420)

        self.original_values = {}
        self.fields = {}

        self._load_original_values()

        main = ttk.Frame(master, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Paramètres du projet", font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        # Container for all setting rows; placing it inside the canvas makes the
        # form scrollable while keeping the scrollbar attached to the canvas.
        self.form_frame = ttk.Frame(canvas)

        self.form_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_form()

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="Générer", command=self.generate).pack(side="right")
        ttk.Button(actions, text="Fermer", command=self.master.destroy).pack(side="right", padx=(0, 8))

    def _load_original_values(self):
        with open("settings.json", "r") as f:
            self.original_values = json.load(f)

    def _is_file_setting(self, name, value):
        if name.endswith("_FILE") or name.endswith("_DIR"):
            return True
        return False

    def _build_form(self):
        for name in sorted(self.original_values):
            value = self.original_values[name]
            
            row = ttk.Frame(self.form_frame, padding=(0, 4))

            row.pack(fill="x")

            label = ttk.Label(row, text=settings_description.get(name, name), width=40, anchor="w")
            label.pack(side="left")

            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=(40, 6))

            if self._is_file_setting(name, value):
                button = ttk.Button(row, text="Parcourir", command=lambda n=name, v=var: self.choose_file(n, v))
                button.pack(side="left")
            self.fields[name] = var

    def choose_file(self, setting_name, variable):
        current_value = variable.get()
        initial_dir = os.path.dirname(current_value) if current_value else os.getcwd()
        filename = filedialog.askopenfilename(
            title=f"Sélectionner le fichier pour {setting_name}",
            initialdir=initial_dir,
            filetypes=[("Fichiers", "*.*")],
        )
        if filename:
            variable.set(filename)

    def generate(self):
        for name, var in self.fields.items():
            value = var.get()
            if value.isdigit():
                value = int(value)
            self.original_values[name] = value

        with open("settings.json", "w") as f:
            json.dump(self.original_values, f, indent=4)

        try:
            algorithme.generate()
            messagebox.showinfo("Succès", "L'algorithme a été exécuté avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors de l'exécution de l'algorithme:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    SettingsEditor(root)
    root.mainloop()
