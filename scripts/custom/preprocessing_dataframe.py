import numpy as np
import pandas as pd

tassi_columns = ["Casi, non vaccinati", "Casi, vaccinati",
                 "Casi, booster", "Ospedalizzati, non vaccinati",
                 "Ospedalizzati, vaccinati", "Ospedalizzati, booster",
                 "In terapia intensiva, non vaccinati", "In terapia intensiva, vaccinati",
                 "In terapia intensiva, booster", "Deceduti, non vaccinati",
                 "Deceduti, vaccinati", "Deceduti, booster"]


def compute_incidence(df, df_pop):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata
    tassi = [df["casi non vaccinati"]/df_pop["casi non vaccinati"],
             df["casi vaccinati"]/df_pop["casi vaccinati completo"],
             df["casi booster"]/df_pop["casi vaccinati booster"],
             df["ospedalizzati non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df["ospedalizzati vaccinati"]/df_pop["ospedalizzati/ti vaccinati"],
             df["ospedalizzati booster"]/df_pop["ospedalizzati/ti booster"],
             df["terapia intensiva non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df["terapia intensiva vaccinati"]/df_pop["ospedalizzati/ti vaccinati"],
             df["terapia intensiva booster"]/df_pop["ospedalizzati/ti booster"],
             df["decessi non vaccinati"]/df_pop["decessi non vaccinati"],
             df["decessi vaccinati"]/df_pop["decessi vaccinati"],
             df["decessi booster"]/df_pop["decessi booster"]]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = tassi_columns
    return df_tassi


def date_parser(x):
    """date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(x, format="%Y/%m/%d")
