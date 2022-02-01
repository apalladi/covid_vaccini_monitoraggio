import numpy as np
import pandas as pd


def compute_incidence(df_epid, df_pop):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata
    tassi = [df_epid["casi non vaccinati"]/df_pop["casi non vaccinati"],
             df_epid["casi vaccinati > 4-6 mesi"]/df_pop["casi vaccinati > 4-6 mesi"],
             df_epid["casi vaccinati > 4-6 mesi"]/df_pop["casi vaccinati < 4-6 mesi"],
             df_epid["casi booster"]/df_pop["casi booster"],
             df_epid["casi vaccinati completo"]/df_pop["casi vaccinati completo"],
             df_epid["ospedalizzati non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["ospedalizzati vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["ospedalizzati vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["terapia intensiva non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["terapia intensiva vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["terapia intensiva vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["decessi non vaccinati"]/df_pop["decessi non vaccinati"],
             df_epid["decessi vaccinati > 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi vaccinati < 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi booster"]/df_pop["decessi booster"],
             df_epid["decessi vaccinati completo"]/df_pop["decessi vaccinati completo"]]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = ["Casi, non vaccinati", "Casi, vaccinati > 4-6 mesi",
                        "Casi, vaccinati < 4-6 mesi", "Casi, booster", "Casi, vaccinati completo",
                        "Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati > 4-6 mesi",
                        "Ospedalizzati, vaccinati < 4-6 mesi", "Ospedalizzati, booster",
                        "Ospedalizzati, vaccinati completo", "In terapia intensiva, non vaccinati",
                        "In terapia intensiva, vaccinati > 4-6 mesi", "In terapia intensiva, vaccinati < 4-6 mesi",
                        "In terapia intensiva, booster", "In terapia intensiva, vaccinati completo",
                        "Deceduti, non vaccinati", "Deceduti, vaccinati > 4-6 mesi",
                        "Deceduti, vaccinati < 4-6 mesi", "Deceduti, booster",
                        "Deceduti, vaccinati completo"]
    return df_tassi


def date_parser(x):
    """date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(x, format="%Y/%m/%d")
