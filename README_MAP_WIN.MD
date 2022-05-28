Per la corretta generazione della mappa installare i seguenti pacchetti nell'ordine indicato:
- GDAL (ultima versione, wheel)
- shapely (ultima versione, wheel)
- fiona (ultima versione, wheel)
- rtree (ultima versione, wheel)
- rasterio (ultima versione, wheel)
- pyproj (ultima versione, wheel)
- GeoPandas (ultima versione, pip o wheel)
- PySAL (scaricare: PySAL‑1.14.4.post2‑py3‑none‑any.whl)
- mapclassify (ultima versione, pip)
- basemap (ultima versione, wheel)

Le wheels sono scaricabili dal sito di Christopher Gohlk: 
[Python Wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

Esempio installazione GDAL, Python 37, Win64:
scaricare l'ultima versione della wheel dal sito indicato ed eseguire il seguente comando:
`pip install GDAL‑3.4.2‑cp37‑cp37m‑win_amd64.whl`