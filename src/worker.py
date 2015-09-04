#!/usr/bin/python

import os.path
import shelve
import subprocess

from .libdocker.exception import *
from .libdocker.container import *


class Workers(Containers):
    """Collection of Worker instances."""
    def_worker_shelf = '/var/hivemined/workers.shelf'
    def_volume_shelf = '/var/hivemined/volumes.shelf'

    def __init__(self, shelf=None, volumes=None):
        if shelf is None:
            shelf = Workers.def_worker_shelf
        if volumes is None:
            self.volumes = Containers(Workers.def_volume_shelf)
        super(Workers, self).__init__(shelf, Worker)

    def create(self, name, image=Worker.def_worker_image, command='', args=None):
        """Create a new Container instance.

        Raises a ContainerDuplicateError if the Container was already in the list.
        """
#        del path, containers
        if not self.get(str(name)) is None:
            raise ContainerDuplicateError(args=name)
        else:
            self[str(name)] = Worker(name, image, command, args, self.volumes, self.shelf)


class Worker(Container):
    """Managed hivemined worker instance."""
    def_worker_image = 'hivemined/worker'

    def __init__(self, name, image=Worker.def_worker_image, command='', args=None, volumes=None, shelf=None):
        self.active = True
        super(Worker, self).__init__(name, image, command, args, None, volumes, shelf)

    def create(self, *args):
        """Create a new container for the worker."""
        self.active = True
        super(Worker, self).create(*args)

    def delete(self):
        """Delete the container for the worker."""
        self.active = False
        super(Worker, self).delete()

    def start(self):
        """Start the container for the worker."""
        self.active = True
        super(Worker, self).start()

    def restart(self):
        """If worker is active then restart, otherwise stop."""
        if self.active:
            super(Worker, self).restart()
        else:
            self.stop()

    def backup(self):
        """Run worker backup procedure."""
        return self.name

    def restore(self):
        """Restore worker from backup."""
        return self.name

    def command(self, command, interactive=False):
        """Execute a command inside the worker container."""
        if not self.container_running():
            return
        if interactive:
            cmd_str = 'exec -it' + str(self.cid) + ' cmd ' + str(command)
        else:
            cmd_str = 'exec ' + str(self.cid) + ' cmd ' + str(command)
        try:
            docker_call(cmd_str)
        except NotImplementedError as e:
            print(e)
            raise ContainerCommandError(args=command)
