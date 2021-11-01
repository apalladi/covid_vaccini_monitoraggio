#!/bin/bash

if [[ -z "$(git status --porcelain)" ]];
then
  echo "No changes to commit!"
else
  # Update the results
  echo "Updating results..."
  python scripts/andamento_epidemia.py
  python scripts/andamento_rapporti_incidenze.py
  python scripts/efficacia_vaccini.py
  python scripts/confronto_2020_2021.py
  python scripts/confronti_europei.py
fi