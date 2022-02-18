import numpy as np
import pandas as pd


def get_df_complessivo():
    # dati ISS
    df_complessivo = pd.read_excel("../dati/dati_ISS_complessivi.xlsx", sheet_name=None)
    df_epid = df_complessivo["dati epidemiologici"]
    df_pop = df_complessivo["popolazioni"]
    df_epid = df_epid[df_epid["data"] > "2021-07-28"]
    df_pop = df_pop[df_pop["data"] > "2021-07-28"]
    return df_epid, df_pop


def compute_incidence(df_epid, df_pop):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata
    tassi = [df_epid["casi non vaccinati"]/df_pop["casi non vaccinati"],
             df_epid["casi vaccinati > 4-6 mesi"]/df_pop["casi vaccinati > 4-6 mesi"],
             df_epid["casi vaccinati < 4-6 mesi"]/df_pop["casi vaccinati < 4-6 mesi"],
             df_epid["casi booster"]/df_pop["casi booster"],
             df_epid["casi vaccinati completo"]/df_pop["casi vaccinati completo"],
             df_epid["ospedalizzati non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["ospedalizzati vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["ospedalizzati vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["terapia intensiva non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["terapia intensiva vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["terapia intensiva vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["decessi non vaccinati"]/df_pop["decessi non vaccinati"],
             df_epid["decessi vaccinati > 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi vaccinati < 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi booster"]/df_pop["decessi booster"],
             df_epid["decessi vaccinati completo"]/df_pop["decessi vaccinati completo"]]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = ["Casi, non vaccinati", "Casi, vaccinati > 4-6 mesi",
                        "Casi, vaccinati < 4-6 mesi", "Casi, booster", "Casi, vaccinati completo",
                        "Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati > 4-6 mesi",
                        "Ospedalizzati, vaccinati < 4-6 mesi", "Ospedalizzati, booster",
                        "Ospedalizzati, vaccinati completo", "In terapia intensiva, non vaccinati",
                        "In terapia intensiva, vaccinati > 4-6 mesi", "In terapia intensiva, vaccinati < 4-6 mesi",
                        "In terapia intensiva, booster", "In terapia intensiva, vaccinati completo",
                        "Deceduti, non vaccinati", "Deceduti, vaccinati > 4-6 mesi",
                        "Deceduti, vaccinati < 4-6 mesi", "Deceduti, booster",
                        "Deceduti, vaccinati completo"]
    return df_tassi


def get_df_popolazione():
    # dati ISS platea vaccinazioni
    # https://github.com/italia/covid19-opendata-vaccini
    url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/platea.csv"
    df_plat = pd.read_csv(url)
    df_plat = df_plat.groupby("fascia_anagrafica").sum()
    df_età = pd.concat([df_plat["12-19":"30-39"].sum(),
                        df_plat["40-49":"50-59"].sum(),
                        df_plat["60-69":"70-79"].sum(),
                        df_plat["80+":].sum()])
    df_età.index = ["12-39", "40-59", "60-79", "80+"]
    return df_età


def compute_incidence_std():
    def calc_inc_std(sel_df):
        df_psi = get_df_popolazione()
        w_sum = 0
        for age in df_età_epid.index.unique():
            w_sum += sel_df.loc[age]*df_psi[age]
        w_sum /= df_psi.sum()
        return w_sum

    df_età = pd.read_excel("../dati/dati_ISS_età.xlsx", sheet_name=None, index_col="età")
    df_età_epid = df_età["dati epidemiologici"]
    df_età_pop = df_età["popolazioni"]
    df_età_epid = df_età_epid[df_età_epid["data"] > "2021-07-28"]
    df_età_pop = df_età_pop[df_età_pop["data"] > "2021-07-28"]

    df_tassi = compute_incidence(df_età_epid, df_età_pop)
    df_tassi.index = df_età_epid.index
    df_tassi.reset_index(inplace=True)
    df_tassi.index = df_età_epid["data"]

    date_reports = df_tassi.index.unique()

    eventi = ["Casi, non vaccinati", "Casi, vaccinati completo", "Casi, booster",
              "Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati completo",
              "Ospedalizzati, booster", "In terapia intensiva, non vaccinati",
              "In terapia intensiva, vaccinati completo", "In terapia intensiva, booster",
              "Deceduti, non vaccinati", "Deceduti, vaccinati completo", "Deceduti, booster"]

    tassi_std = {}
    for date in date_reports:
        df_ = df_tassi.loc[date]
        df_.set_index("età", inplace=True)
        df_std_ = calc_inc_std(df_[eventi])
        tassi_std[date] = df_std_
    return pd.DataFrame(tassi_std).T
