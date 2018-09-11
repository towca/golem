from os import path

from golem.core.common import get_golem_path
from golem.docker.environment import DockerEnvironment


class RaspaTaskEnvironment(DockerEnvironment):
    DOCKER_IMAGE = "golemfactory/raspa"
    DOCKER_TAG = "1.2"
    ENV_ID = "Raspa"
    APP_DIR = path.join(get_golem_path(), 'apps', 'raspa')
    SCRIPT_NAME = "docker_raspatask.py"
    SHORT_DESCRIPTION = "Raspa task"
