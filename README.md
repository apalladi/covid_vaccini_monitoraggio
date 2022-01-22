# Monitoraggio vaccini Italia

[![Sito web](https://img.shields.io/website?up_color=brightgreen&up_message=online&url=https%3A%2F%2Fenricocid.github.io%2Fmonitoraggio-vaccini-italia%2F)](https://enricocid.github.io/monitoraggio-vaccini-italia/)

Questo repository è stato creato allo scopo di monitorare l'andamento dell'epidemia provocata dal virus Sars-Cov-2 in Italia e l'efficacia dei vaccini utilizzando i dati rilasciati nei [**report settimanali**](https://www.epicentro.iss.it/coronavirus/aggiornamenti) dell'Istituto Superiore di Sanità, come ad esempio: 
<p align="center">
  <a href="https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_19-gennaio-2022.pdf">Bollettino-sorveglianza-integrata-COVID-19_19-gennaio-2022.pdf</a>
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

Lo script [**`dati/dati_selezione.py`**](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_selezione.py) estrae i dati per l'analisi a partire dal report selezionato. I dati vengono salvati in [dati/dati_ISS_complessivi.xlsx](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_ISS_complessivi.xlsx). I dati suddivisi per età vengono salvati in [dati/data_iss_età_YY-MM-D.xlsx](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/data_iss_età_2021-11-10.xlsx).

Lo script è stato aggiornato il [10/11/2021](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_10-novembre-2021.pdf) per includere i vaccinati con dose aggiuntiva.
Sono necessari ghostscript e tkinker per il corretto funzionamento di [camelot](https://camelot-py.readthedocs.io/en/master/user/install-deps.html).


I dati possono essere analizzati mediante i seguenti script:


- [**`scripts/andamento_epidemia.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/andamento_epidemia.py) calcola le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinati. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo è possibile calcolare le incidenze (o tassi). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia. 


- [**`scripts/andamento_rapporti_incidenze.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/andamento_rapporti_incidenze.py) calcola il contributo dei non vaccinati rispetto all’incidenza totale nelle varie fasce di età.


- [**`scripts/confronti_europei.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronti_europei.py) aggiorna gli andamenti delle curve epidemiologiche e delle vaccinazioni dei paesi dell’Eurozona.


- [**`scripts/confronto_2020_2021.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronto_2020_2021.py) restituisce gli andamenti delle curve epidemiche 2020 e 2021. Per il 2021 vengono mostrate separatamente le curve dei vaccinati e dei non vaccinati. 


- [**`scripts/efficacia_vaccini.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/efficacia_vaccini.py) calcola i tassi di contagio relativi all'ultimo report dell'ISS, dividendo i dati in 4 fasce d'età e in 2 categorie (vaccinati e non vaccinati). Ciò permette di calcolare le incidenze per ogni fascia d'età e di valutare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso. 


Per eseguire un aggiornamento generale, utilizzare il seguente comando dalla directory principale:

`./update_all.sh`
