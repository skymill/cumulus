""" Manager """
import json
import logging
import os.path
import subprocess
import sys
import time

import boto

import config_handler
import connection_handler

logger = logging.getLogger(__name__)


def deploy():
    """ Ensure stack is up and running (create or update it) """
    # Run pre-deploy-hook
    _pre_deploy_hook()

    for stack in config_handler.get_stacks():
            _ensure_stack(
                stack,
                config_handler.get_environment(),
                config_handler.get_stack_template(stack),
                disable_rollback=config_handler.get_stack_disable_rollback(
                    stack),
                parameters=config_handler.get_stack_parameters(stack))

    # Run post-deploy-hook
    _post_deploy_hook()


def undeploy():
    """ Undeploy an environment """
    message = (
        'This will DELETE all stacks in the environment. '
        'This action cannot be undone. '
        'Are you sure you want to do continue? [N/y] ')
    choice = raw_input(message).lower()
    if choice in ['yes', 'y']:
        for stack in config_handler.get_stacks():
            _delete_stack(stack)
    else:
        print('Skipping undeployment.')


def validate_templates():
    """ Validate the template """
    connection = connection_handler.connect_cloudformation()
    for stack in config_handler.get_stacks():
        template = config_handler.get_stack_template(stack)

        result = connection.validate_template(
            _get_json_from_template(template))
        if result:
            logger.info('Template {} is valid!'.format(template))


def _ensure_stack(
        stack, environment, template,
        disable_rollback=False, parameters=[]):
    """ Ensure stack is up and running (create or update it)

    :type stack: str
    :param stack: Stack name
    :type environment: str
    :param environment: Environment name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    :type parameters: list
    :param parameters: List of tuples with CF parameters
    """
    connection = connection_handler.connect_cloudformation()
    logger.info('Ensuring stack {} with template {}'.format(
        stack, os.path.basename(template)))

    cumulus_parameters = [
        (
            'CumulusBundleBucket',
            config_handler.get_environment_option('bucket')
        ),
        (
            'CumulusEnvironment',
            config_handler.get_environment()
        ),
        (
            'CumulusEnvironment',
            config_handler.get_environment()
        ),
        (
            'CumulusVersion',
            config_handler.get_environment_option('version')
        )
    ]

    try:
        if stack in connection.list_stacks():
            connection.update_stack(
                stack,
                parameters=cumulus_parameters + parameters,
                template_body=_get_json_from_template(template),
                disable_rollback=disable_rollback,
                capabilities=['CAPABILITY_IAM'])
        else:
            connection.create_stack(
                stack,
                parameters=cumulus_parameters + parameters,
                template_body=_get_json_from_template(template),
                disable_rollback=disable_rollback,
                capabilities=['CAPABILITY_IAM'])

        _wait_for_stack_complete(stack)

    except ValueError, error:
        logger.error('Malformatted template: {}'.format(error))
        sys.exit(1)
    except boto.exception.BotoServerError, error:
        logger.error("ERROR - Boto exception: {}".format(error))
        logger.error("Enable debug in manage.py to see more details")


def _delete_stack(stack):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    """
    connection = connection_handler.connect_cloudformation()
    logger.info('Deleting stack {}'.format(stack))
    connection.delete_stack(stack)
    _wait_for_stack_complete(stack)


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


def _get_stack_by_name(stack_name):
    """ Returns a stack given its name

    :type stack_name: str
    :param stack_name: Stack name
    :returns: stack or None
    """
    connection = connection_handler.connect_cloudformation()
    for stack in connection.list_stacks():
        if (stack.stack_status != 'DELETE_COMPLETE' and
                stack.stack_name == stack_name):
            return stack

    return None


def _pre_deploy_hook():
    """ Execute a pre-deploy-hook """
    command = config_handler.get_pre_deploy_hook()

    if not command:
        return None

    logger.info('Running pre-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        logger.error(
            'The pre-deploy-hook returned a non-zero exit code: {}'.format(
                error))
        sys.exit(1)


def _post_deploy_hook():
    """ Execute a post-deploy-hook """
    command = config_handler.get_post_deploy_hook()

    if not command:
        return None

    logger.info('Running post-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        logger.error(
            'The post-deploy-hook returned a non-zero exit code: {}'.format(
                error))
        sys.exit(1)


def _wait_for_stack_complete(stack_name, check_interval=5):
    """ Wait until the stack create/update has been completed

    :type stack_name: str
    :param stack_name: Stack name
    :type check_interval: int
    :param check_interval: Seconds between each console update
    """
    complete = False
    complete_statuses = [
        'CREATE_FAILED',
        'CREATE_COMPLETE',
        'ROLLBACK_FAILED',
        'ROLLBACK_COMPLETE',
        'DELETE_FAILED',
        'DELETE_COMPLETE',
        'UPDATE_COMPLETE',
        'UPDATE_ROLLBACK_FAILED',
        'UPDATE_ROLLBACK_COMPLETE'
    ]
    connection = connection_handler.connect_cloudformation()
    written_events = []

    while not complete:
        stack = _get_stack_by_name(stack_name)
        if stack.stack_status in complete_statuses:
            logger.info('Stack completed with status {}'.format(
                stack.stack_status))
            complete = True
        else:
            for event in connection.describe_stack_events(stack.stack_id):
                if event.event_id not in written_events:
                    written_events.append(event.event_id)
                    logger.info('Stack {} - {} - {}'.format(
                        event.stack_name,
                        event.resource_type,
                        event.resource_status))

        time.sleep(check_interval)
