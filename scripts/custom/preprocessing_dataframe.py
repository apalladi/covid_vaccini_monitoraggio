import numpy as np
import pandas as pd


def compute_incidence(df, is_old=False):
    # ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata

    empty_data = [0]*len(df)
    tassi = 10**5*np.transpose(
             [df["casi non vaccinati"]/df["non vaccinati"],
              df["casi vaccinati"]/df["vaccinati completo"],
              empty_data if is_old else df["casi booster"]/df["vaccinati booster"],
              df["ospedalizzati non vaccinati"]/df["non vaccinati"],
              df["ospedalizzati vaccinati"]/df["vaccinati completo"],
              empty_data if is_old else df["ospedalizzati booster"]/df["vaccinati booster"],
              df["terapia intensiva non vaccinati"]/df["non vaccinati"],
              df["terapia intensiva vaccinati"]/df["vaccinati completo"],
              empty_data if is_old else df["terapia intensiva booster"]/df["vaccinati booster"],
              df["decessi non vaccinati"]/df["non vaccinati"],
              df["decessi vaccinati"]/df["vaccinati completo"],
              empty_data if is_old else df["decessi booster"]/df["vaccinati booster"]])

    df_tassi = pd.DataFrame(tassi)
    columns = ["Casi, non vaccinati", "Casi, vaccinati",
               "Casi, booster", "Ospedalizzati, non vaccinati",
               "Ospedalizzati, vaccinati", "Ospedalizzati, booster",
               "In terapia intensiva, non vaccinati", "In terapia intensiva, vaccinati",
               "In terapia intensiva, booster", "Deceduti, non vaccinati",
               "Deceduti, vaccinati", "Deceduti, booster"]
    df_tassi.columns = columns
    return df_tassi


def date_parser(x):
    """date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(x, format="%Y/%m/%d")
