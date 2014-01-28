""" Bundling functions """
import logging
import os
import subprocess
import tarfile
import tempfile

import config_handler
import connection_handler
from exceptions import HookExecutionException

logger = logging.getLogger(__name__)


def build_bundles():
    """ Build bundles for the environment """
    bundle_types = config_handler.get_bundles()

    if not bundle_types:
        logger.warning(
            'No bundles configured, will deploy without any bundles')
        return None

    for bundle_type in bundle_types:
        logger.info('Building bundle {}'.format(bundle_type))
        logger.debug('Bundle paths: {}'.format(', '.join(
            config_handler.get_bundle_paths(bundle_type))))

        # Run pre-bundle-hook
        _pre_bundle_hook(bundle_type)

        tmptar = tempfile.NamedTemporaryFile(
            suffix='.tar.bz2',
            delete=False)
        logger.debug('Created temporary tar file {}'.format(tmptar.name))

        try:
            _bundle(
                tmptar,
                bundle_type,
                config_handler.get_environment(),
                config_handler.get_bundle_paths(bundle_type))

            tmptar.close()

            # Run post-bundle-hook
            _post_bundle_hook(bundle_type)

            _upload_bundle(tmptar.name, bundle_type)
        finally:
            logger.debug('Removing temporary tar file {}'.format(tmptar.name))
            os.remove(tmptar.name)

    _upload_bundle_handler()


def _bundle(tmpfile, bundle_type, environment, paths):
    """ Create bundle

    :type tmpfile: tempfile instance
    :param tmpfile: Tempfile object
    :type bundle_type: str
    :param bundle_type: Bundle name
    :type environment: str
    :param environment: Environment name
    :type paths: list
    :param paths: List of paths to include
    """
    # Define a filter to modify the tar object
    def tar_filter(tarinfo):
        """ Modify the tar object.

        See: http://docs.python.org/library/tarfile.html#tarfile.TarInfo
        """
        # Make sure that the files are placed in the / root dir
        tarinfo.name = tarinfo.name.replace('{}/'.format(path[1:]), '')
        tarinfo.name = tarinfo.name.replace('{}'.format(path[1:]), '')

        for rewrite in path_rewrites:
            try:
                if tarinfo.name[:len(rewrite['target'])] == rewrite['target']:
                    tarinfo.name = tarinfo.name.replace(
                        rewrite['target'],
                        rewrite['destination'])
                    logger.debug('Replaced {} with {}'.format(
                        rewrite['target'], rewrite['destination']))
            except IndexError:
                pass

        # Remove prefixes
        tarinfo.name = tarinfo.name.replace(
            '__cumulus-{}__'.format(environment),
            '')

        # Change user permissions on all files
        tarinfo.uid = 0
        tarinfo.gid = 0
        tarinfo.uname = 'root'
        tarinfo.gname = 'root'

        return tarinfo

    def exclusion_filter(filename):
            """ Filter excluding files for other environments """
            prefix = '__cumulus-{}__'.format(environment)
            if os.path.basename(filename).startswith('__cumulus-'):
                cnt = len(os.path.basename(filename).split(prefix))
                if cnt == 2:
                    return False
                else:
                    logger.debug('Excluding file {}'.format(filename))
                    return True
            elif prefix in filename.split(os.path.sep):
                logger.debug('Excluding file {}'.format(filename))
                return True
            else:
                return False

    path_rewrites = config_handler.get_bundle_path_rewrites(bundle_type)

    tar = tarfile.open(
        fileobj=tmpfile,
        mode='w:bz2',
        dereference=True)
    for path in paths:
        tar.add(
            path,
            exclude=exclusion_filter,
            filter=tar_filter)
    tar.close()
    logger.info('Wrote bundle to {}'.format(tmpfile.name))


def _post_bundle_hook(bundle_name):
    """ Execute a post-bundle-hook

    :type bundle: str
    :param bundle: Bundle name
    """
    command = config_handler.get_post_bundle_hook(bundle_name)

    if not command:
        return None

    logger.info('Running post-bundle-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The post-bundle-hook returned a non-zero exit code: {}'.format(
                error))


def _pre_bundle_hook(bundle_name):
    """ Execute a pre-bundle-hook

    :type bundle: str
    :param bundle: Bundle name
    """
    command = config_handler.get_pre_bundle_hook(bundle_name)

    if not command:
        return None

    logger.info('Running pre-bundle-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The pre-bundle-hook returned a non-zero exit code: {}'.format(
                error))


def _upload_bundle(bundle_path, bundle_type):
    """ Upload all bundles to S3

    :type bundle_path: str
    :param bundle_path: Local path to the bundle
    :type bundle_type: str
    :param bundle_type: Bundle type
    """
    try:
        connection = connection_handler.connect_s3()
    except Exception:
        raise

    bucket = connection.get_bucket(
        config_handler.get_environment_option('bucket'))

    key_name = (
        '{environment}/{version}/'
        'bundle-{environment}-{version}-{bundle_type}.tar.bz2').format(
            environment=config_handler.get_environment(),
            version=config_handler.get_environment_option('version'),
            bundle_type=bundle_type)
    key = bucket.new_key(key_name)

    logger.info('Starting upload of {} to s3://{}'.format(
        os.path.basename(bundle_path), key_name))

    key.set_contents_from_filename(bundle_path, replace=True)

    logger.info('Completed upload of {} to s3://{}'.format(
        os.path.basename(bundle_path), key_name))


def _upload_bundle_handler():
    """ Upload the bundle handler to S3 """
    try:
        connection = connection_handler.connect_s3()
    except Exception:
        raise
    bucket = connection.get_bucket(
        config_handler.get_environment_option('bucket'))

    logger.info('Uploading the cumulus_bundle_handler.py script')
    key_name = '{}/{}/cumulus_bundle_handler.py'.format(
        config_handler.get_environment(),
        config_handler.get_environment_option('version'))
    key = bucket.new_key(key_name)
    key.set_contents_from_filename(
        '{}/bundle_handler/cumulus_bundle_handler.py'.format(
            os.path.dirname(os.path.realpath(__file__))),
        replace=True)
