# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of table 3 from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/aggiornamenti

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf

Requirements:
Python 3.6+, Ghostscript (ghostscript), Tkinter (python3-tk)
numpy, pandas, camelot, PyMuPDF, Beautiful Soup 4 """


import locale
import re
from datetime import datetime
from os import chdir, path
from urllib import request
from urllib.parse import urljoin

import camelot
import fitz
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


def get_surveillance_reports():
    """get_surveillance_reports() -> list

    return: list of "integrated surveillance of Covid-19 in Italy" reports"""

    # Source of the ISS reports
    epicentro_url = "https://www.epicentro.iss.it/coronavirus/aggiornamenti"
    # Requests URL and get http.client.HTTPResponse object
    with request.urlopen(epicentro_url) as response:
        # Parse text obtained
        soup = BeautifulSoup(response, "html.parser")
        # Find all hyperlinks present on webpage
        links = soup.find_all("a")
        # Table 3 is available since 14/07/2021
        cut_date = pd.to_datetime("2021-07-14")
    return [urljoin(epicentro_url, link["href"]) for link in links
            if "Bollettino-sorveglianza-integrata-COVID-19" in link["href"]
            and (date_from_url(link["href"], is_raw=False) >= cut_date)]


def page_from_url(sel_url):
    """page_from_url(sel_url) -> int

    sel_url: url of the report
    return: number of the page containing table 3"""

    queries = ["TABELLA 3 – POPOLAZIONE ITALIANA",
               "TABELLA 3 – COPERTURA VACCINALE",
               "TABELLA 7 – COPERTURA VACCINALE"]

    with request.urlopen(sel_url) as response:
        content = response.read()
        with fitz.open(stream=content, filetype="pdf") as pdf:
            for query in queries:
                print(f"\nSearching for \n\"{query}\"...")
                # Query for string
                for page in pdf:
                    text = page.get_text()
                    if re.search(query, text, re.IGNORECASE):
                        return page.number + 1
    return None


def date_from_url(sel_url, is_raw=True):
    """date_from_url(str, boolean) -> datetime

    sel_url: url of the report
    is_raw: choose whether to return raw or translated date
    return: datetime"""

    date_ = re.findall(r"\d+[a-z-A-Z]+\d+", sel_url)[0]
    return date_ if is_raw else datetime.strptime(date_, "%d-%B-%Y")


def date_parser(sel_df):
    """date_parser(object) -> datetime

    sel_df: dataframe object
    return: converts argument to datetime"""

    return pd.to_datetime(sel_df, format="%Y/%m/%d")


def check_df(sel_df):
    """check_df(sel_df) -> None

    sel_df: dataframe object
    return: check if the table has 2 columns"""

    error_msg = "Can't extract the table! DIY!"
    if len(sel_df.columns) < 3:
        # Table is incomplete, bye bye
        print(error_msg)
        exit()


def get_data_from_report(auto=True):
    """get_data_from_report(boolean)

    The script saves data extracted from report.

    Select mode:
    - Automatic (auto = True): table of last available PDF
                               is automatically read
    - Manual (auto = False): Index of the report will be asked as input"""

    # Get reports
    reports = get_surveillance_reports()

    if auto:
        # Get most recent report url
        rep_url = reports[0]
    else:
        # Build dictionary for manual mode
        reports_dict = dict(enumerate([date_from_url(report)
                            for report in reports]))
        # Select report index as input
        rep_idx = input(f"\nChoose report index:\n\n{reports_dict}\n\n")
        rep_url = reports[int(rep_idx)]

    # Get report date
    rep_date = date_from_url(rep_url, is_raw=False)
    print(f"\nSelected report ({rep_date.date()}) is:\n{rep_url}")

    if rep_date < pd.to_datetime("2021-11-10"):
        msg_old = "\nFor oldest reports please use"
        msg_old += " the dati_selezione_old.py script!\n"
        print(msg_old)
        exit()

    # Read the csv to update from the repo
    df_0 = pd.read_csv("dati_ISS_complessivi.csv",
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

    # Can't really find the page, stop
    if table_page is None:
        print("Table not found!")
        exit()

    print("\nFound page is:", table_page)

    # Read the found page using camelot
    tables = camelot.read_pdf(rep_url,
                              pages=f"{table_page}",
                              flavor="stream")
    df_raw = tables[0].df

    # Check if there are enough columns
    if len(df_raw.columns) < 5:
        if len(tables) >= 1:
            df_raw = tables[1].df
        check_df(df_raw)

    # We are interested in the last 3 columns
    columns_to_keep = df_raw.columns[-5:]
    df_raw = df_raw[columns_to_keep]

    # Get rows containing "%)" at the end
    df_raw = df_raw[df_raw[df_raw.columns[0]].str.endswith("%)")]

    # Remove dots and parentheses
    to_exclude = r"\((.*)|[^0-9]"
    df_final = df_raw.replace(to_exclude, "", regex=True).astype(np.int64)

    df_final.columns = ["non vaccinati",
                        "vaccinati 1 dose",
                        "vaccinati completo < 6 mesi",
                        "vaccinati completo > 6 mesi",
                        "vaccinati booster"]

    # Merge immunized columns ("vaccinati completo < 6 mesi",
    # "vaccinati completo > 6 mesi") into one
    idx = df_final.columns.tolist().index("vaccinati 1 dose")
    vaccinati_completo = df_final.iloc[:, 2:].sum(axis=1)
    df_final.insert(idx+1, "vaccinati completo", vaccinati_completo)

    # Drop these columns
    df_final.drop(["vaccinati completo < 6 mesi",
                   "vaccinati completo > 6 mesi"], axis=1, inplace=True)
    df_final.reset_index(inplace=True, drop=True)

    # Skip the totals column
    rows_to_keep = [0, 1, 2, 3,
                    5, 6, 7, 8,
                    10, 11, 12, 13,
                    15, 16, 17, 18,
                    20, 21, 22, 23]
    df_final = df_final.iloc[rows_to_keep, :]

    # DEBUGONLY
    # print(df_final)
    # print(df_final.shape)

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
