#!/bin/bash

# Workaround the following error
# fatal: unsafe repository ('/usr/src/myapp' is owned by someone else)
# https://github.com/actions/checkout/issues/760

git config --global --add safe.directory /usr/src/myapp

printf "\nExtracting data from ISS...\n"

python dati/dati_selezione.py

if [[ -z "$(git status --porcelain)" ]];
then
  printf "No changes to commit!\n"
else
  # Update the results
  printf "\nUpdating results...\n"
  python scripts/andamento_epidemia.py
  python scripts/andamento_rapporti_incidenze.py
  python scripts/efficacia_vaccini.py
  python scripts/confronto_2020_2021.py
  python scripts/confronti_europei.py

  printf "\nDONE!"
fi
