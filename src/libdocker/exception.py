#!/usr/bin/python


# Exceptions related to image processing.
class ImageError(Exception):
    pass


class ImageUndefinedError(ImageError):
    def __init__(self, message="Image is not defined.", args=None):
        super(message, args)


class ImageMissingError(ImageError):
    def __init__(self, message="Image does not exist.", args=None):
        super(message, args)


class ImageInvalidError(ImageError):
    def __init__(self, message="Image is not valid.", args=None):
        super(message, args)


class ImagePullError(ImageError):
    def __init__(self, message="Image failed to pull.", args=None):
        super(message, args)


class ImageBuildError(ImageError):
    def __init__(self, message="Image failed to build.", args=None):
        super(message, args)


# --- BEGIN CONTAINER-RELATED EXCEPTIONS --- #

class ContainerError(ValueError):
    pass


class ContainerDuplicateError(ContainerError):
    def __init__(self, **args):
        self.message = "Container already exists."
        super(ContainerDuplicateError, self).__init__(self.message, **args)


class ContainerMissingError(ContainerError):
    def __init__(self, **args):
        self.message = "Container does not exist."
        super(ContainerMissingError, self).__init__(self.message, **args)


class ContainerCreateError(ContainerError):
    def __init__(self, message="Container cannot be created.", args=None):
        super(message, args)


class ContainerDeleteError(ContainerError):
    def __init__(self, message="Container cannot be deleted.", args=None):
        super(message, args)


class ContainerStartError(ContainerError):
    def __init__(self, message="Container cannot be started.", args=None):
        super(message, args)


class ContainerStopError(ContainerError):
    def __init__(self, message="Container cannot be stopped.", args=None):
        super(message, args)


class ContainerBackupError(ContainerError):
    def __init__(self, message="Container backup failed.", args=None):
        super(message, args)


class ContainerCommandError(ContainerError):
    def __init__(self, message="Container command call failed.", args=None):
        super(message, args)


# Exceptions related to file and directory processing.
class PathError(Exception):
    pass


class PathUndefinedError(PathError):
    def __init__(self, message="Path is not defined.", args=None):
        super(message, args)


class PathMissingError(PathError):
    def __init__(self, message="Path does not exist.", args=None):
        super(message, args)
