import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# see: https://personal.sron.nl/~pault/
palette = ["#EE7733", "#0077BB", "#33BBEE", "#EE3377", "#CC3311", "#009988", "#BBBBBB"]
titoli = ["nuovi casi", "ospedalizzazioni", "ingressi TI", "decessi"]
titoli_per = " per 100.000"


def set_size(width=1080, fraction=1, subplots=(1, 1)):
    """Set figure dimensions.
    "https://jwalton.info/Embed-Publication-Matplotlib-Latex/"
    """
    if subplots == (1, 1):
        width = 720

    # Width of figure (in pts)
    fig_width_pt = width * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * subplots[0] / subplots[1]

    return (fig_width_in, fig_height_in)


def apply_plot_treatment():
    plt.style.use("seaborn-dark")
    mpl.rcParams["lines.linewidth"] = 1.5
    mpl.rcParams["lines.markersize"] = 2.5
    mpl.rcParams["lines.marker"] = "o"
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=palette)


def get_xticks_labels(reports_dates=None, full=False):
    if reports_dates is None:
        df_assoluti = pd.read_excel("../dati/dati_ISS_complessivi.xlsx", sheet_name="dati epidemiologici")
        df_assoluti = df_assoluti[df_assoluti["data"] > "2021-07-28"]
        reports_dates = pd.to_datetime(df_assoluti["data"])
    if full:
        reports_dates.sort_values(inplace=True)
        # mostra solo il 25% dei labels
        slice_step = round(len(reports_dates)/(len(reports_dates)*0.25))
        sel_dates = reports_dates[0::slice_step]
        labels = [t.strftime("%d %b") for t in sel_dates]
        ticks = np.arange(0, len(reports_dates), slice_step)
    else:
        ticks = set([x.strftime("%Y-%m-01") for x in reports_dates])
        ticks = sorted(ticks)
        labels = [pd.to_datetime(t).strftime("%b %y")
                  if (i == 1 or pd.to_datetime(t).strftime("%m") == "01") or full
                  else pd.to_datetime(t).strftime("%b")
                  for i, t in enumerate(ticks)]
        labels[0] = ""
    labels = list(map(str.title, labels))
    return ticks, labels


def add_title(ax, title, subtitle=None):
    # Add title to i-th axis

    text = f"$\\bf{title}$"
    if subtitle is not None:
        text += "\n" + f"$\\it{subtitle}$"
    text = text.replace(' ', '\\ ')
    ax.set_title(text, loc="left",
                 fontsize=ax.xaxis.label.get_fontsize())


def add_suptitle(fig, ax, title, subtitle=None):
    text = f"$\\bf{title}$"
    if subtitle is not None:
        text += "\n" + f"$\\it{subtitle}$"
    text = text.replace(' ', '\\ ')
    fig.suptitle(text, fontsize=ax.xaxis.label.get_fontsize()+2)
