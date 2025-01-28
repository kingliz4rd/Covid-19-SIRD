"""Let's load our covid_data that is ready to go."""

import pandas as pd


def load_covid_data(csv_path="data/covid-19-preprocessed.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Last_Update"])
    df = df.sort_values("Last_Update")
    return df.reset_index(drop=True)
