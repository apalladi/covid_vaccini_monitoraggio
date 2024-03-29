# -*- coding: utf-8 -*-
import locale
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from custom.plots import (add_title, apply_plot_treatment, get_xticks_labels,
                          palette, set_size)
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
    axis.set_xticklabels(x_labels, rotation=90)
    axis.legend(["Non vaccinati", "Vaccinati completo",
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
    df_tassi, eventi = compute_incidence(df_epid, df_pop)
    df_tassi.index = pd.to_datetime(df_epid["data"])

    # Ricava i tassi standardizzati per fascia di età
    df_tassi_std = compute_incidence_std()

    # Calcola i numeri assoluti (medi, giornalieri) dell"epidemia
    df_epid = df_epid.copy(deep=True)
    df_epid["data"] = pd.to_datetime(df_epid["data"])
    df_epid = df_epid.set_index("data", drop=True)

    # Trasforma in numeri giornalieri
    df_epid = (1/30)*df_epid

    return df_tassi, df_tassi_std, df_epid, eventi


# Rappresentazione grafica dei risultati
@mpl.rc_context({"legend.handlelength": 1.0, "axes.prop_cycle": mpl.cycler(color=colori_incidenza)})
def plot_incidenza(show=False, is_std=False):
    """ Tassi di infezione, ricovero, decesso """

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=set_size(subplots=(2, 2)))

    # Unpack all the axes subplots
    axes = ax.ravel()

    titoli = ["nuovi casi", "ospedalizzazioni", "ingressi in TI", "decessi"]
    titolo = "Incidenza %s per 100.000"

    for i, evento in enumerate(eventi):
        (df_tassi_std[evento] if is_std else df_tassi[evento]).plot(ax=axes[i])
        add_title(axes[i], title=titolo % titoli[i],
                  subtitle="Aggiustata per fascia di età" if is_std else None)
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

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=set_size(subplots=(2, 2)))

    # Unpack all the axes subplots
    axes = ax.ravel()

    titoli = ["Nuovi casi giornalieri", "Nuovi ospedalizzati giornalieri",
              "Nuovi ricoverati in TI", "Decessi giornalieri"]

    for i, evento in enumerate(eventi):
        df_epid[evento].plot(ax=axes[i])
        add_title(axes[i], title=titoli[i] + " (media 30 gg)")
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

    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=set_size(fraction=1.25,
                                                              subplots=(2, 3)))

    # Unpack all the axes subplots
    axes = ax.ravel()

    # plot incidenze
    titoli = ["ospedalizzazioni", "ricoveri TI", "decessi"]
    titolo = "Incidenza %s per 100.000"

    for i, evento in enumerate(eventi[1:]):
        (df_tassi_std[evento] if is_std else df_tassi[evento]).plot(ax=axes[i])
        add_title(axes[i],
                  title=titolo % titoli[i],
                  subtitle="Aggiustata per fascia di età" if is_std else None)
        which_axe(axes[i])

    # plot numeri assoluti
    titoli = ["Nuovi ospedalizzati giornalieri",
              "Nuovi ricoverati in TI", "Decessi giornalieri"]

    titolo_ = "%s (media 30 gg)"
    for i, evento in enumerate(eventi[1:]):
        df_epid[evento].plot(ax=axes[i+3])
        add_title(axes[i+3], title=titolo_ % titoli[i])
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

    fig, ax = plt.subplots(figsize=set_size())

    tassi = df_tassi_std if is_std else df_tassi
    (tassi["casi non vaccinati"]/tassi["casi vaccinati completo"]).plot(label="Nuovi casi")
    (tassi["ospedalizzati non vaccinati"]/tassi["ospedalizzati vaccinati completo"]).plot(label="Ospedalizzazione")
    (tassi["terapia intensiva non vaccinati"]/tassi["terapia intensiva vaccinati completo"]).plot(label="Ricovero in TI")
    (tassi["decessi non vaccinati"]/tassi["decessi vaccinati completo"]).plot(label="Decesso")

    ax.xaxis.reset_ticks()
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)

    add_title(ax, title="Rapporto fra le incidenze",
              subtitle="Aggiustato per fascia di età" if is_std else None)
    ax.set_ylabel("Non vaccinati/vaccinati")
    ax.set_xlabel("")
    ax.grid()
    ax.legend()
    fig.tight_layout()

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, ax)

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

    df_tassi, df_tassi_std, df_epid, eventi = load_data()

    x_ticks, x_labels = get_xticks_labels(reports_dates=df_epid.index)

    plot_incidenza()
    plot_incidenza(is_std=True)
    plot_rapporto_tassi()
    plot_rapporto_tassi(is_std=True)
    plot_num_assoluti()
    plot_riassunto()
    plot_riassunto(is_std=True)
