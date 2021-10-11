# -*- coding: utf-8 -*-
import locale
from datetime import datetime
from glob import glob
from os import chdir, path
from re import findall

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.preprocessing_dataframe import compute_incidence
from custom.watermarks import add_watermark


def date_from_url(csv_path):
    date_ = findall(r"\d+-\d+-\d+", csv_path)[0]
    return datetime.strptime(date_, "%Y-%m-%d")


# Set work directory for the script
scriptpath = path.dirname(path.realpath(__file__))
chdir(scriptpath)

# plt.style.use("default")
plt.style.use("seaborn-dark")

# Set locale to "it" to parse the month correctly
locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

""" # Importa i dati
# Leggi tutti i file con estensione `.csv`
# che sono presenti nella cartella `dati`.
path = "../dati"
extension = "csv"
os.chdir(path)
file_names = glob.glob("*.{}".format(extension))

# ometti il primo file, relativo ai dati riassuntivi
file_names = np.sort(file_names[1:])

print(file_names) """

# lista i csv
file_path = "../dati/data_iss_età_*.csv"
files = np.sort(glob(file_path))
print("Ultimo file:", files[-1])

ticks = np.arange(0, len(files), 2)
slice_end = round(len(files)/len(ticks))
if (len(files[0::slice_end]) > len(ticks)):
    slice_end += 1
labels = [date_from_url(csv).strftime("%d %b") for csv in files][0::slice_end]

print(labels)


# funzioni per plot
def compute_incidence_ratio(category):

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
                                                        r_dec]
                                                       ))
        rapporto_fra_tassi.columns = ["Casi",
                                      "Ospedalizzati",
                                      "TI",
                                      "Deceduti"
                                      ]
        rapporto_fra_tassi.index = df_tassi.index
        result_list.append(np.array(rapporto_fra_tassi[category]))
    result_list = np.array(result_list)
    return result_list


def add_to_plot():
    plt.xticks(ticks, labels)
    plt.ylabel("Contributo dei non vaccinati alle incidenze")
    plt.legend(["12-39", "40-59", "60-79", "80+"], loc=4)
    plt.yticks(np.arange(50, 101, 10),
               ["50%", "60%", "70%", "80%", "90%", "100%"])
    plt.ylim(60, 102)
    plt.grid()


""" Mostra risultati """

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

# add watermarks
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())

plt.tight_layout()
plt.savefig("../risultati/andamento_rapporti_incidenze.png", dpi=300)
plt.show()
