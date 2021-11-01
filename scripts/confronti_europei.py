# -*- coding: utf-8 -*-

import locale
from os import chdir, path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from custom.plots import aggiorna_ascissa
from custom.watermarks import add_watermark


# Importa dati vaccini e dati epidemiologici
def import_vaccines_data():
    """ Recupera dati sui vaccini da Our World in Data"""
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"  # noqa: E501
    df_vacc = pd.read_csv(url)
    df_vacc = df_vacc.fillna(method="backfill")
    return df_vacc


def get_vaccine_data(country, df_vacc):

    """ Recupera dati vaccini per paese """

    df_vacc_country = df_vacc[df_vacc["location"] == country].iloc[2:, :]

    date = pd.to_datetime(df_vacc_country["date"])
    vacc1 = np.array(df_vacc_country["people_vaccinated_per_hundred"])
    vacc2 = np.array(df_vacc_country["people_fully_vaccinated_per_hundred"])

    df_vacc_new = pd.DataFrame(np.transpose([vacc1, vacc2]))
    df_vacc_new.index = date
    df_vacc_new.columns = ["% vaccinated with 1 dose", "% fully vaccinated"]

    return df_vacc_new


def import_epidem_data():
    """ Recupera dati epidemiologici dal JHU CSSE
        (Johns Hopkins Unversity)"""
    base = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"  # noqa: E501
    file_confirmed = base + "time_series_covid19_confirmed_global.csv"
    file_deaths = base + "time_series_covid19_deaths_global.csv"
    file_recovered = base + "time_series_covid19_recovered_global.csv"
    return pd.read_csv(file_confirmed), pd.read_csv(file_deaths), pd.read_csv(file_recovered)


def get_epidemic_data(country, df_confirmed, df_deaths, df_recovered):
    """ Recupera dati epidemiologia per paese """
    ydata_cases = (df_confirmed[df_confirmed["Country/Region"] == country].iloc[:, 4:]).sum()
    ydata_deaths = (df_deaths[df_deaths["Country/Region"] == country].iloc[:, 4:]).sum()
    ydata_rec = (df_recovered[df_recovered["Country/Region"] == country].iloc[:, 4:]).sum()
    ydata_inf = ydata_cases-ydata_deaths-ydata_rec
    daily_cases = ydata_cases.diff().rolling(window=7).mean()
    daily_deaths = ydata_deaths.diff().rolling(window=7).mean()
    df_epidemic = pd.DataFrame(np.transpose([ydata_cases,
                                             ydata_inf,
                                             ydata_deaths,
                                             ydata_rec,
                                             daily_cases,
                                             daily_deaths]))
    df_epidemic.index = pd.to_datetime(df_confirmed.columns[4:])
    df_epidemic.columns = ["Total cases",
                           "Active infected",
                           "Total deaths",
                           "Total recovered",
                           "Daily cases (avg 7 days)",
                           "Daily deaths (avg 7 days)"]
    return df_epidemic


# Rappresentazione grafica risultati
def plot_data(show=False):
    """ Plot dati epidemiologia e vaccini dei paesi selezionati """

    nomi_nazioni = ["Italy", "Romania", "Portugal", "Spain", "Bulgaria"]  # nota: nomi in Inglese
    label_nazioni = ["Italia", "Romania", "Portogallo", "Spagna", "Bulgaria"]
    abitanti_nazioni = [59.55, 19.29, 10.31, 47.35, 6.927]

    x_date = ["2021-07-01", "2021-08-01", "2021-09-01", "2021-10-01", "2021-11-01"]
    x_label = ["Lug\n2021", "Ago", "Set", "Ott", "Nov"]

    fig, axes2 = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))

    # Unpack all the axes subplots
    axes = axes2.ravel()

    last_updated = pd.to_datetime(x_date[-1])

    for i in range(len(nomi_nazioni)):
        df_epid = get_epidemic_data(nomi_nazioni[i],
                                    df_confirmed,
                                    df_deaths,
                                    df_recovered)
        new_date = df_epid.index[-1]
        mask_ = df_epid.index >= "2021-06-01"
        values = 7/(abitanti_nazioni[i]*10)*df_epid["Daily cases (avg 7 days)"]
        values[mask_].plot(ax=axes[0], label=label_nazioni[i], linewidth=2)
        last_updated, x_date, x_label = aggiorna_ascissa(last_updated,
                                                         new_date,
                                                         x_date,
                                                         x_label)

    axes[0].set_xlim("2021-06-01", last_updated)
    axes[0].set_title("Incidenza settimanale nuovi casi")
    axes[0].set_ylabel("Numeri ogni 100.000 abitanti")
    axes[0].set_xlabel("")
    axes[0].set_xticks(x_date)
    axes[0].set_xticklabels(x_label)
    axes[0].legend()
    axes[0].grid()
    axes[0].minorticks_off()

    for i in range(len(nomi_nazioni)):
        df_country = get_vaccine_data(nomi_nazioni[i], df_vacc)
        new_date = df_country.index[-1]
        mask_ = df_country.index >= "2021-06-01"
        df_country["% fully vaccinated"][mask_].plot(ax=axes[1],
                                                     label=label_nazioni[i],
                                                     linewidth=2)
        last_updated, x_date, x_label = aggiorna_ascissa(last_updated,
                                                         new_date,
                                                         x_date,
                                                         x_label)

    axes[1].set_xlim("2021-06-01", last_updated)
    axes[1].set_ylim(0, 100)
    axes[1].set_yticks(np.arange(0, 101, 20))
    axes[1].set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])
    axes[1].set_title("Vaccinati in modo completo")
    axes[1].set_xlabel("")
    axes[1].set_xticks(x_date)
    axes[1].set_xticklabels(x_label)
    axes[1].legend()
    axes[1].grid()
    axes[1].minorticks_off()

    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())

    plt.tight_layout()
    plt.savefig("../risultati/confronto_nazioni_epidemia-vaccino.png",
                dpi=300,
                bbox_inches="tight")
    if show:
        plt.show()

        
paesi = ['Austria', 'Belgium', 'Bulgaria', 'Cyprus', 'Croatia', 
         'Denmark', 'Estonia', 'Finland', 'France', 
         'Germany', 'Greece', 'Ireland', 'Italy', 'Latvia', 
         'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 
         'Poland', 'Portugal', 'Czechia', 'Romania',
         'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Hungary']

abitanti = {'Austria':8.917, 'Belgium':11.56, 'Bulgaria':6.927, 'Cyprus':1.207, 'Croatia':4.047, 
            'Denmark':5.831, 'Estonia':1.331, 'Finland':5.531, 'France':67.39, 
            'Germany':83.24, 'Greece':10.27, 'Ireland':4.995, 'Italy':59.55, 'Latvia':1.902, 
            'Lithuania':2.795, 'Luxembourg':0.632275, 'Malta':0.525285, 'Netherlands':17.44, 
            'Poland':37.95, 'Portugal':10.31, 'Czechia':10.7, 'Romania':19.29,
            'Slovakia':5.549, 'Slovenia':2.1, 'Spain':47.35, 'Sweden':10.35, 'Hungary':9.75}

def get_vaccine_data_last(country, time_window=30, t0=-1, fully=True, last_day=False):
    """ Recupera dati sulla frazione di vaccinati medi negli ultimi 30 giorni"""

    df_vacc_country = df_vacc[df_vacc["location"] == country].iloc[2:, :]

    if fully==True:
        vacc_fully = np.array(df_vacc_country["people_fully_vaccinated_per_hundred"])
    else:
        vacc_fully = np.array(df_vacc_country["total_vaccinated_per_hundred"])

    if last_day==False:  
        vacc_ultimi_Ngiorni = np.mean(vacc_fully[t0-(time_window+1) : t0])
    elif last_day==True:
        vacc_ultimi_Ngiorni = vacc_fully[-1]

    return vacc_ultimi_Ngiorni

def get_deaths(country, time_window=30, t0=-1):
    decessi = np.array(df_deaths[df_deaths['Country/Region']==country].iloc[:, 4:].sum())
    decessi_ultimi_Ngiorni = decessi[t0] - decessi[t0-(time_window+1)]
    return decessi_ultimi_Ngiorni

def compute_vaccini_decessi(tw):
    # calcola vaccini e decessi nei 27 Paesi europei
    dec_res_2021=[]
    vacc_res_2021=[]
    tw = ideal_window
    t0 = -1
    for p in paesi:
        vacc_res_2021.append(get_vaccine_data_last(p, fully=True, last_day=True))
        dec_res_2021.append(get_deaths(p, time_window = tw, t0=t0)/abitanti[p])
    dec_res_2021 = np.array(dec_res_2021)
    return vacc_res_2021, dec_res_2021

def linear_model(x, coeff_fit):
    y = coeff_fit[1] + coeff_fit[0]*x
    return y

def linear_fit(vacc_res_2021, dec_res_2021):
    # fit lineare
    coeff_fit = np.polyfit(vacc_res_2021, dec_res_2021, 1)
    x_grid = np.arange(0, 100, 1)
    y_grid = [linear_model(v, coeff_fit) for v in x_grid]
    return x_grid, y_grid


def corr_window(tw):

    dec_res=[]
    vacc_res=[]

    for p in paesi:
        vacc_res.append(get_vaccine_data_last(p, fully=True, last_day=True))
        dec_res.append(get_deaths(p, time_window = tw)/abitanti[p])

    corr_tw = np.corrcoef(vacc_res, dec_res)[0, 1]

    return corr_tw

def compute_max_correlation():
    # calcole la finestra temporale in cui si ottiene la massima correlazione
    tw_grid = np.arange(7, 300, 5)
    corr_grid = [np.abs(corr_window(tw)) for tw in tw_grid]
    ideal_window = tw_grid[np.argmax(corr_grid)]
    
    return ideal_window


def plot_correlazione_vaccini_decessi(vacc_res_2021, dec_res_2021, x_grid, y_grid, ideal_window):
    plt.style.use('seaborn-dark')
    fig = plt.figure(figsize=(15, 8))
    for i in range(len(vacc_res_2021)):
        plt.scatter(vacc_res_2021[i], dec_res_2021[i])
        plt.annotate(paesi[i], 
                   xy=(vacc_res_2021[i]+0.1, dec_res_2021[i]),
                   xytext = (-20, -10), 
                   textcoords='offset points', ha='right', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                   arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
    plt.plot(x_grid, y_grid, linestyle='--', label='Regressione lineare')
    plt.xticks(np.arange(0, 101, 20), ['0%', '20%', '40%', '60%', '80%', '100%'])
    plt.ylim(0, 1600)
    plt.xlim(15, 90)
    plt.title('Frazione di vaccinati vs decessi nei 27 Paesi dell\'UE negli ultimi '+str(ideal_window)+' giorni \nCoefficiente di correlazione = '+str(corr_coeff), 
              fontsize=15)
    plt.xlabel('Vaccinati con ciclo completo', fontsize=15)
    plt.ylabel('Decessi per milione di abitanti', fontsize=15)
    plt.legend(fontsize=15)
    plt.grid()
    # Add watermarks
    ax = plt.gca()
    add_watermark(fig, ax.xaxis.label.get_fontsize())
    plt.tight_layout()
    plt.savefig("../risultati/vaccini_decessi_EU.png",
                    dpi=300,
                    bbox_inches="tight")

if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # Imposta stile grafici
    plt.style.use("seaborn-dark")

    df_confirmed, df_deaths, df_recovered = import_epidem_data()
    df_vacc = import_vaccines_data()

    plot_data()
    
    # dati sui vaccini
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"  
    df_vacc = pd.read_csv(url)
    df_vacc = df_vacc.fillna(method="ffill")

    # dati sull'epidemia
    file_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"  
    df_deaths = pd.read_csv(file_deaths)  

    ideal_window = compute_max_correlation()
    vacc_res_2021, dec_res_2021 = compute_vaccini_decessi(tw = ideal_window)
    x_grid, y_grid = linear_fit(vacc_res_2021, dec_res_2021)
    corr_coeff = round(np.corrcoef(vacc_res_2021, dec_res_2021)[0, 1], 2)
    
    print('Coefficiente di correlazione tra vaccinati e deceduti:', corr_coeff)
    print('Finestra temporale in cui si registra la massima correlazione:', ideal_window, 'giorni')

    plot_correlazione_vaccini_decessi(vacc_res_2021, dec_res_2021, x_grid, y_grid, ideal_window)