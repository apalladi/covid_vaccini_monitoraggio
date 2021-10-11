# covid_vaccini_monitoraggio


Questo repository è stato creato con lo scopo di monitorare l'andamento dell'epidemia provocata dal Covid19 in Italia e l'efficacia dei vaccini.

[![Licenza: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](#dettagli-licenza)

- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Risultati](#risultati)
- [Licenza](#dettagli-licenza)


## Installazione

Per utilizzare il repository, aprire la shell e digitare:

`git clone git@github.com:apalladi/covid_vaccini_monitoraggio.git` 

`cd covid_vaccini_monitoraggio`

E' consigliata la creazione di un environment virtuale, tramite i seguenti comandi:

`python -m venv .env`

`source .env/bin/activate`

Nell'environment virtuale è possibile installare automaticamente i pacchetti richiesti utilizzando il seguendo comando:

`pip install -r requirements.txt` 


## Utilizzo

Nel repository vengono utilizzati i dati rilasciati nei [report settimanali](https://www.epicentro.iss.it/coronavirus/aggiornamenti) dell'Istituto Superiore di Sanità, come ad esempio: https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_8-settembre-2021.pdf.


Lo script [`dati\dati_selezione.py`](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/dati/dati_selezione.py) estrae i dati per l'analisi (tabella n.3) a partire dal report selezionato.


I dati possono essere analizzati mediante i seguenti script:

- [**`scripts/andamento_epidemia.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/andamento_epidemia.py) calcola le curve epidemiche relative a nuovi casi, ospedalizzati, ricoverati in terapia intensiva e deceduti, divise per vaccinati e non vaccinati. Le curve epidemiche sono rapportate al numero di vaccinati e non vaccinati, in ogni intervallo temporale. In questo modo è possibile calcolare le incidenze (o tassi). Data la sproporzione tra il numero di vaccinati e non vaccinati, i numeri assoluti risultano infatti poco utili per monitare l'andamento dell'epidemia. 


- [**`scripts/efficacia_vaccini.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/efficacia_vaccini.py) calcola i tassi di contagio relativi all'ultimo report dell'ISS, dividendo i dati in 4 fasce d'età e in 2 categorie (vaccinati e non vaccinati). Ciò permette di calcolare le incidenze per ogni fascia d'età e di valutare correttamente l'efficacia dei vaccini nel prevenire il contagio, l'ospedalizzazione, il ricovero in terapia intensiva e il decesso. 


- [**`scripts/confronto_2020_2021.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronto_2020_2021.py) restituisce gli andamenti delle curve epidemiche 2020 e 2021. Per il 2021 vengono mostrate separatamente le curve dei vaccinati e dei non vaccinati. 


- [**`scripts/confronti_internazionali.py`**:](https://github.com/apalladi/covid_vaccini_monitoraggio/blob/main/scripts/confronti_internazionali.py) aggiorna gli andamenti delle curve epidemiologiche e delle vaccinazioni di vari Paesi esteri. 

Per fare un aggiornamento generale, utilizzare il comando
`./update_all.sh`
dalla directory principale

## Risultati

<details>
  <summary>Andamento epidemia: incidenze settimanali (rapporto eventi/popolazione riferimento)</summary>
  <p align="center"><img width="750" src="/risultati/andamento_epidemia.png"></p>
</details>

<details>
  <summary>Andamento epidemia: rapporto fra le incidenze</summary>
  <p align="center"><img width="750" src="/risultati/rapporto_tra_tassi.png"></p>
</details>

<details>
  <summary>Andamento epidemia: numeri assoluti giornalieri</summary>
  <p align="center"><img width="750" src="/risultati/andamento_epidemia_num_assoluti.png"></p>
</details>

<details>
  <summary>Incidenze settimanali ed efficacia vaccini per fascia di età</summary>
  <p align="center"><img width="750" src="/risultati/tassi_efficacia.png"></p>
</details>

<details>
  <summary>Efficacia vaccini: focus over 60</summary>
  <p align="center"><img width="750" src="/risultati/focus_over60.png"></p>
</details>

<details>
  <summary>Confronto curve epidemiche 2020 e 2021</summary>
  <p align="center"><img width="750" src="/risultati/confrontro_2020_2021.png"></p>
</details>

<details>
  <summary>Confronti internazionali</summary>
    <details>
      <summary>Confronto incidenza contagi tra Bulgaria, Romania e Portogallo</summary>
      <p align="center"><img width="750" src="/risultati/confronto_nazioni_epidemia-vaccino.png"></p>
    </details>
</details>

___


### Dettagli licenza

Questo repository è licenziato in base ai termini della licenza Creative Commons Attribuzione - Condividi allo stesso modo 4.0  (CC-BY-SA 4.0).

[:it:](https://creativecommons.org/licenses/by/4.0/deed.it) - [:gb:](https://creativecommons.org/licenses/by/4.0/)
<pre>
<b>Permessi</b>                 <b>Condizioni</b>
- Condividere            - Attribuzione (menzione di paternità adeguata)
- Modificare             - Divieto restrizioni aggiuntive    
</pre>
