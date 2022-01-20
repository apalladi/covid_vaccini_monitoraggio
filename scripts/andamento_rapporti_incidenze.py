# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import (apply_plot_treatment, date_from_xlsx_path,
                          get_xticks_labels, get_yticks_labels, list_xlsx,
                          palette)
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_last_updated, add_watermark

classi_età = ["12-39", "40-59", "60-79", "80+"]

shared_legend = ["12-39 non vaccinati", "40-59 non vaccinati",
                 "60-79 non vaccinati", "80+ non vaccinati",
                 "12-39 vaccinati", "40-59 vaccinati",
                 "60-79 vaccinati", "80+ vaccinati"]


# Funzioni per il plot
def compute_incidence_ratio(category):
    """ Calcolo rapporti incidenze per età """

    result_list = []

    for f in files:
        df_età = pd.read_excel(f, sheet_name="dati epidemiologici")
        df_pop = pd.read_excel(f, sheet_name="popolazioni")
        df_tassi = compute_incidence(df_età, df_pop)

        r_casi = df_tassi["Casi, non vaccinati"]/(df_tassi["Casi, non vaccinati"] + df_tassi["Casi, vaccinati"])*100
        r_osp = df_tassi["Ospedalizzati, non vaccinati"]/(df_tassi["Ospedalizzati, non vaccinati"] + df_tassi["Ospedalizzati, vaccinati"])*100
        r_ti = df_tassi["In terapia intensiva, non vaccinati"]/(df_tassi["In terapia intensiva, non vaccinati"] + df_tassi["In terapia intensiva, vaccinati"])*100
        r_dec = df_tassi["Deceduti, non vaccinati"]/(df_tassi["Deceduti, non vaccinati"] + df_tassi["Deceduti, vaccinati"])*100
        rapporto_fra_tassi = pd.DataFrame(np.transpose([r_casi, r_osp, r_ti, r_dec]))
        rapporto_fra_tassi.columns = ["Casi", "Ospedalizzati", "TI", "Deceduti"]
        rapporto_fra_tassi.index = df_tassi.index
        result_list.append(np.array(rapporto_fra_tassi[category]))

    return np.array(result_list)


def add_to_plot(ax):
    """ Imposta proprietà grafico """
    ax.set_xticks(ratio_x_ticks)
    ax.set_xticklabels(ratio_x_labels)
    ax.set_ylabel("Contributo dei non vaccinati alle incidenze")
    ax.set_yticks(rapp_yticks)
    ax.set_yticklabels(rapp_ylabels)
    ax.set_ylim(rapp_ymin, 102)
    ax.legend(classi_età)
    ax.grid()


def add_to_plot_abs(ax, title):
    """ Imposta proprietà grafico """
    ax.set_title(title)
    ax.xaxis.reset_ticks()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("")
    ax.legend(shared_legend)
    ax.grid()


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_rapporti_incidenze(show=False):
    """ Rapporto fra incidenze """

    fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(9, 8))

    # unpack axes
    axes = ax.ravel()

    axes[0].plot(incidenza_casi)
    axes[0].set_title("Casi")
    add_to_plot(axes[0])

    axes[1].plot(compute_incidence_ratio("Ospedalizzati"))
    axes[1].set_title("Ospedalizzati")
    add_to_plot(axes[1])

    axes[2].plot(compute_incidence_ratio("TI"))
    axes[2].set_title("In terapia intensiva")
    add_to_plot(axes[2])

    axes[3].plot(compute_incidence_ratio("Deceduti"))
    axes[3].set_title("Decessi")
    add_to_plot(axes[3])

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/andamento_rapporti_incidenze.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def ricava_andamenti_età(files, età, colonna, incidenza_mensile):
    """Ricava andamento delle varie incindenze nel tempo,
    divise per fascia d"età e categoria"""

    # loop around the .xlsx files
    results_date = []
    for f in files:
        data = date_from_xlsx_path(f)
        df = pd.read_excel(f, sheet_name="dati epidemiologici")
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
            df_pop = pd.read_excel(f, sheet_name="popolazioni")
            df_pop = df_pop[df_pop["età"] == età]
            non_vacc_den_labels = ["casi non vaccinati", "ospedalizzati/ti non vaccinati",
                                   "ospedalizzati/ti non vaccinati", "decessi non vaccinati"]
            vacc_den_labels = ["casi vaccinati completo", "ospedalizzati/ti vaccinati",
                               "ospedalizzati/ti vaccinati", "decessi vaccinati"]
            df[non_vacc_labels] = df[non_vacc_labels]/df_pop[non_vacc_den_labels].values[0]*10**5
            df[vacc_labels] = df[vacc_labels]/df_pop[vacc_den_labels].values[0]*10**5
        else:
            # converti in numeri giornalieri, media mobile 30 giorni
            df[colonna] = df[colonna]/30

        result_single_date = [data, np.array(df[colonna])[0]]
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

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    axes = ax.ravel()

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
    add_to_plot_abs(axes[0], titoli[0])

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
    add_to_plot_abs(axes[1], titoli[1])

    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")

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

    # Lista gli xslx
    files = list_xlsx()

    ratio_x_ticks, ratio_x_labels = get_xticks_labels(full=True)

    incidenza_casi = compute_incidence_ratio("Casi")

    rapp_ymin, rapp_yticks, rapp_ylabels = get_yticks_labels(incidenza_casi)

    plot_rapporti_incidenze()

    x_ticks, x_labels = get_xticks_labels()

    categorie = pd.read_excel(files[0], sheet_name="dati epidemiologici").columns
    titolo_0 = "%s giornalieri (media 30 giorni)"
    titolo_1 = "Incidenza mensile %s per 100.000 abitanti"
    nome_file = "../risultati/andamento_fasce_età_%s.png"

    # casi
    plot_assoluti_incidenza_età(categorie=[categorie[1], categorie[3]],
                                titoli=[titolo_0 % "Casi",
                                        titolo_1 % "dei casi"],
                                filename=nome_file % "casi")

    # ospedalizzazioni
    plot_assoluti_incidenza_età(categorie=[categorie[5], categorie[7]],
                                titoli=[titolo_0 % "Ospedalizzati",
                                        titolo_1 % "degli ospedalizzati"],
                                filename=nome_file % "ospedalizzati")

    # in terapia intensiva
    plot_assoluti_incidenza_età(categorie=[categorie[9], categorie[11]],
                                titoli=[titolo_0 % "Ricoverati in TI",
                                        titolo_1 % "dei ricoverati in TI"],
                                filename=nome_file % "ricoveratiTI")

    # decessi
    plot_assoluti_incidenza_età(categorie=[categorie[13], categorie[15]],
                                titoli=[titolo_0 % "Decessi",
                                        titolo_1 % "dei decessi"],
                                filename=nome_file % "decessi")
