# type: ignore

from datetime import datetime
from glob import glob
from re import findall

from numpy import sort
from pandas import to_datetime


def update_labels(df_tassi, x_date, x_label):
    # aggiungi nuovo mese/anno se necessario
    if (df_tassi.index[0].month > df_tassi.index[1].month):
        # aggiorna lista x_date
        date_to_add = df_tassi.index[0].replace(day=1)
        x_date.append(date_to_add.strftime("%Y-%m-%d"))
        # aggiorna lista x_label
        month_abbr = date_to_add.strftime("%b").capitalize()
        year_abbr = date_to_add.strftime("%y").capitalize()
        # specifica nuovo anno se necessario
        if (df_tassi.index[0].year > df_tassi.index[1].year):
            x_label.append(f"\n{month_abbr}\n{year_abbr}")
            print(f"Aggiunto nuovo mese {month_abbr} e anno {year_abbr}")
        # altrimenti aggiungi solo il mese
        else:
            x_label.append(f"\n{month_abbr}")
            print(f"Aggiunto nuovo mese {month_abbr}")
        # rimuovi prima entry liste se la loro lunghezza supera 3
        if (len(x_date) > 3):
            x_date.pop(0)
            x_label.pop(0)
            x_label[0] = f"{x_label[0]}\n{year_abbr}"
    return x_date, x_label


def update_labels2(sel_df, x_date, x_label):
    # aggiungi nuovo mese/anno se necessario
    # aggiorna lista x_date
    date_to_add = sel_df.index[-1].replace(day=1)
    x_date.append(date_to_add.strftime("%Y-%m-%d"))
    # aggiorna lista x_label
    month_abbr = date_to_add.strftime("%b").capitalize()
    year_abbr = date_to_add.strftime("%y").capitalize()
    # specifica nuovo anno se necessario
    if (sel_df.index[-1].year > to_datetime(x_date[-2]).year):
        x_label.append(f"{month_abbr}\n{year_abbr}")
        print(f"Aggiunto nuovo mese {month_abbr} e anno {year_abbr}")
    # altrimenti aggiungi il mese
    else:
        x_label.append(month_abbr)
        print(f"Aggiunto nuovo mese {month_abbr}")
    if (len(x_date) > 4):
        x_date.pop(0)
        x_label.pop(0)
        x_label[0] = f"{x_label[0]}\n{year_abbr}"
    return x_date, x_label


def aggiorna_ascissa(df, new_date, last_updated, x_date, x_label):
    # aggiorna limite ascissa...
    if (new_date.month > last_updated.month):
        x_date, x_label = update_labels2(df,
                                         x_date,
                                         x_label)
        last_updated = last_updated
    # ... e data più recente se necessario
    elif (new_date > last_updated):
        last_updated = new_date
    return last_updated, x_date, x_label


def list_età_csv(is_most_recent=False):
    # lista i csv
    files = sort(glob("../dati/data_iss_età_*.csv"))
    return files[-1] if is_most_recent else files


def date_from_csv_path(csv_path):
    date_ = findall(r"\d+-\d+-\d+", csv_path)[0]
    return datetime.strptime(date_, "%Y-%m-%d")
