Questo repository è stato creato con lo scopo di creare l'andamento dell'epidemia provocata dal Covid19 in Italia e l'efficacia dei vaccini.

Vengono utilizzati i dati rilasciati nei report settimanali dell'Istituto Superiore di Sanità, come ad esempio https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf.

Nel Notebook `andamento_epidemia.ipynb` vengono calcolate le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinate. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo è possibile calcolare le incidenze (o tassi). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia. 


Nel Notebook `efficacia_vaccini.ipynb` vengono calcolati i tassi di contagi relativi all'ultimo report dell'ISS, dividendo i dati in 4 fasce d'età e in 2 categorie (vaccinati e non vaccinati). Ciò permette di calcolare le incidenze per ogni fascia d'età e di calcolare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso. 
