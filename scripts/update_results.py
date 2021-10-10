# -*- coding: utf-8 -*-
import subprocess
import sys
from glob import glob
from os import chdir, path


def run_script(script_path):
    '''run_notebook(str)

    script_path: script path
    return: None'''
    print(f"\nRunning {script_path} ...")
    subprocess.call(script_path, shell=True)


if __name__ == "__main__":
    # Set work directory for the script
    scriptpath = path.dirname(path.realpath(__file__))
    chdir(scriptpath)

    # Finally, update results
    scripts = glob("*.py")
    scripts.remove(path.basename(sys.argv[0]))

    for script in scripts:
        run_script(script)
