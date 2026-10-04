import pandas as pd

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