#!/usr/bin/python3
from .image import Image
from .container import Container

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Drone(Container):
    """Container for performing utility functions."""
    label = 'Hivemined-Drone'
    image = Image('hivemined/drone', path='/usr/local/src/drone/')

    def __init__(self, name, command, worker=None, **kwargs):
        super().__init__(name, image=type(self).image, command=command, volume=worker, **kwargs)
