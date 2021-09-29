Questo repository è stato creato con lo scopo di monitorare l'andamento dell'epidemia provocata dal Covid19 in Italia e l'efficacia dei vaccini.

### Installazione

Per utilizzare il repository, aprire la shell e digitare:

`git clone git@github.com:apalladi/covid_vaccini_monitoraggio.git` 

`cd covid_vaccini_monitoraggio`

È consigliata la creazione di un environment virtuale, tramite i seguenti comandi:

`python -m venv .env`

`source .env/bin/activate`

Nell'environment virtuale è possibile installare automaticamente i pacchetti richiesti (`numpy`, `matplotlib` e `pandas`) utilizzando il seguendo comando:

`pip install -r requirements.txt` 


### Utilizzo

Nel repository vengono utilizzati i dati rilasciati nei [report settimanali](https://www.epicentro.iss.it/coronavirus/aggiornamenti) dell'Istituto Superiore di Sanità, come ad esempio: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf.


Nel Notebook `Notebooks/andamento_epidemia.ipynb` vengono calcolate le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinate. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo è possibile calcolare le incidenze (o tassi). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia. 


Nel Notebook `Notebooks/efficacia_vaccini.ipynb` vengono calcolati i tassi di contagi relativi all'ultimo report dell'ISS, dividendo i dati in 4 fasce d'età  e in 2 categorie (vaccinati e non vaccinati). Ciò permette di calcolare le incidenze per ogni fascia d'età  e di calcolare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso. 


Nel Notebook `Notebooks/confronto_2020_2021.ipynb` vengono confrontati gli andamenti delle curve epidemiche 2020 e 2021. Per il 2021 vengono mostrate separatamente le curve dei vaccinati e dei non vaccinati. 


Nello script [`dati\dati_selezione.py`](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_selezione.py) vengono selezionati i dati per l'analisi a partire dal report e dal numero di pagina contenente la tabella (n.3). Requisiti: Python 3.6+, Java 8+ e tabula-py. 


### Risultati
<details>
  <summary>Andamento epidemia: incidenze settimanali (rapporto n° evento/popolazione riferimento)</summary>
    <p align="center">
      <img width="750" src="/risultati/andamento_epidemia.png">
    </p>
  </summary>
</details>
<details>
  <summary>Andamento epidemia: rapporto fra le incidenze</summary>
    <p align="center">
      <img width="750" src="/risultati/rapporto_tra_tassi.png">
    </p>
  </summary>
</details>
<details>
  <summary>Andamento epidemia: numeri assoluti giornalieri</summary>
    <p align="center">
      <img width="750" src="/risultati/andamento_epidemia_num_assoluti.png">
    </p>
  </summary>
</details>
<details>
  <summary>Incidenze settimanali ed efficacia vaccini per fascia di età</summary>
    <p align="center">
      <img width="750" src="/risultati/tassi_efficacia.png">
    </p>
  </summary>
</details>
<details>
  <summary>Efficacia vaccini: focus over 60</summary>
    <p align="center">
      <img width="750" src="/risultati/focus_over60.png">
    </p>
  </summary>
</details>
<details>
  <summary>Confronto curve epidemiche 2020 e 2021</summary>
    <p align="center">
      <img width="750" src="/risultati/confrontro_2020_2021.png">
    </p>
  </summary>
</details>
