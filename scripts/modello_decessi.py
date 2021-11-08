#!/usr/bin/env python
# coding: utf-8

# Importa librerie

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
from custom.watermarks import add_watermark


# Definizione funzioni

def get_vaccine_data(country, time_window=30, fully=False):
    """ Recupera dati sulla frazione di vaccinati medi negli ultimi time_window giorni (default = 30)"""
    df_vacc_country2 = df_global[df_global["location"] == country]
    df_vacc_country = df_vacc_country2.fillna(method='ffill').copy()
    if fully==False:
        vacc_fully = np.array(df_vacc_country["people_vaccinated_per_hundred"][-(time_window+1):-1])
    else:
        vacc_fully = np.array(df_vacc_country["people_fully_vaccinated_per_hundred"][-(time_window+1):-1])
    
    vacc_ultimi_Ngiorni = np.mean(vacc_fully)   
    return vacc_ultimi_Ngiorni

def get_deaths(country, time_window=30):
    """ Recupera dati sul numero assoluto di decessi negli ultimi time_window giorni (default = 30)"""
    decessi = np.array(df_global[df_global["location"] == country]['total_deaths'])
    decessi_ultimi_Ngiorni = decessi[-1] - decessi[-(time_window+1)]
    return decessi_ultimi_Ngiorni

def get_value_from_df(countries, column, scale_factor=1):
    """ Recupera l'ultimo valore della column specificata, per la lista di countries, e moltiplica per scale_factor (default = 1)"""
    values = []
    for el in countries:
         values.append(df_global[df_global["location"] == el][column].tolist()[-1]*scale_factor)
    return values

# Importa dati da Our World in Data

file_owid = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
df_global = pd.read_csv(file_owid)

# Dataframe solo per paesi europei
eu_countries = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland', 
                'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
                'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden']
df_europe = df_global.loc[df_global['location'].isin(eu_countries)]

# Calcola morti e vaccinati

# Definizione paesi e relative label
paesi = eu_countries
paesi_label = ['Austria', 'Belgio', 'Bulgaria', 'Croazia', 'Cipro', 'Repubblica Ceca', 'Danimarca', 'Estonia', 'Finlandia', 
                'Francia', 'Germania', 'Grecia', 'Ungheria', 'Irlanda', 'Italia', 'Lettonia', 'Lituania', 'Lussemburgo', 
                'Malta', 'Paesi Bassi', 'Polonia', 'Portogallo', 'Romania', 'Slovacchia', 'Slovenia', 'Spagna', 'Svezia']

# Calcola vaccinati e decessi
abitanti = get_value_from_df(paesi, 'population', scale_factor=1e-6)

# Crea dizionario
abitanti_dict = dict(zip(paesi, abitanti))

dec_res=[] # Decessi per milione di abitanti ultimi tw_death giorni
vacc_res=[] # % vaccinati media ultimi tw_vacc giorni

tw_death = 210
tw_vacc = 7
for i in range(len(paesi)):
    vacc_res.append(get_vaccine_data(paesi[i], time_window = tw_vacc, fully=True))
    dec_res.append(get_deaths(paesi[i], time_window = tw_death)/abitanti_dict[paesi[i]])

# Aggiungi altre grandezze

# Definisci dati estratti da df_europe
columns = ['gdp_per_capita', 'population_density', 'aged_70_older', 'extreme_poverty', 
                  'diabetes_prevalence', 'hospital_beds_per_thousand', 'life_expectancy']

data_for_model = []

# Estrai dati da df_europe e aggiungili a data_for_model
for el in columns:
    data_for_model.append(get_value_from_df(paesi, el))

# Aggiungi manualmente dati di latitudine, vaccinati, morti
latitude = [47.516231, 50.503887, 42.733883, 45.1, 35.126413, 49.817492, 56.26392, 58.595272, 61.92411, 46.227638, 51.165691, 39.074208, 47.162494, 53.41291, 41.87194, 56.879635, 55.169438, 49.815273, 35.937496, 52.132633, 51.919438, 39.399872, 45.943161, 48.669026, 46.151241, 40.463667, 60.128161]
data_for_model.append(vacc_res)
data_for_model.append(latitude)    
data_for_model.append(dec_res)

# Aggiungi manualmente colonne di latitudine, vaccinati, morti
columns.append(f'Perc_vacc_last_{tw_vacc}_days')
columns.append('latitude')    
columns.append(f'Deaths_last_{tw_death}_days')

# Trasponi data_for_model
data_for_model = list(map(list, zip(*data_for_model)))

# Crea DataFrame

df_europe_small = pd.DataFrame(data_for_model, columns=columns).round(decimals=2)

# Aggiungi colonna 'Country' e rendila indice
df_europe_small = df_europe_small.assign(Country=pd.Series(paesi_label).values)
df_europe_small.set_index('Country', inplace=True)
df_europe_small.tail(15)

# Matrice di correlazione

corr = df_europe_small.corr()

# Plotta solo metà matrice di correlazione
# mask = np.zeros_like(corr, dtype=bool)
# mask[np.triu_indices_from(mask)] = True
# corr[mask] = np.nan
# (corr.style.background_gradient(cmap='coolwarm', axis=None, vmin=-1, vmax=1).highlight_null(null_color='#f1f1f1'))  # Color NaNs grey

# Modello con regressione lineare

from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

# Definisci dati per modello
X = df_europe_small.drop([f'Deaths_last_{tw_death}_days'], axis=1)
# Riempi i NaN con median/mean
X.fillna(X.median(), inplace=True)
# Scala dati
scaler = StandardScaler()
X[X.columns.tolist()] = scaler.fit_transform(X[X.columns.tolist()])

Y = df_europe_small[f'Deaths_last_{tw_death}_days']

# Crea modello e stampa dati
regr = linear_model.LinearRegression()
regr.fit(X, Y)
score = regr.score(X, Y)

print('Intercetta: \n', regr.intercept_)
print('Coefficienti: \n', regr.coef_)
print('R2 Score', score)

# Stampa grafico dei coefficienti
plt.style.use('seaborn-dark')
fig, ax = plt.subplots(figsize=(8, 4))
plt.barh(X.columns, regr.coef_)
plt.xlabel('Coefficiente della regressione lineare')
plt.grid()
ax = plt.gca()
add_watermark(fig, ax.xaxis.label.get_fontsize())
plt.tight_layout()
plt.savefig('../risultati/coefficienti.png', dpi=300, bbox_inches="tight")
plt.show()

# Aggiungere statsmodels a requirements.txt

import statsmodels.api as sm
# with statsmodels
X = sm.add_constant(X) # adding a constant
 
model = sm.OLS(Y, X).fit()
predictions = model.predict(X) 
 
print_model = model.summary()
print(print_model)



