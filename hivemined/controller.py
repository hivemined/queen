#!/usr/bin/python3
from .core import Docker
from .image import Image
from .container import Container
from .worker import Worker
from .drone import Drone
from .comb import Comb

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


def __main__():
    d = Docker
    d.version()

    i = Image(None)
    c = Container(None, i, '')
    c.start()

    comb = Comb(None, i)
    w = Worker(None, comb)
    w.start()

    d = Drone(None, '')
    d.start()
    pass
