import pandas as pd


def verify_repartition(grid_file, tm_file, duo_file, result_file):
    df_grid = pd.read_csv(grid_file, index_col=0)
    df_grid.index = df_grid.index.astype(str)

    df_tm = pd.read_csv(tm_file, index_col=0)
    df_tm = df_tm[df_tm["Langue"] != "Libre"]

    df_result = pd.read_csv(result_file, index_col=0)
    df_result.index = df_result.index.astype(str)
    choices = pd.to_numeric(df_result["Choice"], errors="coerce")

    df_duo = pd.read_csv(duo_file)
    df_duo["Eleves"] = df_duo["Eleves"].str.split(r" \+ ")
    df_duo["Repr"] = df_duo["Eleves"].str[0]

    assigned_students = set(df_result.index[choices.notna() & choices.ne(0)])
    problems = [
        f"Élève non attribué : {student}"
        for student in df_grid.index
        if student not in assigned_students
    ]

    for tm_id, tm in df_tm.iterrows():
        maximum = pd.to_numeric(tm["Nombre maximal travaux"], errors="coerce")
        if pd.isna(maximum):
            continue

        assigned = df_result.loc[choices.eq(float(tm_id))]
        count = len(assigned)
        tm_duos = df_duo[df_duo["Choix"] == tm_id]

        for _, duo in tm_duos.iterrows():
            if duo["Repr"] not in assigned.index:
                continue
            members_assigned = pd.Series(duo["Eleves"]).isin(assigned.index)
            if members_assigned.all():
                count -= len(members_assigned) - 1

        if count > maximum:
            title = tm.get("Titre", "")
            tm_label = f"TM {tm_id}"
            if pd.notna(title) and title:
                tm_label += f" — {title}"
            problems.append(
                f"{tm_label} : trop d’élèves ({count} attribués, maximum {int(maximum)})"
            )

    return problems


def main():
    for problem in verify_repartition(
        "Annee_28/grid.csv",
        "Annee_28/liste_sujets.csv",
        "Annee_28/duo.csv",
        "r9516.csv",
    ):
        print(problem)


if __name__ == "__main__":
    main()
