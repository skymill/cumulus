""" Connection handler """
import sys

from boto import cloudformation

import config_handler
from logger import logger


def connect_to_cloudformation(environment):
    """ Connect to AWS CloudFormation

    :type environment: str
    :param environment: Environment to use
    :returns: boto.cloudformation.connection
    """
    try:
        return cloudformation.connect_to_region(
            config_handler.get(environment, 'region'),
            aws_access_key_id=config_handler.get(
                environment, 'access-key-id'),
            aws_secret_access_key=config_handler.get(
                environment, 'secret-access-key'))
    except:
        logger.error('A problem occurred connecting to AWS CloudFormation')
        sys.exit(1)
