#!/usr/bin/python

import os.path
import shelve
import subprocess

from .exception import *

# Dictionary of valid docker run arguments and their types.
valid_args = {'--add-host': list,
              '--attach': list,
              '--blkio-weight': int,
              '--cap-add': list,
              '--cap-drop': list,
              '--cgroup-parent': str,
              '--cidfile': str,
              '--cpu-period': int,
              '--cpu-quota': int,
              '--cpu-shares': int,
              '--cpuset-cpus': str,
              '--cpuset-mems': str,
              '--device': list,
              '--dns': list,
              '--dns-search': list,
              '--entrypoint': str,
              '--env': list,
              '--env-file': list,
              '--expose': list,
              '--group-add': list,
              '--hostname': str,
              '--interactive': bool,
              '--ipc': str,
              '--label': list,
              '--label-file': list,
              '--link': list,
              '--log-driver': str,
              '--log-opt': list,
              '--lxc-conf': list,
              '--mac-address': str,
              '--memory': str,
              '--memory-swap': str,
              '--memory-swappiness': str,
              '--name': str,
              '--net': str,
              '--oom-kill-disable': bool,
              '--pid': str,
              '--port': str,
              '--privileged': bool,
              '--read-only': bool,
              '--restart': str,
              '--security-opt': list,
              '--sig-proxy': bool,
              '--tty': bool,
              '--user': str,
              '--ulimit': list,
              '--disable-content-trust': bool,
              '--uts': str,
              '--volume': str,
              '--workdir': str}


def docker_call(command):
    """Call docker cli to run command.

    Raises subprocess.CalledProcess
    """
    call_str = 'docker ' + command
    try:
        output = subprocess.check_output(call_str)
    except subprocess.CalledProcessError as e:
        raise NotImplementedError('Docker command failed!', str(e))
    else:
        return output
    finally:
        return None


def docker_exists():
    """Check if docker commands can be executed."""
    command = 'docker help'
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


class Containers({}):
    """Collection of Container instances with"""
    def __init__(self, shelf, item_type=Container):
        """Create new Containers collection instance."""
        if not docker_exists():
            raise NotImplementedError('Docker commands are not available!')
        super(Containers, self).__init__()
        self.item_type = type(item_type)
        self.shelf = str(shelf)
        self.load_all()

    def load_all(self, shelf=None):
        """Try to load all Container instances from the shelf."""
        if shelf is None:
            shelf = self.shelf

        with shelve.open(str(shelf)) as s:
            for key in s.keys():
                try:
                    obj = s[key]
                except KeyError:
                    pass
                else:
                    # Only load shelved objects of the correct type.
                    if type(obj) == self.item_type:
                        self.setdefault(key, obj)

    def load(self, name, shelf=None):
        """Try to load a Container instance from the shelf."""
        if shelf is None:
            shelf = self.shelf

        with shelve.open(str(shelf)) as s:
            try:
                obj = s[str(name)]
            except KeyError:
                pass
            else:
                # Only load shelved objects of the correct type.
                if type(obj) == self.item_type:
                    self.setdefault(str(name), obj)

    def create(self, name, image, command='', args=None, path=None, containers=None):
        """Create a new Container instance.

        Raises a ContainerDuplicateError if the Container was already in the list.
        """
        if not self.get(str(name)) is None:
            raise ContainerDuplicateError(args=name)
        else:
            self.setdefault(str(name), Container(name, image, command, args, path, containers, self.shelf))

    def delete(self, name):
        """Delete the Container from the list and remove it from the shelf.

        Raises a ContainerMissingError if the Container wasn't in the list.
        """
        if self.get(str(name)) is None:
            raise ContainerMissingError(args=name)
        else:
            with shelve.open(self.get(str(name)).shelf) as s:
                try:
                    del s[self.get(str(name)).name]
                except KeyError:
                    pass
            del self[str(name)]


class Container:
    """Base Container class for specifying docker-based structures in Python.

    'name' is a unique name for the Container (required).
    'image' is the source image for the docker container (required).
    'command' is the command to execute in the docker container.
    'args' is a dict containing parameters to be passed to the docker runtime.
    'path' is the build directory for the image.
    'shelf' is the filename of the shelf to use for persistent storage.
    """
    def __init__(self, name, image, command='', args=None, path=None, containers=None, shelf=None):
        """Initialize a new Container object.

        Raises:
            ImageError on image verification failure.
            PathMissingError if shelf is defined but doesn't exist.
        """
        self.name = str(name)
        self.image = str(image)
        self.command = str(command)
        self.args = dict(args)
        self.path = path
        self.shelf = str(shelf)
        self.cid = None
        try:
            self.check_image()
        except ImageError as e:
            print(e)
            raise
        if self.shelf and not os.path.isfile(self.shelf):
            raise PathMissingError(args=self.shelf)
        self.create(containers=containers)

    def __del__(self):
        """Save data to shelf to ensure persistence."""
        self.sync()

    def sync(self):
        """Sync Container data to shelf file, if shelf is defined.

        Raises IOError on shelf access failure.
        """
        if self.shelf is None:
            return
        with shelve.open(self.shelf) as s:
            s[self.name] = self

    def remove(self):
        """"Remove container data from shelf file, if shelf is defined.

        Raises IOError on shelf access failure.
        """
        if self.shelf is None:
            return
        with shelve.open(self.shelf) as s:
            del s[self.name]

    def image_exists(self):
        """Check if the source image for the Container exists.

        Raises subprocess.CalledProcessError on docker cli failure.
        """
        if not self.image:
            return False
        call_str = "images -q " + str(self.image)
        if docker_call(call_str):
            return True
        else:
            return False

    def container_exists(self):
        """Check if the docker Container exists.

        Raises subprocess.CalledProcessError on docker cli failure.
        """
        if not self.cid:
            return False
        call_str = "ps -aq --filter id=" + str(self.cid)
        try:
            if docker_call(call_str):
                return True
            else:
                return False
        except NotImplementedError as e:
            print(e)
            return False

    def container_running(self):
        """Check if the docker container is running.

        Raises subprocess.CalledProcessError on docker cli failure.
        """
        if not self.cid:
            return False
        call_str = "ps -q --filter id= " + str(self.cid)
        try:
            if docker_call(call_str):
                return True
            else:
                return False
        except NotImplementedError as e:
            print(e)
            return False

    def check_image(self):
        """Check the validity of the container's base image.

        Raises:
            ImageUndefinedError for an unspecified image.
            ImageMissingError for an image that does not exist.
            subprocess.CalledProcessError on docker cli failure.
        """
        if self.image is None:
            raise ImageUndefinedError(args=self.image)
        else:
            try:
                if not self.image_exists():
                    raise ImageMissingError(args=self.image)
            except subprocess.CalledProcessError:
                raise

    def create(self, command=None, containers=None):
        """Create a new docker container for this object.

        Items in self.args are added to the command:
            <key>:<value> becomes:  <key> + ' ' + <value> + ' '

        Some arguments are treated specially:
            '--port':<value>  becomes:  '-p ' + <value> + ' '
                unless <value>==Auto, then it becomes:  '-P '

            '--volume':<value> becomes: '--volumes-from ' + <cid> + ' '
                if containers is defined:
                    Fetch <cid> for the container with name <value>,
                    attempting to start it if necessary.
                else:
                    Assume that <value> == <cid>.

        Raises ContainerCreateError if the operation fails.
        """
        if self.container_exists():
            return
        try:
            self.check_image()
        except ImageError as e:
            print(e)
            raise ContainerCreateError(args=self)
        if command is None:
            command = 'run -d '
            for key in self.args.keys():
                if key == '--port':
                    port = self.args.get(key)
                    if port == 'Auto' or port == 'auto':
                        command += '-P '
                    else:
                        command += '-p ' + port + ' '
                elif key == '--volume':
                    volume = self.args.get(key)
                    if containers is None:
                        command += '--volumes-from ' + volume + ' '
                    elif containers.get(volume):
                        containers.get(volume).start()
                        command += '--volumes-from ' + containers.get(volume).cid + ' '
                    else:
                        raise ContainerMissingError(args=volume)
                elif valid_args.get(key):
                    command += key + ' ' + self.args.get(key) + ' '
            command += self.image + ' ' + self.command
        try:
            self.cid = docker_call(command)
        except NotImplementedError as e:
            self.cid = None
            print(e)
            raise ContainerCreateError(args=self)
        else:
            self.sync()

    def delete(self):
        """Delete the docker container for this object.

        Raises ContainerDeleteError if the operation fails.
        """
        if not self.container_exists():
            return
        if self.container_running():
            self.stop()

        command = 'rm ' + str(self.cid)
        try:
            docker_call(command)
        except NotImplementedError as e:
            print(e)
            raise ContainerDeleteError(args=self)
        else:
            self.cid = None
            self.sync()

    def start(self):
        """Start the docker.

        Raises ContainerStartError if the operation fails.
        """
        if not self.container_exists():
            try:
                self.create()
            except ContainerCreateError as e:
                print(e)
                raise ContainerStartError(args=self)
        if self.container_running():
            return

        command = 'start ' + str(self.cid)
        try:
            docker_call(command)
        except NotImplementedError as e:
            print(e)
            raise ContainerStartError(args=self)

    def stop(self):
        """Stop the docker container.

        Raises ContainerStopError if the operation fails.
        """
        if not self.container_running():
            return

        command = 'stop ' + str(self.cid)
        try:
            docker_call(command)
        except NotImplementedError as e:
            print(e)
            raise ContainerStopError(args=self)

    def restart(self):
        self.stop()
        self.start()
