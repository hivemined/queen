#!/usr/bin/python3
from .core import Docker
from .container import Container

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Comb(Container):
    """Container for storing server binaries and default configuration."""
    label = 'Hivemined-Comb'

    def __init__(self, name, image):
        super().__init__(name, image, command='true')

    @staticmethod
    def validate_image(image):
        """Verify that specified image is a valid Comb."""
        image_data = Docker.inspect_image(image)

        # Checks on image data
        return image_data
