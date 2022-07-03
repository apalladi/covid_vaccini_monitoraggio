# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from custom.plots import apply_plot_treatment, get_xticks_labels, palette
from custom.preprocessing_dataframe import (compute_incidence,
                                            compute_incidence_std,
                                            get_df_complessivo)
from custom.watermarks import add_last_updated, add_watermark

colori_incidenza = [palette[i] for i in [4, 1, 5]]


# Funzioni per il plot
def which_axe(axis):
    """ Imposta proprietà grafico """
    axis.set_xlabel("")
    axis.xaxis.reset_ticks()
    axis.set_xticks(x_ticks)
    axis.set_xticklabels(x_labels)
    axis.legend(["Non vaccinati", "Vaccinati 2/3/4 dosi",
                 "Vaccinati 3 dosi"], loc="upper left")
    axis.grid()


# Importa dati
def load_data():
    """ Importa dati dell'Istituto Superiore di Sanità
    ricavati dai bollettini settimanali."""

    df_epid, df_pop = get_df_complessivo()

    # Calcola tassi di infezione, ospedalizzazione e decessi
    # per vaccinati e non vaccinati

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_epid, df_pop)
    df_tassi.index = pd.to_datetime(df_epid["data"])

    # Ricava i tassi standardizzati per fascia di età
    df_tassi_std = compute_incidence_std()

    # Calcola i numeri assoluti (medi, giornalieri) dell"epidemia
    df_epid = df_epid.copy(deep=True)
    df_epid["data"] = pd.to_datetime(df_epid["data"])
    df_epid.set_index("data", drop=True, inplace=True)

    # Trasforma in numeri giornalieri
    df_epid = (1/30)*df_epid

    return df_tassi, df_tassi_std, df_epid


# Rappresentazione grafica dei risultati
@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_incidenza(show=False, is_std=False):
    """ Tassi di infezione, ricovero, decesso """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8.5, 8.5))

    # Unpack all the axes subplots
    axes = ax.ravel()

    y_label = "Ogni 100.000 persone per ciascun gruppo"

    titoli = ["dei nuovi casi", "degli ospedalizzati",
              "dei ricoverati in TI", "dei deceduti"]

    eventi = [["Casi, non vaccinati", "Casi, vaccinati completo", "Casi, booster"],
              ["Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati completo", "Ospedalizzati, booster"],
              ["In terapia intensiva, non vaccinati", "In terapia intensiva, vaccinati completo", "In terapia intensiva, booster"],
              ["Deceduti, non vaccinati", "Deceduti, vaccinati completo", "Deceduti, booster"]]

    for i, evento in enumerate(eventi):
        (df_tassi_std[evento] if is_std else df_tassi[evento]).plot(ax=axes[i])
        axes[i].set_title("Incidenza mensile " + titoli[i])
        axes[i].set_ylabel(y_label)
        which_axe(axes[i])

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()

    f_suff = "_std" if is_std else ""
    fig.savefig(f"../risultati/andamento_epidemia{f_suff}.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_num_assoluti(show=False):
    """ Andamento dei numeri assoluti """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8.5, 8.5))

    # Unpack all the axes subplots
    axes = ax.ravel()

    titoli = ["Nuovi casi giornalieri", "Nuovi ospedalizzati giornalieri",
              "Nuovi ricoverati in TI", "Decessi giornalieri"]

    eventi = [["casi non vaccinati", "casi vaccinati completo", "casi booster"],
              ["ospedalizzati non vaccinati", "ospedalizzati vaccinati completo", "ospedalizzati booster"],
              ["terapia intensiva non vaccinati", "terapia intensiva vaccinati completo", "terapia intensiva booster"],
              ["decessi non vaccinati", "decessi vaccinati completo", "decessi booster"]]

    for i, evento in enumerate(eventi):
        df_epid[evento].plot(ax=axes[i])
        axes[i].set_title(titoli[i] + " (media 30 gg)")
        which_axe(axes[i])

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/andamento_epidemia_num_assoluti.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_riassunto(show=False, is_std=False):
    """ Plot figura riassuntiva incidenze/numeri assoluti"""

    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

    # Unpack all the axes subplots
    axes = ax.ravel()

    # plot incidenze
    y_label = "Ogni 100.000 persone per ciascun gruppo"

    titoli = ["degli ospedalizzati", "dei ricoverati in TI", "dei deceduti"]

    eventi = [["Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati completo", "Ospedalizzati, booster"],
              ["In terapia intensiva, non vaccinati", "In terapia intensiva, vaccinati completo", "In terapia intensiva, booster"],
              ["Deceduti, non vaccinati", "Deceduti, vaccinati completo", "Deceduti, booster"]]

    for i, evento in enumerate(eventi):
        (df_tassi_std[evento] if is_std else df_tassi[evento]).plot(ax=axes[i])
        axes[i].set_title("Incidenza mensile " + titoli[i])
        axes[i].set_ylabel(y_label)
        which_axe(axes[i])

    # plot numeri assoluti
    titoli = ["Nuovi ospedalizzati giornalieri",
              "Nuovi ricoverati in TI", "Decessi giornalieri"]
    eventi = [["ospedalizzati non vaccinati", "ospedalizzati vaccinati completo", "ospedalizzati booster"],
              ["terapia intensiva non vaccinati", "terapia intensiva vaccinati completo", "terapia intensiva booster"],
              ["decessi non vaccinati", "decessi vaccinati completo", "decessi booster"]]

    for i, evento in enumerate(eventi):
        df_epid[evento].plot(ax=axes[i+3])
        axes[i+3].set_title(titoli[i] + " (media 30 gg)")
        which_axe(axes[i+3])

    fig.tight_layout()

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    f_suff = "_std" if is_std else ""
    fig.savefig(f"../risultati/andamento_epidemia_riassunto{f_suff}.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"lines.marker": None})
def plot_rapporto_tassi(show=False, is_std=False):
    """ Rapporto fra tassi """

    fig, ax = plt.subplots(figsize=(6, 5))

    tassi = df_tassi_std if is_std else df_tassi
    (tassi["Casi, non vaccinati"]/tassi["Casi, vaccinati completo"]).plot(label="Nuovi casi")
    (tassi["Ospedalizzati, non vaccinati"]/tassi["Ospedalizzati, vaccinati completo"]).plot(label="Ospedalizzazione")
    (tassi["In terapia intensiva, non vaccinati"]/tassi["In terapia intensiva, vaccinati completo"]).plot(label="Ricovero in TI")
    (tassi["Deceduti, non vaccinati"]/tassi["Deceduti, vaccinati completo"]).plot(label="Decesso")

    ax.xaxis.reset_ticks()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)

    ax.set_title("Rapporto fra le incidenze")
    ax.set_ylabel("Non vaccinati/vaccinati")
    ax.set_xlabel("")
    ax.grid()
    ax.legend()
    fig.tight_layout()

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, ax, y=-0.030)

    f_suff = "_std" if is_std else ""
    fig.savefig(f"../risultati/rapporto_tra_tassi{f_suff}.png",
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

    df_tassi, df_tassi_std, df_epid = load_data()

    x_ticks, x_labels = get_xticks_labels(reports_dates=df_epid.index)

    plot_incidenza()
    plot_incidenza(is_std=True)
    plot_rapporto_tassi()
    plot_rapporto_tassi(is_std=True)
    plot_num_assoluti()
    plot_riassunto()
    plot_riassunto(is_std=True)
