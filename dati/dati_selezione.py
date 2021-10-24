# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of table 3 from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf

Requirements:
Java 8+, Python 3.6+, numpy, pandas, tabula-py, requests, Beautiful Soup 4 """


import locale
from datetime import datetime
from os import chdir, path
from re import findall
from urllib.parse import urljoin

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from requests import get
from tabula import read_pdf


def get_surveillance_reports():
    '''get_surveillance_reports() -> list

    return: list of "integrated surveillance of Covid-19 in Italy" reports'''

    # Source of the ISS reports
    epicentro_url = "https://www.epicentro.iss.it/coronavirus/aggiornamenti"
    # Requests URL and get response object
    response = get(epicentro_url)
    # Parse text obtained
    soup = BeautifulSoup(response.text, "html.parser")
    # Find all hyperlinks present on webpage
    links = soup.find_all("a")
    # table 3 is available since 14/07/2021
    cut_date = pd.to_datetime('2021-07-14')
    return [urljoin(epicentro_url, link["href"]) for link in links
            if ("Bollettino-sorveglianza-integrata-COVID-19" in link["href"])
            and (date_from_url(link["href"], False) >= cut_date)]


def date_from_url(sel_url, is_raw):
    '''date_from_url(str) -> datetime

    sel_url: url of the report
    return: raw date or datetime extracted from report url'''

    date_ = findall(r"\d+[a-z-A-Z]+\d+", sel_url)[0]
    return date_ if is_raw else datetime.strptime(date_, "%d-%B-%Y")


def date_parser(x):
    '''date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime'''

    return pd.to_datetime(x, format="%Y/%m/%d")


def get_data_from_report(auto=True, table_index=2):
    ''' get_data_from_report(boolean, int) -> None

    The script saves data extracted from report.

    Select mode:
    - Automatic (auto = True): table of last available PDF
                               is automatically read
    - Manual (auto = False): Index of the report will be asked as input'''

    reports = get_surveillance_reports()

    if auto:
        # Get most recent report url
        rep_url = reports[0]
    else:
        # build dictionary for manual mode
        reports_dict = dict(enumerate([date_from_url(report, True)
                            for report in reports]))
        # Select report's index as input
        rep_idx = input(f'\nScegli indice report:\n\n{reports_dict}\n\n')
        rep_url = reports[int(rep_idx)]

    # Get report date
    rep_date = date_from_url(rep_url, False)
    print(f"\nSelected report ({rep_date.date()}) is:\n{rep_url}")

    # Read all tables
    raw_tables = read_pdf(rep_url, pages="all", stream=True, silent=True)

    # keep the last and the third last column
    try:
        # check for errors first, change table_index accordingly
        raw_tables[table_index].columns[[-3, -1]]
    except IndexError:
        # common indexes are 2 and 3, try with 3
        idx_err_msg = "\nIndice tabella incorretto."
        idx_err_msg += " Provo con l'indice 3"
        print(idx_err_msg)
        table_index = 3

    sel_raw_table = raw_tables[table_index]

    columns_to_keep = sel_raw_table.columns[[-3, -1]]

    to_exclude = r"\((.*)|[^a-z-0-9]|\d+-\d+|\d+\+"

    df_raw = sel_raw_table[columns_to_keep]
    df = df_raw.replace(to_exclude, "", regex=True).replace("", np.nan)
    df = df.dropna(subset=columns_to_keep, how="all")

    try:
        df = df.fillna(0).astype(np.int64)
    except ValueError:
        print("\nImpossibile estrarre dati dal report! Procedi manualmente!")
        exit()

    df.columns = ["Non vaccinati", "Immunizzati"]

    # Get data
    # Sum value by age/event
    step_ = 4  # groups (=5) are 4 rows (=20) distant (see foo.pdf)
    results = [df[col][i:i+step_].sum()
               for i in np.arange(0, len(df)-step_+1, step_)
               for col in df.columns]

    # Read the original general data csv from apalladi"s repo
    # https://github.com/apalladi/covid_vaccini_monitoraggio/tree/main/dati
    repo_url = "https://raw.githubusercontent.com/apalladi/covid_"
    repo_url += "vaccini_monitoraggio/main/dati/dati_ISS_complessivi.csv"
    df_0 = pd.read_csv(repo_url,
                       sep=";",
                       parse_dates=["data"],
                       date_parser=date_parser,
                       index_col="data")

    # Add the new row at the top of the df
    df_0.loc[rep_date] = results
    df_0.sort_index(ascending=False, inplace=True)

    # Save to a csv
    df_0.to_csv("dati_ISS_complessivi.csv", sep=";")

    # Get data by age
    ages = ["12-39", "40-59", "60-79", "80+"]
    results_ = {age: df[i::step_].stack().values for i, age in enumerate(ages)}

    # Load dict as df
    df_1 = pd.DataFrame(results_).T
    df_1.columns = df_0.columns
    df_1.index.rename("età", inplace=True)

    # Save to csv
    df_1.to_csv(f"data_iss_età_{rep_date.date()}.csv", sep=";")

    print("\nFinito!")


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # get data
    get_data_from_report()
