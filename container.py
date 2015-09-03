#!/usr/bin/python

import os
import shelve
import subsystem.check_call
import subsystem.check_output

from exception import *

def fetchContainer(shelf, name):
    """Retrieve the data for the named Container from the shelf.

    Returns:
        The Container object with the given name.
        or None if the Container cannot be found.
    Raises IOError on shelf access failure.
    """
    try:
        with shelve.open(shelf) as s:
            try:
                container = s[name]
            except KeyError:
                return None
            else:
                return container
    except IOError:
        raise

class Container:
    def __init__(self, name, image, shelf=None):
        """Initialize a new container object."""
        self.name = name
        self.image = image
        self.shelf = shelf
        self.active = True
        self.cid = None
        self.create()

    def __del__(self):
        """Save data to shelf to ensure persistence."""
        self.sync()

    def sync(self):
        """Sync container data to shelf file, if shelf is defined.

        Raises IOError on shelf access failure.
        """
        if self.shelf=None:
            return
        try:
            with shelve.open(self.shelf) as s:
                s[self.name] = self
        except IOError:
            raise

    def image_exists(self):
        """Check if the source image for the contianer exists.

        Raises CalledProcessError on docker cli failure.
        """
        if not self.image:
            return False
        check = "docker images -q " + self.image
        try:
            test = subprocess.check_output(check)
        except CalledProcessError:
            raise
        else:
            if test:
                return True
            else:
                return False

    def container_exists(self):
        """Check if the docker container exists.

        Raises CalledProcessError on docker cli failure.
        """
        if not self.cid:
            return False
        check = "docker ps -aq --filter id=" + self.cid
        try:
            test = subprocess.check_output(check)
        except CalledProcessError:
            raise
        else:
            if test:
                return True
            else:
                return False

    def container_running(self):
        """Check if the docker container is running.

        Raises CalledProcessError on docker cli failure.
        """
        if not self.cid:
            return False
        check = "docker ps -q --filter id=" + self.cid
        try:
            test = subprocess.check_output(check)
        except CalledProcessError:
            raise
        else:
            if test:
                return True
            else:
                return False

    def check_image(self):
        """Check the validity of the container's base image.

        Raises:
            ImageUndefinedError for an unspecified image.
            ImageMissingError for an image that does not exist.
            CalledProcessError on docker cli failure.
        """
        if self.image == None:
            raise ImageUndefinedError(args= self.image)
        else:
            try:
                if not self.image_exists():
                    raise ImageMissingError(args= self.image)
            except CalledProcessError:
                raise

    def create(self, command=None):
        """Create a new docker container for this object.

        Raises ContainerCreateError if the operation fails.
        """
        if self.container_exists():
            return
        try:
            check_image()
        except ImageError as e:
            raise ContainerCreateError(args= self) from e

        if command == None:
            command = 'docker run -d ' + self.image
        try:
            self.cid = subprocess.check_output(command)
        except CalledProcessError as e:
            self.cid = None
            raise ContainerCreateError(args= self) from e
        finally:
            self.sync()

    def delete(self, command=None):
        """Delete the docker container for this object.

        Raises ContainerDeleteError if the operation fails.
        """
        if not self.container_exists():
            return
        if self.container_running():
            self.stop()

        if command == None:
            command = 'docker rm ' + self.cid
        try:
            subprocess.check_call(command)
        except CalledProcessError as e:
            raise ContainerDeleteError(args= self) from e
        else:
            self.cid = None
        finally:
            self.sync()

    def start(self):
        """Start the docker.

        Raises ContainerStartError if the operation fails.
        """
        return

    def stop(self):
        """Stop the docker container.

        Raises ContainerStopError if the operation fails.
        """
        return

    def restart(self):
        self.start()
        self.stop()

class Worker(Container):

    def create(self):
        """Create a new container for the worker.

        The only argument is the Volumes object to search in.
        """
        self.active = True
        create = 'docker run -d --volumes-from ' + self.volume
        if 'port' in self.options:
            create += ' -p ' + self.options['port'] + ':25565'
        else:
            create += ' -P'
        if 'restart' in self.options:
            create += ' --restart ' + self.options['restart']
        if 'memory' in self.options:
            create += ' --memory ' + self.options['memory']
        if 'memory_swap' in self.options:
            create += ' --memory-swap ' + self.options['memory_swap']
        if 'blkio_weight' in self.options:
            create += ' --blkio-weight ' + self.options['blkio_weight']
        if 'cpu_shares' in self.options:
            create += ' --cpu-shares ' + self.options['cpu_shares']
        create += ' ' + self.image

        # Finally, append any specified java arguments
        if 'java_args' in self.options:
            create += ' ' + self.options['java_args']
        super(Worker, self).create(create)

    def delete(self):
        """Delete the container for the worker."""
        self.active = False
        super(Worker, self).delete()

    def start(self):
        """Start the container for the worker."""
        self.active = True
        if self.running():
            print NOOP_START, self.name
            return
        if not self.exists():
            self.create()
        start = 'docker start ' + self.cid
        try:
            subprocess.check_call(start)
        except CalledProcessError as e:
            print FAIL_START, e
        else:
            if not self.running():
                print FAIL_START, self.name
            else:
                print PASS_START, self.name
        finally:
            self.sync()


    def stop(self):
        """Stop the container for the worker."""
        self.active = False
        if not self.running():
            print NOOP_STOP, self.name
            return
        stop = 'docker stop ' + self.cid
        try:
            subprocess.check_call(stop)
        except CalledProcessError as e:
            print FAIL_STOP, e
        else:
            if self.running()
            print PASS_STOP, self.name
        finally:
            self.sync()

    def restart(self):
        """If worker is active then restart, otherwise stop."""
        if self.exists():
            if self.active:
                if self.running():
                    self.stop()
                self.start()
            else:
                if self.running():
                    self.stop()

    def backup(self):
        """Run worker backup procedure"""
        return False

    def command(self, command):
        """Execute a command inside the worker container."""
        if not self.running():
            print NOOP_COMMAND, self.name, command
            return
        cmd = 'docker exec ' + self.cid + ' cmd ' + str(command)
        try:
            output = subprocess.check_output(cmd)
        except CalledProcessError as e:
            print FAIL_COMMAND, e
        else:
            print output
            print PASS_COMMAND, self.name, command





class Volume:




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
