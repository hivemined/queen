#!/usr/bin/python3
from .core import Docker

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Image:
    """Images used to create a Container."""
    def __init__(self, name, tag=None, path=None):
        self.name = name
        self.tag = tag
        self.path = path

    @staticmethod
    def clean(force=False):
        """Remove all dangling images from docker."""
        for image in Docker.images(filters={'dangling': True}, quiet=True):
            Docker.remove_image(image=image, force=force)

    def list(self, quiet=False):
        """List all images under the repository."""
        return Docker.images(name=self.name, quiet=quiet)

    def exists(self):
        """Return True if the image referenced by this object exists, False otherwise."""
        if not self.name:
            return False
        images = self.list()
        if images and not self.tag:
            return True
        elif next((i for i in images[0].get('RepoTags') if i == self.tag), None):
            return True
        else:
            return False

    def get(self):
        """Get the image from the repository, or build it if self.path is specified."""
        if not self.name:
            raise ValueError('Invalid name parameter.', self.name)
        if self.exists():
            return
        elif self.path:
            build_tag = self.name + ':' + self.tag
            Docker.build(self.path, build_tag, quiet=True)
        else:
            Docker.pull(self.name, self.tag)
        if not self.exists():
            raise LookupError('Image could not be pulled or built.', self.name, self.tag, self.path)
