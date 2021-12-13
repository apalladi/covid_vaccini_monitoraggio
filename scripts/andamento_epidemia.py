# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from custom.plots import apply_plot_treatment, get_xticks_labels, palette
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark


# Funzioni per il plot
def which_axe(axis):
    """ Imposta proprietà grafico """
    axis.set_xlabel("")
    axis.xaxis.reset_ticks()
    axis.set_xticks(x_ticks, x_labels)
    axis.legend(["Non vaccinati", "Vaccinati"])
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
@mpl.rc_context({"legend.handlelength": 1.0})
def plot_incidenza(show=False):
    """ Tassi di infezione, ricovero, decesso """

    fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(8.5, 8.5))

    # Unpack all the axes subplots
    axes = axes2.ravel()

    y_label = "Ogni 100.000 persone per ciascun gruppo"

    df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], color=palette_)
    axes[0].set_title("Incidenza mensile dei nuovi casi")
    axes[0].set_ylabel(y_label)
    which_axe(axes[0])

    df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], color=palette_)
    axes[1].set_title("Incidenza mensile degli ospedalizzati")
    axes[1].set_ylabel(y_label)
    which_axe(axes[1])

    df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], color=palette_)
    axes[2].set_title("Incidenza mensile dei ricoverati in TI")
    axes[2].set_ylabel(y_label)
    which_axe(axes[2])

    df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], color=palette_)
    axes[3].set_title("Incidenza mensile dei deceduti")
    axes[3].set_ylabel(y_label)
    which_axe(axes[3])

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/andamento_epidemia.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"lines.marker": None})
def plot_rapporto_tassi(show=False):
    """ Rapporto fra tassi """

    fig = plt.figure(figsize=(6, 5))

    (df_tassi.iloc[:, 0]/df_tassi.iloc[:, 1]).plot(label="Nuovi casi")
    (df_tassi.iloc[:, 2]/df_tassi.iloc[:, 3]).plot(label="Ospedalizzazione")
    (df_tassi.iloc[:, 4]/df_tassi.iloc[:, 5]).plot(label="Ricovero in TI")
    (df_tassi.iloc[:, 6]/df_tassi.iloc[:, 7]).plot(label="Decesso")

    ax = plt.gca()
    ax.xaxis.reset_ticks()
    ax.set_xticks(x_ticks, x_labels)

    plt.title("Rapporto fra le incidenze")
    plt.ylabel("Non vaccinati/vaccinati")
    plt.xlabel("")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Add watermarks
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.savefig("../risultati/rapporto_tra_tassi.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"legend.handlelength": 1.0})
def plot_num_assoluti(show=False):
    """ Andamento dei numeri assoluti """

    fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(8.5, 8.5))

    # Unpack all the axes subplots
    axes = axes2.ravel()

    df_assoluti.iloc[:, [4, 6]].plot(ax=axes[0], color=palette_)
    axes[0].set_title("Nuovi casi giornalieri \n(media 30 gg)")
    which_axe(axes[0])

    df_assoluti.iloc[:, [8, 10]].plot(ax=axes[1], color=palette_)
    axes[1].set_title("Nuovi ospedalizzati giornalieri \n(media 30 gg)")
    which_axe(axes[1])

    df_assoluti.iloc[:, [12, 14]].plot(ax=axes[2], color=palette_)
    axes[2].set_title("Nuovi ricoverati in TI giornalieri \n(media 30 gg)")
    which_axe(axes[2])

    df_assoluti.iloc[:, [16, 18]].plot(ax=axes[3], color=palette_)
    axes[3].set_title("Decessi giornalieri \n(media 30 gg)")
    which_axe(axes[3])

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/andamento_epidemia_num_assoluti.png",
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

    # Colori per plot vaccinati/non vaccinati
    palette_ = [palette[4], palette[5]]

    df_tassi, df_assoluti = load_data()

    x_ticks, x_labels = get_xticks_labels(reports_dates=df_assoluti.index)

    plot_incidenza()
    plot_rapporto_tassi()
    plot_num_assoluti()
