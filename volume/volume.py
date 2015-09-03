#/usr/bin/python

import os
import shelve
import subprocess.check_call
import subprocess.check_output

from exception import *

class Volumes:
        """Collection of Volume instances.

    Fetches Volume definitions from persistence files in shelf_dir.
    """
    # Method status output strings
    PASS_SYNC = "[INFO]: Volume intialized from file."
    FAIL_SYNC = "[ERR]:  Cannot open persistence file!"

    def __init__(self, shelf_dir='/var/hivemined/volumes.d/'):
        """Create new Volumes collection instance."""
        self.shelf_dir = shelf_dir
        self.volumes = []

        # Populate workers collection from shelves
        for filename in os.listdir(self.shelf_dir):
            if filename.endswith('.shelf'):
                shelf = self.shelf_dir + filename
                try:
                    with shelve.open(shelf) as s:
                        try:
                            volume = s['volume']
                        except KeyError as e:
                            print FAIL_SYNC, e
                        else:
                            self.volumes.append(volume)
                            print PASS_SYNC, volume.name
                except IOError as e:
                    print FAIL_SYNC, e

    def __del__(self):
        """Ensure proper cleanup of volume objects."""
        for volume in self.volumes:
            del volume

    def _shelf_file(self, name):
        """Get filename for named volumes's shelf from pattern."""
        return self.shelf_dir + name + '.shelf'

    def get(self, name):
        """Return the volume with the given name."""
        return next((v for v in volumes if v.name == name), None)

    def create(self, name, path=None, image=None):
        """Create a new volume with the given properties"""
        if self.get(name):
            print "Error: volume already exists with that name!"
            return
        if not path and not image:
            print "Error: either path or image must be specified!"
            return
        shelf = _self.shelf_file(name)
        new_volume = Volume(name, path, image, shelf)
        self.volumes.append(new_volume)


class Volume:
    """Volume for mounting server runtimes and modpacks.

    One of path or image must be speficied for proper operation.
    """
    mnt_point = '/mnt/minecraft'

    # Method status output strings
    FAIL_SYNC = "[ERR]:  Cannot open persistence file!"
    FAIL_LIST = "[ERR]:  Cannot fetch container list!"
    FAIL_LIST_IMAGE = "[ERR]:  Cannot fetch image list!"

    PASS_PULL = "[INFO]: Image pulled."
    NOOP_PULL = "[WARN]: No image speficied to pull."
    FAIL_PULL = "[ERR]:  Image pull failed!"

    PASS_BUILD = "[INFO]: Image built."
    NOOP_BUILD = "[WARN]: No image specified to build."
    FAIL_BUILD = "[ERR]:  Image build failed!"

    PASS_CREATE = "[INFO]: Container created."
    NOOP_CREATE = "[WARN]: Container already exists."
    FAIL_CREATE = "[ERR]:  Container creation failed!"

    PASS_DELETE = "[INFO]: Container deleted."
    NOOP_DELETE = "[WARN]: Container does not exist."
    FAIL_DELETE = "[ERR]:  Container deletion failed!"

    def __init__(self, name, path=None, image=None, shelf=None):
        self.name = name
        self.cid = None
        self.path = path
        self.image = image
        self.shelf = shelf
        if image:
            self.source = 'image'
            if not self.exists():
                try:
                    self.pull()
                except VolumeImageError as pull_error:
                    if self._dir_exists():
                        try:
                            self.build()
                        except: BaseVolumeError as build_error
                            print pull_error, build_error
                            raise
                    else:
                        print pull_error
                        raise

            self.create()
        elif path:
            self.source = 'directory'
            if not self.exists():
                errstr = "Volume path not valid."
                raise VolumePathError(errstr, self.name)
            self.sync()
        else
            self.source = None

    def __del__(self):
        """Save volume data to shelf for persistence."""
        self.sync()

    def sync(self):
        """Sync volume data to shelf, if shelf is defined.

        Raises IOError on shelf access failure.
        """
        if not self.shelf:
            return
        try:
            with shelve.open(self.shelf) as s:
                s['volume'] = self
        except IOError:
            raise

    def check_image(self):
        """Check the integrity of the specified image.

        Raises:
            VolumeImageUndefinedError for an unspecified image.
            VolumeImageMissingError for an image that does not exist.
            VolumeImageInvalidError for an image that is not a volume.
            CalledProcessError on docker cli failure.
        """
        if self.image == None:
            raise VolumeImageUndefinedError()
        else:
            if not self.image_exists():
                raise VolumeImageMissingError()
            else:
                check = "docker inspect --format {{.Config.Volumes}} "
                check += self.image
                try:
                    test = subprocess.check_output(check)
                except CalledProcessError as e:
                    raise
                else:
                    if not test == 'map[' + self.mnt_point + ':map[]]':
                        raise VolumeImageInvalidError()

    def check_path(self):
        """Check the integrity of the specified path.

        Raises:
            VolumePathUndefinedError for an unspecified path.
            VolumePathMissingError for a path that isn't a directory.
        """
        if self.path == None:
            raise VolumePathUndefinedError()
        else:
            if not os.path_isdir():
                raise VolumePathMissingError()
            else:
                return True

    def check_container(self):
        if not self.container_exists():
            raise VolumeContainerMissingError()

    def image_exists(self):
        """Check if the source image for the volume exists.

        Raises CalledProcessError on docker cli failure.
        """
        if self.image == None:
            return False
        check = "docker images -q " + self.image
        try:
            test = subprocess.check_output(check)
        except CalledProcessError as e:
            raise
        else:
            if test:
                return True
            else:
                return False

    def container_exists(self):
        """Check if the container for the volume exists.

        Raises CalledProcessError on docker cli failure.
        """
        if self.cid == None:
            return False
        check = "docker ps -aq --filter id=" + self.cid
        try:
            test = subprocess.check_output(check)
        except CalledProcessError as e:
            raise
        else:
            if test:
                return True
            else:
                return False

    def pull(self):
        """Attempt to pull down the image for the volume mount"""
        try:
            self.check_image()
        except VolumeImageError as e:
            raise
        else:
            pull = 'docker pull ' + self.image
            try:
                subprocess.check_call(pull)
            except CalledProcessError as e:
                raise VolumeImagePullError() from e

    def build(self):
        """Attempt to build a new image for the volume mount."""
        if not self.source == 'image':
            errstr = "No image speficied."
            raise VolumeImageError(errstr, self.name)

        if not os.path_isdir(self.path):
            errstr = "Path to volume source is invalid."
            raise VolumePathError(errstr, self.name)

        build = 'docker build -t ' + self.image + ' ' + self.path
        try:
            subprocess.check_call(build)
        except CalledProcessError as e:
            errstr = "Could not build '" + self.image + "'."
            raise VolumeImageError(errstr, self.path) from e
        else:
            if not self.exists():
                errstr = "The image is still missing."
                raise VolumeImageError(errstr, self.name)
            return True

    def destroy(self):
        """Delete the image for the volume mount."""
        if not self.source == 'image':
            errstr = "No image specified."
            raise VolumeImageError(errstr, self.name)

        if not self.exists():
            return

        destroy = 'docker rmi ' + self.image
        try:
            subprocess.check_call(destroy)
        except CalledProcessError as e:
            errstr = "Could not delete '" + self.image + "'."
            raise VolumeImageError(errstr, self.name) from e
        else:
            if self.exists():
                errstr = "The image still exists."
                raise VolumeImageError(errstr)

    def create(self):
        """Create a new container for the volume mount."""
        if not self.source == 'image':
            errstr = "No image specified."
            raise VolumeImageError(errstr, self.name)

        if self.running():
            print NOOP_CREATE, self.name
            return
        if not self.exists():
            try:
                self.pull()
            except VolumeImageError as pull_error:
                try:
                    self.build()
                except BaseVolumeError as build_error
                        print pull_error, build_error
                        raise

        create = 'docker create ' + this.image + ' true'
        try:
            self.cid = subprocess.check_output(create)
        except CalledProcessError as e:
            self.cid = None
            errstr = "Could not create container from image."
            raise VolumeImageError(errstr, self.name) from e
        else:
            if not self.running():
                errstr = "Container still not running."
                raise VolumeImageError(errstr, self.name)
        finally:
            self.sync()

    def delete(self):
        """Delete the container for the volume mount."""
        if not self.source == 'image':
            errstr = "No image specified."
            raise VolumeImageError(errstr, self.name)

        if not self.running():
            print NOOP_DELETE, self.name
            return
        delete = 'docker rm ' + self.cid
        try:
            subprocess.check_call(delete)
        except CalledProcessError as e:
            errstr = "Could not delete container."
            raise VolumeImageError(errstr, self.name)
        else:
            self.cid = None
            print PASS_DELETE, self.name
        finally:
            self.sync()

    def reset(self):
        """Reset container to image specification."""
        try:
            self.delete()
            self.create()
        except BaseVolumeError as e:
            print e
            raise

    def get_mount(self):
        """Return the volume mount option for this volume."""
        if self.vol_type = 'image' and self.validate():
            return ' --volumes-from ' + self.cid
        elif self.vol_type = 'directory' and self.validate():
            return ' -v ' + self.path + ':/mnt/minecraft'
        else
            return None
