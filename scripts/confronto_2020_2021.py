# -*- coding: utf-8 -*-
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import apply_plot_treatment
from custom.preprocessing_dataframe import compute_incidence, date_parser
from custom.watermarks import add_last_updated, add_watermark


# Importa dati
def import_data():
    """ Imposta dati ISS e Protezione Civile """

    # Dati nazionali sui contagi
    url = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    df_IT = pd.read_csv(url,
                        parse_dates=["data"],
                        date_parser=date_parser,
                        index_col="data")

    # Dati ISS
    df_assoluti = pd.read_excel("../dati/dati_ISS_complessivi.xlsx", sheet_name="dati epidemiologici")
    df_pop = pd.read_excel("../dati/dati_ISS_complessivi.xlsx", sheet_name="popolazioni")

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_assoluti, df_pop)

    df_tassi.index = pd.to_datetime(df_assoluti["data"], format="%Y/%m/%d")
    df_tassi = df_tassi.iloc[::-1]
    return df_IT, df_assoluti, df_tassi


def get_epidemic_data_2020():
    """ Importa dati epidemiologici 2020 """

    # Casi e decessi 2020
    abitanti_over12 = 540*10**5

    df_2020 = df_IT.loc["2020-06-15":"2021-02-28"]
    df_2020 = df_2020[["totale_casi",
                       "deceduti"]].diff().rolling(window=30).mean()
    df_2020 = df_2020*30/(abitanti_over12/(10**5))
    df_2020.columns = ["casi", "decessi"]

    casi_2020 = np.array(df_2020["casi"])[30:]
    dec_2020 = np.array(df_2020["decessi"])[30:]
    return casi_2020, dec_2020


def get_epidemic_data_2021():
    """ Importa dati epidemiologici 2021 """

    casi_2021_vacc = df_tassi["Casi, vaccinati"]
    casi_2021_novacc = df_tassi["Casi, non vaccinati"]
    dec_2021_vacc = df_tassi["Deceduti, vaccinati"]
    dec_2021_novacc = df_tassi["Deceduti, non vaccinati"]
    return casi_2021_vacc, casi_2021_novacc, dec_2021_vacc, dec_2021_novacc


def which_axe(ax, title="Casi"):
    "Imposta proprietà grafici"
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_title(f"{title} mensili (media mobile 30 gg)")
    ax.set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    ax.legend()
    ax.set_xlim(0, )
    ax.grid()


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_confronto_2020_2021(show=False):
    """ Andamento curve epidemiche """

    xgrid_2020 = np.arange(0, len(casi_2020))
    xgrid_2021 = np.arange(0, 7*len(casi_2021_vacc), 7)

    # Casi e decessi 2021
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    axes = ax.ravel()

    axes[0].plot(xgrid_2020, casi_2020, label="2020-21")
    axes[0].plot(xgrid_2021, casi_2021_vacc, label="2021-22 (vaccinati)")
    axes[0].plot(xgrid_2021, casi_2021_novacc, label="2021-22 (non vaccinati)")
    which_axe(axes[0])

    axes[1].plot(xgrid_2020, dec_2020, label="2020-21")
    axes[1].plot(xgrid_2021, dec_2021_vacc, label="2021-22 (vaccinati)")
    axes[1].plot(xgrid_2021, dec_2021_novacc, label="2021-22 (non vaccinati)")
    which_axe(axes[1], title="Decessi")

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1], dati="ISS, Protezione Civile", y=-0.05)

    fig.tight_layout()
    fig.savefig("../risultati/confrontro_2020_2021.png",
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

    x_ticks = np.arange(15, 230, 30)
    x_labels = ["Ago", "Set", "Ott", "Nov", "Dic", "Gen", "Feb", "Mar"]

    # Plot data
    plot_confronto_2020_2021()
