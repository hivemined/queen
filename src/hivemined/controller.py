#!/usr/bin/python3
from .image import Image
from .queen import Queen
from .worker import Worker
from .drone import Drone
from .comb import Comb

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Controller:

    def __init__(self, workers=None, combs=None, queen=None):
        if not workers:
            workers = {}
        if not combs:
            combs = {}
        if not queen:
            queen = Queen()

        self.workers = workers
        self.combs = combs
        self.queen = queen

    def comb_create(self, name, image, tag=None, path=None):
        if self.combs.get(name):
            raise LookupError('Comb already exists!', name)

        image_dat = Image(image, tag, path)
        comb = Comb(name, image_dat)
        self.combs[name] = comb
        return comb

    def comb_delete(self, name):
        comb = self.combs.get(name)
        if not comb:
            raise LookupError('Comb not found!', name)

        comb.delete()
        del self.combs[name]

    def comb_update(self, name):
        comb = self.combs.get(name)
        if not comb:
            raise LookupError('Comb not found!', name)

        comb.update()

    def worker_create(self, name, comb, java_args='', data=True, **kwargs):
        if self.workers.get(name):
            raise LookupError('Worker already exists!', name)

        if self.combs.get(comb):
            comb_dat = self.combs.get(comb)
        else:
            comb_dat = Comb(comb, Image(comb))
            self.combs[comb] = comb_dat

        worker = Worker(name, comb_dat, java_args, data, **kwargs)
        self.workers[name] = worker
        return worker

    def worker_delete(self, name):
        worker = self.workers.get(name)
        if not worker:
            raise LookupError('Worker not found!', name)

        worker.delete()
        del self.workers[name]

    def worker_update(self, name):
        worker = self.workers.get(name)
        if not worker:
            raise LookupError('Worker not found!', name)

        worker.update()

    def worker_op(self, op, name, command=""):
        worker = self.workers.get(name)
        if not worker:
            raise LookupError('Worker not found!', name)

        if op == 'start':
            worker.start()

        elif op == 'stop':
            worker.stop()

        elif op == 'restart':
            worker.restart()

        elif op == 'command':
            worker.command(command)

        elif op == 'debug':
            worker.super().command(command='/bin/bash -l', tty=True)

        else:
            pass

    def worker_backup(self, name):
        worker = self.workers.get(name)
        if not worker:
            raise LookupError('Worker not found!', name)

        Drone(self.queen, worker, 'backup')

    def worker_restore(self, name, backup):
        worker = self.workers.get(name)
        if not worker:
            raise LookupError('Worker not found!', name)

        Drone(self.queen, worker, 'restore', backup)
