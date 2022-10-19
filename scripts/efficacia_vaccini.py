# -*- coding: utf-8 -*-
import locale
from datetime import timedelta
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import (add_suptitle, add_title, apply_plot_treatment,
                          palette, set_size)
from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_last_updated, add_watermark

colori_incidenza = [palette[i] for i in [6, 0, 1, 2, 3]]


def compute_efficacia():
    """ Calcola efficacia vaccini """
    eff_contagio = (1 - df_tassi["casi vaccinati completo"]/df_tassi["casi non vaccinati"])*100
    eff_osp = (1 - df_tassi["ospedalizzati vaccinati completo"]/df_tassi["ospedalizzati non vaccinati"])*100
    eff_terint = (1 - df_tassi["terapia intensiva vaccinati completo"]/df_tassi["terapia intensiva non vaccinati"])*100
    eff_decessi = (1 - df_tassi["decessi vaccinati completo"]/df_tassi["decessi non vaccinati"])*100
    return eff_contagio, eff_osp, eff_terint, eff_decessi


# Funzioni per il plot
def get_data_labels():
    """ Ricava label data dei grafici """
    csv_date_start = csv_date - timedelta(days=30)
    start_month = csv_date_start.strftime("%b").capitalize()
    start_day = csv_date_start.strftime("%d")
    start_date = f"{start_day} {start_month}"
    end_month = csv_date.strftime("%b").capitalize()
    csv_date_day = csv_date.strftime("%d")
    end_date = f"{csv_date_day} {end_month}"
    return start_date, end_date


def which_axe(axis):
    """ Imposta proprietà grafici """
    axis.set_xlabel("Fascia d'età")
    axis.legend(["Non vaccinati",
                 "Vaccinati completo",
                 "Vaccinati 2 dosi < 4-6 mesi",
                 "Vaccinati 2 dosi > 4-6 mesi",
                 "Vaccinati terza dose"])
    axis.grid()
    axis.xaxis.set_tick_params(rotation=0)


def which_axe_bar(axis):
    """ Imposta proprietà grafici """
    axis.set_ylim(None, 105)
    axis.set_xlabel("Fascia d'età")
    axis.grid()
    axis.xaxis.set_tick_params(rotation=0)


def add_to_plot(ax):
    """ Imposta proprietà grafici """
    ax.set_xlabel("Fascia d'età")
    ax.set_ylim(None, 105)
    ax.grid()


# Rappresentazione grafica dei risultati
@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_tassi(show=False):
    """ Tassi di contagio """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=set_size(subplots=(2, 2)))

    # Unpack all the axes subplots
    axes = ax.ravel()
    titolo = "Incidenza %s per 100.000"
    for i, evento in enumerate(eventi):
        df_tassi[evento].plot(ax=axes[i], kind="bar")
        add_title(axes[i], title=titolo % titoli[i])
        which_axe(axes[i])

    add_suptitle(fig, axes[-1], title=plots_suptitle)

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/tassi_per_età.png", dpi=300, bbox_inches="tight")
    if show:
        plt.show()


def plot_efficacia(show=False):
    """ Efficacia dei vaccini """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=set_size(width=720,
                                                              subplots=(2, 2)))
    axes = ax.ravel()

    axes[0].bar(eff_contagio.index, eff_contagio, color=palette[1], width=0.5)
    add_title(axes[0], title="Efficacia contro il contagio")
    add_to_plot(axes[0])

    axes[1].bar(eff_osp.index, eff_osp, color=palette[5], width=0.5)
    add_title(axes[1], title="Efficacia contro l'ospedalizzazione")
    add_to_plot(axes[1])

    axes[2].bar(eff_terint.index, eff_terint, color=palette[4], width=0.5)
    add_title(axes[2], title="Efficacia contro l'ingresso in TI")
    add_to_plot(axes[2])

    axes[3].bar(eff_decessi.index, eff_decessi, color="black", width=0.5)
    add_title(axes[3], title="Efficacia contro il decesso")
    add_to_plot(axes[3])

    add_suptitle(fig, axes[-1], "Efficacia dei vaccini", plots_suptitle)

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/efficacia_vaccini.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_riassunto(show=False):
    """ Grafico riassuntivo """

    fig, ax = plt.subplots(nrows=2, ncols=4, figsize=set_size(fraction=2, subplots=(2, 4)))

    # Unpack all the axes subplots
    axes = ax.ravel()
    titolo = "Incidenza %s per 100.000"

    for i, evento in enumerate(eventi):
        df_tassi[evento].plot(ax=axes[i], kind="bar")
        add_title(axes[i], title=titolo % titoli[i])
        which_axe(axes[i])

    eff_contagio.plot(kind="bar", ax=axes[4], color=palette[1])
    add_title(axes[4], title="Efficacia contro il contagio")
    which_axe_bar(axes[4])

    eff_osp.plot(kind="bar", ax=axes[5], color=palette[5])
    add_title(axes[5], title="Efficacia contro l'ospedalizzazione")
    which_axe_bar(axes[5])

    eff_terint.plot(kind="bar", ax=axes[6], color=palette[4])
    add_title(axes[6], title="Efficacia contro l'ingresso in TI")
    which_axe_bar(axes[6])

    eff_decessi.plot(kind="bar", ax=axes[7], color="black")
    add_title(axes[7], title="Efficacia contro il decesso")
    which_axe_bar(axes[7])

    add_suptitle(fig, axes[-1], title=plots_suptitle,
                 subtitle="Tassi ed efficacia dei vaccini")

    # add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/tassi_efficacia.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def plot_focus_60(show=False):
    """ Focus sugli over 60 """

    df_età_ = df_età.set_index("età")
    df_pop_ = df_pop.set_index("età")

    df_over60 = df_età_.loc[["60-79", "80+"],
                            ["terapia intensiva non vaccinati",
                             "terapia intensiva vaccinati completo",
                             "decessi non vaccinati",
                             "decessi vaccinati completo"]].sum()
    over60_array = np.array(df_over60)

    df_ = df_pop_.loc[["60-79", "80+"],
                      ["ospedalizzati/ti non vaccinati",
                       "ospedalizzati/ti vaccinati completo",
                       "decessi non vaccinati",
                       "decessi vaccinati completo"]].sum()
    over60_array = np.concatenate((np.array(df_), over60_array))

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=set_size(subplots=(2, 2)))
    axes = ax.ravel()

    x_ticks = [0, 1]
    x_labels = ["Non vaccinati", "Vaccinati"]
    pop_yticks = 10**6*np.arange(0, 17, 2)
    pop_ylabels = ["0", "2M", "4M", "6M", "8M", "10M", "12M", "14M", "16M"]
    pop_ytitle = "Popolazione over 60"

    axes[0].bar(0, over60_array[0], width=0.5, color=palette[4])
    axes[0].bar(1, over60_array[1], width=0.5, color=palette[5])
    axes[0].set_xticks(x_ticks)
    axes[0].set_xticklabels(x_labels)
    axes[0].set_yticks(pop_yticks)
    axes[0].set_yticklabels(pop_ylabels)
    add_title(axes[0], title=pop_ytitle)
    axes[0].grid()

    axes[1].bar(0, over60_array[4], width=0.5, color=palette[4])
    axes[1].bar(1, over60_array[5], width=0.5, color=palette[5])
    axes[1].set_xticks(x_ticks)
    axes[1].set_xticklabels(x_labels)
    add_title(axes[1], title="In terapia intensiva")
    axes[1].grid()

    axes[2].bar(0, over60_array[2], width=0.5, color=palette[4])
    axes[2].bar(1, over60_array[3], width=0.5, color=palette[5])
    axes[2].set_xticks(x_ticks)
    axes[2].set_xticklabels(x_labels)
    axes[2].set_yticks(pop_yticks)
    axes[2].set_yticklabels(pop_ylabels)
    add_title(axes[2], title=pop_ytitle)
    axes[2].grid()

    axes[3].bar(0, over60_array[6], width=0.5, color=palette[4])
    axes[3].bar(1, over60_array[7], width=0.5, color=palette[5])
    axes[3].set_xticks(x_ticks)
    axes[3].set_xticklabels(x_labels)
    add_title(axes[3], title="Deceduti")
    axes[3].grid()

    add_suptitle(fig, axes[-1], title=plots_suptitle)

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1])

    fig.tight_layout()
    fig.savefig("../risultati/focus_over60.png", dpi=300, bbox_inches="tight")

    ratio_vacc_novacc_ti = round(over60_array[1]/over60_array[0], 1)
    ratio_vacc_novacc_dec = round(over60_array[3]/over60_array[2], 1)

    ratio_terint = round(over60_array[4]/over60_array[5], 1)
    ratio_dec = round(over60_array[6]/over60_array[7], 1)

    print("Rapporto popolazioni vaccinati e non vaccinati (terapia intensiva)", ratio_vacc_novacc_ti)
    print("Rapporto tra ricoverati in terapia intensiva (novacc/vacc)", ratio_terint)
    print("Rapporto popolazioni vaccinati e non vaccinati (decessi)", ratio_vacc_novacc_dec)
    print("Rapporto tra deceduti (novacc/vacc)", ratio_dec)

    print("Peso sul sistema sanitario di un non vaccinato over 60:",
          round(ratio_vacc_novacc_ti*ratio_terint, 2))
    print("Peso sulla mortalità di un non vaccinato over 60:      ",
          round(ratio_vacc_novacc_dec*ratio_dec, 2))

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

    titoli = ["nuovi casi", "ospedalizzazioni", "ingressi in TI", "decessi"]

    # Recupera dati età
    df_età = pd.read_excel("../dati/dati_ISS_età.xlsx", sheet_name=None,
                           index_col="data", parse_dates=["data"])
    df_età_epid = df_età["dati epidemiologici"]
    df_età_pop = df_età["popolazioni"]
    date_reports = df_età_epid.index.unique()

    df_età_epid = df_età_epid[df_età_epid["età"] != "5-11"]
    df_età_pop = df_età_pop[df_età_pop["età"] != "5-11"]

    # Data più recente
    csv_date = date_reports[0]
    df_età = df_età_epid.loc[csv_date]
    df_pop = df_età_pop.loc[csv_date]

    start_date, end_date = get_data_labels()
    print(f"Report del {csv_date.date()}",
          "\nI dati si riferiscono ai 30 giorni precedenti.\n"
          f"{start_date} - {end_date}")

    report_date = csv_date.strftime("%d/%m/%Y")
    plots_suptitle = f"Report del {report_date} ({start_date} - {end_date})"

    # Ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
    eventi_templ = ["%s non vaccinati", "%s vaccinati completo", "%s vaccinati < 4-6 mesi",
                    "%s vaccinati > 4-6 mesi", "%s booster"]
    df_tassi, eventi = compute_incidence(df_età, df_pop,
                                         eventi_templ=eventi_templ)

    df_tassi.index = df_età["età"]

    # Ricava efficacia
    eff_contagio, eff_osp, eff_terint, eff_decessi = compute_efficacia()

    plot_tassi()
    plot_efficacia()
    plot_riassunto()
    plot_focus_60()
