#!/bin/bash

# first update the data
python dati/dati_selezione.py

# then update the results
python scripts/andamento_epidemia.py
python scripts/andamento_rapporti_incidenze.py
python scripts/efficacia_vaccini.py
python scripts/confronto_2020_2021.py
python scripts/confronti_internazionali.py