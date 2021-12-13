from datetime import datetime
from glob import glob
from re import findall

import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import sort
from pandas import read_csv, to_datetime

# see: https://personal.sron.nl/~pault/
palette = ["#EE7733", "#0077BB", "#33BBEE", "#EE3377", "#CC3311", "#009988", "#BBBBBB"]


def apply_plot_treatment():
    plt.style.use("seaborn-dark")
    mpl.rcParams["lines.linewidth"] = 1.5
    mpl.rcParams["lines.markersize"] = 3
    mpl.rcParams["lines.marker"] = "o"
    mpl.rcParams["legend.labelspacing"] = 0.25
    mpl.rcParams["legend.borderaxespad"] = 0.25
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=palette)


def list_età_csv(is_most_recent=False):
    # lista i csv
    files = sort(glob("../dati/data_iss_età_*.csv"))
    return files[-1] if is_most_recent else files


def date_from_csv_path(csv_path):
    date_ = findall(r"\d+-\d+-\d+", csv_path)[0]
    return datetime.strptime(date_, "%Y-%m-%d")


def get_xticks_labels(reports_dates=None):
    if reports_dates is None:
        df_assoluti = read_csv("../dati/dati_ISS_complessivi.csv", sep=";")
        reports_dates = to_datetime(df_assoluti["data"])

    ticks = set([x.strftime("%Y-%m-01") for x in reports_dates])
    ticks = sorted(ticks)
    labels = [to_datetime(t).strftime("%b\n%Y")
              if (i == 1 or to_datetime(t).strftime("%m") == "01")
              else to_datetime(t).strftime("%b")
              for i, t in enumerate(ticks)]
    labels[0] = ""
    labels = list(map(str.capitalize, labels))
    return ticks, labels
