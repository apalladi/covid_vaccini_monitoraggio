# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from custom.plots import apply_plot_treatment, get_xticks_labels, palette
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_last_updated, add_watermark

colori_incidenza = [palette[i] for i in [4, 1, 5]]


# Funzioni per il plot
def which_axe(axis):
    """ Imposta proprietà grafico """
    axis.set_xlabel("")
    axis.xaxis.reset_ticks()
    axis.set_xticks(x_ticks)
    axis.set_xticklabels(x_labels)
    axis.legend(["Non vaccinati", "Vaccinati con 2 o più dosi",
                 "Vaccinati con terza dose"], loc="upper left")
    axis.grid()


# Importa dati
def load_data():
    """ Importa dati dell'Istituto Superiore di Sanità
    ricavati dai bollettini settimanali. Vedi ad esempio:
    epicentro.iss.it/coronavirus/bollettino/
    Bollettino-sorveglianza-integrata-COVID-19_15-settembre-2021.pdf"""

    df_assoluti = pd.read_csv("../dati/dati_ISS_complessivi.csv", sep=";")

    # Calcola tassi di infezione, ospedalizzazione e decessi
    # per vaccinati e non vaccinati

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_assoluti)
    df_tassi.index = pd.to_datetime(df_assoluti["data"])

    # Calcola i numeri assoluti (medi, giornalieri) dell"epidemia
    df_assoluti = df_assoluti.copy(deep=True)
    df_assoluti["data"] = pd.to_datetime(df_assoluti["data"])
    df_assoluti.set_index("data", drop=True, inplace=True)

    # Trasforma in numeri giornalieri
    df_assoluti = (1/30)*df_assoluti

    return df_tassi, df_assoluti


# Rappresentazione grafica dei risultati
@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_incidenza(show=False):
    """ Tassi di infezione, ricovero, decesso """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8.5, 8.5))

    # Unpack all the axes subplots
    axes = ax.ravel()

    y_label = "Ogni 100.000 persone per ciascun gruppo"

    titoli = ["dei nuovi casi", "degli ospedalizzati",
              "dei ricoverati in TI", "dei deceduti"]
    eventi = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]

    for i, evento in enumerate(eventi):
        df_tassi.iloc[:, evento].plot(ax=axes[i])
        axes[i].set_title("Incidenza mensile " + titoli[i])
        axes[i].set_ylabel(y_label)
        which_axe(axes[i])

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()

    fig.savefig("../risultati/andamento_epidemia.png",
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
    eventi = [[4, 6, 7], [8, 10, 11], [12, 14, 15], [16, 18, 19]]

    for i, evento in enumerate(eventi):
        df_assoluti.iloc[:, evento].plot(ax=axes[i])
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
def plot_riassuto(show=False):
    """ Plot figura riassuntiva incidenze/numeri assoluti"""

    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

    # Unpack all the axes subplots
    axes = ax.ravel()

    # plot incidenze
    y_label = "Ogni 100.000 persone per ciascun gruppo"

    titoli = ["degli ospedalizzati", "dei ricoverati in TI", "dei deceduti"]
    eventi = [[3, 4, 5], [6, 7, 8], [9, 10, 11]]

    for i, evento in enumerate(eventi):
        df_tassi.iloc[:, evento].plot(ax=axes[i])
        axes[i].set_title("Incidenza mensile " + titoli[i])
        axes[i].set_ylabel(y_label)
        which_axe(axes[i])

    # plot numeri assoluti
    titoli = ["Nuovi ospedalizzati giornalieri",
              "Nuovi ricoverati in TI", "Decessi giornalieri"]
    eventi = [[8, 10, 11], [12, 14, 15], [16, 18, 19]]

    for i, evento in enumerate(eventi):
        df_assoluti.iloc[:, evento].plot(ax=axes[i+3])
        axes[i+3].set_title(titoli[i] + " (media 30 gg)")
        which_axe(axes[i+3])

    fig.tight_layout()

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.savefig("../risultati/andamento_epidemia_riassunto.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"lines.marker": None})
def plot_rapporto_tassi(show=False):
    """ Rapporto fra tassi """

    fig, ax = plt.subplots(figsize=(6, 5))

    (df_tassi.iloc[:, 0]/df_tassi.iloc[:, 1]).plot(label="Nuovi casi")
    (df_tassi.iloc[:, 3]/df_tassi.iloc[:, 4]).plot(label="Ospedalizzazione")
    (df_tassi.iloc[:, 6]/df_tassi.iloc[:, 7]).plot(label="Ricovero in TI")
    (df_tassi.iloc[:, 9]/df_tassi.iloc[:, 10]).plot(label="Decesso")

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
    add_last_updated(fig, ax)

    fig.savefig("../risultati/rapporto_tra_tassi.png",
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

    df_tassi, df_assoluti = load_data()

    x_ticks, x_labels = get_xticks_labels(reports_dates=df_assoluti.index)

    plot_incidenza()
    plot_rapporto_tassi()
    plot_num_assoluti()
    plot_riassuto()
