#!/usr/bin/python


# Exceptions related to image processing.
class ImageError(Exception):
    pass
class ImageUndefinedError(ImageError):
    __init__(self, message="Image is not defined.", args=None):
        super(message, args)
class ImageMissingError(ImageError):
    __init__(self, message="Image does not exist.", args=None):
        super(message, args)
class ImageInvalidError(ImageError):
    __init__(self, message="Image is not valid.", args=None):
        super(message, args)
class ImagePullError(ImageError):
    __init__(self, message="Image failed to pull.", args=None):
        super(message, args)
class ImageBuildError(ImageError):
    __init__(self, message="Image failed to build.", args=None):
        super(message, args)


# Exceptions related to container processing.
class ContainerError(Exception):
    pass
class ContainerMissingError(ContainerError):
    __init__(self, message="Container does not exist.", args=None):
        super(message, args)
class ContainerCreateError(ContainerError):
    __init__(self, message="Container cannot be created.", args=None):
        super(message, args)
class ContainerDeleteError(ContainerError):
    __init__(self, message="Container cannot be deleted.", args=None):
        super(message, args)
class ContainerStartError(ContainerError):
    __init__(self, message="Container cannot be started.", args=None):
        super(message, args)
class ContainerStopError(ContainerError):
    __init__(self, message="Container cannot be stopped.", args=None):
        super(message, args)
class ContainerBackupError(ContainerError):
    __init__(self, message="Container backup failed.", args=None):
        super(message, args)
class ContainerCommandError(ContainerError):
    __init__(self, message="Container command call failed.", args=None):
        super(message, args)


# Exceptions related to path processing.
class PathError(Exception):
    pass
class PathUndefinedError(PathError):
    __init__(self, message="Path is not defined.", args=None):
        super(message, args)
class PathMissingError(PathError):
    __init__(self, message="Path does not exist.", args=None):
        super(message, args)
