def update_labels2(sel_df):
    # aggiungi nuovo mese/anno se necessario
    # aggiorna lista x_date
    date_to_add = sel_df.index[-1].replace(day=1)
    x_date.append(date_to_add.strftime('%Y-%m-%d'))
    # aggiorna lista x_label
    month_abbr = date_to_add.strftime("%b").capitalize()
    year_abbr = date_to_add.strftime("%y").capitalize()
    # specifica nuovo anno se necessario
    if (sel_df.index[-1].year > pd.to_datetime(x_date[-2]).year):
        x_label.append(f'{month_abbr}\n{year_abbr}')
        print(f'Aggiunto nuovo mese {month_abbr} e anno {year_abbr}')
    # altrimenti aggiungi il mese
    else:
        x_label.append(month_abbr)
        print(f'Aggiunto nuovo mese {month_abbr}')
        
        
def update_labels(df_tassi):
    # aggiungi nuovo mese/anno se necessario
    if (df_tassi.index[0].month > df_tassi.index[1].month):
        # aggiorna lista x_date
        date_to_add = df_tassi.index[0].replace(day=1)
        x_date.append(date_to_add.strftime('%Y-%m-%d'))
        # aggiorna lista x_label
        month_abbr = date_to_add.strftime("%b").capitalize()
        year_abbr = date_to_add.strftime("%y").capitalize()
        # specifica nuovo anno se necessario
        if (df_tassi.index[0].year > df_tassi.index[1].year):
            x_label.append(f'{month_abbr}\n{year_abbr}')
            print(f'Aggiunto nuovo mese {month_abbr} e anno {year_abbr}')
        # altrimenti aggiungi solo il mese
        else:
            x_label.append(month_abbr)
            print(f'Aggiunto nuovo mese {month_abbr}')
