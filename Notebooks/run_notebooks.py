from glob import glob
from os import chdir, path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def run_notebook(nb_path):
    '''run_notebook(str)

    nb_path: notebook path
    return: None'''

    print(f'\nRunning {nb_path} ...')

    # open the notebook
    with open(nb_path, encoding='utf-8-sig') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    # execute the notebook
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb)

    # update the notebook
    with open(nb_path, 'w', encoding='utf-8-sig') as f:
        nbformat.write(nb, f)


# Set work directory for the script
scriptpath = path.dirname(path.realpath(__file__))
chdir(scriptpath)


# Finally, update notebooks/results
notebooks = glob('*.ipynb')
for nb in notebooks:
    run_notebook(nb)
