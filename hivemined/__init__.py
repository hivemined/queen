#!/usr/bin/python3
from .core import Docker
from .image import Image
from .container import Container
from .worker import Worker
from .drone import Drone
from .comb import Comb

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


def __main__():
    """Hivemined library test suite"""
    pass

"""
Worker usage:
    worker = Worker(name, volume, **kwargs)     Instantiate a new Worker and create the corresponding Docker container.
    worker.create()                             Create a new Docker container for the Worker (called by init).
    worker.delete()                             Delete the Docker container for the Worker.
    worker.exists()                             Return True if the container for the Worker exists, else False.
    worker.exists(running=True)                 Return True if the container for the Worker is running, else False.
    worker.[start|stop|restart]                 Start|Stop|Restart the worker container.
    worker.command(command)                     Send the specified command to the Worker's java server.
    worker.set_volume(volume)                   Specify volume as the runtime source for the Worker's Docker container.

Drone usage:
    [TODO]

worker list
       create <name> <comb> [java_args] [docker_args]
       <name> delete
       <name> start
       <name> stop
       <name> restart
       <name> command <command>
       <name> set_volume <comb>

drone backup <worker>
      restore <worker> <backup>

comb list
     create <name> <tag> [path]
     <name> delete
     <name> update
"""