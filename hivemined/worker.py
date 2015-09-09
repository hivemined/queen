#!/usr/bin/python3
from .core import Docker
from .image import Image
from .container import Container

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Worker(Container):
    """Container for running a Minecraft server."""
    label = 'Hivemined-Worker'
    image = Image('hivemined/worker', path='/usr/local/src/worker/')

    def __init__(self, name, volume, java_args='', data=True, **kwargs):
        if data:
            data_name = name + '-data'
            self.data = Worker(data_name, volume=None, entrypoint='true', data=False)
        else:
            self.data = None
        super().__init__(name, image=type(self).image, volumes=self.set_volume(volume), command=java_args, **kwargs)

    def delete(self, volumes=True):
        super().delete(volumes)
        if volumes:
            Docker.remove_container(self.data.container['Id'], v=True)

    def command(self, command, tty=False):
        exec_str = 'cmd ' + command
        super().command(exec_str)

    def set_volume(self, volume):
        if self.data:
            return [self.data, volume]
        else:
            return [volume]

#    def reset(self):
#        """Recreate the Worker, reusing the previous data volumes."""
#        orig_container = self.container
#        self.create(force=True)
#        Docker.remove_container(orig_container['Id'])
