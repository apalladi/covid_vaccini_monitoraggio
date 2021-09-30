# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of table 3from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf

Requirements: Java 8+, Python 3.6+, tabula-py, requests, Beautiful Soup 4 """


import locale
import os
from datetime import datetime
from re import findall
from urllib.parse import urljoin
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from requests import get
from tabula import read_pdf


def get_surveillance_reports():
    '''get_surveillance_reports() -> list

    return: list of integrated surveillance of Covid-19 in Italy reports'''

    # Source
    epicentro_url = "https://www.epicentro.iss.it/coronavirus/aggiornamenti"
    # Requests URL and get response object
    response = get(epicentro_url)
    # Parse text obtained
    soup = BeautifulSoup(response.text, "html.parser")
    # Find all hyperlinks present on webpage
    links = soup.find_all("a")
    return [urljoin(epicentro_url, link["href"]) for link in links
            if 'Bollettino-sorveglianza-integrata-COVID-19' in link["href"]]


def date_from_url(repo_url):
    '''date_from_url(url) -> datetime

    repo_url: url of the report
    return: datetime extracted from report url'''

    date_ = findall(r"\d+[a-z-A-Z]+\d+", repo_url)[0]
    # Set locale to "it" to be able to parse month correctly
    locale.setlocale(locale.LC_ALL, "it_IT")
    return datetime.strptime(date_, "%d-%B-%Y")


def date_parser(x):
    '''date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime'''

    return pd.to_datetime(x, format="%Y/%m/%d")


# Set work directory for the script
scriptpath = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptpath)

'''Select mode:
- Automatic (auto = True): table 3 of last available PDF is automatically read
- Manual: you have to specify PDF link and report date
'''

# Define mode
auto = True

# Replace with index of table of interest
table_index = 2

if auto:
    # Get most recent report and date
    url_ = get_surveillance_reports()[0]
    rep_date = date_from_url(url_)
    print(f"\nLatest report ({rep_date.date()}) is:\n{url_}")
else:
    # Replace with pdf url
    url_ = "https://www.epicentro.iss.it/coronavirus/bollettino/"
    url_ += "Bollettino-sorveglianza-integrata-COVID-19_22-settembre-2021.pdf"
    # Replace with report data
    rep_date = pd.to_datetime("22/09/2021")

# Read all tables
raw_tb = read_pdf(url_, pages="all", stream=True, silent=True)

# keep the last and the third last column
columns_to_keep = raw_tb[table_index].columns[[-3, -1]]
to_exclude = r"\((.*)|[^a-z-0-9]|\d+-\d+|\d+\+"

df = raw_tb[table_index][columns_to_keep]
df = df.replace(to_exclude, "", regex=True).replace("", np.nan)
df = df.dropna(subset=columns_to_keep, how="all").fillna(0).astype(np.int64)
df.columns = ["Non vaccinati", "Immunizzati"]

# Get data
# Sum value by age/event
step_ = 4  # groups (=5) are 4 rows (=20) distant (see foo.pdf)
results = [df[col][i:i+step_].sum()
           for i in np.arange(0, len(df)-step_+1, step_) for col in df.columns]

# Read the original general data csv from apalladi"s repo
# https://github.com/apalladi/covid_vaccini_monitoraggio/tree/main/dati
repo_url = "https://raw.githubusercontent.com/apalladi/covid_"
repo_url += "vaccini_monitoraggio/main/dati/dati_ISS_complessivi.csv"
df_0 = pd.read_csv(repo_url,
                   sep=";",
                   parse_dates=["data"],
                   date_parser=date_parser,
                   index_col="data"
                   )

# Add the new row at the top of the df
df_0.loc[rep_date] = results
df_0.sort_index(ascending=False, inplace=True)

# Save to a csv
df_0.to_csv("dati_ISS_complessivi.csv", sep=";")

# Get data by age
ages = ["12-39", "40-59", "60-79", "80+"]
results_ = {age: df[ages.index(age)::step_].stack().values for age in ages}

# Load dict as df
df_1 = pd.DataFrame(results_).T
df_1.columns = df_0.columns
df_1.index.rename("età", inplace=True)

# Save to csv
df_1.to_csv(f"data_iss_età_{rep_date.date()}.csv", sep=";")
