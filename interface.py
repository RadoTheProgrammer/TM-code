import os
import csv
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

import json


settings_description = {
    "TM_FILE": "Fichier CSV contenant les travaux de maturité.",
    "ELEVES_FILE": "Fichier CSV contenant les voeux des élèves.",
    "DIR": "Répertoire de travail pour les fichiers d'entrée et de sortie.",
}

class SettingsEditor:
    def __init__(self, master:tk.Tk):
        self.master = master
        self.master.title("TM Settings")
        self.master.geometry("760x520")
        self.master.minsize(700, 420)

        self.original_values = {}
        self.fields = {}
        self.generating = False
        self.stop_requested = False
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

        self.progress_text = tk.StringVar()
        ttk.Label(actions, textvariable=self.progress_text).pack(side="left")

        self.generate_button = ttk.Button(actions, text="Générer", command=self.generate)
        self.generate_button.pack(side="right")
        ttk.Button(actions, text="Fermer", command=self.close).pack(side="right", padx=(0, 8))

    def close(self):
        self.stop_generating()
        self.master.destroy()
    def _load_original_values(self):
        try:
            with open(os.path.expanduser("~/tm-settings.json"), "r") as f:
                self.original_values = json.load(f)
        except FileNotFoundError:
            self.original_values = {
    "DIR": "",
    "GRID_FILE": "grid.csv",
    "OUTPUT_DIR": "results",
    "OUTPUT_FILE": "results/o.csv",
    "TM_FILE": "",
    "DUO_FILE": "duo.csv",
    "NPROBLEMS_ELEVES_FILE": "nproblems_eleves.csv",
    "NPROBLEMS_TM_FILE": "nproblems_tm_df.csv",
    "ELEVES_FILE": "",
    "N_TRIES": 10000,
    "RANDOM_SEED": 67
}

    def _is_file_setting(self, name, value):
        if name.endswith("_FILE") or name.endswith("_DIR"):
            return True
        return False
    def stop_generating(self):
        self.stop_requested = True
        while self.stop_requested:
            self.master.update()
    def _build_form(self):
        for name in ("TM_FILE","ELEVES_FILE","DIR"):
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

            if name in ("TM_FILE", "ELEVES_FILE"):
                button = ttk.Button(row, text="Parcourir", command=lambda n=name, v=var: self.choose_file(n, v))
                button.pack(side="left")

            if name=="DIR":
                # Add a button to open the directory in the file explorer
                button = ttk.Button(row, text="Parcourir", command=lambda v=var: self.choose_directory(v))
                button.pack(side="left")
            self.fields[name] = var

    def choose_directory(self, variable):
        current_value = variable.get()
        initial_dir = current_value if current_value else os.getcwd()
        directory = filedialog.askdirectory(
            title="Sélectionner le répertoire de travail",
            initialdir=initial_dir,
        )
        if directory:
            variable.set(directory)
    def _build_results_frame(self):
        if hasattr(self, "results_frame"):
            self.results_frame.destroy()

        self.results_frame = ttk.LabelFrame(self.form_frame, text="Résultats")
        self.results_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

        self.auto_scroll = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.results_frame,
            text="Défilement automatique vers le bas",
            variable=self.auto_scroll,
        ).pack(anchor="w", padx=6, pady=(6, 0))

        table_frame = ttk.Frame(self.results_frame)
        table_frame.pack(fill="both", expand=True, padx=6, pady=6)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

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

        columns = ["Index", *columns]
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self._configure_sortable_tree(tree, columns)

        for index, row in enumerate(rows):
            tree.insert(
                "",
                "end",
                values=[index, *[row.get(column, "") for column in columns[1:]]],
            )

        # Put the results table in the upper-left cell of the layout.  ``nsew``
        # makes the tree expand in every direction when the window is resized.
        tree.grid(row=0, column=0, sticky="nsew")

        # Keep the vertical scrollbar beside the tree and stretch it vertically.
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        # Place the horizontal scrollbar below the tree and let it fill the
        # available width.  It occupies row 1, while the tree occupies row 0.
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.results_tree = tree
        tree.bind("<Double-1>", self.show_result_details)

    def show_result_details(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            return

        index = tree.set(item, "Index")
        details_path = os.path.join(
            self.fields["OUTPUT_DIR"].get(),
            f"r{index}.csv",
        )

        try:
            with open(details_path, "r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                columns = list(reader.fieldnames or [])
                rows = list(reader)
        except (OSError, csv.Error) as error:
            messagebox.showerror(
                "Détails indisponibles",
                f"Impossible de lire le fichier de détails : {error}",
                parent=self.master,
            )
            return

        details_window = tk.Toplevel(self.master)
        details_window.title(f"Détails de la répartition {index}")
        details_window.geometry("700x450")
        details_window.minsize(500, 300)

        if not columns:
            ttk.Label(details_window, text="Le fichier de détails est vide.").pack(
                anchor="w", padx=12, pady=12
            )
            return

        details_tree = ttk.Treeview(details_window, columns=columns, show="headings")
        vertical_scrollbar = ttk.Scrollbar(
            details_window, orient="vertical", command=details_tree.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            details_window, orient="horizontal", command=details_tree.xview
        )
        details_tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self._configure_sortable_tree(details_tree, columns)

        for row in rows:
            details_tree.insert("", "end", values=[row.get(column, "") for column in columns])

        details_window.rowconfigure(0, weight=1)
        details_window.columnconfigure(0, weight=1)
        details_tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

    def _configure_sortable_tree(self, tree, columns):
        for column in columns:
            tree.heading(
                column,
                text=column,
                command=lambda selected_column=column: self._sort_results(
                    tree, selected_column, False
                ),
            )
            tree.column(column, width=max(100, len(column) * 10), anchor="w")

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
        if self.generating:
            self.progress_text.set("Arrêt de la génération ...")
            self.stop_generating()
            self.generating = False
            self.generate_button.configure(text="Générer")
            
        else:
            self.stop_requested = False
            self.generating = True
            for name, var in self.fields.items():
                value = var.get()
                if value.isdigit():
                    value = int(value)
                self.original_values[name] = value

            with open(os.path.expanduser("~/tm-settings.json"), "w") as f:
                json.dump(self.original_values, f, indent=4)

            # change text of generate button to "Arrêter"
            self.generate_button.configure(text="Arrêter")

            self.progress_text.set("Démarrage de la génération ...")
            threading.Thread(target=self._run_generation, daemon=True).start()

    def _run_generation(self):
        try:
            if not os.path.exists(self.original_values["GRID_FILE"]):
                import create_grid
            import algorithme
            algorithme.generate(self)
        except Exception as error:
            self.master.after(0, self._generation_finished, error)
        else:
            self.master.after(0, self._generation_finished, None)

    def _generation_finished(self, error):
        self.generate_button.configure(text="Générer")
        self.progress_text.set("")
        if error is None:
            messagebox.showinfo("Succès", "L'algorithme a été exécuté avec succès.")
        else:
            messagebox.showerror(
                "Erreur",
                f"Une erreur s'est produite lors de l'exécution de l'algorithme:\n{error}",
            )

    def update_progress(self, data_single):
        def insert_row():
            tree = getattr(self, "results_tree", None)
            if tree is None:
                return

            columns = tree["columns"]
            index = len(tree.get_children())
            tree.insert(
                "",
                "end",
                values=[index, *[data_single.get(column, "") for column in columns[1:]]],
            )
            if self.auto_scroll.get():
                tree.yview_moveto(1.0)

        # Generation runs in a worker thread; Tkinter widgets must be updated
        # from the main thread.
        print("HELLO WORLD")
        self.master.after(0, insert_row)
        
if __name__ == "__main__":
    root = tk.Tk()
    SettingsEditor(root)
    root.mainloop()
