#!/usr/bin/python3
from .core import Docker

__author__ = 'Ryan Clarke - faceless.saint@gmail.com'


class Image:
    """Images used to create a Container."""
    def __init__(self, name, tag=None, path=None):
        self.name = name
        self.tag = tag
        self.path = path
        self.get()

    @staticmethod
    def clean(force=False):
        """Remove all dangling images from docker."""
        for image in Docker.images(filters={'dangling': True}, quiet=True):
            Docker.remove_image(image=image, force=force)

    def list(self, quiet=False):
        """List all images under the repository.

        :param quiet: Whether to output a list of dicts or strings.
        """
        return Docker.images(name=self.name, quiet=quiet)

    def exists(self):
        """Return True if the image referenced by this object exists, False otherwise."""
        if not self.name:
            return False
        images = self.list()
        if images:
            if not self.tag:
                return True
            else:
                for i in images:
                    if next((True for t in i.get('RepoTags') if t == self.tag), False):
                        return True
                # next((True for i in images[0].get('RepoTags') if i == self.tag), False)
        return False

    def get(self, update=False):
        """Get the image from the repository, or build it if self.path is specified.

        Raise LookupError if the image cannot be built or pulled.

        :param update: Whether to pull/build even if the image already exists.
        """
        if self.exists() and not update:
            return
        elif self.path:
            if self.tag:
                build_tag = self.name + ':' + self.tag
            else:
                build_tag = self.name
            Docker.build(self.path, build_tag, quiet=True)
        else:
            Docker.pull(self.name, self.tag)
        if not self.exists():
            raise LookupError('Image could not be pulled or built.', self.name, self.tag, self.path)
