# -*- coding: utf-8 -*-
import locale
from datetime import timedelta
from os import chdir, path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import (apply_plot_treatment, date_from_csv_path,
                          list_età_csv, palette)
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark


# Recupero dati dai csv estratti dai report
def load_data():
    """ Recupera i dati estratti precedentemente """

    # Recupera csv più recente
    last_file = list_età_csv(True)

    # Data ultimo csv
    csv_date = date_from_csv_path(last_file)

    csv_date_d = csv_date.strftime("%d")
    csv_date_m = csv_date.strftime("%B")
    report_date = f"{csv_date_d}-{csv_date_m}-{csv_date.year}"

    message = f"Report ISS del {csv_date_d} {csv_date_m.capitalize()}: "
    message += f"https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_{report_date}.pdf"
    message += " I dati si riferiscono ai 30 giorni precedenti."
    print(message)

    df_età = pd.read_csv(last_file, sep=";")

    return report_date, df_età, csv_date, csv_date_d


def compute_efficacia():
    """ Calcola efficacia vaccini """
    eff_contagio = (1 - df_tassi.iloc[:, 1]/df_tassi.iloc[:, 0])*100
    eff_osp = (1 - df_tassi.iloc[:, 3]/df_tassi.iloc[:, 2])*100
    eff_terint = (1 - df_tassi.iloc[:, 5]/df_tassi.iloc[:, 4])*100
    eff_decessi = (1 - df_tassi.iloc[:, 7]/df_tassi.iloc[:, 6])*100
    return eff_contagio, eff_osp, eff_terint, eff_decessi


# Funzioni per il plot
def get_data_labels():
    """ Ricava label data dei grafici """
    csv_date_start = csv_date - timedelta(days=30)
    start_month = csv_date_start.strftime("%b").capitalize()
    start_day = csv_date_start.strftime("%d")
    start_date = f"{start_day} {start_month}"
    end_month = csv_date.strftime("%b").capitalize()
    end_date = f"{csv_date_d} {end_month}"
    return start_date, end_date


def which_axe(axis):
    """ Imposta proprietà grafici """
    axis.set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    axis.set_xlabel("Fascia d'età")
    axis.legend(["Non vaccinati", "Vaccinati"])
    axis.grid()
    for tick in axis.get_xticklabels():
        tick.set_rotation(0)


def which_axe_bar(axis):
    """ Imposta proprietà grafici """
    axis.set_xlabel("Fascia d'età")
    axis.grid()
    for tick in axis.get_xticklabels():
        tick.set_rotation(0)


def add_to_plot():
    """ Imposta proprietà grafici """
    plt.grid()
    plt.xlabel("Fascia d'età")


# Rappresentazione grafica dei risultati
def plot_tassi(show=False):
    """ Tassi di contagio """

    fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(7, 7))

    # Unpack all the axes subplots
    axes = axes2.ravel()

    df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], kind="bar")
    axes[0].set_title("Incidenza mensile dei nuovi casi")
    which_axe(axes[0])

    df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], kind="bar")
    axes[1].set_title("Incidenza mensile degli ospedalizzati")
    which_axe(axes[1])

    df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], kind="bar")
    axes[2].set_title("Incidenza mensile dei ricoveri in TI")
    which_axe(axes[2])

    df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], kind="bar")
    axes[3].set_title("Incidenza mensile dei deceduti")
    which_axe(axes[3])

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/tassi_per_età.png", dpi=300, bbox_inches="tight")
    if show:
        plt.show()


def plot_efficacia(show=False):
    """ Efficacia dei vaccini """

    fig = plt.figure(figsize=(7.5, 7.5))

    plt.subplot(2, 2, 1)
    plt.bar(eff_contagio.index,
            eff_contagio,
            color=palette[1],
            width=0.5)
    plt.title("Efficacia contro il contagio")
    add_to_plot()

    plt.subplot(2, 2, 2)
    plt.bar(eff_osp.index, eff_osp, color=palette[5], width=0.5)
    plt.title("Efficacia contro l'ospedalizzazione")
    add_to_plot()

    plt.subplot(2, 2, 3)
    plt.bar(eff_terint.index, eff_terint, color=palette[4], width=0.5)
    plt.title("Efficacia contro il ricovero in TI")
    add_to_plot()

    plt.subplot(2, 2, 4)
    plt.bar(eff_decessi.index,
            eff_decessi,
            color="black",
            width=0.5)
    plt.title("Efficacia contro il decesso")
    add_to_plot()

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/efficacia_vaccini.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def plot_riassunto(show=False):
    """ Grafico riassuntivo """

    fig, axes2 = plt.subplots(nrows=2, ncols=4, figsize=(15, 7.5))

    # Unpack all the axes subplots
    axes = axes2.ravel()

    df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], kind="bar")
    axes[0].set_title("Incidenza mensile dei nuovi casi")
    which_axe(axes[0])

    df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], kind="bar")
    axes[1].set_title("Incidenza mensile degli ospedalizzati")
    which_axe(axes[1])

    df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], kind="bar")
    axes[2].set_title("Incidenza mensile dei ricoveri in TI")
    which_axe(axes[2])

    df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], kind="bar")
    axes[3].set_title("Incidenza mensile dei deceduti")
    which_axe(axes[3])

    eff_contagio.plot(kind="bar", ax=axes[4], color=palette[1])
    axes[4].set_title("Efficacia contro il contagio")
    which_axe_bar(axes[4])

    eff_osp.plot(kind="bar", ax=axes[5], color=palette[5])
    axes[5].set_title("Efficacia contro l'ospedalizzazione")
    which_axe_bar(axes[5])

    eff_terint.plot(kind="bar", ax=axes[6], color=palette[4])
    axes[6].set_title("Efficacia contro il ricovero in TI")
    which_axe_bar(axes[6])

    eff_decessi.plot(kind="bar", ax=axes[7], color="black")
    axes[7].set_title("Efficacia contro il decesso")
    which_axe_bar(axes[7])

    # add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/tassi_efficacia.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def plot_focus_60(show=False):
    """ Focus sugli over 60 """

    df_over60 = df_età.loc[[2, 3],
                           ["non vaccinati",
                            "vaccinati completo",
                            "terapia intensiva non vaccinati",
                            "terapia intensiva vaccinati",
                            "decessi non vaccinati",
                            "decessi vaccinati"]].sum()
    over60_array = np.array(df_over60)

    fig = plt.figure(figsize=(10, 3.5))

    plt.subplot(1, 3, 1)
    plt.bar(0, over60_array[0], width=0.5, color=palette[4])
    plt.bar(1, over60_array[1], width=0.5, color=palette[5])
    plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
    plt.yticks(10**6*np.arange(0, 17, 2),
               ["0", "2M", "4M", "6M", "8M", "10M", "12M", "14M", "16M"])
    plt.grid()
    plt.title(f"Popolazione over 60 \n{start_date} - {end_date}")

    plt.subplot(1, 3, 2)
    plt.bar(0, over60_array[2], width=0.5, color=palette[4])
    plt.bar(1, over60_array[3], width=0.5, color=palette[5])
    plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
    plt.grid()
    plt.title(f"In terapia intensiva \n{start_date} - {end_date}")

    plt.subplot(1, 3, 3)
    plt.bar(0, over60_array[4], width=0.5, color=palette[4])
    plt.bar(1, over60_array[5], width=0.5, color=palette[5])
    plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
    plt.grid()
    plt.title(f"Deceduti \n{start_date} - {end_date}")

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/focus_over60.png", dpi=300, bbox_inches="tight")

    ratio_vacc_novacc = round(over60_array[1]/over60_array[0], 1)
    ratio_terint = round(over60_array[2]/over60_array[3], 1)
    ratio_dec = round(over60_array[4]/over60_array[5], 1)

    print("Rapporto tra vaccinati e non vaccinati", ratio_vacc_novacc)
    print("Rapporto tra ricoverati in terapia intensiva (novacc/vacc)",
          ratio_terint)
    print("Rapporto tra deceduti (novacc/vacc)", ratio_dec)

    print("Peso sul sistema sanitario di un non vaccinato over 60:",
          round(ratio_vacc_novacc*ratio_terint, 2))
    print("Peso sulla mortalità di un non vaccinato over 60:      ",
          round(ratio_vacc_novacc*ratio_dec, 2))

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

    report_date, df_età, csv_date, csv_date_d = load_data()

    start_date, end_date = get_data_labels()

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    df_tassi = compute_incidence(df_età)
    df_tassi.index = df_età["età"]

    # Ricava efficacia
    eff_contagio, eff_osp, eff_terint, eff_decessi = compute_efficacia()

    plot_tassi()
    plot_efficacia()
    plot_riassunto()
    plot_focus_60()
