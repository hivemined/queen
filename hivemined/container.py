#!/usr/bin/python3
import docker
import docker.utils

from .core import Docker

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Container:
    """Base Container Class for docker containers managed by hivemined."""
    label = 'Hivemined'

    def __init__(self, name, image, command='', volumes=list(), port=None, memory=None, swap=None, cpu=None, **kwargs):
        self.name = name
        self.image = image
        self.command = command
        self.volumes = volumes
        self.port = port
        self.limits = {
            'Memory': memory,
            'Swap': swap,
            'Cpu': cpu
        }
        self.restart = {
            'Name': 'always',       # 'always' | 'on-failure' | 'no'
            'MaximumRetryCount': 0
        }
        self.container = None
        self.create(**kwargs)

    def list(self, show_all=False, quiet=False):
        """List all containers manages by the calling class (respects inheritance)."""
        return Docker.containers(all=show_all, quiet=quiet, filters={'label': 'Managed=' + type(self).label})

    def exists(self, running=False):
        """Return True if the container referenced by this object exists, or False otherwise.

        If running==True, check if the container is running instead.
        """
        containers = self.list(show_all=(not running))
        if next((c for c in containers if c['Id'] == self.container['Id']), None):
            return True
        else:
            return False

    def create(self, force=False, **kwargs):
        """Create a new managed docker container.

        If force==True, create new a container even if one already exists.
        """
        labels = {'Managed': type(self).label, 'Name': self.name}
        if self.exists() and not force:
            return
        self.image.get()    # Ensure that the specified Image exists.

        volume_list = []
        for v in self.volumes:
            volume_list.append(v.container["Id"])

        if self.port is None:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, port_bindings={25565: self.port})
        else:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, publish_all_ports=True)

        self.container = Docker.create_container(
            host_config=host_cfg, labels=labels, image=self.image.name, command=self.command,
            mem_limit=self.limits.get('memory'), memswap_limit=self.limits.get('swap'),
            cpu_shares=self.limits.get('cpu'), **kwargs)

        if self.container['Warnings']:
            raise Warning("Container creation includes warnings.", self.container)

    def delete(self, volumes=True):
        if self.exists(running=True):
            self.stop()
        Docker.remove_container(self.container['Id'], v=volumes)

    def start(self, tty=False):
        if not self.exists():
            self.create()
        Docker.start(self.container['Id'], tty=tty)

    def stop(self):
        Docker.stop(self.container['Id'])

    def restart(self):
        Docker.restart(self.container['Id'])

    def command(self, command, tty=False):
        exec_str = Docker.exec_create(self.container['Id'], cmd=command, tty=tty)
        Docker.exec_start(exec_str, tty=tty)
