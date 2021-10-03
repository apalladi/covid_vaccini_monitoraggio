from glob import glob
from os import chdir, path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def run_notebook(nb_path):
    '''run_notebook(str)

    nb_path: notebook path
    return: None'''

    print(f"\nRunning {nb_path} ...")

    # open the notebook
    with open(nb_path, encoding="utf-8") as fp:
        nb = nbformat.read(fp, as_version=4)

    # execute the notebook
    abs_path = path.dirname(path.realpath(nb_path))
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": abs_path}})

    # update the notebook
    with open(nb_path, "w", encoding="utf-8") as fp:
        nbformat.write(nb, fp)


# Set work directory for the script
scriptpath = path.dirname(path.realpath(__file__))
chdir(scriptpath)

# Finally, update notebooks/results
notebooks = glob("*.ipynb")
for nb in notebooks:
    run_notebook(nb)
