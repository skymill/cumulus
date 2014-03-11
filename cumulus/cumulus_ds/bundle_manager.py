""" Bundling functions """
import fnmatch
import hashlib
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
from cumulus_ds.config import CONFIG as config
from cumulus_ds.exceptions import (
    ChecksumMismatchException,
    HookExecutionException,
    UnsupportedCompression)

logger = logging.getLogger(__name__)


def build_bundles():
    """ Build bundles for the environment """
    bundle_types = config.get_bundles()

    if not bundle_types:
        logger.warning(
            'No bundles configured, will deploy without any bundles')
        return None

    for bundle_type in bundle_types:
        # Run pre-bundle-hook
        _pre_bundle_hook(bundle_type)

        if config.has_pre_built_bundle(bundle_type):
            bundle_path = config.get_pre_built_bundle_path(
                bundle_type)
            logger.info('Using pre-built bundle: {}'.format(bundle_path))

            try:
                _upload_bundle(bundle_path, bundle_type)
            except UnsupportedCompression:
                raise
        else:
            logger.info('Building bundle {}'.format(bundle_type))
            logger.info('Bundle paths: {}'.format(', '.join(
                config.get_bundle_paths(bundle_type))))

            tmptar = tempfile.NamedTemporaryFile(
                suffix='.zip',
                delete=False)
            logger.debug('Created temporary tar file {}'.format(tmptar.name))

            try:
                _bundle_zip(
                    tmptar,
                    bundle_type,
                    config.get_environment(),
                    config.get_bundle_paths(bundle_type))

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

        logger.info('Done bundling {}'.format(bundle_type))


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
    logger.info('Generating zip file for {}'.format(bundle_type))
    archive = zipfile.ZipFile(tmpfile, 'w')
    path_rewrites = config.get_bundle_path_rewrites(bundle_type)

    for path in paths:
        path = _convert_paths_to_local_format(path)
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
                target = _convert_paths_to_local_format(
                    rewrite['target'].replace('\\\\', '\\'))
                destination = _convert_paths_to_local_format(
                    rewrite['destination'].replace('\\\\', '\\'))

                try:
                    if arcname[:len(target)] == target:
                        arcname = arcname.replace(
                            target,
                            destination)
                        logger.debug(
                            'Replaced "{}" with "{}" in bundle {}'.format(
                                target,
                                destination,
                                bundle_type))
                except IndexError:
                    pass

            archive.write(filename, arcname, zipfile.ZIP_DEFLATED)

    archive.close()


def _convert_paths_to_local_format(path):
    """ Convert paths to have the local path separator

    On Windows systems: Convert any / to \\
    On Other systems: Convert any \ to /

    :type path: str
    :param path: Path to operate open
    :returns: str -- Altered version of path
    """
    if sys.platform in ['win32', 'cygwin']:
        path = path.split('/')
    else:
        path = path.split('\\')

    return ospath.sep.join(path)


def _find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = ospath.join(root, basename)
                yield filename


def _generate_local_md5hash(filename):
    """ Get the MD5 hash of a local file

    :type filename: str
    :param filename: Path to the file to read
    :returns: str -- MD5 of the file
    """
    if not ospath.exists(filename):
        logger.warning(
            'Unable to generate MD5 of local file {}. '
            'File does not exist.'.format(filename))
        return None

    hash = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    logger.debug('Generated md5 checksum for {} ({})'.format(
        ospath.basename(filename), hash))

    return hash


def _key_exists(bucket_name, key_name, checksum=None):
    """ Check if the given key exists in AWS S3.

    If checksum is given, also check if the md5 checksum is the same

    :type bucket_name: str
    :param bucket_name: S3 bucket name
    :type key_name: str
    :param key_name: S3 key name
    :type checksum: str
    :param checksum: MD5 checksum
    :returns: bool -- True if the key exists
    """
    try:
        connection = connection_handler.connect_s3()
    except Exception:
        raise

    bucket = connection.get_bucket(bucket_name)

    key = bucket.get_key(key_name)
    if not key:
        return False

    if checksum:
        if key.etag.replace('"', '') == checksum:
            return True
        return False

    return True


def _post_bundle_hook(bundle_name):
    """ Execute a post-bundle-hook

    :type bundle: str
    :param bundle: Bundle name
    """
    command = config.get_post_bundle_hook(bundle_name)

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
    command = config.get_pre_bundle_hook(bundle_name)

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
        config.get_environment_option('bucket'))

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

    # Generate a md5 checksum for the local bundle
    local_hash = _generate_local_md5hash(bundle_path)

    key_name = (
        '{environment}/{version}/'
        'bundle-{environment}-{version}-{bundle_type}.{compression}').format(
            environment=config.get_environment(),
            version=config.get_environment_option('version'),
            bundle_type=bundle_type,
            compression=compression)

    # Do not upload bundles if the key already exists and has the same
    # md5 checksum
    if _key_exists(
            config.get_environment_option('bucket'),
            key_name,
            checksum=local_hash):
        logger.info(
            'This bundle is already uploaded to AWS S3. Skipping upload.')
        return

    # Get the key object
    key = bucket.new_key(key_name)

    logger.info('Starting upload of {} to s3://{}/{}'.format(
        bundle_type, bucket.name, key_name))

    key.set_contents_from_filename(bundle_path, replace=True)

    logger.info('Completed upload of {} to s3://{}/{}'.format(
        bundle_type, bucket.name, key_name))

    # Compare MD5 checksums
    if local_hash == key.md5:
        logger.debug('Uploaded bundle checksum OK ({})'.format(key.md5))
    else:
        logger.error('Mismatching md5 checksum {} ({}) and {} ({})'.format(
            bundle_path, local_hash, key_name, key.md5))
        raise ChecksumMismatchException(
            'Mismatching md5 checksum {} ({}) and {} ({})'.format(
                bundle_path, local_hash, key_name, key.md5))
