#!/usr/bin/python

import subprocess.check_call
import subprocess.check_output
import shelve
import os


class Worker:
    """Managed hivemined worker instance.

    The worker must have both a name and a volume to use in order to
    function.  The optional 'options' dictionary contains additional
    parameters for modifying the behavior of the worker at runtime.
    The worker also saves its state data into a shelf file if one is
    provided for it, allowing for object persistence.
    """
    image = 'hivmeined/worker'

    # Method status output strings
    FAIL_SYNC = "[ERR]:  Cannot open persistence file!"
    FAIL_LIST = "[ERR]:  Cannot fetch container list!"

    PASS_CREATE = "[INFO]: Container created."
    NOOP_CREATE = "[WARN]: Container already exists."
    FAIL_CREATE = "[ERR]:  Container creation failed!"

    PASS_DELETE = "[INFO]: Container deleted."
    NOOP_DELETE = "[WARN]: Container does not exist."
    FAIL_DELETE = "[ERR]:  Container deletion failed!"

    PASS_START = "[INFO]: Container started."
    NOOP_START = "[WARN]: Container is already running."
    FAIL_START = "[ERR]:  Container cannot be started!"

    PASS_STOP = "[INFO]: Container stopped."
    NOOP_STOP = "[WARN]: Container is not running."
    FAIL_STOP = "[ERR]:  Container cannot be stoped!"

    PASS_BACKUP = "[INFO]: Backup completed."
    NOOP_BACKUP = "[INFO]: Backups already up to date."
    FAIL_BACKUP = "[ERR]:  Backup failed!"

    PASS_COMMAND = "[INFO]: Command executed."
    NOOP_COMMAND = "[WARN]: Worker not running, ignoring command."
    FAIL_COMMAND = "[ERR]:  Command failed!"

    def __init__(self, volume, options={}, shelf=None):
        """Create a new worker instance."""
        self.name = name
        self.volume = volume
        self.options = options
        self.shelf = shelf
        self.cid = None
        self.start()

    def __del__(self):
        """Save worker data to shelf for persistence."""
        self.sync()

    def sync(self):
        """Sync worker data to shelf, if shelf is present."""
        if not self.shelf:
            return
        try:
            with shelve.open(self.shelf) as s:
                s['worker'] = self
        except IOError as e:
            print FAIL_SYNC, e

    def exists(self):
        """Check if the container for the worker exists."""
        if not self.cid:
            return False
        list_all = 'docker ps -aq --filter id=' + self.cid
        try:
            test = subprocess.check_output(list_all)
        except CalledProcessError as e:
            print FAIL_LIST, e
            return False
        else:
            if len(test) > 2:
                return True
            else:
                return False

    def running(self):
        """Check if the container for the worker is running."""
        if not self.cid:
            return False
        list_running = 'docker ps -q --filter id=' + self.cid
        try:
            test = subprocess.check_output(list_running)
        except CalledProcessError as e:
            print FAIL_LIST, e
            return False
        else:
            if len(test) > 2:
                return True
            else:
                return False

    def create(self):
        """Create a new container for the worker."""
        self.active = True
        if self.exists():
            print NOOP_CREATE, self.name
            return
        create = 'docker run -d'
        if self.volume.source == 'image':
            if not self.volume.running():
                self.volume.create()
                if not self.volume.running():
                    print FAIL_CREATE, "Bad volume.", self.volume.name
                    return
            create += ' --volumes-from ' + self.volume.cid
        elif self.volume.source == 'directory':
            if not self.volume.exists():
                print FAIL_CREATE, "Bad volume.", self.volume.name
            create += ' -v ' + self.volume.path + ':/mnt/minecraft'
        else:
            print FAIL_CREATE, "Bad volume!", self.volume.name
            return
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
        if 'java_args' in self.options:
            create += ' ' + self.options['java_args']
        try:
            self.cid = subprocess.check_output(create)
        except CalledProcessError as e:
            self.cid = None
            print FAIL_CREATE, e
        else:
            if not self.exists():
                print FAIL_CREATE, self.name
            else:
                print PASS_CREATE, self.name
        finally:
            self.sync()

    def delete(self):
        """Delete the container for the worker."""
        self.active = False
        if not self.exists():
            print NOOP_DELETE, self.name
            return
        if self.running():
            self.stop()
        delete = 'docker rm ' + self.cid
        try:
            subprocess.check_call(delete)
        except CalledProcessError as e:
            print FAIL_DELETE, e
        else:
            if self.exists():
                print FAIL_DELETE, self.name
            else:
                self.cid = None
                print PASS_DELETE, self.name
        finally:
            self.sync()

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


class Workers:
    """Collection of Worker instances.

    Fetches Worker definitions from persistence files in shelf_dir.
    """
    # Method status output strings
    PASS_SYNC = "[INFO]: Worker intialized from file."
    FAIL_SYNC = "[ERR]:  Cannot open persistence file!"

    __init__(self, shelf_dir = '/var/hivemined/workers.d/'):
        """Create new Workers collection instance."""
        self.shelf_dir = shelf_dir
        self.workers = []

        # Populate workers collection from shelves
        for filename in os.listdir(self.shelf_dir):
            if filename.endswith('.shelf'):
                shelf = self.shelf_dir + filename
                try:
                    with shelve.open(shelf) as s:
                        try:
                            worker = s['worker']
                        except KeyError as e:
                            print FAIL_SYNC, e
                        else:
                            self.workers.append(worker)
                            print PASS_SYNC, worker.name
                except IOError as e:
                    print FAIL_SYNC, e

    __del__(self):
        """Ensure proper cleanup of worker objects."""
        for worker in self.workers:
            del worker

    def _shelf_file(self, name):
        """Get filename for named worker's shelf from pattern."""
        return self.shelf_dir + name + '.shelf'

    def get(self, name):
        """Return the worker with the given name."""
        return next((w for w in workers if w.name == name), None)

    def create(self, name, volume, options={}):
        """Create a new worker with the given properties"""
        if self.get(name):
            print "Error: worker already exists with that name!"
            return
        shelf = _self.shelf_file(name)
        new_worker = Worker(name, volume, options, shelf)
        self.workers.append(new_worker)


class BaseVolumeError(Exception):
    """Base Exception for volume-related errors."""
    pass
class VolumePathError(BaseVolumeError):
    """Raised when the path given is not valid."""
    pass
class VolumeImageError(BaseVolumeError):
    """Raised when the image given is not valid."""
    pass

class Volume:
    """Volume for mounting server runtimes and modpacks.

    One of path or image must be speficied for proper operation.
    """
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
            self.create()
        elif path:
            self.source = 'directory'
            self.sync()
        else
            self.source = None

    def __del__(self):
        """Save volume data to shelf for persistence."""
        self.sync()

    def sync(self):
        """Sync volume data to shelf, if shelf is present."""
        if not self.shelf:
            return
        try:
            with shelve.open(self.shelf) as s:
                s['volume'] = self
        except IOError as e:
            print FAIL_SYNC, e

    def exists(self):
        """Check if the source for the volume exists."""
        if self.source == 'directory':
            return self._dir_exists()
        elif self.source == 'image':
            return self._img_exists()
        else:
            return False

    def _dir_exists(self)
        """Check whether the directory for the volume exists."""
        if os.path_isdir(self.path):
            return True
        else:
            return False

    def _img_exists(self)
        """Check whether the image for the volume exists."""
        if not self.cid:
            return False
        list_all = 'docker images -q ' + self.image
        try:
            test = subprocess.check_output(list_all)
        except CalledProcessError as e:
            print FAIL_LIST_IMAGE, e
            return False
        else:
            if len(test) > 2:
                return True
            else:
                return False

    def running(self):
        """Check if the container for the volume exists."""
        if not self.source == 'container' ot not self.cid:
            return False
        list_all = 'docker ps -aq --filter id=' + self.cid
        try:
            test = subprocess.check_output(list_all)
        except CalledProcessError as e:
            print FAIL_LIST, e
            return False
        else:
            if len(test) > 2:
                return True
            else:
                return False

    def pull(self):
        """Attempt to pull down the image for the volume mount"""
        if not self.source == 'image':
            errstr = "No image speficied."
            raise VolumeImageError(errstr, self.name)

        pull = 'docker pull ' + self.image
        try:
            subprocess.check_call(pull)
        except CalledProcessError as e:
            errstr = "Could not find '" + self.image + "' remotely."
            raise VolumeImageError(errstr) from e
        else:
            if not self.exists():
                errstr = "The image is still missing."
                raise VolumeImageError(errstr, self.name)
            return True

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
