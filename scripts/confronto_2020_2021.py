# -*- coding: utf-8 -*-
import locale
from calendar import monthrange
from datetime import timedelta
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import apply_plot_treatment, palette
from custom.preprocessing_dataframe import (compute_incidence,
                                            compute_incidence_std,
                                            get_df_complessivo,
                                            get_df_popolazione)
from custom.watermarks import add_last_updated, add_watermark


# Importa dati
def import_data():
    """ Imposta dati ISS e Protezione Civile """

    # Dati nazionali sui contagi
    url = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    df_IT = pd.read_csv(url,
                        parse_dates=["data"],
                        index_col="data")
    df_epid, df_pop = get_df_complessivo()

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_epid, df_pop)

    df_tassi.index = pd.to_datetime(df_epid["data"])
    df_tassi = df_tassi.iloc[::-1]

    # Ricava i tassi standardizzati per fascia di età
    df_tassi_std = compute_incidence_std().iloc[::-1]

    return df_IT, df_epid, df_tassi, df_tassi_std


def get_epidemic_data_2020():
    """ Importa dati epidemiologici 2020 """

    # Casi e decessi 2020
    abitanti_over12 = get_df_popolazione().sum()

    df_2020 = df_IT.loc["2020-06-15":end_date]
    df_2020 = df_2020[["totale_casi",
                       "deceduti"]].diff().rolling(window=30).mean()
    df_2020 = df_2020*30/(abitanti_over12/(10**5))
    df_2020.columns = ["casi", "decessi"]

    # Genera ticks e labels prima di plottare
    to_labels = sorted(set([x.strftime("%Y-%m-01") for x in df_2020[30:].index]))
    x_labels = [pd.to_datetime(t).strftime("%b")
                if i != 0 else "" for i, t in enumerate(to_labels)]
    x_labels = list(map(str.title, x_labels))
    x_ticks = np.arange(0, len(x_labels)*30, 30)

    casi_2020 = np.array(df_2020["casi"])[30:]
    dec_2020 = np.array(df_2020["decessi"])[30:]

    return casi_2020, dec_2020, x_ticks, x_labels


def get_epidemic_data_2021(is_std=False):
    """ Importa dati epidemiologici 2021 """

    tassi = df_tassi_std if is_std else df_tassi
    casi_2021_vacc = tassi["Casi, vaccinati completo"]
    casi_2021_novacc = tassi["Casi, non vaccinati"]
    dec_2021_vacc = tassi["Deceduti, vaccinati completo"]
    dec_2021_novacc = tassi["Deceduti, non vaccinati"]
    return casi_2021_vacc, casi_2021_novacc, dec_2021_vacc, dec_2021_novacc


def which_axe(ax, title="Casi"):
    "Imposta proprietà grafici"
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_title(f"{title} mensili (media mobile 30 gg)")
    ax.set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    ax.legend(loc="upper left")
    ax.margins(x=0)
    ax.grid()


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_confronto_2020_2021(show=False):
    """ Andamento curve epidemiche """

    xgrid_2020 = np.arange(0, len(casi_2020))
    xgrid_2021 = np.arange(0, 7*len(casi_2021_vacc), 7)
    xgrid_2021_std = np.arange(0, 7*len(dec_2021_vacc_std), 7)

    # Casi e decessi 2021
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    axes = ax.ravel()

    axes[0].plot(xgrid_2020[:xgrid_2021[-1]], casi_2020[:xgrid_2021[-1]], label="2020-21", color="black")
    axes[0].plot(xgrid_2020[xgrid_2021[-2]:], casi_2020[xgrid_2021[-2]:], color="black", alpha=0.25)
    axes[0].plot(xgrid_2021, casi_2021_novacc, label="2021-22 (non vaccinati)")
    axes[0].plot(xgrid_2021, casi_2021_vacc, label="2021-22 (vaccinati)")

    which_axe(axes[0])

    axes[1].plot(xgrid_2020[:xgrid_2021[-1]], dec_2020[:xgrid_2021[-1]], label="2020-21", color="black")
    axes[1].plot(xgrid_2020[xgrid_2021[-2]:], dec_2020[xgrid_2021[-2]:], color="black", alpha=0.25)
    axes[1].plot(xgrid_2021, dec_2021_novacc, label="2021-22 (non vaccinati)")
    axes[1].plot(xgrid_2021_std, dec_2021_novacc_std, color=palette[0], alpha=0.25,
                 label="Standarizzato", linestyle="--")
    axes[1].plot(xgrid_2021, dec_2021_vacc, label="2021-22 (vaccinati)")
    axes[1].plot(xgrid_2021_std, dec_2021_vacc_std, color=palette[1], alpha=0.25,
                 label="Standarizzato", linestyle="--")

    which_axe(axes[1], title="Decessi")

    fig.suptitle("Confronto 2020-2021 vs stesso periodo 2021-22")

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1], dati="ISS, Protezione Civile", y=-0.05)

    fig.tight_layout()
    fig.savefig("../risultati/confrontro_2020_2021.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # Imposta stile grafici
    apply_plot_treatment()

    df_IT, df_epid, df_tassi, df_tassi_std = import_data()

    # Calcola data fine df 2020-21
    # E' il primo giorno del mese successivo alla data dell'ultimo report
    end_date = df_tassi.index[-1].date().replace(year=2021)
    end_date = end_date.replace(day=monthrange(end_date.year, end_date.month)[1])\
        + timedelta(days=1)

    casi_2020, dec_2020, x_ticks, x_labels = get_epidemic_data_2020()
    casi_2021_vacc, casi_2021_novacc, dec_2021_vacc, dec_2021_novacc = get_epidemic_data_2021()
    _, _, dec_2021_vacc_std, dec_2021_novacc_std = get_epidemic_data_2021(is_std=True)

    # Plot data
    plot_confronto_2020_2021()
