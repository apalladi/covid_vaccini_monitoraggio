# -*- coding: utf-8 -*-
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import apply_plot_treatment
from custom.preprocessing_dataframe import compute_incidence, date_parser
from custom.watermarks import add_watermark


# Importa dati
def import_data():
    """ Imposta dati ISS e Protezione Civile """

    # Dati nazionali sui contagi
    url = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"  # noqa: E501
    df_IT = pd.read_csv(url,
                        parse_dates=["data"],
                        date_parser=date_parser,
                        index_col="data")

    # Dati ISS
    df_assoluti = pd.read_csv("../dati/dati_ISS_complessivi.csv", sep=";")

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_assoluti)

    df_tassi.index = pd.to_datetime(df_assoluti["data"], format="%Y/%m/%d")
    df_tassi = df_tassi.iloc[::-1]
    return df_IT, df_assoluti, df_tassi


def get_epidemic_data_2020():
    """ Importa dati epidemiologici 2020 """

    # Casi e decessi 2020
    abitanti_over12 = 540*10**5

    mask_2020 = (df_IT.index >= "2020-06-15") & (df_IT.index <= "2020-12-31")
    df_2020 = df_IT[mask_2020]
    df_2020 = df_2020[["totale_casi",
                       "deceduti"]].diff().rolling(window=30).mean()
    df_2020 = df_2020*30/(abitanti_over12/(10**5))
    df_2020.columns = ["casi", "decessi"]

    casi_2020 = np.array(df_2020["casi"])[30:]
    dec_2020 = np.array(df_2020["decessi"])[30:]
    return casi_2020, dec_2020


def get_epidemic_data_2021():
    """ Importa dati epidemiologici 2021 """

    casi_2021_vacc = np.array(df_tassi["Casi, vaccinati"])
    casi_2021_novacc = np.array(df_tassi["Casi, non vaccinati"])
    dec_2021_vacc = np.array(df_tassi["Deceduti, vaccinati"])
    dec_2021_novacc = np.array(df_tassi["Deceduti, non vaccinati"])
    return casi_2021_vacc, casi_2021_novacc, dec_2021_vacc, dec_2021_novacc


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_confronto_2020_2021(show=False):
    """ Andamento curve epidemiche """

    x_label1 = np.arange(15, 170, 30)
    x_label2 = ["Ago", "Set", "Ott", "Nov", "Dic", "Gen"]
    xgrid_2020 = np.arange(0, len(casi_2020))
    xgrid_2021 = np.arange(0, 7*len(casi_2021_vacc), 7)

    # Casi e decessi 2021
    fig = plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(xgrid_2020, casi_2020, label="2020")
    plt.plot(xgrid_2021, casi_2021_vacc,
             label="2021 (vaccinati)")
    plt.plot(xgrid_2021,
             casi_2021_novacc,
             label="2021 (non vaccinati)")
    plt.xticks(x_label1, x_label2)
    plt.title("Casi mensili (media mobile 30 gg)")
    plt.ylabel("Ogni 100.000 persone per ciascun gruppo")
    plt.legend()
    plt.xlim(0, 165)
    plt.grid()

    plt.subplot(1, 2, 2)
    plt.plot(xgrid_2020, dec_2020, label="2020")
    plt.plot(xgrid_2021,
             dec_2021_vacc, label="2021 (vaccinati)")
    plt.plot(xgrid_2021,
             dec_2021_novacc,
             label="2021 (non vaccinati)")
    plt.xticks(x_label1, x_label2)
    plt.title("Decessi mensili (media mobile 30 gg)")
    plt.ylabel("Ogni 100.000 persone per ciascun gruppo")
    plt.legend()
    plt.xlim(0, 165)
    plt.grid()

    # Add watermarks
    add_watermark(fig)

    plt.tight_layout()
    plt.savefig("../risultati/confrontro_2020_2021.png",
                dpi=300,
                bbox_inches="tight")
    if show is True:
        plt.show()


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Imposta stile grafici
    apply_plot_treatment()

    df_IT, df_assoluti, df_tassi = import_data()
    casi_2020, dec_2020 = get_epidemic_data_2020()
    casi_2021_vacc, casi_2021_novacc, dec_2021_vacc, dec_2021_novacc = get_epidemic_data_2021()

    # Plot data
    plot_confronto_2020_2021()
