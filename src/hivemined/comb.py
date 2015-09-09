#!/usr/bin/python3
from .core import Docker
from .container import Container

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Comb(Container):
    """Container for storing server binaries and default configuration."""
    label = 'hivemined.comb'

    def __init__(self, name, image, mock=False):
        if not mock:
            if not Comb.validate(image):
                raise ValueError('Invalid source image', image)
            super().__init__(name, image, command='true')

    @staticmethod
    def validate(image):
        """Verify that image is a valid base image for COmb.

        :param image: The image to validate
        """
        image_data = Docker.inspect_image(image)

        # Checks on image data
        if image_data:
            return True
        else:
            return False
