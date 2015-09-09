#!/usr/bin/python3
from .core import Docker
from .image import Image
from .container import Container
from .comb import Comb

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Worker(Container):
    """Container for running a managed Minecraft server."""
    label = 'hivemined.worker'
    image = Image('hivemined/worker', path='/usr/local/src/worker/')

    def __init__(self, name, comb, java_args='', data=True, **kwargs):
        if data:
            data_name = str(name) + '-data'
            self.data = Worker(data_name, comb=Comb(None, None, mock=True), entrypoint='true', data=False)
        else:
            self.data = None
        volume_list = self.set_comb(comb, init=True)
        super().__init__(name, image=type(self).image, volumes=volume_list, command=java_args, **kwargs)

    def delete(self, volumes=True):
        """Delete the Worker container.

        :param volumes: Whether to delete the data container as well
        """
        super().delete(volumes)
        if volumes:
            Docker.remove_container(self.data.container['Id'], v=True)

    def command(self, command, tty=False):
        """Send a command to the Minecraft server.

        :param command: The command to send
        """
        exec_str = 'cmd ' + str(command)
        super().command(exec_str)

    def set_comb(self, comb, init=False):
        """Set the Comb container for the Worker to use.

        :param comb: The Comb instance to use
        """
        if not comb.exists():
            comb.create()

        if init:
            if self.data:
                return [self.data, comb]
            else:
                return [comb]
        else:
            if self.data:
                self.volumes = [self.data, comb]
            else:
                self.volumes = [comb]
