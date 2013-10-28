#!/usr/bin/env python

""" Script downloading and unpacking Cumulus bundles for the host """

import logging
import os
import shutil
import sys
import tarfile
import tempfile
from subprocess import call
from ConfigParser import SafeConfigParser

try:
    from boto import s3
except ImportError:
    print('Could not import boto. Try installing it with "pip install boto"')
    sys.exit(1)


# Configure logging
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
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
})

logger = logging.getLogger('cumulus_bundle_handler')

config = SafeConfigParser()
config.read('/etc/cumulus/metadata.conf')


def main():
    """ Main function """
    _remove_old_files()
    _download_and_unpack_bundle()
    _run_init_scripts()

    logger.info("Done updating host")


def _download_and_unpack_bundle():
    """ Download the bundle from AWS S3 """
    logger.debug("Connecting to AWS S3")
    connection = s3.connect_to_region(
        config.get('metadata', 'region'),
        aws_access_key_id=config.get('metadata', 'aws-access-key-id'),
        aws_secret_access_key=config.get(
            'metadata', 'aws-secret-access-key'))

    # Download the bundle
    key_name = (
        '{env}/{version}/bundle-{env}-{version}-{bundle}.tar.bz2'.format(
            env=config.get('metadata', 'environment'),
            version=config.get('metadata', 'version'),
            bundle=config.get('metadata', 'bundle-type')))
    bucket = connection.get_bucket(config.get('metadata', 's3-bundles-bucket'))
    key = bucket.get_key(key_name)

    # If the bundle does not exist
    if not key:
        logger.error('No bundle matching {} found'.format(key_name))
        sys.exit(1)

    bundle = tempfile.NamedTemporaryFile(suffix='.tar.bz2', delete=False)
    bundle.close()
    logger.info("Downloading s3://{}/{} to {}".format(
        config.get('metadata', 's3-bundles-bucket'),
        key.name,
        bundle.name))
    key.get_contents_to_filename(bundle.name)

    # Unpack the bundle
    logger.info("Unpacking {}".format(bundle.name))
    tar = tarfile.open(bundle.name, 'r:bz2')
    _store_bundle_files(tar.getnames())
    tar.extractall()
    tar.close()

    # Remove the downloaded package
    logger.info("Removing temporary file {}".format(bundle.name))
    os.remove(bundle.name)


def _remove_old_files():
    """ Remove files from previous bundle """
    cache_file = '/var/local/cumulus-bundle-handler.cache'

    if not os.path.exists(cache_file):
        logger.info('No previous bundle files to clean up')
        return

    with open(cache_file, 'r') as file_handle:
        for line in file_handle.readlines():
            line = line.replace('\n', '')

            if not os.path.exists(line):
                continue

            if os.path.isdir(line):
                if os.listdir(line) == []:
                    logger.info('Removing empty directory {}'.format(line))
                    shutil.rmtree(line)
            elif os.path.isfile(line):
                logger.info('Removing file {}'.format(line))
                os.remove(line)

                if os.listdir(os.path.dirname(line)) == []:
                    logger.info('Removing empty directory {}'.format(
                        os.path.dirname(line)))
                    shutil.rmtree(os.path.dirname(line))

            elif os.path.islink(line):
                logger.info('Removing link {}'.format(line))

                if os.listdir(os.path.dirname(line)) == []:
                    logger.info('Removing empty directory {}'.format(
                        os.path.dirname(line)))
                    shutil.rmtree(os.path.dirname(line))
            else:
                logger.warning('Unknown file type {}'.format(line))


def _run_init_scripts():
    """ Execute scripts in /etc/cumulus-init.d """
    # Run the post install scripts provided by the bundle
    if os.path.exists('/etc/cumulus-init.d'):
        logger.info("Running all post deploy scripts in /etc/cumulus-init.d")
        call(
            'run-parts -v --regex ".*" /etc/cumulus-init.d',
            shell=True)


def _store_bundle_files(filenames):
    """ Store a list of bundle paths

    :type filenames: list
    :param filenames: List of full paths for all paths in the bundle
    """
    cache_file = '/var/local/cumulus-bundle-handler.cache'

    if os.path.exists(cache_file):
        os.remove(cache_file)

    file_handle = open(cache_file, 'w')
    try:
        for filename in filenames:
            if not filename:
                continue

            if filename[0] != '/':
                filename = '/{}'.format(filename)

            file_handle.write('{}\n'.format(filename))

        logger.debug('Stored bundle information in {}'.format(cache_file))
    finally:
        file_handle.close()


if __name__ == '__main__':
    main()
    sys.exit(0)

sys.exit(1)
