#!/usr/bin/python3
from .image import Image
from .container import Container

from subprocess import check_call
from subprocess import CalledProcessError

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'

# docker run -it --privileged -v /var/run/docker.sock:/var/run/docker.sock \
#   --volumes-from $(docker create --name hivemined-data -v /var/hivemined/ --label hivemined.data scratch true) \
#   --name hivemined-queen hivemined/queen


class Queen(Container):
    """Container for managing Hivemined."""
    label = 'hivemined.queen'
    image = Image('hivemined/queen')

    def __init__(self):
        super().__init__(None, type(self).image)

    def exists(self, running=False):
        return True

    def create(self, force=False, **kwargs):
        self.container = {'Id': self.list(quiet=True)[0]}

    def delete(self, volumes=True):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def start(self, tty=False):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def restart(self):
        raise NotImplementedError

    def command(self, command, tty=False):
        raise NotImplementedError
