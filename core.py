import docker
import docker.utils

__author__ = 'Ryan Clarke'


def connect(url='unix://var/run/docker.sock', tls=None):
    global DockerClient
    DockerClient = docker.Client(base_url=url, version='auto', tls=tls)

connect()


class Image:
    """Images used to create a Container."""
    def __init__(self, name, tag=None, path=None):
        self.name = name
        self.tag = tag
        self.path = path

    @staticmethod
    def clean(force=False):
        """Remove all dangling images from docker."""
        for image in DockerClient.images(filters={'dangling': True}, quiet=True):
            DockerClient.remove_image(image=image, force=force)

    def list(self, quiet=False):
        """List all images under the repository."""
        return DockerClient.images(name=self.name, quiet=quiet)

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
            DockerClient.build(self.path, build_tag, quiet=True)
        else:
            DockerClient.pull(self.name, self.tag)
        if not self.exists():
            raise LookupError('Image could not be pulled or built.', self.name, self.tag, self.path)


class Container:
    """Base Container Class for docker containers managed by hivemined."""
    label = 'Hivemined'

    def __init__(self, name, image, command='', volumes=list(), port=None, memory=None, swap=None, cpu=None, **kwargs):
        self.name = name
        self.image = image
        self.command = command
        self.volumes = volumes
        self.port = port
        self.limits = {
            'Memory': memory,
            'Swap': swap,
            'Cpu': cpu
        }
        self.restart = {
            'Name': 'always',       # 'always' | 'on-failure' | 'no'
            'MaximumRetryCount': 0
        }
        self.container = None
        self.create(**kwargs)

    def list(self, show_all=False, quiet=False):
        """List all containers manages by the calling class (respects inheritance)."""
        return DockerClient.containers(all=show_all, quiet=quiet, filters={'label': 'Managed=' + type(self).label})

    def exists(self, running=False):
        """Return True if the container referenced by this object exists, or False otherwise.

        If running==True, check if the container is running instead.
        """
        containers = self.list(show_all=(not running))
        if next((c for c in containers if c['Id'] == self.container['Id']), None):
            return True
        else:
            return False

    def create(self, force=False, **kwargs):
        """Create a new managed docker container.

        If force==True, create new a container even if one already exists.
        """
        labels = {'Managed': type(self).label, 'Name': self.name}
        if self.exists() and not force:
            return
        self.image.get()    # Ensure that the specified Image exists.

        volume_list = []
        for v in self.volumes:
            volume_list.append(v.container["Id"])

        if self.port is None:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, port_bindings={25565: self.port})
        else:
            host_cfg = docker.utils.create_host_config(
                volumes_from=volume_list, restart_policy=self.restart, publish_all_ports=True)

        self.container = DockerClient.create_container(
            host_config=host_cfg, labels=labels, image=self.image.name, command=self.command,
            mem_limit=self.limits.get('memory'), memswap_limit=self.limits.get('swap'),
            cpu_shares=self.limits.get('cpu'), **kwargs)

        if self.container['Warnings']:
            raise Warning("Container creation includes warnings.", self.container)

    def delete(self, volumes=True):
        if self.exists(running=True):
            self.stop()
        DockerClient.remove_container(self.container['Id'], v=volumes)

    def start(self, tty=False):
        if not self.exists():
            self.create()
        DockerClient.start(self.container['Id'], tty=tty)

    def stop(self):
        DockerClient.stop(self.container['Id'])

    def restart(self):
        DockerClient.restart(self.container['Id'])

    def exec(self, command, tty=False):
        exec_str = DockerClient.exec_create(self.container['Id'], cmd=command, tty=tty)
        DockerClient.exec_start(exec_str, tty=tty)


class Worker(Container):
    """Container for running a Minecraft server."""
    label = 'Hivemined-Worker'
    image = Image('hivemined/worker', path='/usr/local/src/worker/')

    def __init__(self, name, volume, java_args='', data=True, **kwargs):
        if data:
            data_name = name + '-data'
            self.data = Worker(data_name, volume=None, entrypoint='true', data=False)
        else:
            self.data = None
        super().__init__(name, image=type(self).image, volumes=self.set_volume(volume), command=java_args, **kwargs)

    def delete(self, volumes=True):
        super().delete(volumes)
        if volumes:
            DockerClient.remove_container(self.data.container['Id'], v=True)

    def command(self, command, tty):
        cmd = 'cmd ' + command
        self.exec(cmd, tty)

    def set_volume(self, volume):
        if self.data:
            return [self.data, volume]
        else:
            return [volume]

    def reset(self):
        """Recreate the Worker, reusing the previous data volumes."""
        orig_container = self.container
        self.create(force=True)
        DockerClient.remove_container(orig_container['Id'])


class Drone(Container):
    """Container for performing utility functions."""
    label = 'Hivemined-Drone'
    image = Image('hivemined/drone', path='/usr/local/src/drone/')

    def __init__(self, name, command, worker=None, **kwargs):
        super().__init__(name, image=type(self).image, command=command, volume=worker, **kwargs)


class Comb(Container):
    """Container for storing server binaries and default configuration."""
    label = 'Hivemined-Comb'

    def __init__(self, name, image):
        super().__init__(name, image, command='true')

    @staticmethod
    def validate_image(image):
        """Verify that specified image is a valid Comb."""
        image_data = DockerClient.inspect_image(image)

        # Checks on image data
        return image_data
