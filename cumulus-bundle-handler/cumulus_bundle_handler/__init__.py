""" Script downloading and unpacking Cumulus bundles for the host """

import logging
import logging.config
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from ConfigParser import SafeConfigParser, NoOptionError

try:
    from boto import s3
except ImportError:
    print('Could not import boto. Try installing it with "pip install boto"')
    sys.exit(1)

CONFIG = SafeConfigParser()

if sys.platform in ['win32', 'cygwin']:
    CONFIG_PATH = 'C:\\cumulus\\conf\\metadata.conf'
else:
    CONFIG_PATH = '/etc/cumulus/metadata.conf'

if not os.path.exists(CONFIG_PATH):
    print('Error: Configuration file not found: {}'.format(CONFIG_PATH))
    sys.exit(1)

CONFIG.read(CONFIG_PATH)


# Configure logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_LOGGERs': False,
    'formatters': {
        'standard': {
            'format': (
                '%(asctime)s - cumulus-bundle-handler - '
                '%(levelname)s - %(message)s'
            )
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '/var/log/cumulus-bundle-handler.log',
            'mode': 'a',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True
        },
        'cumulus_bundle_handler': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Change the log file path on Windows systems
if sys.platform in ['win32', 'cygwin']:
    if not os.path.exists('C:\\cumulus\\logs'):
        os.makedirs('C:\\cumulus\\logs')
    LOGGING_CONFIG['handlers']['file']['filename'] = \
        'C:\\cumulus\\logs\\cumulus-bundle-handler.log'

# Read log level from the metadata.conf
try:
    LOGGING_CONFIG['handlers']['console']['level'] = CONFIG.get(
        'metadata', 'log-level').upper()
    LOGGING_CONFIG['handlers']['file']['level'] = CONFIG.get(
        'metadata', 'log-level').upper()
except NoOptionError:
    pass

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger('cumulus_bundle_handler')


def main():
    """ Main function """
    _run_init_scripts(kill=True, start=False, other=True)

    bundle_types = CONFIG.get('metadata', 'bundle-types').split(',')
    if not bundle_types:
        LOGGER.error('Missing "bundle-types" in metadata.conf')
        sys.exit(1)

    _remove_old_files()

    for bundle_type in bundle_types:
        _download_and_unpack_bundle(bundle_type.strip())

    _run_init_scripts(kill=False, start=True, other=True)

    LOGGER.info("Done updating host")


def _download_and_unpack_bundle(bundle_type):
    """ Download the bundle from AWS S3

    :type bundle_type: str
    :param bundle_type: Bundle type to download
    """
    key, compression = _get_key(bundle_type)

    # If the bundle does not exist
    if not key:
        LOGGER.error('No bundle found. Exiting.')
        sys.exit(1)

    bundle = tempfile.NamedTemporaryFile(
        suffix='.{}'.format(compression),
        delete=False)
    bundle.close()
    LOGGER.info("Downloading s3://{}/{} to {}".format(
        CONFIG.get('metadata', 'bundle-bucket'),
        key.name,
        bundle.name))
    key.get_contents_to_filename(bundle.name)

    extraction_path = _get_extraction_path(bundle_type)

    # Unpack the bundle
    LOGGER.info("Unpacking {}".format(bundle.name))
    if compression == 'tar.bz2':
        archive = tarfile.open(bundle.name, 'r:bz2')
        _store_bundle_files(archive.getnames(), extraction_path)
    elif compression == 'tar.gz':
        archive = tarfile.open(bundle.name, 'r:gz')
        _store_bundle_files(archive.getnames(), extraction_path)
    elif compression == 'zip':
        archive = zipfile.ZipFile(bundle.name, 'r')
        _store_bundle_files(archive.namelist(), extraction_path)
    else:
        logging.error('Unsupported compression format: "{}"'.format(
            compression))
        sys.exit(1)

    try:
        LOGGER.info('Unpacking {} to {}'.format(bundle.name, extraction_path))
        archive.extractall(extraction_path)
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

    if not os.path.exists(path):
        LOGGER.debug('Created extraction path {}'.format(path))
        os.makedirs(path)

    try:
        bundle_paths = CONFIG.get('metadata', 'bundle-extraction-paths')\
            .split('\n')

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

    except NoOptionError:
        pass

    LOGGER.debug('Determined bundle extraction path to {} for {}'.format(
        path, bundle_type))

    return path


def _get_key(bundle_type):
    """ Returns the bundle key

    :type bundle_type: str
    :param bundle_type: Bundle type to download
    :returns: (boto.s3.key, str) -- (S3 key object, compression type)
    """
    LOGGER.debug("Connecting to AWS S3")
    connection = s3.connect_to_region(
        CONFIG.get('metadata', 'region'),
        aws_access_key_id=CONFIG.get('metadata', 'access-key-id'),
        aws_secret_access_key=CONFIG.get('metadata', 'secret-access-key'))

    # Get the relevant bucket
    bucket_name = CONFIG.get('metadata', 'bundle-bucket')
    LOGGER.debug('Using bucket {}'.format(bucket_name))
    bucket = connection.get_bucket(bucket_name)

    # Download the bundle
    for compression in ['tar.bz2', 'tar.gz', 'zip']:
        key_name = (
            '{env}/{version}/bundle-{env}-{version}-{bundle}.{comp}'.format(
                env=CONFIG.get('metadata', 'environment'),
                version=CONFIG.get('metadata', 'version'),
                bundle=bundle_type,
                comp=compression))
        LOGGER.debug('Looking for bundle {}'.format(key_name))
        key = bucket.get_key(key_name)

        # When we have found a key, don't look any more
        if key:
            LOGGER.debug('Found bundle: {}'.format(key_name))
            return (key, compression)
        LOGGER.debug('Bundle not found: {}'.format(key_name))

    return (None, None)


def _remove_old_files():
    """ Remove files from previous bundle """
    cache_file = '/var/local/cumulus-bundle-handler.cache'
    if sys.platform in ['win32', 'cygwin']:
        if not os.path.exists('C:\\cumulus\\cache'):
            os.makedirs('C:\\cumulus\\cache')
        cache_file = 'C:\\cumulus\\cache\\cumulus-bundle-handler.cache'

    if not os.path.exists(cache_file):
        LOGGER.info('No previous bundle files to clean up')
        return

    LOGGER.info('Removing old files and directories')

    with open(cache_file, 'r') as file_handle:
        for line in file_handle.readlines():
            line = line.replace('\n', '')

            if not os.path.exists(line):
                continue

            if os.path.isdir(line):
                try:
                    os.removedirs(line)
                    LOGGER.debug('Removing directory {}'.format(line))
                except OSError:
                    pass
            elif os.path.isfile(line):
                LOGGER.debug('Removing file {}'.format(line))
                os.remove(line)

                try:
                    os.removedirs(os.path.dirname(line))
                except OSError:
                    pass
            elif os.path.islink(line):
                LOGGER.debug('Removing link {}'.format(line))
                os.remove(line)

                try:
                    os.removedirs(os.path.dirname(line))
                except OSError:
                    pass
            else:
                LOGGER.warning('Unknown file type {}'.format(line))

    # Remove the cache file when done
    os.remove(cache_file)


def _run_command(command):
    """ Run arbitary command

    :type command: str
    :param command: Command to execute
    """
    LOGGER.info('Executing command: {}'.format(command))

    cmd = subprocess.Popen(
        command,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

    stdout, stderr = cmd.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    if cmd.returncode != 0:
        LOGGER.error('Command "{}" returned non-zero exit code {}'.format(
            command,
            cmd.returncode))
        sys.exit(cmd.returncode)


def _run_init_scripts(start=False, kill=False, other=False):
    """ Execute scripts in /etc/cumulus-init.d or C:\\cumulus\\init.d

    :type start: bool
    :param start: Run scripts starting with S
    :type kill: bool
    :param kill: Run scripts starting with K
    :type others: bool
    :param others: Run scripts not starting with S or K
    """
    init_dir = '/etc/cumulus-init.d'
    if sys.platform in ['win32', 'cygwin']:
        init_dir = 'C:\\cumulus\\init.d'

    # Run the post install scripts provided by the bundle
    if not os.path.exists(init_dir):
        LOGGER.info('No init scripts found in {}'.format(init_dir))
        return

    LOGGER.info('Running init scripts from {}'.format(init_dir))

    filenames = []
    for filename in os.listdir(init_dir):
        if os.path.isfile(os.path.join(init_dir, filename)):
            filenames.append(os.path.join(init_dir, filename))

    if start:
        for filename in filenames:
            if os.path.basename(filename)[0] == 'S':
                _run_command(os.path.abspath(filename))

    if kill:
        for filename in filenames:
            if os.path.basename(filename)[0] == 'K':
                _run_command(os.path.abspath(filename))

    if other:
        for filename in filenames:
            if os.path.basename(filename)[0] not in ['K', 'S']:
                _run_command(os.path.abspath(filename))


def _store_bundle_files(filenames, extraction_path):
    """ Store a list of bundle paths

    :type filenames: list
    :param filenames: List of full paths for all paths in the bundle'
    :type extraction_path: str
    :param extraction_path: Path to prefix all filenames with
    """
    cache_file = '/var/local/cumulus-bundle-handler.cache'
    if sys.platform in ['win32', 'cygwin']:
        if not os.path.exists('C:\\cumulus\\cache'):
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
