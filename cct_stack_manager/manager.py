""" Manager """
import json
import os.path
import sys

import boto

import connector
from logger import logger


def _get_json_from_template(template):
    """ Returns a JSON string given a template file path

    :type template: str
    :param template: Template path to use
    :returns: JSON object
    """
    file_handle = open(template)
    json_data = json.dumps(json.loads(file_handle.read()))
    file_handle.close()
    return json_data


def create_stack(stack, environment, template, disable_rollback=False):
    """ Create a new stack

    :type stack: str
    :param stack: Stack name
    :type environment: str
    :param environment: Environment name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    """
    connection = connector.connect_to_cloudformation(environment)
    logger.info('Creating stack {} with template {}'.format(
        stack, os.path.basename(template)))

    try:
        connection.create_stack(
            stack,
            template_body=_get_json_from_template(template),
            disable_rollback=disable_rollback,
            capabilities=['CAPABILITY_IAM'])

        logger.info(
            'CloudFormation is now creating your stack. '
            'Please see the AWS Console for mode details.')
    except ValueError, error:
        logger.error('Malformatted template: {}'.format(error))
        sys.exit(1)
    except boto.exception.BotoServerError, error:
        logger.error("ERROR - Boto exception: {}".format(error))
        logger.error("Enable debug in manage.py to see more details")


def delete_stack(stack, environment):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    :type environment: str
    :param environment: Environment name
    """
    connection = connector.connect_to_cloudformation(environment)
    logger.info('Deleting stack {}'.format(stack))
    connection.delete_stack()


def list_stacks(environment):
    """ List stacks in the environment

    :type environment: str
    :param environment: Environment name
    """
    connection = connector.connect_to_cloudformation(environment)
    logger.info('Current stacks: {}'.format(
        ', '.join(connection.list_stacks())))


def update_stack(stack, environment, template, disable_rollback=False):
    """ Update an existing stack

    :type stack: str
    :param stack: Stack name
    :type environment: str
    :param environment: Environment name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    """
    connection = connector.connect_to_cloudformation(environment)
    logger.info('Updating stack {} with template {}'.format(
        stack, os.path.basename(template)))

    try:
        connection.update_stack(
            stack,
            template_body=_get_json_from_template(template),
            disable_rollback=disable_rollback,
            capabilities=['CAPABILITY_IAM'])

        logger.info(
            'CloudFormation is now updating your stack. '
            'Please see the AWS Console for mode details.')
    except ValueError, error:
        logger.error('Malformatted template: {}'.format(error))
        sys.exit(1)
    except boto.exception.BotoServerError, error:
        logger.error("ERROR - Boto exception: {}".format(error))
        logger.error("Enable debug in manage.py to see more details")


def validate_template(environment, template):
    """ Validate the template

    :type environment: str
    :param environment: Environment name
    :type template: str
    :param template: Template path to use
    """
    connection = connector.connect_to_cloudformation(environment)
    result = connection.validate_template(_get_json_from_template(template))
    if result:
        logger.info('Template {} is valid'.format(os.path.basename(template)))
