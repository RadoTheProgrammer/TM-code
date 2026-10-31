import json

import pandas as pd
import os
class DataError(Exception):
    pass

def dataerror(message):
    raise DataError(message)

def datawarning(message):
    print(f"Warning: {message}")

def func_read_csv_excel(file):
    if file.endswith(".csv"):
        return pd.read_csv
    elif file.endswith(".xlsx"):
        return pd.read_excel
    else:
        dataerror(f"Unsupported file format: {file}")
        return pd.read_csv
    
try:
    with open(os.path.expanduser("tm-settings.json"), "r") as f:
        settings_data = json.load(f)
except FileNotFoundError:
    settings_data = {"DIR": "",
    "GRID_FILE": "{DIR}/grid.csv",
    "OUTPUT_DIR": "{DIR}/results",
    "OUTPUT_FILE": "{DIR}/results/o.csv",
    "TM_FILE": "",
    "DUO_FILE": "{DIR}/duo.csv",
    "NPROBLEMS_ELEVES_FILE": "{DIR}/nproblems_eleves.csv",
    "NPROBLEMS_TM_FILE": "{DIR}/nproblems_tm_df.csv",
    "ELEVES_FILE": "",
    "N_TRIES": 10000,
    "RANDOM_SEED": 67,
    "PUISSANCE_ELEVE": 20.0,
    "PUISSANCE_TM": 2.0,
    "ELEVES_NPROBLEMS_MODE": None,
    "WARNINGS_FILE": "{DIR}/warnings.txt"
    }

def gf_setting(key):
    """Get and format setting"""
    value = settings_data[key]

    return format_setting(value)
def format_setting(value):
    return value.format(**settings_data).format(**settings_data)
def save_settings():
    with open(os.path.expanduser("tm-settings.json"), "w") as f:
        json.dump(settings_data, f, indent=4)