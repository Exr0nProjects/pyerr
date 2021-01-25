# type:ignore

import glob
import pandas as pd


def globit(filepath):
    files = glob.glob(filepath)


    dataframes = []
    for fileName in files:
        df_raw = pd.read_csv(fileName)
        clean_row = df_raw.loc[df_raw[df_raw.columns[0]] == "background"].index[0] + 2
        experimentType = [i.strip() for i in df_raw.iloc[clean_row-1, 0].split(",")]
        background = {"seconds": df_raw.iloc[clean_row-2, 1], "counts": df_raw.iloc[clean_row-2, 2]}
        df_cleaned = df_raw.iloc[0:clean_row-2, 0:3]
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce')
        breakpoint()
        dataframes.append({"meta":experimentType, "data": df_cleaned, "background": background})

    return dataframes

