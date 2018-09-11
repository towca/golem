from os import path

from golem.core.common import get_golem_path
from golem.docker.environment import DockerEnvironment


class PDFgenTaskEnvironment(DockerEnvironment):
    DOCKER_IMAGE = "golemfactory/pdfgen"
    DOCKER_TAG = "1.2"
    ENV_ID = "PDFgen"
    APP_DIR = path.join(get_golem_path(), 'apps', 'pdfgen')
    SCRIPT_NAME = "docker_pdfgentask.py"
    SHORT_DESCRIPTION = "PDFgen task"
