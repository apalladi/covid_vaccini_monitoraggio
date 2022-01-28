# -*- coding: utf-8 -*-
""" dati_selezione.ipynb

Extraction of data from ISS weekly covid-19 reports
https://www.epicentro.iss.it/coronavirus/aggiornamenti

See example pdf:
https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_12-gennaio-2022.pdf

Requirements:
Python 3.6+, Ghostscript (ghostscript), Tkinter (python3-tk)
numpy, pandas, camelot, PyMuPDF, Beautiful Soup 4 """


import locale
import re
from datetime import datetime, timedelta
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
        # The script has been updated to 2022-01-12 report
        # for older reports than 2022-01-12 use "dati_selezione_old1.py" and "dati_ISS_complessivi_old1.csv"
        # for older reports than 2021-11-10 use "dati_selezione_old.py and "dati_ISS_complessivi_old.csv"
        cut_date = pd.to_datetime("2022-01-12")
    return [urljoin(epicentro_url, link["href"]) for link in links
            if "Bollettino-sorveglianza-integrata-COVID-19" in link["href"]
            and date_from_url(link["href"], is_raw=False) >= cut_date]


def page_from_url(sel_url, is_pop=False):
    """page_from_url(str, boolean) -> int

    sel_url: url of the report
    is_pop: choose between populations and general data
    return: number of the page containing the table"""

    query = "TABELLA A[0-9] - POPOLAZIONE DI RIFERIMENTO" if is_pop else \
            "TABELLA [0-9] – NUMERO DI CASI DI COVID-19"

    with request.urlopen(sel_url) as response:
        content = response.read()
        with fitz.open(stream=content, filetype="pdf") as pdf:
            print("\nSearching for the selected table...")
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
    columns_to_keep = sel_df.columns[-5:]
    df_raw = sel_df[columns_to_keep]

    # select rows containing numbers
    selection = r"[0-9]"
    df_raw = df_raw[df_raw[df_raw.columns[0]].str.match(selection)]

    # Remove dots and parentheses
    to_exclude = r"\((.*)|[^0-9]"
    df_final = df_raw.replace(to_exclude, "", regex=True).apply(np.int64)

    df_final.columns = ["non vaccinati",
                        "vaccinati 1 dose",
                        "vaccinati completo < x mesi",
                        "vaccinati completo > x mesi",
                        "vaccinati booster"]

    # Merge immunized columns ("vaccinati completo < x mesi",
    # "vaccinati completo > x mesi", "vaccinati booster") into one
    idx = df_final.columns.tolist().index("vaccinati 1 dose")
    vaccinati_completo = df_final.iloc[:, 2:].sum(axis=1)
    df_final.insert(idx+1, "vaccinati completo", vaccinati_completo)

    # Drop these columns
    df_final.drop(["vaccinati completo < x mesi",
                   "vaccinati completo > x mesi"], axis=1, inplace=True)
    df_final.reset_index(inplace=True, drop=True)
    return df_final


def extract_data_from_raw(raw_df, to_df, sel_rows=None):
    """extract_data_from_raw(df, df, list) -> df, df

    raw_df: raw dataframe
    to_df: dataframe to update
    sel_rows: selected raw df rows
    return: processed dataframes"""

    if sel_rows is None:
        f_pop = "data_iss_età_%s.xlsx"
        # Align hospitalizations/ti and deaths populations
        # Get hospitalizations/ti populations from 2nd latest report
        # Get deaths populations from 3rd latest report
        date_osp = rep_date - timedelta(days=15)
        df_hosp = pd.read_excel(f_pop % date_osp.date(), sheet_name="popolazioni")
        date_dec = rep_date - timedelta(days=22)
        df_deaths = pd.read_excel(f_pop % date_dec.date(), sheet_name="popolazioni")

        # Get general data
        results = np.concatenate((raw_df.iloc[4, :].values,
                                  to_df.loc[date_osp].values[0:4],
                                  to_df.loc[date_dec].values[0:4]))
        # Build ages dataframe
        # Merge df together
        df_ = pd.concat([raw_df.iloc[:4, :5], df_hosp.iloc[:, 1:5], df_deaths.iloc[:, 1:5]], axis=1)
        df_.columns = df_deaths.columns[1:]
        df_.set_index(df_deaths["età"], inplace=True)
    else:
        # Get general data
        results = raw_df.iloc[sel_rows, :].stack().values
        # Get data by age
        ages = ["12-39", "40-59", "60-79", "80+"]
        rows_to_keep = np.arange(0, len(raw_df), 5)
        results_ = {age: raw_df.iloc[rows_to_keep+i, :].stack().values
                    for i, age in enumerate(ages)}
        # Build ages dataframe
        df_ = pd.DataFrame(results_).T
        df_.columns = to_df.columns
        df_.index.rename("età", inplace=True)

    # Add the new row at the top of the general df
    to_df.loc[rep_date] = results
    to_df.sort_index(ascending=False, inplace=True)
    to_df = to_df.apply(np.int64)

    return to_df, df_


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
                        \nFor oldest reports please use \
                        the dati_selezione_old.py script!\n\
                        \n\n{reports_dict}\n\n")
        rep_url = reports[int(rep_idx)]

    # Get report date
    rep_date = date_from_url(rep_url, is_raw=False)
    print(f"\nSelected report ({rep_date.date()}) is:\n{rep_url}")
    return rep_date, rep_url


def merge_df_into_excel(df_0, df_1, filename="dati_ISS_complessivi.xlsx"):
    """merge_df_into_excel(df, df, str)

    df_0: epidemiological data dataframe
    df_1: populations data dataframe
    filename: name of the output xlsx
    return: merges two dataframes into an xlsx"""

    with pd.ExcelWriter(filename) as writer:
        df_0.to_excel(writer, sheet_name="dati epidemiologici")
        df_1.to_excel(writer, sheet_name="popolazioni")


def get_data_from_report(force=False):
    """get_data_from_report(boolean)

    The script saves data extracted from report.
    Use force=True to skip checks and force data extraction"""

    # Read the csv to update from the repo
    df_0 = pd.read_excel("dati_ISS_complessivi.xlsx",
                         sheet_name="dati epidemiologici",
                         parse_dates=["data"],
                         index_col="data")

    # If table is already up-to-date stop the script
    if rep_date in df_0.index and not force:
        print("\nCSV are already up-to-date!")
        exit()

    # Get the main table page number
    main_table_pg = page_from_url(rep_url)

    # Can't really find the page, stop
    if main_table_pg is None:
        print("Table not found!")
        exit()

    print("\nFound page is:", main_table_pg)

    # get and clean the raw df
    df_raw = get_raw_table(rep_url, main_table_pg)
    df_raw = clean_raw_table(df_raw)

    # Finally, get the data

    # Keep totals only
    rows_tot = [4, 9, 14, 19]
    df_0, df_1 = extract_data_from_raw(df_raw, df_0, sel_rows=rows_tot)

    # retrieve population data
    pop_table_pg = page_from_url(rep_url, is_pop=True)

    # Can't really find the page, stop
    if pop_table_pg is None:
        print("Table not found!")
        exit()

    print("\nFound page is:", pop_table_pg)

    # Read the csv to update from the repo
    df_pop = pd.read_excel("dati_ISS_complessivi.xlsx",
                           sheet_name="popolazioni",
                           parse_dates=["data"],
                           index_col="data")

    # Get and clean the raw populations df
    df_raw_ = get_raw_table(rep_url, pop_table_pg)
    df_raw_ = clean_raw_table(df_raw_)

    df_2, df_3 = extract_data_from_raw(df_raw_, df_pop)

    # Save to xlsx
    merge_df_into_excel(df_0, df_2)
    merge_df_into_excel(df_1, df_3, filename=f"data_iss_età_{rep_date.date()}.xlsx")

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

    # Get data
    # Use force=True to skip the checks/for debug purposes
    get_data_from_report()
