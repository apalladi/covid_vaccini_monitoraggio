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

""" path = "../dati"
extension = "csv"
os.chdir(path)
file_names = glob("*.{}".format(extension))

# ometti il primo file, relativo ai dati riassuntivi
files = np.sort(file_names[1:])
files = files[::-1]

print("Ultimo file", files[0]) """

# lista i csv
files = np.sort(glob("../dati/data_iss_età_*.csv"))
last_file = files[-1]
print("Ultimo file:", last_file)

# recupera data csv
csv_date = date_from_url(last_file)

csv_date_d = csv_date.strftime("%d")
csv_date_m = csv_date.strftime("%B")
report_date = f"{csv_date_d}-{csv_date_m}-{csv_date.year}"

message = f"Report ISS del {csv_date_d} {csv_date_m.capitalize()}: "
message += "https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_{report_date}.pdf"  # noqa: E501
message += "I dati si riferiscono ai 30 giorni precedenti."

print(message)

df_età = pd.read_csv(last_file, sep=";")

""" Elaborazione dati """

# ricava i tassi, dividendo per la popolazione vaccinati e non vaccinata
df_tassi = compute_incidence(df_età)
df_tassi.index = df_età["età"]


# funzioni per plot
def which_axe(x):
    axes[x].set_ylabel("Ogni 100.000 persone per ciascun gruppo")
    axes[x].set_xlabel("Fascia d\"età")
    axes[x].legend(["Non vaccinati", "Vaccinati"])
    axes[x].grid()
    for tick in axes[x].get_xticklabels():
        tick.set_rotation(0)


def add_to_plot():
    plt.ylim(70, 100)
    plt.grid()
    plt.xlabel("Fascia d\"età")
    plt.yticks(np.arange(70, 101, 5),
               ["70%", "75%", "80%", "85%", "90%", "95%", "100%"])


def which_axe_bar(x):
    axes[x].set_ylim(80, 100)
    axes[x].set_yticks(np.arange(70, 101, 5))
    axes[x].set_yticklabels(["70%", "75%", "80%", "85%", "90%", "95%", "100%"])
    axes[x].set_xlabel("Fascia d\"età")
    axes[x].grid()
    for tick in axes[x].get_xticklabels():
        tick.set_rotation(0)


"""Rappresentazione grafica dei risultati"""

# colori per plot vaccinati/non vaccinati
palette = ["tab:red", "tab:green"]

""" Tassi di contagio """

fig, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(7, 7))

# unpack all the axes subplots
axes = axes2.ravel()

df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], kind="bar")
axes[0].set_title("Incidenza settimanale dei nuovi casi")
which_axe(0)

df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], kind="bar")
axes[1].set_title("Incidenza settimanale degli ospedalizzati")
which_axe(1)

df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], kind="bar")
axes[2].set_title("Incidenza settimanale dei ricoveri in TI")
which_axe(2)

df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], kind="bar")
axes[3].set_title("Incidenza settimanale dei deceduti")
which_axe(3)

# add watermarks
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())

plt.tight_layout()
plt.savefig("../risultati/tassi_per_età.png", dpi=300, bbox_inches="tight")
plt.show()

""" Efficacia dei vaccini """

efficacia_contagio = (1 - df_tassi.iloc[:, 1]/df_tassi.iloc[:, 0])*100
efficacia_osp = (1 - df_tassi.iloc[:, 3]/df_tassi.iloc[:, 2])*100
efficacia_terint = (1 - df_tassi.iloc[:, 5]/df_tassi.iloc[:, 4])*100
efficacia_decessi = (1 - df_tassi.iloc[:, 7]/df_tassi.iloc[:, 6])*100

fig = plt.figure(figsize=(7.5, 7.5))

plt.subplot(2, 2, 1)
plt.bar(efficacia_contagio.index, efficacia_contagio, color="blue", width=0.5)
plt.title("Efficacia contro il contagio")
add_to_plot()

plt.subplot(2, 2, 2)
plt.bar(efficacia_osp.index, efficacia_osp, color="green", width=0.5)
plt.title("Efficacia contro l\"ospedalizzazione")
add_to_plot()

plt.subplot(2, 2, 3)
plt.bar(efficacia_terint.index, efficacia_terint, color="red", width=0.5)
plt.title("Efficacia contro il ricovero in TI")
add_to_plot()

plt.subplot(2, 2, 4)
plt.bar(efficacia_decessi.index, efficacia_decessi, color="black", width=0.5)
plt.title("Efficacia contro il decesso")
add_to_plot()

# add watermarks
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())

plt.tight_layout()
plt.savefig("../risultati/efficacia_vaccini.png", dpi=300, bbox_inches="tight")
plt.show()

""" Grafico riassuntivo """

fig, axes2 = plt.subplots(nrows=2, ncols=4, figsize=(13, 7))

# unpack all the axes subplots
axes = axes2.ravel()

df_tassi.iloc[:, [0, 1]].plot(ax=axes[0], kind="bar")
axes[0].set_title("Incidenza settimanale dei nuovi casi")
which_axe(0)

df_tassi.iloc[:, [2, 3]].plot(ax=axes[1], kind="bar")
axes[1].set_title("Incidenza settimanale degli ospedalizzati")
which_axe(1)

df_tassi.iloc[:, [4, 5]].plot(ax=axes[2], kind="bar")
axes[2].set_title("Incidenza settimanale dei ricoveri in TI")
which_axe(2)

df_tassi.iloc[:, [6, 7]].plot(ax=axes[3], kind="bar")
axes[3].set_title("Incidenza settimanale dei deceduti")
which_axe(3)

efficacia_contagio.plot(kind="bar", ax=axes[4], color="blue")
axes[4].set_title("Efficacia contro il contagio")
which_axe_bar(4)

efficacia_osp.plot(kind="bar", ax=axes[5], color="green")
axes[5].set_title("Efficacia contro l\"ospedalizzazione")
which_axe_bar(5)

efficacia_terint.plot(kind="bar", ax=axes[6], color="red")
axes[6].set_title("Efficacia contro il ricovero in TI")
which_axe_bar(6)

efficacia_decessi.plot(kind="bar", ax=axes[7], color="black")
axes[7].set_title("Efficacia contro il decesso")
which_axe_bar(7)

# add watermarks
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())

plt.tight_layout()
plt.savefig("../risultati/tassi_efficacia.png", dpi=300, bbox_inches="tight")
plt.show()

""" Focus sugli over 60 """

df_over60 = df_età.loc[[2, 3],
                       ["non vaccinati",
                        "vaccinati completo",
                        "terapia intensiva non vaccinati",
                        "terapia intensiva vaccinati",
                        "decessi non vaccinati",
                        "decessi vaccinati"]
                       ].sum()

over60_array = np.array(df_over60)

c = csv_date.strftime("%b").capitalize()
label_date = f"{csv_date_d} {c}"

fig = plt.figure(figsize=(9, 3))
plt.subplot(1, 3, 1)
plt.bar(0, over60_array[0], width=0.5, color="red")
plt.bar(1, over60_array[1], width=0.5, color="green")
plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
plt.yticks(10**6*np.arange(0, 17, 2),
           ["0", "2M", "4M", "6M", "8M", "10M", "12M", "14M", "16M"])
plt.grid()
plt.title(f"Popolazione over 60 \n30 Ago - {label_date}")

plt.subplot(1, 3, 2)
plt.bar(0, over60_array[2], width=0.5, color="red")
plt.bar(1, over60_array[3], width=0.5, color="green")
plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
plt.grid()
plt.title(f"In terapia intensiva \n30 Ago - {label_date}")

plt.subplot(1, 3, 3)
plt.bar(0, over60_array[4], width=0.5, color="red")
plt.bar(1, over60_array[5], width=0.5, color="green")
plt.xticks([0, 1], ["Non vaccinati", "Vaccinati"])
plt.grid()
plt.title(f"Deceduti \n30 Ago - {label_date}")

# add watermarks
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())

plt.tight_layout()
plt.savefig("../risultati/focus_over60.png", dpi=300, bbox_inches="tight")
plt.show()

ratio_vacc_novacc = round(over60_array[1]/over60_array[0], 1)
ratio_terint = round(over60_array[2]/over60_array[3], 1)
ratio_dec = round(over60_array[4]/over60_array[5], 1)

print("Rapporto tra vaccinati e non vaccinati", ratio_vacc_novacc)
print("Rapporto tra ricoverati in terapia intensiva (novacc/vacc)",
      ratio_terint
      )
print("Rapporto tra deceduti (novacc/vacc)", ratio_dec)

print("Peso sul sistema sanitario di un non vaccinato over 60:",
      round(ratio_vacc_novacc*ratio_terint, 2))
print("Peso sulla mortalità di un non vaccinato over 60:      ",
      round(ratio_vacc_novacc*ratio_dec, 2))
