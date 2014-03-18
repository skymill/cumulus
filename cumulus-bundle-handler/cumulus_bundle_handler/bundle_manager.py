""" Bundle manager responsible for download and extraction of bundle """
import logging
import os
import sys
import tempfile
import zipfile

from cumulus_bundle_handler import config

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

try:
    from boto import s3
except ImportError:
    print('Could not import boto. Try installing it with "pip install boto"')
    sys.exit(1)

LOGGER = logging.getLogger('cumulus_bundle_handler')


def download_and_unpack_bundle(bundle_type):
    """ Download the bundle from AWS S3

    :type bundle_type: str
    :param bundle_type: Bundle type to download
    """
    key = _get_key(bundle_type)

    # If the bundle does not exist
    if not key:
        LOGGER.error('No bundle found. Exiting.')
        sys.exit(0)

    bundle = tempfile.NamedTemporaryFile(
        suffix='.zip',
        delete=False)
    bundle.close()
    LOGGER.info("Downloading s3://{}/{} to {}".format(
        config.get('bundle-bucket'),
        key.name,
        bundle.name))
    key.get_contents_to_filename(bundle.name)

    extraction_path = _get_extraction_path(bundle_type)

    # Unpack the bundle
    archive = zipfile.ZipFile(bundle.name, 'r')
    _store_bundle_files(archive.namelist(), extraction_path)

    try:
        LOGGER.info('Unpacking {} to {}'.format(bundle.name, extraction_path))
        archive.extractall(extraction_path)
        for info in archive.infolist():
            archive.extract(info, extraction_path)
            if not ospath.isdir(ospath.join(extraction_path, info.filename)):
                os.chmod(
                    ospath.join(extraction_path, info.filename),
                    info.external_attr >> 16)
    except Exception as err:
        LOGGER.error('Error when unpacking bundle: {}'.format(err))
    finally:
        archive.close()

    # Remove the downloaded package
    LOGGER.info("Removing temporary file {}".format(bundle.name))
    os.remove(bundle.name)


def _get_extraction_path(bundle_type):
    """ Returns the path to where the bundle should be extracted

    :type bundle_type: str
    :param bundle_type: Bundle type to download
    :returns: str -- Path
    """
    path = '/'
    if sys.platform in ['win32', 'cygwin']:
        path = 'C:\\'

    if not ospath.exists(path):
        LOGGER.debug('Created extraction path {}'.format(path))
        os.makedirs(path)

    bundle_paths = config.get('bundle-extraction-paths').split('\n')

    if bundle_paths:
        for line in bundle_paths:
            if not line:
                continue

            try:
                for_bundle_type, extraction_path = line.split('->')
                for_bundle_type = for_bundle_type.strip()
                extraction_path = extraction_path.strip()

                if for_bundle_type == bundle_type:
                    path = extraction_path

            except ValueError:
                LOGGER.error(
                    'Error parsing bundle-extraction-paths: {}'.format(line))
                sys.exit(1)

    LOGGER.debug('Determined bundle extraction path to {} for {}'.format(
        path, bundle_type))

    return path


def _get_key(bundle_type):
    """ Returns the bundle key

    :type bundle_type: str
    :param bundle_type: Bundle type to download
    :returns: boto.s3.key -- S3 key object
    """
    LOGGER.debug("Connecting to AWS S3")
    connection = s3.connect_to_region(
        config.get('region'),
        aws_access_key_id=config.get('access-key-id'),
        aws_secret_access_key=config.get('secret-access-key'))

    # Get the relevant bucket
    bucket_name = config.get('bundle-bucket')
    LOGGER.debug('Using bucket {}'.format(bucket_name))
    bucket = connection.get_bucket(bucket_name)

    # Download the bundle
    key_name = (
        '{env}/{version}/bundle-{env}-{version}-{bundle}.zip'.format(
            env=config.get('environment'),
            version=config.get('version'),
            bundle=bundle_type))
    LOGGER.debug('Looking for bundle {}'.format(key_name))
    key = bucket.get_key(key_name)

    # When we have found a key, don't look any more
    if key:
        LOGGER.debug('Found bundle: {}'.format(key_name))
        return key

    LOGGER.debug('Bundle not found: {}'.format(key_name))
    return None


def _store_bundle_files(filenames, extraction_path):
    """ Store a list of bundle paths

    :type filenames: list
    :param filenames: List of full paths for all paths in the bundle'
    :type extraction_path: str
    :param extraction_path: Path to prefix all filenames with
    """
    cache_file = '/var/local/cumulus-bundle-handler.cache'
    if sys.platform in ['win32', 'cygwin']:
        if not ospath.exists('C:\\cumulus\\cache'):
            os.makedirs('C:\\cumulus\\cache')
        cache_file = 'C:\\cumulus\\cache\\cumulus-bundle-handler.cache'

    file_handle = open(cache_file, 'a')
    try:
        for filename in filenames:
            if not filename:
                continue

            if sys.platform in ['win32', 'cygwin']:
                filename = '{}\\{}'.format(extraction_path, filename)
            else:
                filename = '{}/{}'.format(extraction_path, filename)

            file_handle.write('{}\n'.format(filename))

        LOGGER.debug('Stored bundle information in {}'.format(cache_file))
    finally:
        file_handle.close()
