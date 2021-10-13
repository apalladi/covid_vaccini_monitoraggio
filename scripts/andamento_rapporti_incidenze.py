# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import date_from_csv_path, list_età_csv
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark


# Funzioni per il plot
def compute_incidence_ratio(category):
    """ Calcolo rapporti incidenze per età """

    result_list = []

    for f_name in files:
        df_età = pd.read_csv(f_name, sep=";")
        df_tassi = compute_incidence(df_età)
        r_casi = df_tassi.iloc[:, 0]/(df_tassi.iloc[:, 0]+df_tassi.iloc[:, 1])
        r_casi *= 100
        r_osp = df_tassi.iloc[:, 2]/(df_tassi.iloc[:, 2]+df_tassi.iloc[:, 3])
        r_osp *= 100
        r_ti = df_tassi.iloc[:, 4]/(df_tassi.iloc[:, 4]+df_tassi.iloc[:, 5])
        r_ti *= 100
        r_dec = df_tassi.iloc[:, 6]/(df_tassi.iloc[:, 6]+df_tassi.iloc[:, 7])
        r_dec *= 100
        rapporto_fra_tassi = pd.DataFrame(np.transpose([r_casi,
                                                        r_osp,
                                                        r_ti,
                                                        r_dec]))
        rapporto_fra_tassi.columns = ["Casi",
                                      "Ospedalizzati",
                                      "TI",
                                      "Deceduti"]
        rapporto_fra_tassi.index = df_tassi.index
        result_list.append(np.array(rapporto_fra_tassi[category]))

    return np.array(result_list)


def get_ticks_labels():
    # Aggiorna ticks e label dinamicamente
    ticks = np.arange(0, len(files), 2)

    # Calcola step in base ai ticks
    # arrotonda il risultato
    n_ticks = len(ticks)
    slice_end = round(len(files)/n_ticks)
    if (len(files[0::slice_end]) > n_ticks):
        # Arrotonda per eccesso
        slice_end += 1

    labels = [date_from_csv_path(csv).strftime("%d\n%b").title()
              for csv in files][0::slice_end]
    return ticks, labels


def add_to_plot(ticks, labels):
    """ Imposta proprietà grafico """
    plt.xticks(ticks, labels)
    plt.ylabel("Contributo dei non vaccinati alle incidenze")
    plt.legend(["12-39", "40-59", "60-79", "80+"], loc=4)
    plt.yticks(np.arange(50, 101, 10),
               ["50%", "60%", "70%", "80%", "90%", "100%"])
    plt.ylim(60, 102)
    plt.grid()


# Rappresentazione grafica risultati
def plot_rapporti_incidenze(ticks, labels, show=False):
    """ Rapporto fra incidenze """

    fig = plt.figure(figsize=(9, 8))

    plt.subplot(2, 2, 1)
    plt.plot(compute_incidence_ratio("Casi"))
    plt.title("Casi")
    add_to_plot(ticks, labels)

    plt.subplot(2, 2, 2)
    plt.plot(compute_incidence_ratio("Ospedalizzati"))
    plt.title("Ospedalizzati")
    add_to_plot(ticks, labels)

    plt.subplot(2, 2, 3)
    plt.plot(compute_incidence_ratio("TI"))
    plt.title("In terapia intensiva")
    add_to_plot(ticks, labels)

    plt.subplot(2, 2, 4)
    plt.plot(compute_incidence_ratio("Deceduti"))
    plt.title("Decessi")
    add_to_plot(ticks, labels)

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/andamento_rapporti_incidenze.png",
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
    plt.style.use("seaborn-dark")

    # Lista i csv
    files = list_età_csv()

    ticks, labels = get_ticks_labels()

    plot_rapporti_incidenze(ticks, labels)
