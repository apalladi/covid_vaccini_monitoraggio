# -*- coding: utf-8 -*-
import subprocess
from glob import glob
from os import chdir, path


def run_script(script_path):
    '''run_notebook(str)

    script_path: script path
    return: None'''
    print(f"\nRunning {script_path} ...")
    subprocess.call(script_path, shell=True)


# Set work directory for the script
scriptpath = path.dirname(path.realpath(__file__))
chdir(scriptpath)

# Finally, update notebooks/results
scripts = glob("*.py")
scripts.remove("update_results.py")
print(scripts)

for script in scripts:
    run_script(script)
