TM répartiteur de TMs

# Structure des fichiers:
* `.gitignore`: fichiers ignoré par git
* `best_tm.py`: extrait le TM le plus apprécié
* `create_grid.py`: crée la grille d'envies
* `Donnees_TMs`: contient les données d'entrées et de sorties de chaque TM
    * `Annee_1`:
        * `duo.csv`: donnée intermédiaire sur les duos avec leurs numéros d'élèves et leur TM
        * `grid.csv`: entrée: grille d'envie
        * `liste_sujets.csv`: entrée: liste des sujets de TMs
        * `nproblems_eleves.csv`: créé et utilisé par le programme pour stocker les élèves ayant le plus de problèmes
        * `nproblems_tm.csv`: idem pour les TMs
        * `results`
            * `r0.csv`: une répartition généré
            * `r1.csv`
            * `r2.csv`
            * ...
            * `o2.csv`: tableau des répartitions avec leur ID, somme des envies, moyenne des envies
    * `Annee_2`: même structure que année 1
* `interface.py`: code pour l'interface
* `main.py`: le code principal pour l'algorithme
* `pick_repartition.py`: questionne la valeur d'une répartition
* `README.md`: ce fichier
* `sandbox.ipynb` et `sandbox.py`: fichiers temporaires pour mes petits essais
* `verificateur.py`: vérifie si une répartition est valide
