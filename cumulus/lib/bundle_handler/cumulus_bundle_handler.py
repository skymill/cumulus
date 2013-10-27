#!/usr/bin/env python

""" Script downloading and unpacking Cumulus bundles for the host """

import os
import sys
import logging
import tarfile
import tempfile
from subprocess import call
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '/var/log/cumulus-bundle-handler.log',
            'mode': 'a',
            'maxbytes': 10485760,  # 10 MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    config = SafeConfigParser()
    config.read('/etc/cumulus/metadata.conf')

    #
    # Connect to AWS S3
    #
    logger.debug("Connecting to AWS S3")
    try:
        con = s3.connect_to_region(
            config.get('metadata', 'region'),
            aws_access_key_id=config.get('metadata', 'aws-access-key-id'),
            aws_secret_access_key=config.get(
                'metadata', 'aws-secret-access-key'))
    except NoSectionError, error:
        logger.error('Missing config section: {}'.format(error))
        sys.exit(1)
    except NoOptionError, error:
        logger.error('Missing config option: {}'.format(error))
        sys.exit(1)
    except AttributeError:
        logger.error(
            'It seems like boto is outdated. Please upgrade '
            'by running \"pip install --upgrade boto\"')
        sys.exit(1)
    except:
        logger.error('Unhandled exception when connecting to S3.')
        sys.exit(1)

    #
    # Download the bundle
    #
    key_name = (
        '{env}/{version}/bundle-{env}-{version}-{bundle}.tar.bz2'.format(
            env=config.get('metadata', 'environment'),
            version=config.get('metadata', 'version'),
            bundle=config.get('metadata', 'bundle-type')))
    bucket = con.get_bucket(config.get('metadata', 's3-bundles-bucket'))
    key = bucket.get_key(key_name)

    # If the bundle does not exist
    if not key:
        logger.error('No bundle matching {} found'.format(key_name))
        return

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
    tar.extractall()
    tar.close()

    # Remove the downloaded package
    logger.info("Removing temporary file {}".format(bundle.name))
    os.remove(bundle.name)

    # Run the post install scripts provided by the bundle
    if os.path.exists('/etc/cumulus-init.d'):
        logger.info("Run all post deploy scripts in /etc/cumulus-init.d")
        call(
            'run-parts -v --regex ".*" /etc/cumulus-init.d',
            shell=True)

    logger.info("Done updating host")


if __name__ == '__main__':
    main()
    sys.exit(0)

sys.exit(1)
