#/usr/bin/python

import os
import shelve
import subprocess.check_call
import subprocess.check_output

from exception import *
import volume

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

    def __init__(self, name, volume, vol_list, options={}, shelf=None):
        """Create a new worker instance."""
        self.name = name
        self.volume = volume
        self.options = options
        self.shelf = shelf
        self.cid = None
        self.start(vol_list)

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

    def create(self, vol_list):
        """Create a new container for the worker.

        The only argument is the Volumes object to search in.
        """
        self.active = True
        if self.exists():
            print NOOP_CREATE, self.name
            return
        create = 'docker run -d'

        # Determine volume mount point
        volume = vol_list.get(self.volume)
        if volume:
            if volume.source = 'image':
                if not volume.running():
                    volume.start()
                create += ' --volumes-from ' + volume.cid
            elif volume.source = 'directory':
                if volume.exists():

        else:
            errstr = "Volume '" + self.volume + "' does not exist."
            raise BaseVolumeError(errstr)

        # Append options if they are specified
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
