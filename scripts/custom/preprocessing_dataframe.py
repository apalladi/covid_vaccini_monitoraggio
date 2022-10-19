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


def compose_labels(labels, templates):
    return [templ % lab for lab in labels for templ in templates]


def compute_incidence(df_epid, df_pop, eventi_templ=["%s non vaccinati", "%s vaccinati completo", "%s booster"]):
    # ricava i tassi dividendo per la popolazione vaccinata e non vaccinata

    # eventi interessati
    num_labs = ["casi", "ospedalizzati", "terapia intensiva", "decessi"]
    den_labs = ["casi", "ospedalizzati/ti", "ospedalizzati/ti", "decessi"]

    # template labels colonne
    templates = ["%s non vaccinati", "%s vaccinati 1 dose", "%s vaccinati > 4-6 mesi",
                 "%s vaccinati < 4-6 mesi", "%s booster", "%s qt dose", "%s vaccinati completo"]

    # costruisci i label usati per selezionare le colonne del dataframe
    num_labs_ = compose_labels(num_labs, templates)
    den_labs_ = compose_labels(den_labs, templates)

    # calcolo tassi
    tassi = [df_epid[num_labs_[i]].div(df_pop[den_labs_[i]])
             for i in range(len(num_labs_))]
    tassi = 10**5*np.transpose(tassi)
    df_tassi = pd.DataFrame(tassi)
    df_tassi.columns = num_labs_
    df_tassi = df_tassi.replace([np.inf, -np.inf], np.nan)

    selezione = [[sel_templ % lab for sel_templ in eventi_templ]
                 for lab in num_labs]
    return df_tassi, selezione


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

    df_tassi, _ = compute_incidence(df_età_epid, df_età_pop)

    df_tassi.index = df_età_epid.index
    df_tassi = df_tassi.reset_index()
    df_tassi.index = df_età_epid["data"]

    return calc_df_adj(df_tassi)
