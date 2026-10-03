"""
Crée la matrice d'envie, un tableau avec les élèves comme lignes et les TMs comme colonnes, 
qui indique donc pour chaque élève à quel point il a envie de ce TM
"""


DUO_SEP = " + "
DIR = "Donnees_TMs/Annee_2"
TM_FILE = f"{DIR}/liste_sujets.csv" # tableau avec les TMs, leurs langues et le nombre de places

COLUMN_IGI = "Individuel/groupe/ indifférent"  # Colonne indiquant les préférences de groupe/individuel
IGI_INDIVIDUEL ="individuel"
IGI_GROUPE = "groupe"
IGI_INDIFFERENT = "indifférent"


import json
import os
import time

import pandas as pd
import numpy as np

with open("settings.json", "r") as f:
    settings_data = json.load(f)
def func_read_csv_excel(file):
    if file.endswith(".csv"):
        return pd.read_csv
    elif file.endswith(".xlsx"):
        return pd.read_excel
    else:
        raise ValueError(f"Unsupported file format: {file}")

def verify_tm_file(file):
    normalized_path = os.path.normpath(file).replace("\\", "/").casefold()
    if not normalized_path.endswith((
        "donnees_tms/annee_1/liste_sujets.csv",
        "donnees_tms/annee_2/liste_sujets.csv",
    )):
        raise ValueError(
            "TM_FILE must point to Donnees_TMs/Annee_1/liste_sujets.csv "
            "or Donnees_TMs/Annee_2/liste_sujets.csv"
        )

    tm_data = func_read_csv_excel(file)(file)
    if tm_data.empty or tm_data.columns[0] != "N° TM":
        raise ValueError("TM_FILE must have 'N° TM' as its first column")
    tm_data = tm_data.set_index("N° TM")
    required_columns = {
        "Langue",
        COLUMN_IGI,
        "Nombre minimal travaux",
        "Nombre maximal travaux",
    }
    missing_columns = required_columns - set(tm_data.columns)
    if missing_columns:
        raise ValueError(f"TM_FILE is missing columns: {sorted(missing_columns)}")
    if tm_data.empty:
        raise ValueError("TM_FILE contains no TM rows")

    tm_ids = pd.to_numeric(pd.Series(tm_data.index), errors="coerce")
    if (
        pd.isna(tm_ids).any()
        or (tm_ids <= 0).any()
        or (tm_ids % 1 != 0).any()
        or tm_data.index.duplicated().any()
    ):
        raise ValueError("TM_FILE must have unique positive integer TM IDs")

    allowed_languages = {"français", "allemand", "anglais", "espagnol", "italien", "libre"}
    invalid_languages = set()
    for value in tm_data["Langue"].dropna():
        languages = {language.strip().casefold() for language in str(value).split("/")}
        if not languages <= allowed_languages:
            invalid_languages.add(str(value))
    if tm_data["Langue"].isna().any() or invalid_languages:
        raise ValueError(f"TM_FILE contains invalid languages: {sorted(invalid_languages)}")

    free_tm = tm_data["Langue"].astype(str).str.strip().str.casefold().eq("libre")
    allowed_igi = {IGI_INDIVIDUEL, IGI_GROUPE, IGI_INDIFFERENT}
    invalid_igi = {
        str(value)
        for value in tm_data[COLUMN_IGI].dropna()
        if str(value).strip().casefold() not in allowed_igi
    }
    if (tm_data[COLUMN_IGI].isna() & ~free_tm).any() or invalid_igi:
        raise ValueError(f"TM_FILE contains invalid individual/group values: {sorted(invalid_igi)}")

    maximum = pd.to_numeric(tm_data["Nombre maximal travaux"], errors="coerce")
    maximum_values = maximum[maximum.notna()]
    if (
        (maximum.isna() & ~free_tm).any()
        or not np.isfinite(maximum_values).all()
        or (maximum_values <= 0).any()
        or (maximum_values % 1 != 0).any()
    ):
        raise ValueError("TM_FILE maximum capacities must be positive whole numbers")

    minimum_raw = tm_data["Nombre minimal travaux"].astype("string").str.strip()
    minimum_present = minimum_raw.notna() & minimum_raw.ne("")
    minimum = pd.to_numeric(minimum_raw, errors="coerce")
    if (minimum_present & minimum.isna()).any():
        raise ValueError("TM_FILE minimum capacities must be numbers or empty")
    minimum_values = minimum[minimum_present]
    if (
        (minimum_present & maximum.isna()).any()
        or not np.isfinite(minimum_values).all()
        or (minimum_values < 0).any()
        or (minimum_values % 1 != 0).any()
        or (minimum_values > maximum[minimum_present]).any()
    ):
        raise ValueError("TM_FILE minimum capacities must be whole numbers between 0 and the maximum")

    return tm_data

def verify_eleves_file(file, tm_data):
    normalized_path = os.path.normpath(file).replace("\\", "/").casefold()
    if not normalized_path.endswith((
        "donnees_tms/annee_1/voeux_eleves.csv",
        "donnees_tms/annee_2/voeux_eleves.csv",
    )):
        raise ValueError(
            "ELEVES_FILE must point to Donnees_TMs/Annee_1/voeux_eleves.csv "
            "or Donnees_TMs/Annee_2/voeux_eleves.csv"
        )

    student_data = func_read_csv_excel(file)(file, dtype=str)
    if student_data.empty or student_data.columns[0] != "Elève":
        raise ValueError("ELEVES_FILE must have 'Elève' as its first column")
    student_data = student_data.set_index("Elève")
    required_columns = {
        "Choix 1",
        "Langue (si choix proposé)",
        "Individuel ou en duo",
        "Choix 1 en duo avec Nom Prénom (si case cochée précédemment)",
        "Choix 2",
        "Langue (si choix proposé).1",
        "Individuel ou en duo.1",
        "Choix 2 en duo avec Nom Prénom (si case cochée précédemment)",
        "Choix 3",
        "Langue (si choix proposé).2",
        "Individuel ou en duo.2",
        "Choix 3 en duo avec Nom Prénom (si case cochée précédemment)",
    }
    missing_columns = required_columns - set(student_data.columns)
    if missing_columns:
        raise ValueError(f"ELEVES_FILE is missing columns: {sorted(missing_columns)}")
    if student_data.empty:
        raise ValueError("ELEVES_FILE contains no student rows")

    student_ids = student_data.index.to_series().astype("string").str.strip()
    if student_ids.isna().any() or student_ids.eq("").any() or student_ids.duplicated().any():
        raise ValueError("ELEVES_FILE must have unique, non-empty student IDs")

    tm_ids = set(pd.to_numeric(pd.Series(tm_data.index), errors="coerce").astype(int))
    allowed_languages = {"0", "français", "allemand", "anglais", "espagnol", "italien"}
    for number, suffix in ((1, ""), (2, ".1"), (3, ".2")):
        choice = student_data[f"Choix {number}"].fillna("").astype(str).str.strip()
        choice_ids = choice.str.extract(r"^TM(\d+)$", expand=False)
        invalid_choices = ~choice.eq("0") & choice_ids.isna()
        if invalid_choices.any():
            raise ValueError(f"ELEVES_FILE has invalid values in Choix {number}")
        selected_ids = pd.to_numeric(choice_ids, errors="coerce")
        unknown_ids = choice_ids.notna() & ~selected_ids.isin(tm_ids)
        if unknown_ids.any():
            raise ValueError(f"ELEVES_FILE Choix {number} refers to unknown TM IDs")

        language = student_data[f"Langue (si choix proposé){suffix}"].fillna("").astype(str).str.strip()
        if not language.str.casefold().isin(allowed_languages).all():
            raise ValueError(f"ELEVES_FILE has invalid languages for Choix {number}")

        mode = student_data[f"Individuel ou en duo{suffix}"].fillna("").astype(str).str.strip()
        normalized_mode = mode.str.casefold()
        if not normalized_mode.isin({"0", "individuel", "duo"}).all():
            raise ValueError(f"ELEVES_FILE has invalid individual/group values for Choix {number}")
        if (choice.eq("0") & normalized_mode.ne("0")).any():
            raise ValueError(f"ELEVES_FILE empty Choix {number} must have mode 0")

        partner_column = f"Choix {number} en duo avec Nom Prénom (si case cochée précédemment)"
        partner = student_data[partner_column].fillna("").astype(str).str.strip()
        if (normalized_mode.eq("duo") & partner.eq("")).any():
            raise ValueError(f"ELEVES_FILE has a Duo without a partner for Choix {number}")

    return student_data

df_tm = verify_tm_file(settings_data["TM_FILE"])
df = verify_eleves_file(settings_data["ELEVES_FILE"], df_tm)

n_tm = len(df_tm)
tm_libre = df_tm[df_tm["Langue"]=="Libre"]
df.index = df.index.astype(str)

# Vérifier que toutes les valeurs de la colonne IGI sont parmi les valeurs autorisées
allowed_igi = {IGI_INDIVIDUEL, IGI_GROUPE, IGI_INDIFFERENT}
if COLUMN_IGI not in df_tm.columns:
    raise ValueError(f"Colonne attendue manquante: {COLUMN_IGI}")
df_tm["Langue"] = df_tm["Langue"].str.split("/")
df_tm[COLUMN_IGI] = df_tm[COLUMN_IGI].str.lower()
unique_igi = set(df_tm[COLUMN_IGI].dropna().unique())
invalid_igi = unique_igi - allowed_igi
if invalid_igi:
    raise ValueError(f"Valeurs invalides dans la colonne '{COLUMN_IGI}': {sorted(invalid_igi)}")


df_grid = pd.DataFrame(np.nan,index=df.index,columns=range(1,n_tm+1))
df_duo = pd.DataFrame(columns=["Eleves","Choix","ElevesAccord","Envies"])
duo_repr = [] # liste des représentants de duos, pour vérifier que les représentants sont bien dans les duos accordés

for nom_eleve,eleve in df.iterrows():
    n_tm_libre = 0
    for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
        choix = eleve[f"Choix {nchoix}"]
        envie = {1:9, 2:3, 3:1}[nchoix]
        if choix=="0":
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix in tm_libre.index: # TM libre
            n_tm_libre+=1
            continue
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]
        langue = eleve[f"Langue (si choix proposé){indice}"]
        langue_tm = df_tm.at[choix,"Langue"]
        if langue!="0" and langue not in langue_tm:
            if choix==35:
                print(tm_libre.index)
                pass
            print(f"Attention: élève {nom_eleve} a choisi le TM {choix} avec langue '{langue}' qui ne correspond pas à la langue du TM '{langue_tm}'")
        igi = df_tm.at[choix,COLUMN_IGI]
        if igi==IGI_INDIVIDUEL:
            if ind_ou_duo!="Individuel":
                print(f"TM {choix} est marqué comme individuel mais l'élève {nom_eleve} a indiqué '{ind_ou_duo}'")
        elif igi==IGI_GROUPE:
            if ind_ou_duo!="Duo":
                print(f"TM {choix} est marqué comme groupe mais l'élève {nom_eleve} a indiqué '{ind_ou_duo}'")
        if ind_ou_duo=="Duo":

            nom_eleve2 = str(eleve[f"Choix {nchoix} en duo avec Nom Prénom (si case cochée précédemment)"])
            assert not pd.isna(nom_eleve2)

            eleves = {str(nom_eleve)}
            for nom_eleve2 in nom_eleve2.split(DUO_SEP):
                if nom_eleve2 not in df.index:
                    print(f"Nom eleve: {nom_eleve2}")
                eleves.add(nom_eleve2)
            if eleves=={"117","280"}:
                pass
            #eleves.sort() # type: ignore
            #eleves = DUO_SEP.join(eleves)
            duo_bool = (df_duo["Eleves"]==eleves) & (df_duo["Choix"]==choix)
            if duo_bool.any():
                duo = df_duo[duo_bool]
                assert len(duo)==1
                duo = duo.iloc[0]

                duo["ElevesAccord"].add(nom_eleve)
                duo["Envies"].add(envie)

            else:
                df_duo.loc[len(df_duo)]=[eleves,choix,{nom_eleve},{envie}]

        else:
            assert ind_ou_duo=="Individuel"
        


        df_grid.at[nom_eleve,choix] = envie

    if n_tm_libre>1:
        print(f"Eleve {nom_eleve} a {n_tm_libre} tm libre")
for _,duo in df_duo.iterrows():
    if duo["Eleves"]!=duo["ElevesAccord"]:
        print(f"Problème duo: {duo}")

df_duo["Eleves"] = df_duo["Eleves"].apply(lambda x: " + ".join(x))
df_duo["ElevesAccord"] = df_duo["ElevesAccord"].apply(lambda x: " + ".join(x))
df_duo.to_csv(settings_data["DUO_FILE"],index=False)

df_grid.to_csv(settings_data["GRID_FILE"])