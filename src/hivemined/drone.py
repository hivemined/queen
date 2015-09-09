#!/usr/bin/python3
from .image import Image
from .container import Container

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Drone(Container):
    """Container for performing utility functions."""
    label = 'hivemined.drone'
    image = Image('hivemined/drone', path='/usr/local/src/drone/')

    def __init__(self, queen, worker, command, backup_path=None, **kwargs):
        if command == 'backup':
            call = command
        elif command == 'restore':
            call = command + ' ' + backup_path
        else:
            raise ValueError('Invalid command.', command)

        volumes = [queen, worker]
        super().__init__(None, image=type(self).image, command=call, volumes=volumes, **kwargs)
        self.start()
