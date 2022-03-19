# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of data from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/aggiornamenti

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_19-gennaio-2022.pdf

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
        # The table is available since 14/07/2021
        # The script has been updated to 2022-01-19 report
        cut_date = pd.to_datetime("2022-01-19")
        cut_date_end = pd.to_datetime("2022-03-16")
    return [urljoin(epicentro_url, link["href"]) for link in links
            if "Bollettino-sorveglianza-integrata-COVID-19" in link["href"]
            and date_from_url(link["href"], is_raw=False) >= cut_date
            and (date_from_url(link["href"], is_raw=False) < cut_date_end)]


def pages_from_url(sel_url):
    """page_from_url(str) -> list

    sel_url: url of the report
    return: numbers of the pages containing the tables"""

    query = "TABELLA [4-5][A-C] - POPOLAZIONE ITALIANA"

    with request.urlopen(sel_url) as response:
        content = response.read()
        with fitz.open(stream=content, filetype="pdf") as pdf:
            print("\nSearching for the selected table...")
            # Query for string
            found_pages = []
            for page in pdf:
                text = page.get_text()
                if re.search(query, text, re.IGNORECASE):
                    n = page.number + 1
                    print(f"Found: {n}")
                    found_pages.append(n)
    return found_pages


def date_from_url(sel_url, is_raw=True):
    """date_from_url(str, boolean) -> datetime

    sel_url: url of the report
    is_raw: choose whether to return raw or translated date
    return: datetime"""

    date_ = re.findall(r"\d+[a-z-A-Z]+\d+", sel_url)[0]
    return date_ if is_raw else datetime.strptime(date_, "%d-%B-%Y")


def check_df(sel_df):
    """check_df(df) -> None

    sel_df: dataframe
    return: check if the table has at least 2 columns"""

    error_msg = "Can't extract the table! DIY!"
    if len(sel_df.columns) < 3:
        # Table is incomplete, bye bye
        print(error_msg)
        exit()


def get_raw_table(sel_url, table):
    """get_raw_table(str, int) -> df

    sel_url: url of the report
    table: the page number of the table
    return: raw dataframe"""

    # Read the found page using camelot
    tables = camelot.read_pdf(sel_url,
                              pages=f"{table}",
                              flavor="stream")
    df_raw = tables[0].df

    # Check if there are enough columns
    if len(df_raw.columns) < 5:
        if len(tables) >= 1:
            df_raw = tables[1].df
        check_df(df_raw)
    return df_raw


def clean_raw_table(sel_df):
    """clean_raw_table(df) -> df

    sel_df: raw dataframe
    return: extract numerical data from the dataframe"""

    # We are interested in the last 5 columns
    df_raw = sel_df.iloc[:, -5:]

    # select rows containing numbers
    selection = r"[0-9]"
    df_raw = df_raw[df_raw[df_raw.columns[0]].str.match(selection)]

    # Remove dots and parentheses
    to_exclude = r"\((.*)|[^0-9]"
    df_final = df_raw.replace(to_exclude, "", regex=True).apply(np.int64)

    # Merge columns "vaccinati completo > 4-6 mesi", "vaccinati completo < 4-6 mesi",
    # "vaccinati booster" into "vaccinati completo" (fully immunized + third dose)
    vaccinati_completo = df_final.iloc[:, 2:].sum(axis=1)
    df_final.insert(len(df_final.columns), "vaccinati completo", vaccinati_completo)
    df_final.reset_index(inplace=True, drop=True)
    return df_final


def extract_data_main(clean_tables):
    totals_epidem = []
    totals_pop = []
    for i, table in enumerate(clean_tables):
        if i == 1:
            totals_epidem.extend(table.iloc[[9, 14], :].stack().values)
        else:
            totals_epidem.extend(table.iloc[9, :].values)
        totals_pop.extend(table.iloc[4, :].values)
    return totals_epidem, totals_pop


def extract_data_by_age(clean_tables):
    for i, table in enumerate(clean_tables):
        # Population data
        if i == 0:
            df_pop_eta = table.iloc[:4, :]
        else:
            df_pop_eta = pd.concat((df_pop_eta, table.iloc[:4, :]), axis=1)

        # Epidemiological data
        if i == 0:
            df_epid_eta = table.iloc[5:9, :].reset_index(drop=True)
        elif i == 1:
            hosp = table.iloc[5:9, :].reset_index(drop=True)
            ti = table.iloc[10:14, :].reset_index(drop=True)
            df_epid_eta = pd.concat([df_epid_eta, hosp, ti], axis=1)
        else:
            dec = table.iloc[5:9, :].reset_index(drop=True)
            df_epid_eta = pd.concat((df_epid_eta, dec), axis=1)
    return df_epid_eta, df_pop_eta


def add_new_row(sel_df, results):
    """add_new_row(df, list)

    sel_df: selected dataframe
    results: list of integers
    return: add the new row at the top of the selected df"""
    sel_df.loc[rep_date] = results
    sel_df.sort_index(ascending=False, inplace=True)
    return sel_df.apply(np.int64)


def add_index_cols(sel_df, columns):
    """add_index_cols(df, list)

    sel_df: selected dataframe
    columns: columns list
    return: dataframe with index and columns"""
    sel_df.columns = columns
    sel_df.insert(0, "età", ages)
    sel_df.index = [rep_date]*len(sel_df)
    sel_df.index.rename("data", inplace=True)
    return sel_df


def merge_df_into_xlsx(df_0, df_1, filename="dati_ISS_complessivi.xlsx"):
    """merge_df_into_xlsx(df, df, str)

    df_0: epidemiological data dataframe
    df_1: populations data dataframe
    filename: name of the output xlsx
    return: merges two dataframes into an xlsx"""

    with pd.ExcelWriter(filename) as writer:
        df_0.to_excel(writer, sheet_name="dati epidemiologici")
        df_1.to_excel(writer, sheet_name="popolazioni")


def get_report(auto=True):
    """get_report(boolean)

    The script get the selected report.
    Select mode:
    - Automatic (auto=True): table of last available PDF is automatically read
    - Manual (auto=False): Index of the report will be asked as input"""

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
        rep_idx = input(f"\nChoose report index:\
                        \n\n{reports_dict}\n\n")
        rep_url = reports[int(rep_idx)]

    # Get report date
    rep_date = date_from_url(rep_url, is_raw=False)
    print(f"\nSelected report ({rep_date.date()}) is:\n{rep_url}")
    return rep_date, rep_url


def get_data_from_report(force=False):
    """get_data_from_report(boolean)

    The script saves data extracted from report.
    Use force=True to skip checks and force data extraction"""

    # Read the csv to update from the repo
    df_complessivo = pd.read_excel("dati_ISS_complessivi.xlsx", sheet_name=None,
                                   index_col="data", parse_dates=["data"])
    df_0 = df_complessivo["dati epidemiologici"]
    df_1 = df_complessivo["popolazioni"]

    # If table is already up-to-date stop the script
    if rep_date in df_0.index and not force:
        print("\nCSV are already up-to-date!")
        exit()

    # Get tables pages
    tables_pages = pages_from_url(rep_url)

    # Failed to extract the tables
    if len(tables_pages) < 3:
        print("An error occurred!")
        exit()

    # get and clean the raw tables
    raw_tables = [get_raw_table(rep_url, n) for n in tables_pages]
    clean_tables = [clean_raw_table(raw) for raw in raw_tables]

    # Finally, get the data

    # Get general data
    totals_epidem, totals_pop = extract_data_main(clean_tables)
    # Update the dataframes
    add_new_row(df_0, totals_epidem)
    add_new_row(df_1, totals_pop)
    # Save to xlsx
    merge_df_into_xlsx(df_0, df_1)

    # Get data by age
    df_epid_età, df_pop_età = extract_data_by_age(clean_tables)
    # Add index and columns to the dataframes
    df_epid_età = add_index_cols(df_epid_età, df_0.columns)
    df_pop_età = add_index_cols(df_pop_età, df_1.columns)

    # Add the two df to dati_ISS_età.xlsx
    df_età = pd.read_excel("dati_ISS_età.xlsx", sheet_name=None,
                           index_col="data", parse_dates=["data"])
    df_epid_età = pd.concat((df_epid_età, df_età["dati epidemiologici"]))
    df_pop_età = pd.concat((df_pop_età, df_età["popolazioni"]))
    merge_df_into_xlsx(df_epid_età, df_pop_età, filename="dati_ISS_età.xlsx")

    print("\nDone!")


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Set locale to "it" to parse the month correctly
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")

    # Get the report
    # Use force=False for manual selection
    rep_date, rep_url = get_report()

    ages = ["12-39", "40-59", "60-79", "80+"]

    # Get data
    # Use force=True to skip the checks/for debug purposes
    get_data_from_report()
