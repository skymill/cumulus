""" Bundling functions """
import fnmatch
import logging
import os
import subprocess
import sys
import tempfile
import zipfile

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

from cumulus_ds import connection_handler
import cumulus_ds
from cumulus_ds.exceptions import HookExecutionException, UnsupportedCompression

logger = logging.getLogger(__name__)


def build_bundles():
    """ Build bundles for the environment """
    bundle_types = cumulus_ds.config.get_bundles()

    if not bundle_types:
        logger.warning(
            'No bundles configured, will deploy without any bundles')
        return None

    for bundle_type in bundle_types:
        # Run pre-bundle-hook
        _pre_bundle_hook(bundle_type)

        if cumulus_ds.config.has_pre_built_bundle(bundle_type):
            bundle_path = cumulus_ds.config.get_pre_built_bundle_path(
                bundle_type)
            logger.info('Using pre-built bundle: {}'.format(bundle_path))

            try:
                _upload_bundle(bundle_path, bundle_type)
            except UnsupportedCompression:
                raise
        else:
            logger.info('Building bundle {}'.format(bundle_type))
            logger.debug('Bundle paths: {}'.format(', '.join(
                cumulus_ds.config.get_bundle_paths(bundle_type))))

            tmptar = tempfile.NamedTemporaryFile(
                suffix='.zip',
                delete=False)
            logger.debug('Created temporary tar file {}'.format(tmptar.name))

            try:
                _bundle_zip(
                    tmptar,
                    bundle_type,
                    cumulus_ds.config.get_environment(),
                    cumulus_ds.config.get_bundle_paths(bundle_type))

                tmptar.close()

                try:
                    _upload_bundle(tmptar.name, bundle_type)
                except UnsupportedCompression:
                    raise
            finally:
                logger.debug('Removing temporary tar file {}'.format(
                    tmptar.name))
                os.remove(tmptar.name)

        # Run post-bundle-hook
        _post_bundle_hook(bundle_type)


def _bundle_zip(tmpfile, bundle_type, environment, paths):
    """ Create a zip archive

    :type tmpfile: tempfile instance
    :param tmpfile: Tempfile object
    :type bundle_type: str
    :param bundle_type: Bundle name
    :type environment: str
    :param environment: Environment name
    :type paths: list
    :param paths: List of paths to include
    """
    archive = zipfile.ZipFile(tmpfile, 'w')
    path_rewrites = cumulus_ds.config.get_bundle_path_rewrites(bundle_type)

    for path in paths:
        for filename in _find_files(path, '*.*'):
            arcname = filename

            # Exclude files with other target environments
            prefix = '__cumulus-{}__'.format(environment)
            basename = ospath.basename(filename)

            if basename.startswith('__cumulus-'):
                if len(basename.split(prefix)) != 2:
                    logger.debug('Excluding file {}'.format(filename))
                    continue
            elif prefix in filename.split(ospath.sep):
                logger.debug('Excluding file {}'.format(filename))
                continue

            # Do all rewrites
            for rewrite in path_rewrites:
                try:
                    if arcname[:len(rewrite['target'])] == rewrite['target']:
                        arcname = arcname.replace(
                            rewrite['target'],
                            rewrite['destination'])
                        logger.debug(
                            'Replaced "{}" with "{}" in bundle {}'.format(
                                rewrite['target'],
                                rewrite['destination'],
                                bundle_type))
                except IndexError:
                    pass

            archive.write(filename, arcname, zipfile.ZIP_DEFLATED)

    archive.close()


def _find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = ospath.join(root, basename)
                yield filename


def _post_bundle_hook(bundle_name):
    """ Execute a post-bundle-hook

    :type bundle: str
    :param bundle: Bundle name
    """
    command = cumulus_ds.config.get_post_bundle_hook(bundle_name)

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
    command = cumulus_ds.config.get_pre_bundle_hook(bundle_name)

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
        cumulus_ds.config.get_environment_option('bucket'))

    # Check that the bundle actually exists
    if not ospath.exists(bundle_path):
        logger.error('File not found: {}'.format(bundle_path))
        sys.exit(1)

    if bundle_path.endswith('.zip'):
        compression = 'zip'
    else:
        raise UnsupportedCompression(
            'Unknown compression format for {}. '
            'We are currently only supporting .zip'.format(bundle_path))

    key_name = (
        '{environment}/{version}/'
        'bundle-{environment}-{version}-{bundle_type}.{compression}').format(
            environment=cumulus_ds.config.get_environment(),
            version=cumulus_ds.config.get_environment_option('version'),
            bundle_type=bundle_type,
            compression=compression)
    key = bucket.new_key(key_name)

    logger.info('Starting upload of {} to s3://{}/{}'.format(
        ospath.basename(bundle_path), bucket.name, key_name))

    key.set_contents_from_filename(bundle_path, replace=True)

    logger.info('Completed upload of {} to s3://{}/{}'.format(
        ospath.basename(bundle_path), bucket.name, key_name))
