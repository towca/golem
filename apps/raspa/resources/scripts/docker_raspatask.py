from __future__ import print_function

import imp
import os
from shutil import copyfile


import params  # This module is generated before this script is run

def run():
    code_file = os.path.join(params.RESOURCES_DIR, "code", "computing.py")
    computing = imp.load_source("code", code_file)

    src = os.path.join(params.RESOURCES_DIR, "data", "simulation.input")
    dst = os.path.join(params.OUTPUT_DIR, "simulation.input")
    copyfile(src, dst)

    os.chdir(params.OUTPUT_DIR)
    computing.run_raspa_task(dst)

run()
