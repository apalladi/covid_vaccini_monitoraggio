# Monitoraggio vaccini Italia

[![Sito web](https://img.shields.io/website?up_color=brightgreen&up_message=online&url=https%3A%2F%2Fenricocid.github.io%2Fmonitoraggio-vaccini-italia%2F)](https://enricocid.github.io/monitoraggio-vaccini-italia/)

Questo repository è stato creato allo scopo di monitorare l'andamento dell'epidemia provocata dal virus Sars-Cov-2 in Italia e l'efficacia dei vaccini utilizzando i dati rilasciati nei [**report settimanali**](https://www.epicentro.iss.it/coronavirus/aggiornamenti) dell'Istituto Superiore di Sanità, come ad esempio: 
<p align="center">
  <a href="https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_16-marzo-2022.pdf">Bollettino-sorveglianza-integrata-COVID-19_16-marzo-2022.pdf</a>
</p>

Per rimanere aggiornato sui risultati puoi dare una occhiata al nostro [**sito**](https://enricocid.github.io/monitoraggio-vaccini-italia/)!


## Installazione

Per utilizzare il repository, aprire la shell e digitare:

`git clone git@github.com:apalladi/covid_vaccini_monitoraggio.git` 

`cd covid_vaccini_monitoraggio`

E' consigliata la creazione di un environment virtuale, tramite i seguenti comandi:

`python -m venv .env`

`source .env/bin/activate`

Nell'environment virtuale è possibile installare automaticamente i pacchetti richiesti utilizzando il seguendo comando:

`pip install -r requirements.txt` 


## Utilizzo e spiegazione degli script

Lo script [**`dati/dati_selezione.py`**](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_selezione.py) estrae i dati per l'analisi a partire dal report selezionato. I dati epidemiologici e delle popolazioni di riferimento vengono salvati in [dati/dati_ISS_complessivi.xlsx](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_ISS_complessivi.xlsx) mentre quelli suddivisi per età in [dati/dati_ISS_età.xlsx](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_ISS_età.xlsx)[^1].

Lo script è stato aggiornato il [10/11/2021](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_10-novembre-2021.pdf) per includere i vaccinati con dose aggiuntiva.
Sono necessari ghostscript e tkinker per il corretto funzionamento di [camelot](https://camelot-py.readthedocs.io/en/master/user/install-deps.html).


I dati possono essere analizzati mediante i seguenti script:


- [**`scripts/andamento_epidemia.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/andamento_epidemia.py) calcola le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinati. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo è possibile calcolare i tassi standardizzati (aggiustati per fascia di età[^2]). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia.


- [**`scripts/andamento_rapporti_incidenze.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/andamento_rapporti_incidenze.py) calcola il contributo dei non vaccinati rispetto all’incidenza totale nelle varie fasce di età.


- [**`scripts/confronti_europei.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronti_europei.py) aggiorna gli andamenti delle curve epidemiologiche e delle vaccinazioni dei paesi dell’Eurozona.


- [**`scripts/confronto_2020_2021.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronto_2020_2021.py) restituisce gli andamenti delle curve epidemiche 2020 e 2021. Per il 2021 vengono mostrate separatamente le curve dei vaccinati e dei non vaccinati. 


- [**`scripts/efficacia_vaccini.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/efficacia_vaccini.py) calcola i tassi per ogni fascia di età e per stato vaccinale (vaccinati e non vaccinati) relativi all'ultimo report dell'ISS. Ciò permette di calcolare le incidenze per ogni fascia d'età e di valutare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso.


Per eseguire un aggiornamento generale, utilizzare il seguente comando dalla directory principale:

`./update_all.sh`


[^1]: Nota sulle popolazioni di riferimento: si considera un ritardo medio stimato di due settimane per ospedalizzazioni e ricoveri in TI e di tre settimane per i decessi.

[^2]: Si ottengono moltiplicando ciascun tasso specifico per classe di età - ossia il rapporto tra la numerosità dell’evento considerato e la popolazione di riferimento del report - per la numerosità della popolazione standard della stessa classe di età <sup>[fonte dati popolazione italiana](https://github.com/italia/covid19-opendata-vaccini/blob/master/dati/platea.csv)</sup>; sommando questi prodotti e dividendo tutto per il totale delle popolazioni standard (**over 12**) si ottiene il tasso di incidenza standardizzato.