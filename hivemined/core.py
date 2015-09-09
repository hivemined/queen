#!/usr/bin/python3
import docker
import docker.utils

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'

Docker = docker.Client(base_url='unix://var/run/docker.sock', version='auto')


def connect(url='unix://var/run/docker.sock', **kwargs):
    """Connect to specified docker client."""
    global Docker
    Docker = docker.Client(base_url=url, **kwargs)
