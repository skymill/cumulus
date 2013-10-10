#!/usr/bin/env python

""" Script downloading and unpacking Cumulus bundles for the host """

import os
import sys
import tarfile
import tempfile
from subprocess import call
from datetime import datetime
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

try:
    from boto import s3
except ImportError:
    print('Could not import boto. Try installing it with "pip install boto"')
    sys.exit(1)


def main():
    """ Main function """
    config = SafeConfigParser()
    config.read('/etc/cumulus/metadata.conf')

    #
    # Connect to AWS S3
    #
    log("Connecting to AWS S3")
    try:
        con = s3.connect_to_region(
            config.get('metadata', 'region'),
            aws_access_key_id=config.get('metadata', 'aws-access-key-id'),
            aws_secret_access_key=config.get(
                'metadata', 'aws-secret-access-key'))
    except NoSectionError, error:
        log('Missing config section: {}'.format(error))
        sys.exit(1)
    except NoOptionError, error:
        log('Missing config option: {}'.format(error))
        sys.exit(1)
    except AttributeError:
        log(
            'It seems like boto is outdated. Please upgrade '
            'by running \"pip install --upgrade boto\"')
        sys.exit(1)
    except:
        log('Unhandled exception when connecting to S3.')
        sys.exit(1)

    #
    # Download the bundle
    #
    bucket = con.get_bucket(config.get('metadata', 's3-bundles-bucket'))
    key = bucket.get_key(
        '{env}/{version}/bundle-{env}-{version}-{bundle}.tar.bz2'.format(
            env=config.get('metadata', 'environment'),
            version=config.get('metadata', 'version'),
            bundle=config.get('metadata', 'bundle-type')))
    bundle = tempfile.NamedTemporaryFile(suffix='.tar.bz2', delete=False)
    bundle.close()
    log("Downloading s3://{}/{} to {}".format(
        config.get('metadata', 's3-bundles-bucket'),
        key.name,
        bundle.name))
    key.get_contents_to_filename(bundle.name)

    # Unpack the bundle
    log("Unpacking {}".format(bundle.name))
    tar = tarfile.open(bundle.name, 'r:bz2')
    tar.extractall()
    tar.close()

    # Remove the downloaded package
    log("Removing temporary file {}".format(bundle.name))
    os.remove(bundle.name)

    # Run the post install scripts provided by the bundle
    if os.path.exists('/etc/cumulus-init.d'):
        log("Run all post deploy scripts in /etc/cumulus-init.d")
        call(
            'run-parts -v --regex ".*" /etc/cumulus-init.d',
            shell=True)

    log("Done updating host")


def log(message):
    """ Print a message with a timestamp

    :type message: str
    :param message: Log message to print
    """
    print '{} - {}'.format(datetime.utcnow().isoformat(), message)


if __name__ == '__main__':
    main()
    sys.exit(0)

sys.exit(1)
