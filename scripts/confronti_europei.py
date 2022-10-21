# -*- coding: utf-8 -*-
import locale
from datetime import date
from os import chdir, path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from matplotlib.ticker import PercentFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from custom.plots import (add_suptitle, add_title, apply_plot_treatment,
                          get_xticks_labels, palette, set_size)
from custom.plots_confronti import (compute_vaccini_decessi_eu, fit_model,
                                    get_epidemic_data, get_vaccine_data,
                                    import_epidem_data, import_vaccines_data,
                                    paesi_abitanti_eu, paesi_eu_ita)
from custom.watermarks import add_last_updated, add_watermark


def which_axe(axis, step=10):
    axis.set_yticklabels([])
    start, end = axis.get_xlim()
    axis.xaxis.set_ticks(np.arange(start, end, step))
    x_ticks = axis.xaxis.get_major_ticks()
    x_ticks[0].label1.set_visible(False)
    x_ticks[-1].label1.set_visible(False)
    ymin, ymax = axis.get_ylim()
    axis.axvline(0.1, ymin=ymin, ymax=ymax, color="black", linewidth=0.5)
    axis.grid()


def map_vaccinated(f_vacc):
    if f_vacc >= 0 and f_vacc < 20:
        return "0-20%"
    elif f_vacc >= 20 and f_vacc < 40:
        return "20-40%"
    elif f_vacc >= 40 and f_vacc < 60:
        return "40-60%"
    elif f_vacc >= 60 and f_vacc < 80:
        return "60-80%"
    elif f_vacc >= 80 and f_vacc <= 100:
        return "80-100%"


def group_vaccinated(vacc_res_2021, dec_res_2021):
    df_res = pd.DataFrame(vacc_res_2021, columns=["vaccinati"])
    df_res["deceduti"] = dec_res_2021
    df_res["vacc_mapped"] = df_res["vaccinati"].apply(map_vaccinated)
    df_grouped = df_res.groupby("vacc_mapped").mean()["deceduti"]
    return df_grouped


# Rappresentazione grafica risultati
@mpl.rc_context({"lines.marker": None})
def plot_selection(show=False):
    """ Plot dati epidemiologia e vaccini dei paesi selezionati """

    # nota: nomi in Inglese
    nomi_nazioni = ["Italy", "Romania", "Portugal", "Spain", "Bulgaria"]

    label_nazioni = ["Italia", "Romania", "Portogallo", "Spagna", "Bulgaria"]
    abitanti_nazioni = [59.55, 19.29, 10.31, 47.35, 6.927]

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=set_size(subplots=(1, 2)))

    # Unpack all the axes subplots
    axes = ax.ravel()

    for i in range(len(nomi_nazioni)):
        df_epid = get_epidemic_data(nomi_nazioni[i],
                                    df_confirmed,
                                    df_deaths,
                                    df_recovered)
        mask_ = df_epid.index >= "2021-06-01"
        df_epid = df_epid.loc[mask_, :]
        values = 1/(abitanti_nazioni[i])*(df_epid["Total deaths"]-df_epid["Total deaths"][0])
        values.plot(ax=axes[0], label=label_nazioni[i])

    for i in range(len(nomi_nazioni)):
        df_country = get_vaccine_data(df_vacc, nomi_nazioni[i])
        mask_ = df_country.index >= "2021-06-01"
        df_country = df_country.loc[mask_, :]
        df_country["% fully vaccinated"].plot(ax=axes[1],
                                              label=label_nazioni[i],
                                              linewidth=2)

    x_ticks, x_labels = get_xticks_labels(df_country.index)

    add_title(axes[0], title="Decessi dal 1° Giugno ad oggi")
    axes[0].set_ylabel("Decessi per milione di abitanti")
    axes[0].set_xlabel("")
    axes[0].set_xticks(x_ticks)
    axes[0].set_xticklabels(x_labels, rotation=90)
    axes[0].legend()
    axes[0].grid()

    axes[1].set_ylim(0, 100)
    axes[1].set_yticks(np.arange(0, 101, 20))
    axes[1].set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    add_title(axes[1], title="Vaccinati con ciclo completo")
    axes[1].set_xlabel("")
    axes[1].set_xticks(x_ticks)
    axes[1].set_xticklabels(x_labels)
    axes[1].legend()
    axes[1].grid()

    # Add watermarks
    add_last_updated(fig, axes[-1], dati="JHU, Our World in Data")

    fig.tight_layout()
    fig.savefig("../risultati/confronto_nazioni_epidemia-vaccino.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


@mpl.rc_context({"lines.marker": None})
def plot_corr_vaccini_decessi(show=False):
    """ scatter plot correlazione vaccini e decessi """

    # linear fit
    x_grid, y_grid, score = fit_model(vacc_res, dec_res)

    # calcola coefficiente di correlazione (pearson)
    corr_coeff = round(np.corrcoef(vacc_res, dec_res)[0, 1], 2)

    fig, ax = plt.subplots(figsize=set_size(fraction=1.5))

    # scatter plot
    volume = dec_res.max()*0.050

    # genera lista di colori
    num_colors = len(paesi_abitanti_eu)
    cm = plt.get_cmap("GnBu_r")
    ax.set_prop_cycle("color", [cm(i/num_colors) for i in range(num_colors)])

    for i in range(num_colors):
        ax.scatter(df_["% vaccini"].values[i], df_["decessi"].values[i],
                   alpha=0.50, edgecolor="black", linewidth=0.75, s=volume)

    texts = [ax.text(vacc_res[i], dec_res[i], paesi_eu_ita[i])
             for i in range(len(paesi_eu_ita))]

    # fix text overlap
    adjust_text(texts,
                expand_text=(1.20, 1.35),
                arrowprops=dict(arrowstyle="-", color="black",
                                linewidth=.75))

    # linear fit plot
    ax.plot(x_grid, y_grid, linestyle="--", c=palette[0],
            label=f"Fit lineare, R$^2$ score={score}")

    # parabolic fit
    x_grid_p, y_grid_p, score_p = fit_model(vacc_res, dec_res, degree=2)
    ax.plot(x_grid_p, y_grid_p, linestyle="--", c=palette[2],
            label=f"Fit parabolico, R$^2$ score={score_p}")

    ax.set_ylim(-70, )
    ax.set_xlim(0, 100)

    title = "Frazione di vaccinati vs decessi nei 27 Paesi dell'UE dal 22/09/2021"
    subtitle = f"Coefficiente di correlazione = {corr_coeff}"
    add_suptitle(fig, ax, title=title, subtitle=subtitle)
    ax.set_xlabel("Frazione media di vaccinati con almeno 1 dose al 22/09/2021", fontsize=15)
    ax.set_ylabel("Decessi per milione di abitanti", fontsize=15)
    ax.set_xticks(np.arange(0, 101, 20), ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.grid()
    ax.legend()
    fig.tight_layout()

    # bar plot
    df_grouped = group_vaccinated(vacc_res, dec_res)

    ax_bar = inset_axes(ax, "30%", "30%",
                        loc="lower left",
                        bbox_to_anchor=(0.01, 0.075, 0.98, 0.95),
                        bbox_transform=ax.transAxes)
    ax_bar.set_facecolor((0, 0, 0, 0))
    ax_bar.bar(df_grouped.index, df_grouped, width=1,
               edgecolor="black", color=palette[1], alpha=0.30)
    labels_pad = 50 if df_grouped.max() > 1000 else 10
    for index, data in enumerate(df_grouped):
        ax_bar.text(x=index, y=data+labels_pad,
                    ha="center", s=round(data),
                    fontdict=dict(fontweight="bold"))

    ax_bar.xaxis.set_tick_params(rotation=0)
    ax_bar.set_title("Decessi medi per milione", pad=15)
    ax_bar.set_xlabel("Frazione media vaccinati")
    ax_bar.set_yticks([])
    ax_bar.spines["bottom"].set_linewidth(1.5)
    ax_bar.spines["bottom"].set_color("black")

    # Add watermarks
    fig.text(0.95, 0.425,
             "github.com/apalladi/covid_vaccini_monitoraggio",
             fontsize=16,
             alpha=0.50,
             color=palette[-1],
             va="center",
             rotation="vertical")
    add_last_updated(fig, ax, dati="JHU, Our World in Data")

    fig.savefig("../risultati/vaccini_decessi_EU.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()


def plot_corr_vaccini_decessi_div(show=False):
    """ tornado plot vaccini vs decessi """

    # ordina valori in un df
    df_ = pd.DataFrame({"% vaccini": vacc_res, "decessi": dec_res})
    df_.index = paesi_eu_ita
    df_ = df_.sort_values(by="% vaccini")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=set_size(subplots=(1, 2)), sharey=True)

    # Unpack all the axes subplots
    axes = ax.ravel()

    mask = df_.index == "Italia"
    colors = np.where(mask, palette[5], "#44AA99")

    axes[0].barh(df_.index, df_["% vaccini"], color=colors)
    axes[0].set_xlim(0, 101)
    axes[0].xaxis.set_major_formatter(PercentFormatter())
    add_title(axes[0], title="Frazione di vaccinati")
    axes[0].set_xlabel("Frazione media di vaccinati con almeno 1 dose al 22/09/2021")
    which_axe(axes[0])
    axes[0].invert_xaxis()

    for country in df_.index:
        axes[0].text(x=1.0, y=country, color="white",
                     va="center", ha="right", s=country,
                     fontdict=dict(fontweight="bold", size=6))

    colors_ = np.where(mask, palette[4], "#CC6677")
    axes[1].barh(df_.index, df_["decessi"], color=colors_)
    add_title(axes[1], title="Decessi per milione di abitanti")
    axes[1].set_xlabel("Decessi per milione di abitanti dal 22/09/2021")
    which_axe(axes[1], step=250)

    titolo = "Frazione di vaccinati vs decessi nei 27 Paesi dell'UE dal 22/09/2021"
    add_suptitle(fig, axes[-1], title=titolo)

    # Add watermarks
    add_watermark(fig)
    add_last_updated(fig, axes[-1], dati="JHU, Our World in Data", y=-0.1)

    fig.subplots_adjust(wspace=0, hspace=0)
    fig.savefig("../risultati/vaccini_decessi_EU_div.png", dpi=300, bbox_inches="tight")
    if show:
        plt.show()


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # importa dati
    df_confirmed, df_deaths, df_recovered = import_epidem_data()
    df_vacc = import_vaccines_data()

    # recupera dati vaccini vs. decessi
    # da inizio autunno (22 settembre 2021)
    window = abs((date.today() - date(2021, 9, 22)).days)

    # recupera dati per la finestra temporale selezionata
    vacc_res, dec_res = compute_vaccini_decessi_eu(df_vacc, df_deaths,
                                                   window, fully=False)

    # Imposta stile grafici
    apply_plot_treatment()

    # plot dati selezione paesi
    plot_selection()

    # ordina valori in un df per far si che seguano la sequenza dei colori
    df_ = pd.DataFrame({"% vaccini": vacc_res, "decessi": dec_res})
    df_.index = paesi_eu_ita
    df_ = df_.sort_values(by="% vaccini")

    # plot correlazione vaccini vs. decessi per paesi eu dal 1° settembre 2021
    plot_corr_vaccini_decessi()
    plot_corr_vaccini_decessi_div()
