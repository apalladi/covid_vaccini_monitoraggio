import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

paesi_abitanti_eu = {"Austria": 8.917, "Belgium": 11.56, "Bulgaria": 6.927,
                     "Cyprus": 1.207, "Croatia": 4.047, "Denmark": 5.831,
                     "Estonia": 1.331, "Finland": 5.531, "France": 67.39,
                     "Germany": 83.24, "Greece": 10.27, "Ireland": 4.995,
                     "Italy": 59.55, "Latvia": 1.902, "Lithuania": 2.795,
                     "Luxembourg": 0.632275, "Malta": 0.525285, "Netherlands": 17.44,
                     "Poland": 37.95, "Portugal": 10.31, "Czechia": 10.7,
                     "Romania": 19.29, "Slovakia": 5.549, "Slovenia": 2.1,
                     "Spain": 47.35, "Sweden": 10.35, "Hungary": 9.75}

paesi_eu_ita = ["Austria", "Belgio", "Bulgaria", "Cipro", "Croazia", "Danimarca",
                "Estonia", "Finlandia", "Francia", "Germania", "Grecia", "Irlanda",
                "Italia", "Lettonia", "Lituania", "Lussemburgo", "Malta", "Olanda",
                "Polonia", "Portogallo", "Repubblica Ceca", "Romania", "Slovacchia",
                "Slovenia", "Spagna", "Svezia", "Ungheria"]


def stat_model(x, coeff_fit):
    if len(coeff_fit) == 2:
        y = coeff_fit[1] + coeff_fit[0]*x
    elif len(coeff_fit) == 3:
        y = coeff_fit[2] + coeff_fit[1]*x + coeff_fit[0]*x**2
    else:
        raise ValueError("Fit not supported")
    return y


def fit_model(vacc_res_2021, dec_res_2021, degree=1):
    """ fit """

    coeff_fit = np.polyfit(vacc_res_2021, dec_res_2021, degree)
    x_grid = np.arange(0, 100, 1)
    y_grid = [stat_model(v, coeff_fit) for v in x_grid]

    # calcola R2 score
    y_pred = [stat_model(v, coeff_fit) for v in vacc_res_2021]
    y_test = dec_res_2021

    score = round(r2_score(y_test, y_pred), 2)
    print("R\u00b2 score è pari a", score)

    return x_grid, y_grid, score


# Importa dati vaccini e dati epidemiologici
def import_vaccines_data():
    """ Recupera dati sui vaccini da Our World in Data"""

    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"
    df_vacc = pd.read_csv(url)
    df_vacc = df_vacc.fillna(method="ffill")
    return df_vacc


def get_vaccine_data(df_vacc, country):
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


def get_frac_vacc(df_vacc, country, days_ago=30, fully=False):
    """ Recupera dati sulla frazione di vaccinati """
    frac_vacc = get_vaccine_data(df_vacc, country)["% fully vaccinated"
                                                   if fully else
                                                   "% vaccinated with 1 dose"]
    return frac_vacc.iloc[-days_ago]


def get_deaths(df_deaths, country, time_window=30, t0=-1):
    """ Recupera decessi per la finestra temporale selezionata """
    decessi = np.array(df_deaths[df_deaths["Country/Region"] == country].iloc[:, 4:].sum())
    decessi_ultimi_Ngiorni = decessi[t0] - decessi[t0-(time_window+1)]
    return decessi_ultimi_Ngiorni


def compute_vaccini_decessi_eu(df_vacc, df_deaths, time, fully=True):
    """ calcola vaccini e decessi nei 27 Paesi europei """

    dec_res_2021 = []
    vacc_res_2021 = []
    t0 = -1
    for p, abitanti in paesi_abitanti_eu.items():
        vacc_res_2021.append(get_frac_vacc(df_vacc,
                                           p,
                                           days_ago=time,
                                           fully=fully))
        dec_res_2021.append(get_deaths(df_deaths, p, time_window=time, t0=t0)/abitanti)
    dec_res_2021 = np.array(dec_res_2021)
    return vacc_res_2021, dec_res_2021
