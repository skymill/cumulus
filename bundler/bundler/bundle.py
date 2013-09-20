""" Bundling functions """
import os
import tarfile
from datetime import datetime

from logger import logger


class Bundle:
    """ Bundle object """
    base_path = str()
    target_path = str()
    environment = str()
    instance_types = []

    def __init__(self, base_path, environment):
        """ Construct a new bundle

        :type base_path: str
        :param base_path: Path to the base
        :type environment: str
        :param environment: Environment name
        """
        self.base_path = base_path
        self.target_path = '{}/target'.format(os.path.dirname(base_path))
        self.environment = environment

        for instance_type in os.listdir(base_path):
            if (instance_type not in ['.skymill', 'target'] and
                    os.path.isdir(os.path.join(base_path, instance_type))):
                    self.instance_types.append(instance_type)

    def create(self, instance_type=None):
        """ Create a new bundle

        :type instance_type: str
        :param instance_type: Instnace type name
        """
        if instance_type:
            self._bundle(instance_type)
        else:
            for inst_type in self.instance_types:
                self._bundle(inst_type)

    def _bundle(self, instance_type):
        """ Bundle a given instance type

        :type instance_type: str
        :param instance_type: Instnace type name
        """
        # Define a filter to modify the tar object
        def tar_filter(tarinfo):
            """ Modify the tar object.

            See: http://docs.python.org/library/tarfile.html#tarfile.TarInfo
            """
            # Make sure that the files are placed in the / root dir
            tarinfo.name = tarinfo.name.replace(
                '{}/'.format(self.base_path[1:]),
                '')

            # Change user permissions on all files
            tarinfo.uid = 0
            tarinfo.gid = 0
            tarinfo.uname = 'root'
            tarinfo.gname = 'root'

            return tarinfo

        def exclusion_filter(filename):
            """ Filter excluding files for other environments """
            if os.path.basename(filename).startswith('__sct-'):
                cnt = len(os.path.basename(filename).split(
                    '__sct-{}__'.format(self.environment)))

                if cnt == 2:
                    return False
                else:
                    logger.debug('Excluding file {}'.format(filename))
                    return True
            else:
                return False

        bundle = '{}/bundle-{}-{}-{}.tar.bz2'.format(
            self.target_path,
            self.environment,
            instance_type,
            datetime.utcnow().strftime('%Y%m%dT%H%M%S'))
        logger.info('Bundling the backup for instance type {}'.format(
            instance_type))
        tar = tarfile.open(bundle, 'w:bz2')
        tar.add(
            os.path.join(self.base_path, instance_type),
            exclude=exclusion_filter,
            filter=tar_filter)
        tar.close()
