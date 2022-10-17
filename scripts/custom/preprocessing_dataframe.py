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
             df_epid["casi vaccinati 1 dose"]/df_pop["casi vaccinati 1 dose"],
             df_epid["casi vaccinati > 4-6 mesi"]/df_pop["casi vaccinati > 4-6 mesi"],
             df_epid["casi vaccinati < 4-6 mesi"]/df_pop["casi vaccinati < 4-6 mesi"],
             df_epid["casi booster"]/df_pop["casi booster"],
             df_epid["casi qt dose"]/df_pop["casi qt dose"],
             df_epid["casi vaccinati completo"]/df_pop["casi vaccinati completo"],
             df_epid["ospedalizzati non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["ospedalizzati vaccinati 1 dose"]/df_pop["ospedalizzati/ti vaccinati 1 dose"],
             df_epid["ospedalizzati vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["ospedalizzati booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["ospedalizzati qt dose"]/df_pop["ospedalizzati/ti qt dose"],
             df_epid["ospedalizzati vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["terapia intensiva non vaccinati"]/df_pop["ospedalizzati/ti non vaccinati"],
             df_epid["terapia intensiva vaccinati 1 dose"]/df_pop["ospedalizzati/ti vaccinati 1 dose"],
             df_epid["terapia intensiva vaccinati > 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva vaccinati < 4-6 mesi"]/df_pop["ospedalizzati/ti vaccinati > 4-6 mesi"],
             df_epid["terapia intensiva booster"]/df_pop["ospedalizzati/ti booster"],
             df_epid["terapia intensiva qt dose"]/df_pop["ospedalizzati/ti qt dose"],
             df_epid["terapia intensiva vaccinati completo"]/df_pop["ospedalizzati/ti vaccinati completo"],
             df_epid["decessi non vaccinati"]/df_pop["decessi non vaccinati"],
             df_epid["decessi vaccinati 1 dose"]/df_pop["decessi vaccinati 1 dose"],
             df_epid["decessi vaccinati > 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi vaccinati < 4-6 mesi"]/df_pop["decessi vaccinati > 4-6 mesi"],
             df_epid["decessi booster"]/df_pop["decessi booster"],
             df_epid["decessi qt dose"]/df_pop["decessi qt dose"],
             df_epid["decessi vaccinati completo"]/df_pop["decessi vaccinati completo"]]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = ["Casi, non vaccinati", "Casi, vaccinati 1 dose", "Casi, vaccinati > 4-6 mesi",
                        "Casi, vaccinati < 4-6 mesi", "Casi, booster", "Casi, qt dose", "Casi, vaccinati completo",
                        "Ospedalizzati, non vaccinati", "Ospedalizzati, vaccinati 1 dose", "Ospedalizzati, vaccinati > 4-6 mesi",
                        "Ospedalizzati, vaccinati < 4-6 mesi", "Ospedalizzati, booster", "Ospedalizzati, qt dose",
                        "Ospedalizzati, vaccinati completo", "In terapia intensiva, non vaccinati",
                        "In terapia intensiva, vaccinati 1 dose",
                        "In terapia intensiva, vaccinati > 4-6 mesi", "In terapia intensiva, vaccinati < 4-6 mesi",
                        "In terapia intensiva, booster", "In terapia intensiva, qt dose", "In terapia intensiva, vaccinati completo",
                        "Deceduti, non vaccinati", "Deceduti, vaccinati 1 dose", "Deceduti, vaccinati > 4-6 mesi",
                        "Deceduti, vaccinati < 4-6 mesi", "Deceduti, booster", "Deceduti, qt dose",
                        "Deceduti, vaccinati completo"]
    return df_tassi


def get_df_popolazione():
    # dati ISS platea vaccinazioni
    # https://github.com/italia/covid19-opendata-vaccini
    url = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/platea.csv"
    df_plat = pd.read_csv(url)
    df_plat = df_plat.groupby("eta").sum()
    map_dict = {
      "5-11": "05-11",
      "12-39": ("12-19", "30-39"),
      "40-59": ("40-49", "50-59"),
      "60-79": ("60-69", "70-79"),
      "80+": "80+"
    }
    pop_dict = {k: df_plat.loc[v[0]:v[1]].sum()
                if type(v) is tuple else df_plat.loc[v]
                for k, v in map_dict.items()}
    return pd.DataFrame(pop_dict).T


def compute_incidence_std():
    def calc_df_adj(df_tassi):
        # recupera popolazione (pesi)
        df_pesi = get_df_popolazione()
        # filtra classe età 5-11
        df_pesi = df_pesi[df_pesi.index != "5-11"]
        # aggiungi colonna pesi a df tassi
        df_tassi_ = df_tassi.reset_index().merge(df_pesi,
                                                 how="left",
                                                 left_on="età",
                                                 right_on=df_pesi.index,
                                                 sort=False).set_index("data")
        weights = df_tassi_["totale_popolazione"].to_numpy()
        weights_sum = df_pesi["totale_popolazione"].sum()
        # moltiplica i tassi calcolati per i pesi
        df_tassi_adj = df_tassi_.iloc[:, 1:-1].mul(weights, axis=0).reset_index()
        # somma tassi
        df_tassi_adj = df_tassi_adj.groupby("data").agg(sum)
        # dividi per somma pesi
        df_tassi_adj = df_tassi_adj.apply(lambda x: x/weights_sum)
        df_tassi_adj = df_tassi_adj.replace(0, np.nan)
        return df_tassi_adj

    df_età = pd.read_excel("../dati/dati_ISS_età.xlsx", sheet_name=None, index_col="età")
    df_età_epid = df_età["dati epidemiologici"]
    df_età_epid = df_età_epid[df_età_epid.index != "5-11"]
    df_età_pop = df_età["popolazioni"]
    df_età_pop = df_età_pop[df_età_pop.index != "5-11"]
    df_età_epid = df_età_epid[df_età_epid["data"] > "2021-07-28"]
    df_età_pop = df_età_pop[df_età_pop["data"] > "2021-07-28"]

    df_tassi = compute_incidence(df_età_epid, df_età_pop)
    df_tassi.index = df_età_epid.index
    df_tassi = df_tassi.reset_index()
    df_tassi.index = df_età_epid["data"]

    return calc_df_adj(df_tassi)
