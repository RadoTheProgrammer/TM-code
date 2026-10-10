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
import utils
from utils import settings_data
import pandas as pd
import numpy as np



class DataError(Exception):
    pass

def dataerror(message):
    raise DataError(message)

def datawarning(message):
    print(f"Warning: {message}")
def verify_tm_file(file):


    tm_data = utils.func_read_csv_excel(file)(file)
    if tm_data.empty or tm_data.columns[0] != "N° TM":
        raise utils.DataError("TM_FILE doit avoir 'N° TM' comme première colonne")
    tm_data = tm_data.set_index("N° TM")
    required_columns = {
        "Langue",
        COLUMN_IGI,
        "Nombre minimal travaux",
        "Nombre maximal travaux",
    }
    missing_columns = required_columns - set(tm_data.columns)
    if missing_columns:
        utils.dataerror(f"TM_FILE manque les colonnes : {sorted(missing_columns)}")
    if tm_data.empty:
        raise utils.DataError("TM_FILE ne contient aucune ligne de TM")

    tm_ids = pd.Series(pd.to_numeric(pd.Series(tm_data.index), errors="coerce").to_numpy(), index=tm_data.index)
    invalid_tm_ids = tm_ids.isna() | tm_ids.le(0) | tm_ids.mod(1).ne(0)
    duplicate_tm_ids = tm_data.index.to_series().duplicated(keep=False)
    if invalid_tm_ids.any() or duplicate_tm_ids.any():
        bad_ids = tm_data.index[invalid_tm_ids | duplicate_tm_ids].tolist()
        raise utils.DataError(f"TM_FILE doit avoir des identifiants TM entiers positifs uniques; identifiants invalides ou dupliqués : {bad_ids}")

    allowed_languages = {"français", "allemand", "anglais", "espagnol", "italien", "libre"}
    abbreviations = {"f":"français", "fr":"français", "fra":"français", "ang":"anglais", "all":"allemand", "esp":"espagnol", "it":"italien"}
    invalid_languages = []
    for tm_id, value in tm_data["Langue"].items():
        if pd.isna(value):
            invalid_languages.append((tm_id, value))
            continue
        original_value = str(value).strip()
        languages = {language.strip().casefold() for language in original_value.split("/")}
        languages = {abbreviations.get(language, language) for language in languages}
        tm_data.at[tm_id, "Langue"] = "/".join(sorted(languages))
        if not languages <= allowed_languages:
            invalid_languages.append((tm_id, original_value))
    if invalid_languages:
        utils.datawarning(f"TM_FILE contains invalid languages (TM ID, value): {invalid_languages}")

    free_tm = tm_data["Langue"].astype(str).str.strip().str.casefold().eq("libre")
    allowed_igi = {IGI_INDIVIDUEL, IGI_GROUPE, IGI_INDIFFERENT}
    tm_data[COLUMN_IGI] = tm_data[COLUMN_IGI].astype(str).str.strip().str.casefold()
    igi = tm_data[COLUMN_IGI]
    invalid_igi = (~igi.isin(allowed_igi) & igi.notna()) | (igi.isna() & ~free_tm)
    if invalid_igi.any():
        utils.datawarning(
            "TM_FILE contains invalid individual/group values:\n"
            + tm_data.loc[invalid_igi, [COLUMN_IGI, "Langue"]].to_string()
        )

    maximum = pd.to_numeric(tm_data["Nombre maximal travaux"], errors="coerce")
    invalid_maximum = (
        maximum.isna()
        | ~np.isfinite(maximum)
        | maximum.le(0)
        | maximum.mod(1).ne(0)
    ) & ~free_tm
    if invalid_maximum.any():
        raise utils.DataError(
            "Les capacités maximales du TM_FILE doivent être des nombres entiers positifs; lignes invalides:\n"
            + tm_data.loc[invalid_maximum, ["Nombre maximal travaux"]].to_string()
        )

    minimum_raw = tm_data["Nombre minimal travaux"].astype("string").str.strip()
    minimum_present = minimum_raw.notna() & minimum_raw.ne("")
    minimum = pd.to_numeric(minimum_raw, errors="coerce")
    invalid_minimum = minimum_present & (
        minimum.isna()
        | ~np.isfinite(minimum)
        | minimum.lt(0)
        | minimum.mod(1).ne(0)
        | maximum.isna()
        | minimum.gt(maximum)
    )
    if invalid_minimum.any():
        raise utils.DataError(
            "Les capacités minimales du TM_FILE doivent être des nombres entiers entre 0 et le maximum; lignes invalides:\n"
            + tm_data.loc[invalid_minimum, ["Nombre minimal travaux", "Nombre maximal travaux"]].to_string()
        )

    return tm_data

def verify_eleves_file(file, tm_data):

    student_data = utils.func_read_csv_excel(file)(file, dtype=str)
    if student_data.empty or student_data.columns[0] != "Elève":
        raise utils.DataError("ELEVES_FILE doit avoir 'Elève' comme première colonne")
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
        raise utils.DataError(f"ELEVES_FILE manque les colonnes : {sorted(missing_columns)}")
    if student_data.empty:
        raise utils.DataError("ELEVES_FILE ne contient aucune ligne d'élève")

    student_ids = student_data.index.to_series().astype("string").str.strip()
    invalid_student_ids = student_ids.isna() | student_ids.eq("") | student_ids.duplicated(keep=False)
    if invalid_student_ids.any():
        raise utils.DataError(
            "ELEVES_FILE doit avoir des identifiants d'élèves uniques et non vides; lignes invalides:\n"
            + student_data.loc[invalid_student_ids].to_string()
        )

    tm_ids = set(pd.to_numeric(pd.Series(tm_data.index), errors="coerce").astype(int))
    allowed_languages = {"0", "français", "allemand", "anglais", "espagnol", "italien"}
    for number, suffix in ((1, ""), (2, ".1"), (3, ".2")):
        choice = student_data[f"Choix {number}"].fillna("").astype(str).str.strip()
        choice_ids = choice.str.extract(r"^TM(\d+)$", expand=False)
        invalid_choices = ~choice.eq("0") & choice_ids.isna()
        if invalid_choices.any():
            raise utils.DataError(
                f"ELEVES_FILE contient des valeurs invalides dans Choix {number}:\n"
                + student_data.loc[invalid_choices, [f"Choix {number}"]].to_string()
            )
        selected_ids = pd.to_numeric(choice_ids, errors="coerce")
        unknown_ids = choice_ids.notna() & ~selected_ids.isin(tm_ids)
        if unknown_ids.any():
            raise utils.DataError(
                f"ELEVES_FILE Choix {number} fait référence à des identifiants TM inconnus:\n"
                + student_data.loc[unknown_ids, [f"Choix {number}"]].to_string()
            )

        language = student_data[f"Langue (si choix proposé){suffix}"].fillna("0").astype(str).str.strip()
        invalid_language = ~language.str.casefold().isin(allowed_languages)
        if invalid_language.any():
            column = f"Langue (si choix proposé){suffix}"
            raise utils.DataError(
                f"ELEVES_FILE contient des langues invalides pour Choix {number}:\n"
                + student_data.loc[invalid_language, [column]].to_string()
            )

        mode = student_data[f"Individuel ou en duo{suffix}"].fillna("").astype(str).str.strip()
        normalized_mode = mode.str.casefold()
        invalid_mode = ~normalized_mode.isin({"0", "individuel", "duo"})
        if invalid_mode.any():
            column = f"Individuel ou en duo{suffix}"
            raise utils.DataError(
                f"ELEVES_FILE contient des valeurs invalides de type individuel/groupe pour Choix {number}:\n"
                + student_data.loc[invalid_mode, [column]].to_string()
            )
        empty_choice_mode = choice.eq("0") & normalized_mode.ne("0")
        if empty_choice_mode.any():
            column = f"Individuel ou en duo{suffix}"
            raise utils.DataError(
                f"Le Choix {number} vide dans ELEVES_FILE doit avoir le mode 0; lignes invalides:\n"
                + student_data.loc[empty_choice_mode, [f"Choix {number}", column]].to_string()
            )

        partner_column = f"Choix {number} en duo avec Nom Prénom (si case cochée précédemment)"
        partner = student_data[partner_column].fillna("").astype(str).str.strip()
        missing_partner = normalized_mode.eq("duo") & partner.eq("")
        if missing_partner.any():
            raise utils.DataError(
                f"ELEVES_FILE contient un duo sans partenaire pour Choix {number}:\n"
                + student_data.loc[missing_partner, [f"Choix {number}", partner_column]].to_string()
            )

    return student_data

df_tm = verify_tm_file(settings_data["TM_FILE"])
df = verify_eleves_file(settings_data["ELEVES_FILE"], df_tm)

n_tm = len(df_tm)
tm_libre = df_tm[df_tm["Langue"]=="libre"]
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
        envie = {1:3, 2:2, 3:1}[nchoix]
        if choix=="0":
            df_grid.drop(nom_eleve, inplace=True)
            break
        choix = int(choix[2:])
        if choix in tm_libre.index: # TM libre
            n_tm_libre+=1
            continue
        ind_ou_duo = eleve[f"Individuel ou en duo{indice}"]
        langue = str(eleve[f"Langue (si choix proposé){indice}"]).strip().casefold()
        langue_tm = df_tm.at[choix,"Langue"]
        if langue not in ("0","nan") and langue not in langue_tm:
            if choix==35:
                print(tm_libre.index)
                pass
            print(f"Attention: élève {nom_eleve} a choisi le TM {choix} avec langue '{langue}' qui ne correspond pas à la langue du TM '{langue_tm}'")
            continue
        igi = df_tm.at[choix,COLUMN_IGI]
        if nom_eleve=="PERS_0001":
            pass

        if ind_ou_duo=="Individuel":
            if igi==IGI_GROUPE:
                print(f"TM {choix} est marqué comme groupe mais l'élève {nom_eleve} a indiqué 'Individuel' (choix {nchoix})")
                continue
            df_grid.at[nom_eleve,choix] = envie
        else:
            assert ind_ou_duo=="Duo"
            if igi==IGI_INDIVIDUEL:
                print(f"TM {choix} est marqué comme individuel mais l'élève {nom_eleve} a indiqué 'Duo' (choix {nchoix})")
                continue

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
            df_grid.at[nom_eleve,choix] = envie


        


        

    if n_tm_libre>1:
        print(f"Eleve {nom_eleve} a {n_tm_libre} tm libre")
n = 0
for _,duo in df_duo.iterrows():
    if duo["Eleves"]!=duo["ElevesAccord"]:
        print(f"Problème duo: {duo}")
        for eleve in duo["Eleves"]:
            if eleve in duo["ElevesAccord"]:
                df_grid.at[eleve,duo["Choix"]] = np.nan
            else:
                for nchoix,indice in ((1,""),(2,".1"),(3,".2")):
                    if duo["Choix"]==int(df.at[eleve,f"Choix {nchoix}"][-2:]):
                        if df.at[eleve,f"Individuel ou en duo{indice}"]=="Individuel":
                            print(f"élève {eleve} a peut-être mal indiqué son partenaire pour le TM {duo['Choix']} choix {nchoix}")

        n+=1
print(f"{n} duos sur {len(df_duo)} non accordés")
df_duo["Eleves"] = df_duo["Eleves"].apply(lambda x: " + ".join(x))
df_duo["ElevesAccord"] = df_duo["ElevesAccord"].apply(lambda x: " + ".join(x))
df_duo.to_csv(settings_data["DUO_FILE"],index=False)

df_grid.to_csv(settings_data["GRID_FILE"])