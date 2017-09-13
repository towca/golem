import logging
import rlp
from golem.core.simpleserializer import CBORSedes
from docker.errors import NotFound, APIError

from .client import local_client

log = logging.getLogger(__name__)


class DockerImage(rlp.Serializable):
    fields = [
        ('repository', CBORSedes),
        ('image_id', CBORSedes),
        ('tag', CBORSedes)
    ]

    def __init__(self, repository=None, image_id=None, tag=None):
        self.id = image_id
        tag = tag if tag else "latest"
        rlp.Serializable.__init__(self, repository, image_id, tag)

        self.name = "{}:{}".format(self.repository, self.tag)

    def cmp_name_and_tag(self, docker_image):
        return docker_image.name == self.name and docker_image.tag == self.tag

    def __repr__(self):
        return "DockerImage(repository=%r, image_id=%r, tag=%r)" % (self.repository, self.image_id, self.tag)

    def is_available(self):
        client = local_client()
        try:
            if self.id:
                info = client.inspect_image(self.id)
                return self.name in info["RepoTags"]
            else:
                info = client.inspect_image(self.name)
                return self.id is None or info["Id"] == self.id
        except NotFound:
            log.debug('DockerImage NotFound', exc_info=True)
            return False
        except APIError:
            log.debug('DockerImage APIError', exc_info=True)
            if self.tag is not None:
                return False
            raise
        except ValueError:
            log.debug('DockerImage ValueError', exc_info=True)
            return False
