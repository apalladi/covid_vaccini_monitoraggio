# type: ignore

from datetime import datetime
from glob import glob
from re import findall

import matplotlib.pyplot as plt
from numpy import sort


# Funzioni per il plot
def get_cap_labels(axis, add_new_line=False):
    plt.gcf().canvas.draw()
    x_ticks = axis.get_xticks()
    new_labels = [f"\n{lb.get_text().title()}"
                  if add_new_line else lb.get_text().title()
                  for lb in axis.get_xmajorticklabels()]
    return x_ticks, new_labels


def list_età_csv(is_most_recent=False):
    # lista i csv
    files = sort(glob("../dati/data_iss_età_*.csv"))
    return files[-1] if is_most_recent else files


def date_from_csv_path(csv_path):
    date_ = findall(r"\d+-\d+-\d+", csv_path)[0]
    return datetime.strptime(date_, "%Y-%m-%d")
