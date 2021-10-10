# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib.pyplot as plt
import pandas as pd

from custom.plots import update_labels
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark


# Funzioni per il plot
def which_axe(x, axes, x_date, x_label):
    axes[x].set_xticks(x_date)
    axes[x].set_xlabel("")
    axes[x].set_xticklabels(x_label)
    axes[x].legend(["Non vaccinati", "Vaccinati"])
    axes[x].grid()


# Importa dati
def load_data():
    """ Importa dati dell"Istituto Superiore di Sanità
Questi dati sono ricavati dai bollettini settimanali dell"ISS. Vedi ad esempio:
epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_15-settembre-2021.pdf
"""
    df_assoluti = pd.read_csv("../dati/dati_ISS_complessivi.csv", sep=";")

    """ Elaborazione dati """

    # Calcola tassi di infezione, ospedalizzazione e decessi
    # per vaccinati e non vaccinati

    # ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_assoluti)
    df_tassi.index = pd.to_datetime(df_assoluti["data"], format="%Y/%m/%d")

    # Calcola i numeri assoluti (medi, giornalieri) dell"epidemia
    df_assoluti2 = df_assoluti.copy(deep=True)
    df_assoluti2.index = pd.to_datetime(df_assoluti2["data"],
                                        format="%Y/%m/%d")
    df_assoluti2.drop("data", axis=1, inplace=True)
    # trasforma in numeri settimanali
    df_assoluti2 = (1/30)*df_assoluti2

    return df_tassi, df_assoluti2


# Rappresentazione grafica dei risultati
def plot_incidenza(show=False):
    plt.style.use("seaborn-dark")
    """ Tassi di infezione, ricovero, decesso """
    fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(7.5, 7.5))

    # unpack all the axes subplots
    axes = axes2.ravel()

    # colori per plot vaccinati/non vaccinati
    palette = ["tab:red", "tab:green"]

    df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], marker="o", color=palette)
    axes[0].set_title("Incidenza settimanale dei nuovi casi")
    axes[0].set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    which_axe(0, axes, x_date, x_label)

    df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], marker="o", color=palette)
    axes[1].set_title("Incidenza settimanale degli ospedalizzati")
    axes[1].set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    which_axe(1, axes, x_date, x_label)

    df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], marker="o", color=palette)
    axes[2].set_title("Incidenza settimanale dei ricoverati in TI")
    axes[2].set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    which_axe(2, axes, x_date, x_label)

    df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], marker="o", color=palette)
    axes[3].set_title("Incidenza settimanale dei deceduti")
    axes[3].set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    which_axe(3, axes, x_date, x_label)

    # add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/andamento_epidemia.png",
                dpi=300,
                bbox_inches="tight")

    if show:
        plt.show()


def plot_rapporto_tassi(show=False):
    plt.style.use("seaborn-dark")
    """ Rapporto fra tassi """
    fig = plt.figure(figsize=(6, 5))
    (df_tassi.iloc[:, 0]/df_tassi.iloc[:, 1]).plot(label="Nuovi casi",
                                                   color="blue")
    (df_tassi.iloc[:, 2]/df_tassi.iloc[:, 3]).plot(label="Ospedalizzazione",
                                                   color="green")
    (df_tassi.iloc[:, 4]/df_tassi.iloc[:, 5]).plot(label="Ricovero in TI",
                                                   color="red")
    (df_tassi.iloc[:, 6]/df_tassi.iloc[:, 7]).plot(label="Decesso",
                                                   color="gray")
    plt.title("Rapporto fra le incidenze")
    plt.ylabel("Non vaccinati/vaccinati")
    plt.xlabel("")
    plt.xticks(x_date, x_label)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.savefig("../risultati/rapporto_tra_tassi.png",
                dpi=300,
                bbox_inches="tight")

    if show:
        plt.show()


def plot_num_assoluti(show=False):
    plt.style.use("seaborn-dark")
    """ Andamento dei numeri assoluti """
    fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(7.5, 7.5))

    # unpack all the axes subplots
    axes = axes2.ravel()

    # colori per plot vaccinati/non vaccinati
    palette = ["tab:red", "tab:green"]

    df_assoluti.iloc[:, [2, 3]].plot(ax=axes[0], marker="o", color=palette)
    axes[0].set_title("Nuovi casi giornalieri \n(media mobile 30 gg)")
    which_axe(0, axes, x_date, x_label)

    df_assoluti.iloc[:, [4, 5]].plot(ax=axes[1], marker="o", color=palette)
    axes[1].set_title("Nuovi ospedalizzati giornalieri \n(media mobile 30 gg)")
    which_axe(1, axes, x_date, x_label)

    df_assoluti.iloc[:, [6, 7]].plot(ax=axes[2], marker="o", color=palette)
    axes[2].set_title("Nuovi ricoverati in TI giornalieri \n(media mobile 30 gg)")  # noqa: E501
    which_axe(2, axes, x_date, x_label)

    df_assoluti.iloc[:, [8, 9]].plot(ax=axes[3], marker="o", color=palette)
    axes[3].set_title("Decessi giornalieri \n(media mobile 30 gg)")
    which_axe(3, axes, x_date, x_label)

    # add watermarks
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

    x_date = ["2021-07-01", "2021-08-01", "2021-09-01", "2021-10-01"]
    x_label = ["\nLug\n21", "\nAgo", "\nSet", "\nOtt"]

    df_tassi, df_assoluti = load_data()
    x_date, x_label = update_labels(df_tassi, x_date, x_label)

    plot_incidenza()
    plot_rapporto_tassi()
    plot_num_assoluti()
