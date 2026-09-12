import os
import csv
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import algorithme
import json


settings_description = {
    "TM_FILE": "Fichier CSV contenant les travaux de maturité.",
    "OUTPUT_DIR": "Répertoire où seront enregistrés les résultats.",
    "OUTPUT_FILE": "Fichier CSV où seront enregistrés les résultats.",
    "ELEVES_FILE": "Fichier CSV contenant les voeux des élèves.",
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
        self._build_results_frame()

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
        for name in ("TM_FILE", "OUTPUT_DIR", "OUTPUT_FILE", "ELEVES_FILE"):
            value = self.original_values[name]
            # row = tk.Frame(
            #     self.form_frame,
            #     bg="red",
            #     padx=0,
            #     pady=12,
            # )
            # row.pack(fill="x", pady=0)

            row = tk.Frame(self.form_frame)
            row.pack(fill="x", pady=12)
            #row = ttk.Frame(self.form_frame, bg="red",padding=(0, 12))

            #row.pack(fill="x",pady=0)

            label = ttk.Label(row, text=settings_description.get(name, name), width=40, anchor="w")
            label.pack(side="left")

            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=(40, 6))

            if self._is_file_setting(name, value):
                button = ttk.Button(row, text="Parcourir", command=lambda n=name, v=var: self.choose_file(n, v))
                button.pack(side="left")
            self.fields[name] = var

    def _build_results_frame(self):
        if hasattr(self, "results_frame"):
            self.results_frame.destroy()

        self.results_frame = ttk.LabelFrame(self.form_frame, text="Résultats")
        self.results_frame.pack(fill="both", expand=True, pady=(12, 0))

        table_frame = ttk.Frame(self.results_frame)
        table_frame.pack(fill="both", expand=True, padx=6, pady=6)

        output_file = self.fields.get("OUTPUT_FILE")
        output_path = output_file.get() if output_file else self.original_values.get("OUTPUT_FILE", "")

        try:
            with open(output_path, "r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                columns = list(reader.fieldnames or [])
                rows = list(reader)
                print(rows)
                pass
        except (OSError, csv.Error) as error:
            ttk.Label(
                table_frame,
                text=f"Impossible de lire le fichier de résultats : {error}",
            ).pack(anchor="w")
            return

        if not columns:
            ttk.Label(table_frame, text="Le fichier de résultats est vide.").pack(anchor="w")
            return

        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        for column in columns:
            tree.heading(
                column,
                text=column,
                command=lambda selected_column=column: self._sort_results(
                    tree, selected_column, False
                ),
            )
            tree.column(column, width=max(100, len(column) * 10), anchor="w")

        for row in rows:
            tree.insert("", "end", values=[row.get(column, "") for column in columns])

        # Put the results table in the upper-left cell of the layout.  ``nsew``
        # makes the tree expand in every direction when the window is resized.
        tree.grid(row=0, column=0, sticky="nsew")

        # Keep the vertical scrollbar beside the tree and stretch it vertically.
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        # Place the horizontal scrollbar below the tree and let it fill the
        # available width.  It occupies row 1, while the tree occupies row 0.
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        # Give the tree's row and column the extra space available in
        # ``table_frame``.  Without these weights, the tree would keep its
        # requested size instead of growing with the results frame.
        # table_frame.rowconfigure(0, weight=1)
        # table_frame.columnconfigure(0, weight=1)
        self.results_tree = tree

    @staticmethod
    def _sort_results(tree, column, reverse):
        items = [(tree.set(item, column), item) for item in tree.get_children("")]

        def sort_key(item):
            value = item[0].strip()
            try:
                return (0, float(value))
            except ValueError:
                return (1, value.casefold())

        items.sort(key=sort_key, reverse=reverse)
        for index, (_, item) in enumerate(items):
            tree.move(item, "", index)

        tree.heading(
            column,
            command=lambda: SettingsEditor._sort_results(tree, column, not reverse),
        )

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
        if not os.path.exists(self.original_values["GRID_FILE"]):
            messagebox.showerror("Erreur", "Le fichier de grille n'existe pas.")
            return
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
