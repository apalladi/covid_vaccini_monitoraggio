# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import (apply_plot_treatment, date_from_csv_path,
                          get_xticks_labels, list_età_csv, palette)
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark

classi_età = ["12-39", "40-59", "60-79", "80+"]


# Funzioni per il plot
def compute_incidence_ratio(category):
    """ Calcolo rapporti incidenze per età """

    result_list = []

    for f_name in files:
        df_età = pd.read_csv(f_name, sep=";")
        df_tassi = compute_incidence(df_età)
        r_casi = df_tassi.iloc[:, 0]/(df_tassi.iloc[:, 0] + df_tassi.iloc[:, 1])*100
        r_osp = df_tassi.iloc[:, 2]/(df_tassi.iloc[:, 2] + df_tassi.iloc[:, 3])*100
        r_ti = df_tassi.iloc[:, 4]/(df_tassi.iloc[:, 4] + df_tassi.iloc[:, 5])*100
        r_dec = df_tassi.iloc[:, 6]/(df_tassi.iloc[:, 6] + df_tassi.iloc[:, 7])*100
        rapporto_fra_tassi = pd.DataFrame(np.transpose([r_casi, r_osp, r_ti, r_dec]))
        rapporto_fra_tassi.columns = ["Casi", "Ospedalizzati", "TI", "Deceduti"]
        rapporto_fra_tassi.index = df_tassi.index
        result_list.append(np.array(rapporto_fra_tassi[category]))

    return np.array(result_list)


def add_to_plot():
    """ Imposta proprietà grafico """
    plt.xticks(ratio_x_ticks, ratio_x_labels)
    plt.ylabel("Contributo dei non vaccinati alle incidenze")
    plt.legend(classi_età, loc=4)
    plt.yticks(np.arange(50, 101, 10), ["50%", "60%", "70%", "80%", "90%", "100%"])
    plt.ylim(60, 102)
    plt.grid()


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_rapporti_incidenze(show=False):
    """ Rapporto fra incidenze """

    fig = plt.figure(figsize=(9, 8))

    plt.subplot(2, 2, 1)
    plt.plot(compute_incidence_ratio("Casi"))
    plt.title("Casi")
    add_to_plot()

    plt.subplot(2, 2, 2)
    plt.plot(compute_incidence_ratio("Ospedalizzati"))
    plt.title("Ospedalizzati")
    add_to_plot()

    plt.subplot(2, 2, 3)
    plt.plot(compute_incidence_ratio("TI"))
    plt.title("In terapia intensiva")
    add_to_plot()

    plt.subplot(2, 2, 4)
    plt.plot(compute_incidence_ratio("Deceduti"))
    plt.title("Decessi")
    add_to_plot()

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/andamento_rapporti_incidenze.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def ricava_andamenti_età(files, età, colonna, incidenza_mensile):
    """Ricava andamento delle varie incindenze nel tempo,
    divise per fascia d"età e categoria"""

    # create dates
    dates = [date_from_csv_path(f) for f in files]

    # loop around the .csv files
    results_date = []
    for i in range(len(files)):
        df = pd.read_csv(files[i], sep=";")
        df = df[df["età"] == età]

        non_vacc_labels = ["casi non vaccinati",
                           "ospedalizzati non vaccinati",
                           "terapia intensiva non vaccinati",
                           "decessi non vaccinati"]

        vacc_labels = ["casi vaccinati", "ospedalizzati vaccinati",
                       "terapia intensiva vaccinati", "decessi vaccinati"]

        if incidenza_mensile is True:
            # calcola incidenza mensile ogni
            # 100.000 abitanti per ciascun gruppo
            df[non_vacc_labels] = df[non_vacc_labels]/df["non vaccinati"].values[0]*10**5
            df[vacc_labels] = df[vacc_labels]/df["vaccinati completo"].values[0]*10**5
        else:
            # converti in numeri giornalieri, media mobile 30 giorni
            df[colonna] = df[colonna]/30

        result_single_date = [dates[i], np.array(df[colonna])[0]]
        results_date.append(result_single_date)

    df_results = pd.DataFrame(results_date)

    if incidenza_mensile is True:
        df_results.columns = ["date", "incidenza "+str(colonna)+", "+str(età)]
    else:
        df_results.columns = ["date", str(colonna)+", "+str(età)]

    df_results.index = pd.to_datetime(df_results["date"])
    df_results.drop("date", axis=1, inplace=True)

    return df_results


@mpl.rc_context({"lines.marker": None, "axes.prop_cycle": mpl.cycler(color=palette[:4])})
def plot_assoluti_incidenza_età(categorie, titoli, filename, show=False):
    """Plot delle incidenze in funzione del tempo"""

    shared_legend = ["12-39 non vaccinati", "40-59 non vaccinati",
                     "60-79 non vaccinati", "80+ non vaccinati",
                     "12-39 vaccinati", "40-59 vaccinati",
                     "60-79 vaccinati", "80+ vaccinati"]

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    for età in classi_età:
        ricava_andamenti_età(files,
                             età,
                             categorie[0],
                             incidenza_mensile=False).plot(ax=axes[0])
    for età in classi_età:
        ricava_andamenti_età(files,
                             età,
                             categorie[1],
                             incidenza_mensile=False).plot(ax=axes[0],
                                                           linestyle="--")
    axes[0].set_title(titoli[0])
    axes[0].legend(shared_legend)
    axes[0].grid()
    axes[0].xaxis.reset_ticks()
    axes[0].set_xticks(x_ticks)
    axes[0].set_xticklabels(x_labels)
    axes[0].set_xlabel("")

    for età in classi_età:
        ricava_andamenti_età(files,
                             età,
                             categorie[0],
                             incidenza_mensile=True).plot(ax=axes[1])
    for età in classi_età:
        ricava_andamenti_età(files,
                             età,
                             categorie[1],
                             incidenza_mensile=True).plot(ax=axes[1],
                                                          linestyle="--")
    axes[1].set_title(titoli[1])
    axes[1].grid()
    axes[1].legend(shared_legend)
    axes[1].xaxis.reset_ticks()
    axes[1].set_xticks(x_ticks)
    axes[1].set_xticklabels(x_labels)
    axes[1].set_xlabel("")

    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")

    if show is True:
        plt.show()


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # Imposta stile grafici
    apply_plot_treatment()

    # Lista i csv
    files = list_età_csv()

    ratio_x_ticks, ratio_x_labels = get_xticks_labels(full=True)

    plot_rapporti_incidenze()

    x_ticks, x_labels = get_xticks_labels()

    categorie = pd.read_csv(files[0], sep=";").columns
    titolo_0 = "%s giornalieri (media 30 giorni)"
    titolo_1 = "Incidenza mensile %s per 100.000 abitanti"
    nome_file = "../risultati/andamento_fasce_età_%s.png"

    # casi
    plot_assoluti_incidenza_età(categorie=[categorie[4], categorie[6]],
                                titoli=[titolo_0 % "Casi",
                                        titolo_1 % "dei casi"],
                                filename=nome_file % "casi")

    # ospedalizzazioni
    plot_assoluti_incidenza_età(categorie=[categorie[7], categorie[9]],
                                titoli=[titolo_0 % "Ospedalizzati",
                                        titolo_1 % "degli ospedalizzati"],
                                filename=nome_file % "ospedalizzati")

    # in terapia intensiva
    plot_assoluti_incidenza_età(categorie=[categorie[10], categorie[12]],
                                titoli=[titolo_0 % "Ricoverati in TI",
                                        titolo_1 % "dei ricoverati in TI"],
                                filename=nome_file % "ricoveratiTI")

    # decessi
    plot_assoluti_incidenza_età(categorie=[categorie[13], categorie[15]],
                                titoli=[titolo_0 % "Decessi",
                                        titolo_1 % "dei decessi"],
                                filename=nome_file % "decessi")
