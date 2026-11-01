import json

import pandas as pd
import os
from platformdirs import user_data_path

class DataError(Exception):
    pass
udp = user_data_path("repartiteur-de-tm")
os.makedirs(udp, exist_ok=True)
settings_file = os.path.join(udp, "tm-settings.json")

def dataerror(message):
    """Lève une erreur de données avec le message fourni."""
    raise DataError(message)

def datawarning(message):
    """Signale un avertissement de données."""
    print(f"Warning: {message}")

def func_read_csv_excel(file):
    """Retourne le lecteur adapté au format du fichier."""
    if file.endswith(".csv"):
        return pd.read_csv
    elif file.endswith(".xlsx"):
        return pd.read_excel
    else:
        dataerror(f"Unsupported file format: {file}")
        return pd.read_csv
    
try:
    with open(settings_file, "r") as f:
        settings_data = json.load(f)
except FileNotFoundError:
    settings_data = {"DIR": "Donnees_TMs/Annee_28",
    "GRID_FILE": "{DIR}/grid.csv",
    "GRID_PARAMS_FILE": "{DIR}/grid_params.json",
    "OUTPUT_DIR": "{DIR}/results",
    "OUTPUT_FILE": "{DIR}/results/o.csv",
    "NREP_FILE": "{OUTPUT_DIR}/nrep.txt",
    "TM_FILE": "{DIR}/liste_sujets.csv",
    "DUO_FILE": "{DIR}/duo.csv",
    "NPROBLEMS_ELEVES_FILE": "{DIR}/nproblems_eleves2.csv",
    "NPROBLEMS_TM_FILE": "{DIR}/nproblems_tm_df2.csv",
    "ELEVES_FILE": "{DIR}/voeux_eleves.csv",
    "N_TRIES": 10000,
    "RANDOM_SEED": 3,
    "PUISSANCE_ELEVE": 20.0,
    "PUISSANCE_TM": 2.0,
    "ELEVES_NPROBLEMS_MODE": None,
    "WARNINGS_FILE": "{DIR}/warnings.txt",
    "TOLERANCE_IGI_GROUPE":True,
    "TOLERANCE_IGI_IND":True,
    "TOLERANCE_LANGUE":True
}

def gf_setting(key):
    """Get and format setting"""
    value = settings_data[key]

    return format_setting(value)
def format_setting(value):
    """D?veloppe les r?f?rences de param?tres dans une cha?ne."""
    if isinstance(value, str):
        return value.format(**settings_data).format(**settings_data)
    return value
def save_settings():
    """Enregistre les param?tres courants dans le fichier JSON."""
    with open(settings_file, "w") as f:
        json.dump(settings_data, f, indent=4)