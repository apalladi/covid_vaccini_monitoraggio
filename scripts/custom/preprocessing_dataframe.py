import numpy as np
import pandas as pd

tassi_columns = ["Casi, non vaccinati", "Casi, vaccinati",
                 "Casi, booster", "Ospedalizzati, non vaccinati",
                 "Ospedalizzati, vaccinati", "Ospedalizzati, booster",
                 "In terapia intensiva, non vaccinati", "In terapia intensiva, vaccinati",
                 "In terapia intensiva, booster", "Deceduti, non vaccinati",
                 "Deceduti, vaccinati", "Deceduti, booster"]


def compute_incidence_main(df, is_old=False):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata
    # dal file principale, "dati_ISS_complessivi.csv"

    df_pop = pd.read_csv("../dati/dati_ISS_popolazioni.csv", sep=";")

    empty_data = [0]*len(df)
    tassi = [df["casi non vaccinati"]/df_pop["casi non vaccinati"],
             df["casi vaccinati"]/df_pop["casi vaccinati completo"],
             empty_data if is_old else df["casi booster"]/df_pop["casi vaccinati booster"],
             df["ospedalizzati non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df["ospedalizzati vaccinati"]/df_pop["ospedalizzati/ti vaccinati"],
             empty_data if is_old else df["ospedalizzati booster"]/df_pop["ospedalizzati/ti booster"],
             df["terapia intensiva non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df["terapia intensiva vaccinati"]/df_pop["ospedalizzati/ti vaccinati"],
             empty_data if is_old else df["terapia intensiva booster"]/df_pop["ospedalizzati/ti booster"],
             df["decessi non vaccinati"]/df_pop["decessi non vaccinati"],
             df["decessi vaccinati"]/df_pop["decessi vaccinati"],
             empty_data if is_old else df["decessi booster"]/df_pop["decessi booster"]]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = tassi_columns
    return df_tassi


def compute_incidence_età(df, is_old=False, df_pop=None):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata
    # dai file di età...

    if df_pop is None:
        # ...più vecchi del 12/01/2022
        empty_data = [0]*len(df)
        tassi = [df["casi non vaccinati"]/df["non vaccinati"],
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
                 empty_data if is_old else df["decessi booster"]/df["vaccinati booster"]]
    else:
        # ...più recenti
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
