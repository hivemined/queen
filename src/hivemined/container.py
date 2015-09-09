#!/usr/bin/python3
import docker
import docker.utils

from .core import Docker
from .image import Image

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Container:
    """Base Container class for docker containers managed by Hivemined."""
    label = 'hivemined.container'

    def __init__(self, name, image, command='', volumes=list(), port=None, memory=None, swap=None, cpu=None, **kwargs):
        self.name = str(name)
        self.command = str(command)

        # Type checking for image
        if isinstance(image, Image):
            self.image = image
        else:
            raise TypeError('Parameter must be an Image', image)

        # Type checking for volumes
        if next((False for v in volumes if not isinstance(v, Container)), True):
            self.volumes = volumes
        else:
            raise TypeError('Parameter must be a list of Containers.', volumes)

        # Set network port and resource limits
        self.port = port
        self.limits = {}
        if memory:
            self.limits['Memory'] = str(memory)
        if swap:
            self.limits['Swap'] = str(swap)
        if cpu:
            self.limits['Cpu'] = int(cpu)

        self.restart = {
            'Name': 'always',       # 'always' | 'on-failure' | 'no'
            'MaximumRetryCount': 0
        }
        self.container = None
        self.create(**kwargs)

    def list(self, show_all=False, quiet=False):
        """List all containers manages by the calling class (respects inheritance)."""
        return Docker.containers(all=show_all, quiet=quiet, filters={'label': type(self).label})

    def exists(self, running=False):
        """Return True if the container referenced by this object exists, or False otherwise.

        If running==True, check if the container is running instead.
        """
        if not self.container.get('Id'):
            return False
        containers = self.list(show_all=(not running))
        return next((True for c in containers if c.get('Id') == self.container.get('Id')), False)

    def create(self, force=False, **kwargs):
        """Create a new managed docker container.

        If force==True, create new a container even if one already exists.
        Propagates LookupError from self.image.get() f the image does not exist and cannot be pulled or built,
        Raises Warning if container creation resulted in warnings form Docker.
        """
        labels = {type(self).label: None, 'name': self.name}
        if self.exists() and not force:
            return

        try:
            self.image.get()    # Ensure that the specified Image exists.
        except LookupError as e:
            print(e)
            raise

        volume_list = []
        for v in self.volumes:
            volume_list.append(v.container.get("Id"))

        if self.port:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, port_bindings={25565: int(self.port)})
        else:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, publish_all_ports=True)

        self.container = Docker.create_container(
            host_config=host_cfg, labels=labels, image=self.image.name, command=self.command,
            mem_limit=self.limits.get('memory'), memswap_limit=self.limits.get('swap'),
            cpu_shares=self.limits.get('cpu'), **kwargs)

        if self.container.get('Warnings'):
            raise Warning("Container creation warning.", self)

    def delete(self, volumes=True):
        if self.exists(running=True):
            self.stop()
        Docker.remove_container(self.container.get('Id'), v=volumes)

    def update(self):
        self.image.get(update=True)
        old_container = self.container
        self.create(force=True)
        Docker.remove_container(old_container.get('Id'))

    def start(self, tty=False):
        if not self.exists():
            self.create()
        Docker.start(self.container.get('Id'), tty=tty)

    def stop(self):
        Docker.stop(self.container.get('Id'))

    def restart(self):
        Docker.restart(self.container.get('Id'))

    def command(self, command, tty=False):
        exec_str = Docker.exec_create(self.container.get('Id'), cmd=command, tty=tty)
        Docker.exec_start(exec_str, tty=tty)
