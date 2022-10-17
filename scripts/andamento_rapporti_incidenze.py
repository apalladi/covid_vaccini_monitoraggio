# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import (add_title, apply_plot_treatment, get_xticks_labels,
                          palette, set_size)
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_last_updated, add_watermark

classi_età = ["12-39", "40-59", "60-79", "80+"]


# Funzioni per il plot
def compute_incidence_ratio(category):
    """ Calcolo rapporti incidenze per età """

    result_list = []

    for date in np.flip(date_reports):
        df_epid = df_età_epid.loc[date]
        df_pop = df_età_pop.loc[date]
        df_tassi = compute_incidence(df_epid, df_pop)

        r_casi = df_tassi["Casi, non vaccinati"]/(df_tassi["Casi, non vaccinati"] + df_tassi["Casi, vaccinati completo"])*100
        r_osp = df_tassi["Ospedalizzati, non vaccinati"]/(df_tassi["Ospedalizzati, non vaccinati"] + df_tassi["Ospedalizzati, vaccinati completo"])*100
        r_ti = df_tassi["In terapia intensiva, non vaccinati"]/(df_tassi["In terapia intensiva, non vaccinati"] + df_tassi["In terapia intensiva, vaccinati completo"])*100
        r_dec = df_tassi["Deceduti, non vaccinati"]/(df_tassi["Deceduti, non vaccinati"] + df_tassi["Deceduti, vaccinati completo"])*100
        rapporto_fra_tassi = pd.DataFrame(np.transpose([r_casi, r_osp, r_ti, r_dec]))
        rapporto_fra_tassi.columns = ["Casi", "Ospedalizzati", "TI", "Deceduti"]
        rapporto_fra_tassi.index = df_tassi.index
        result_list.append(np.array(rapporto_fra_tassi[category]))

    return np.array(result_list)


def add_to_plot(ax):
    """ Imposta proprietà grafico """
    ax.set_xticks(ratio_x_ticks)
    ax.set_xticklabels(ratio_x_labels, rotation=90)
    ax.set_ylabel("Contributo dei non vaccinati alle incidenze")
    ax.set_ylim(None, 105)
    ax.legend(classi_età)
    ax.grid()


def add_to_plot_abs(ax, title):
    """ Imposta proprietà grafico """
    add_title(ax, title=title)
    ax.xaxis.reset_ticks()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=90)
    ax.set_xlabel("")
    ax.legend(shared_legend)
    ax.grid()


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_rapporti_incidenze(show=False):
    """ Rapporto fra incidenze """

    fig, ax = plt.subplots(ncols=2, nrows=2, figsize=set_size(subplots=(2, 2)))

    # unpack axes
    axes = ax.ravel()

    axes[0].plot(incidenza_casi)
    add_title(axes[0], title="Casi")
    add_to_plot(axes[0])

    axes[1].plot(compute_incidence_ratio("Ospedalizzati"))
    add_title(axes[1], title="Ospedalizzazioni")
    add_to_plot(axes[1])

    axes[2].plot(compute_incidence_ratio("TI"))
    add_title(axes[2], title="Ingressi in TI")
    add_to_plot(axes[2])

    axes[3].plot(compute_incidence_ratio("Deceduti"))
    add_title(axes[3], title="Decessi")
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


def ricava_andamenti_età(età, colonna, incidenza_mensile):
    """Ricava andamento delle varie incindenze nel tempo,
    divise per fascia d"età e categoria"""

    # loop around the reports
    results_date = []
    for data in date_reports:
        df = df_età_epid.loc[data]
        df = df[df["età"] == età]

        non_vacc_labels = ["casi non vaccinati",
                           "ospedalizzati non vaccinati",
                           "terapia intensiva non vaccinati",
                           "decessi non vaccinati"]

        vacc_labels = ["casi vaccinati completo", "ospedalizzati vaccinati completo",
                       "terapia intensiva vaccinati completo", "decessi vaccinati completo"]

        if incidenza_mensile is True:
            # calcola incidenza mensile ogni
            # 100.000 abitanti per ciascun gruppo
            df_pop = df_età_pop.loc[data]
            df_pop = df_pop[df_pop["età"] == età]
            non_vacc_den_labels = ["casi non vaccinati", "ospedalizzati/ti non vaccinati",
                                   "ospedalizzati/ti non vaccinati", "decessi non vaccinati"]
            vacc_den_labels = ["casi vaccinati completo", "ospedalizzati/ti vaccinati completo",
                               "ospedalizzati/ti vaccinati completo", "decessi vaccinati completo"]
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
    df_results = df_results.drop("date", axis=1)
    return df_results


@mpl.rc_context({"lines.marker": None, "axes.prop_cycle": mpl.cycler(color=palette[:len(classi_età)])})
def plot_assoluti_incidenza_età(categorie, titoli, filename, show=False):
    """Plot delle incidenze in funzione del tempo"""

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=set_size(subplots=(1, 2)))
    axes = ax.ravel()

    for età in classi_età:
        ricava_andamenti_età(età,
                             categorie[0],
                             incidenza_mensile=False).plot(ax=axes[0])
    for età in classi_età:
        ricava_andamenti_età(età,
                             categorie[1],
                             incidenza_mensile=False).plot(ax=axes[0],
                                                           linestyle="--")
    add_to_plot_abs(axes[0], titoli[0])

    for età in classi_età:
        ricava_andamenti_età(età,
                             categorie[0],
                             incidenza_mensile=True).plot(ax=axes[1])
    for età in classi_età:
        ricava_andamenti_età(età,
                             categorie[1],
                             incidenza_mensile=True).plot(ax=axes[1],
                                                          linestyle="--")
    add_to_plot_abs(axes[1], titoli[1])

    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")

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

    shared_legend = ["12-39 non vaccinati", "40-59 non vaccinati",
                     "60-79 non vaccinati", "80+ non vaccinati",
                     "12-39 vaccinati", "40-59 vaccinati",
                     "60-79 vaccinati", "80+ vaccinati"]

    # Recupera dati età
    df_età = pd.read_excel("../dati/dati_ISS_età.xlsx", sheet_name=None,
                           index_col="data", parse_dates=["data"])
    df_età_epid = df_età["dati epidemiologici"]
    df_età_pop = df_età["popolazioni"]

    # Filtra fascia 5-11
    df_età_epid = df_età_epid[df_età_epid["età"] != "5-11"]
    df_età_pop = df_età_pop[df_età_pop["età"] != "5-11"]

    df_epid = df_età_epid[df_età_epid.index > "2021-07-28"]
    df_pop = df_età_pop[df_età_pop.index > "2021-07-28"]
    date_reports = df_epid.index.unique()

    ratio_x_ticks, ratio_x_labels = get_xticks_labels(full=True)

    incidenza_casi = compute_incidence_ratio("Casi")

    plot_rapporti_incidenze()

    x_ticks, x_labels = get_xticks_labels()

    titolo_0 = "%s giornalieri (media 30 giorni)"
    titolo_1 = "Incidenza %s per 100.000"
    nome_file = "../risultati/andamento_fasce_età_%s.png"

    # casi
    plot_assoluti_incidenza_età(categorie=["casi non vaccinati", "casi vaccinati completo"],
                                titoli=[titolo_0 % "Casi",
                                        titolo_1 % "nuovi casi"],
                                filename=nome_file % "casi")

    # ospedalizzazioni
    plot_assoluti_incidenza_età(categorie=["ospedalizzati non vaccinati", "ospedalizzati vaccinati completo"],
                                titoli=[titolo_0 % "Ospedalizzati",
                                        titolo_1 % "ospedalizzazioni"],
                                filename=nome_file % "ospedalizzati")

    # in terapia intensiva
    plot_assoluti_incidenza_età(categorie=["terapia intensiva non vaccinati", "terapia intensiva vaccinati completo"],
                                titoli=[titolo_0 % "Ricoverati in TI",
                                        titolo_1 % "ingressi in TI"],
                                filename=nome_file % "ricoveratiTI")

    # decessi
    plot_assoluti_incidenza_età(categorie=["decessi non vaccinati", "decessi vaccinati completo"],
                                titoli=[titolo_0 % "Decessi",
                                        titolo_1 % "decessi"],
                                filename=nome_file % "decessi")
