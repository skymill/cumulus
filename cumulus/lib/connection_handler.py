""" Connection handler """
import boto
import logging
import sys
from boto import cloudformation

import config_handler

logger = logging.getLogger(__name__)


def connect_s3():
    """ Connect to AWS S3

    :returns: boto.s3.connection
    """
    try:
        return boto.connect_s3(
            aws_access_key_id=config_handler.get_environment_option(
                'access-key-id'),
            aws_secret_access_key=config_handler.get_environment_option(
                'secret-access-key'))
    except Exception, err:
        logger.error('A problem occurred connecting to AWS S3: {}'.format(err))
        sys.exit(1)


def connect_cloudformation(environment):
    """ Connect to AWS CloudFormation

    :returns: boto.cloudformation.connection
    """
    try:
        return cloudformation.connect_to_region(
            config_handler.get_environment_option('region'),
            aws_access_key_id=config_handler.get_environment_option(
                'access-key-id'),
            aws_secret_access_key=config_handler.get_environment_option(
                'secret-access-key'))
    except Exception, err:
        logger.error(
            'A problem occurred connecting to AWS CloudFormation: {}'.format(
                err))
        sys.exit(1)
