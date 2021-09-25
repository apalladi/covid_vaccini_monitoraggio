Questo repository � stato creato con lo scopo di monitorare l'andamento dell'epidemia provocata dal Covid19 in Italia e l'efficacia dei vaccini.


Vengono utilizzati i dati rilasciati nei [report settimanali](https://www.epicentro.iss.it/coronavirus/aggiornamenti) dell'Istituto Superiore di Sanit�, come ad esempio: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf.


Nel Notebook `andamento_epidemia.ipynb` vengono calcolate le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinate. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo � possibile calcolare le incidenze (o tassi). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia. 


Nel Notebook `efficacia_vaccini.ipynb` vengono calcolati i tassi di contagi relativi all'ultimo report dell'ISS, dividendo i dati in 4 fasce d'et� e in 2 categorie (vaccinati e non vaccinati). Ci� permette di calcolare le incidenze per ogni fascia d'et� e di calcolare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso. 


Nel Notebook `confronto_2020_2021.ipynb` vengono confrontati gli andamenti delle curve epidemiche 2020 e 2021.


Nel Notebook [`\dati\dati_selezione.ipynb`](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_selezione.ipynb) vengono selezionati i dati per l'analisi a partire dal report e dal numero di pagina contenente la tabella (n.3). Requisiti: Python 3.6+, Java 8+ e tabula-py. 
