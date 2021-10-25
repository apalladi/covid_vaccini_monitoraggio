# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of table 3 from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/aggiornamenti

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf

Requirements:
Python 3.6+, Ghostscript (ghostscript), Tkinter (python3-tk)
numpy, pandas, camelot, pdfplumber, requests, Beautiful Soup 4 """


import locale
import re
from datetime import datetime
from io import BytesIO
from os import chdir, path
from urllib.parse import urljoin

import camelot
import numpy as np
import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup


def get_surveillance_reports():
    """get_surveillance_reports() -> list

    return: list of "integrated surveillance of Covid-19 in Italy" reports"""

    # Source of the ISS reports
    epicentro_url = "https://www.epicentro.iss.it/coronavirus/aggiornamenti"
    # Requests URL and get response object
    with requests.get(epicentro_url) as response:
        # Parse text obtained
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all hyperlinks present on webpage
        links = soup.find_all("a")
        # Table 3 is available since 14/07/2021
        cut_date = pd.to_datetime('2021-07-14')
    return [urljoin(epicentro_url, link["href"]) for link in links
            if ("Bollettino-sorveglianza-integrata-COVID-19" in link["href"])
            and (date_from_url(link["href"], False) >= cut_date)]


def page_from_url(sel_url,
                  s="TABELLA 3 – POPOLAZIONE ITALIANA DI ETÀ >12 ANNI"):
    """page_from_url(sel_url) -> int

    sel_url: url of the report
    s: search string
    return: number of the page containing table 3"""

    with requests.get(sel_url) as response:
        # Get raw data from url
        raw_data = response.content
        with BytesIO(raw_data) as data:
            # Open the pdf file
            pdf = pdfplumber.open(data)
            # Get number of pages
            num_pages = len(pdf.pages)
            print(f"\nNum. of pages is: {num_pages}",
                  f"\nSearching for: {s}")
            # Extract text and do the search
            found_page = None
            for i in range(num_pages):
                text = pdf.pages[i].extract_text()
                if re.search(s, text, re.IGNORECASE):
                    found_page = i
                    break
    return found_page + 1 if found_page is not None else None


def date_from_url(sel_url, is_raw):
    """date_from_url(str) -> datetime

    sel_url: url of the report
    return: raw date or datetime extracted from report url"""

    date_ = re.findall(r"\d+[a-z-A-Z]+\d+", sel_url)[0]
    return date_ if is_raw else datetime.strptime(date_, "%d-%B-%Y")


def date_parser(x):
    """date_parser(object) -> datetime

    x: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(x, format="%Y/%m/%d")


def get_data_from_report(auto=True):
    """get_data_from_report(boolean, int) -> None

    The script saves data extracted from report.

    Select mode:
    - Automatic (auto = True): table of last available PDF
                               is automatically read
    - Manual (auto = False): Index of the report will be asked as input"""

    error_msg = "Can't extract the table! DIY!"

    # Get reports
    reports = get_surveillance_reports()

    if auto:
        # Get most recent report url
        rep_url = reports[0]
    else:
        # Build dictionary for manual mode
        reports_dict = dict(enumerate([date_from_url(report, True)
                            for report in reports]))
        # Select report index as input
        rep_idx = input(f'\nChoose report index:\n\n{reports_dict}\n\n')
        rep_url = reports[int(rep_idx)]

    # Get report date
    rep_date = date_from_url(rep_url, False)
    print(f"\nSelected report ({rep_date.date()}) is:\n{rep_url}")

    # Read the csv to update from the repo
    repo_url = "https://raw.githubusercontent.com/apalladi/covid_"
    repo_url += "vaccini_monitoraggio/main/dati/dati_ISS_complessivi.csv"
    df_0 = pd.read_csv(repo_url,
                       sep=";",
                       parse_dates=["data"],
                       date_parser=date_parser,
                       index_col="data")

    # If table is already up-to-date stop the script
    if rep_date in df_0.index:
        print("\nCSV are already up-to-date!")
        exit()

    # Get table 3 page number
    table_page = page_from_url(rep_url)

    # Try a different pattern is no page is found
    if table_page is None:
        print("Something went wrong! Trying again!")
        # Older report?
        new_s = "TABELLA 7 – COPERTURA VACCINALE NELLA"
        new_s += " POPOLAZIONE ITALIANA DI ETÀ >12 ANNI"
        table_page = page_from_url(rep_url,
                                   s=new_s)
        # Can't really find the page, stop
        if table_page is None:
            print(error_msg)
            exit()

    print("\nFound page is:", table_page)

    # Read the found page using camelot
    df_raw = camelot.read_pdf(rep_url,
                              pages=f"{table_page}",
                              flavor="stream")[0].df

    # Check if there are enough columns
    if len(df_raw.columns) < 3:
        # Table is incomplete, bye bye
        print(error_msg)
        exit()

    # Keep the last and the third last column
    columns_to_keep = df_raw.columns[[-3, -1]]
    df_raw = df_raw[columns_to_keep]

    # Get rows containing the following pattern # (# %)
    to_find = r"[0-9]|\((.*)"
    df_raw = df_raw[df_raw[columns_to_keep[0]].str.match(to_find)]

    # Remove dots and parentheses
    to_exclude = r"\((.*)|[^0-9]"
    df_final = df_raw.replace(to_exclude, "", regex=True).astype(np.int64)

    # Get data
    # Sum value by age/event
    step_ = 4  # groups (=5) are 4 rows (=20) distant (see foo.pdf)
    results = [df_final[col][i:i+step_].sum()
               for i in np.arange(0, len(df_final)-step_+1, step_)
               for col in df_final.columns]

    # Add the new row at the top of the df
    df_0.loc[rep_date] = results
    df_0.sort_index(ascending=False, inplace=True)

    # Save to a csv
    df_0.to_csv("dati_ISS_complessivi.csv", sep=";")

    # Get data by age
    ages = ["12-39", "40-59", "60-79", "80+"]
    results_ = {age: df_final[i::step_].stack().values
                for i, age in enumerate(ages)}

    # Load dict as df
    df_1 = pd.DataFrame(results_).T
    df_1.columns = df_0.columns
    df_1.index.rename("età", inplace=True)

    # Save to csv
    df_1.to_csv(f"data_iss_età_{rep_date.date()}.csv", sep=";")

    print("\nDone!")


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # Get data
    get_data_from_report()
