from __future__ import print_function

import imp
import os
from shutil import copyfile

import params  # This module is generated before this script is run

def run(content, output_name):
    code_file = os.path.join(params.RESOURCES_DIR, "code", "computing.py")
    computing = imp.load_source("code", code_file)
    os.chdir(params.OUTPUT_DIR)
    computing.run_pdfgen_task(content, output_name)

run(params.content, params.output_name)
