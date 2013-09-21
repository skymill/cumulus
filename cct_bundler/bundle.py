""" Bundling functions """
import os
import tarfile

import config_handler
from connector import connect_aws_s3
from logger import logger


class Bundle:
    """ Bundle object """
    base_path = str()
    target_path = str()
    environment = str()
    instance_types = []
    bundle_paths = []
    version = str()

    def __init__(self, base_path, environment, version):
        """ Construct a new bundle

        :type base_path: str
        :param base_path: Path to the base
        :type environment: str
        :param environment: Environment name
        :type version: str
        :param version: Version string
        """
        self.base_path = base_path
        self.target_path = '{}/target'.format(os.path.dirname(base_path))
        self.environment = environment
        self.version = version

        for instance_type in os.listdir(base_path):
            if (instance_type not in ['.cumulus', 'target'] and
                    os.path.isdir(os.path.join(base_path, instance_type))):
                    self.instance_types.append(instance_type)

    def create_and_upload(self, instance_type=None):
        """ Create a new bundle and upload it to S3

        :type instance_type: str
        :param instance_type: Instnace type name
        """
        if instance_type:
            self._bundle(instance_type)
        else:
            for inst_type in self.instance_types:
                self._bundle(inst_type)

        self._upload_to_s3()

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
            if os.path.basename(filename).startswith('__cumulus-'):
                cnt = len(os.path.basename(filename).split(
                    '__cumulus-{}__'.format(self.environment)))

                if cnt == 2:
                    return False
                else:
                    logger.debug('Excluding file {}'.format(filename))
                    return True
            else:
                return False

        bundle = '{}/cct-bundle-{}-{}-{}.tar.bz2'.format(
            self.target_path,
            self.environment,
            self.version,
            instance_type)
        logger.info('Bundling the backup for instance type {}'.format(
            instance_type))
        tar = tarfile.open(bundle, 'w:bz2')
        tar.add(
            os.path.join(self.base_path, instance_type),
            exclude=exclusion_filter,
            filter=tar_filter)
        tar.close()
        self.bundle_paths.append(bundle)
        logger.info('Wrote bundle to {}'.format(bundle))

    def _upload_to_s3(self):
        """ Upload all bundles to S3 """
        connection = connect_aws_s3(
            config_handler.get(self.environment, 'access-key-id'),
            config_handler.get(self.environment, 'secret-access-key'))
        bucket = connection.get_bucket(
            config_handler.get(self.environment, 'bucket'))
        logger.info('Starting bundle uploads')

        for bundle in self.bundle_paths:
            key_name = '{}/{}'.format(
                self.environment,
                os.path.basename(bundle))
            key = bucket.new_key(key_name)
            logger.info('Starting upload of {} to {}'.format(
                os.path.basename(bundle),
                key_name))
            key.set_contents_from_filename(bundle)
            logger.info('Completed upload of {} to {}'.format(
                os.path.basename(bundle),
                key_name))
