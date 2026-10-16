from pathlib import Path

import pandas as pd


RESULT_DIRECTORIES = (
    Path("Annee_28/results"),
    Path("Annee_28/results-old"),
    Path("Annee_2/results"),
    Path("Annee_1/results"),
)
ROUND_COLUMNS = {
    "mean",
    "std",
    "nbenvie1",
    "nbenvie2",
    "nbenvie3",
    "temps",
}


def main() -> None:
    data_directory = Path(__file__).resolve().parent

    for directory in RESULT_DIRECTORIES:
        csv_path = data_directory / directory / "o.csv"
        results = pd.read_csv(csv_path)
        columns_to_round = [
            column
            for column in results.columns
            if column.casefold() in ROUND_COLUMNS
        ]
        results[columns_to_round] = results[columns_to_round].round(2)
        results.to_csv(csv_path, index=False)
        print(f"Rounded {csv_path}")


if __name__ == "__main__":
    main()
