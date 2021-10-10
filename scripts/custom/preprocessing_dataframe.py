import pandas as pd
import numpy as np


def compute_incidence(df_età):
    # ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    tassi = (7/30)*10**5*np.transpose([df_età["casi non vaccinati"]/df_età["non vaccinati"],  # noqa: E501
             df_età["casi vaccinati"]/df_età["vaccinati completo"],  # noqa: E128, E501
             df_età["ospedalizzati non vaccinati"]/df_età["non vaccinati"],
             df_età["ospedalizzati vaccinati"]/df_età["vaccinati completo"],
             df_età["terapia intensiva non vaccinati"]/df_età["non vaccinati"],
             df_età["terapia intensiva vaccinati"]/df_età["vaccinati completo"],  # noqa: E501
             df_età["decessi non vaccinati"]/df_età["non vaccinati"],
             df_età["decessi vaccinati"]/df_età["vaccinati completo"]])

    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = ["Casi, non vaccinati",
                        "Casi, vaccinati",
                        "Ospedalizzati, non vaccinati",
                        "Ospedalizzati, vaccinati",
                        "In terapia intensiva, non vaccinati",
                        "In terapia intensiva, vaccinati",
                        "Deceduti, non vaccinati",
                        "Deceduti, vaccinati"]
    return df_tassi


def date_parser(x):
    """date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(x, format="%Y/%m/%d")
