from datetime import datetime
from glob import glob
from re import findall

from numpy import sort
from pandas import to_datetime


def aggiorna_ascissa(last_updated, new_date, x_date, x_label):
    # aggiorna limite ascissa...
    if (new_date.month > last_updated.month):
        # aggiungi nuovo mese/anno se necessario
        # aggiorna lista x_date
        date_to_add = new_date.replace(day=1)
        x_date.append(date_to_add.strftime("%Y-%m-%d"))
        # aggiorna lista x_label
        new_month = date_to_add.strftime("%b").capitalize()
        new_year = date_to_add.strftime("%Y")
        # specifica nuovo anno se necessario
        if (new_date.year > to_datetime(x_date[-2]).year):
            x_label.append(f"{new_month}\n{new_year}")
            print(f"Aggiunto nuovo mese {new_month} e anno {new_year}")
        # altrimenti aggiungi il mese
        else:
            x_label.append(new_month)
            print(f"Aggiunto nuovo mese {new_month}")
        # mantieni lunghezza liste a 4
        if (len(x_date) > 4):
            x_date.pop(0)
            x_label.pop(0)
            x_label[0] = f"{x_label[0]}\n{new_year}"
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
