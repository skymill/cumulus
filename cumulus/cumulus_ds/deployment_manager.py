""" Manager """
import json
import logging
import os.path
import subprocess
import time
from datetime import datetime, timedelta

import boto

from cumulus_ds import config_handler
from cumulus_ds import connection_handler
from cumulus_ds.exceptions import (
    InvalidTemplateException,
    HookExecutionException)

LOGGER = logging.getLogger(__name__)


def deploy():
    """ Ensure stack is up and running (create or update it) """
    # Run pre-deploy-hook
    _pre_deploy_hook()

    stacks = config_handler.get_stacks()
    if not stacks:
        LOGGER.warning('No stacks configured, nothing to deploy')
        return
    for stack in stacks:
        _ensure_stack(
            stack,
            config_handler.get_stack_template(stack),
            disable_rollback=config_handler.get_stack_disable_rollback(
                stack),
            parameters=config_handler.get_stack_parameters(stack),
            timeout_in_minutes=config_handler.get_stack_timeout_in_minutes(
                stack),
            tags=config_handler.get_stack_tags(stack))

    # Run post-deploy-hook
    _post_deploy_hook()


def list_events():
    """ List events """
    try:
        con = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack_name in config_handler.get_stacks():
        stack = _get_stack_by_name(stack_name)
        written_events = []

        if not stack:
            break

        _print_event_log_title()

        for event in reversed(con.describe_stack_events(stack.stack_id)):
            if event.event_id not in written_events:
                written_events.append(event.event_id)
                _print_event_log_event(event)


def list_stacks():
    """ List stacks and their statuses """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in connection.list_stacks():
        if (stack.stack_status != 'DELETE_COMPLETE' and
                stack.stack_name in config_handler.get_stacks()):
            print('{:<30}{}'.format(stack.stack_name, stack.stack_status))


def undeploy():
    """ Undeploy an environment """
    message = (
        'This will DELETE all stacks in the environment. '
        'This action cannot be undone. '
        'Are you sure you want to do continue? [N/y] ')
    choice = raw_input(message).lower()
    if choice in ['yes', 'y']:
        stacks = config_handler.get_stacks()
        stacks.reverse()
        for stack in stacks:
            _delete_stack(stack)
    else:
        print('Skipping undeployment.')


def validate_templates():
    """ Validate the template """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in config_handler.get_stacks():
        template = config_handler.get_stack_template(stack)

        result = connection.validate_template(
            _get_json_from_template(template))
        if result:
            LOGGER.info('Template {} is valid!'.format(template))


def _ensure_stack(
        stack_name, template,
        disable_rollback=False, parameters=[],
        timeout_in_minutes=None, tags=None):
    """ Ensure stack is up and running (create or update it)

    :type stack_name: str
    :param stack_name: Stack name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    :type parameters: list
    :param parameters: List of tuples with CF parameters
    :type timeout_in_minutes: int or None
    :param timeout_in_minutes:
        Consider the stack FAILED if creation takes more than x minutes
    :type tags: dict or None
    :param tags: Dictionary of keys and values to use as CloudFormation tags
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    LOGGER.info('Ensuring stack {} with template {}'.format(
        stack_name, template))

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
            'CumulusVersion',
            config_handler.get_environment_option('version')
        )
    ]

    if timeout_in_minutes:
        LOGGER.debug('Will time out stack creation after {:d} minutes'.format(
            timeout_in_minutes))

    for parameter in cumulus_parameters + parameters:
        LOGGER.debug(
            'Adding parameter "{}" with value "{}" to CF template'.format(
                parameter[0], parameter[1]))

    try:
        if _stack_exists(stack_name):
            LOGGER.debug('Updating existing stack to version {}'.format(
                config_handler.get_environment_option('version')))

            if template[0:4] == 'http':
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)

            _wait_for_stack_complete(stack_name, filter_type='UPDATE')
        else:
            LOGGER.debug('Creating new stack with version {}'.format(
                config_handler.get_environment_option('version')))
            if template[0:4] == 'http':
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)

            _wait_for_stack_complete(stack_name, filter_type='CREATE')

    except ValueError as error:
        raise InvalidTemplateException(
            'Malformatted template: {}'.format(error))
    except boto.exception.BotoServerError as error:
        code = eval(error.error_message)['Error']['Code']
        message = eval(error.error_message)['Error']['Message']

        if code == 'ValidationError':
            if message == 'No updates are to be performed.':
                # Do not raise this exception if it is due to lack of updates
                # We do not want to fail any other stack updates after this
                # stack
                LOGGER.warning(
                    'No CloudFormation updates are to be '
                    'performed for {}'.format(stack_name))
                return

        LOGGER.error('Boto exception {}: {}'.format(code, message))
        return


def _delete_stack(stack):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    LOGGER.info('Deleting stack {}'.format(stack))
    connection.delete_stack(stack)
    _wait_for_stack_complete(stack, filter_type='DELETE')


def _get_json_from_template(template):
    """ Returns a JSON string given a template file path

    :type template: str
    :param template: Template path to use
    :returns: JSON object
    """
    template_path = os.path.expandvars(os.path.expanduser(template))
    LOGGER.debug('Parsing template file {}'.format(template_path))

    file_handle = open(template_path)
    json_data = json.dumps(json.loads(file_handle.read()))
    file_handle.close()

    return json_data


def _get_stack_by_name(stack_name):
    """ Returns a stack given its name

    :type stack_name: str
    :param stack_name: Stack name
    :returns: stack or None
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

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

    LOGGER.info('Running pre-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The pre-deploy-hook returned a non-zero exit code: {}'.format(
                error))


def _print_event_log_event(event):
    """ Print event log row to stdout

    :type event: event object
    :param event: CloudFormation event object
    """
    # Colorize status
    event_status = event.resource_status.split('_')
    if event_status[len(event_status) - 1] == 'COMPLETE':
        # Green text
        status = '\033[92m' + event.resource_status + '\033[0m'
    elif event_status[len(event_status) - 1] == 'PROGRESS':
        # Blue text
        status = '\033[94m' + event.resource_status + '\033[0m'
    elif event_status[len(event_status) - 1] == 'FAILED':
        # Red text
        status = '\033[91m' + event.resource_status + '\033[0m'
    else:
        status = event.resource_status

    print((
        '{timestamp:<20} | {type:<45} | '
        '{logical_id:<42} | {status:<25}').format(
            timestamp=datetime.strftime(
                event.timestamp,
                '%Y-%m-%dT%H:%M:%S'),
            type=event.resource_type,
            logical_id=event.logical_resource_id,
            status=status))


def _print_event_log_separator():
    """ Print separator line for the event log """
    print((
        '---------------------+---------------'
        '--------------------------------+----------'
        '----------------------------------+--------'
        '------------'))


def _print_event_log_title():
    """ Print event log title row on stdout """
    _print_event_log_separator()
    print((
        '{timestamp:<20} | {type:<45} | '
        '{logical_id:<42} | {status:<25}'.format(
            timestamp='Timestamp',
            type='Resource type',
            logical_id='Logical ID',
            status='Status')))
    _print_event_log_separator()


def _post_deploy_hook():
    """ Execute a post-deploy-hook """
    command = config_handler.get_post_deploy_hook()

    if not command:
        return None

    LOGGER.info('Running post-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The post-deploy-hook returned a non-zero exit code: {}'.format(
                error))


def _stack_exists(stack_name):
    """ Check if a stack exists

    :type stack_name: str
    :param stack_name: Stack name
    :returns: bool
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in connection.list_stacks():
        if (stack.stack_status != 'DELETE_COMPLETE' and
                stack.stack_name == stack_name):
            return True

    return False


def _wait_for_stack_complete(stack_name, check_interval=5, filter_type=None):
    """ Wait until the stack create/update has been completed

    :type stack_name: str
    :param stack_name: Stack name
    :type check_interval: int
    :param check_interval: Seconds between each console update
    :type filter_type: str
    :param filter_type: Filter events by type. Supported values are None,
        CREATE, DELETE, UPDATE. Rollback events are always shown.
    """
    start_time = datetime.utcnow() - timedelta(0, 10)
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
    try:
        con = connection_handler.connect_cloudformation()
    except Exception:
        raise

    written_events = []

    while not complete:
        stack = _get_stack_by_name(stack_name)
        if not stack:
            _print_event_log_separator()
            break

        if not written_events:
            _print_event_log_title()

        for event in reversed(con.describe_stack_events(stack.stack_id)):
            # Don't print written events
            if event.event_id in written_events:
                continue

            # Don't print old events
            if event.timestamp < start_time:
                continue

            written_events.append(event.event_id)

            event_type, _ = event.resource_status.split('_', 1)
            log = False
            if not filter_type:
                log = True
            elif (filter_type == 'CREATE'
                    and event_type in ['CREATE', 'ROLLBACK']):
                log = True
            elif (filter_type == 'DELETE'
                    and event_type in ['DELETE', 'ROLLBACK']):
                log = True
            elif (filter_type == 'UPDATE'
                    and event_type in ['UPDATE', 'ROLLBACK']):
                log = True

            if not log:
                continue

            _print_event_log_event(event)

        if stack.stack_status in complete_statuses:
            _print_event_log_separator()
            LOGGER.info('Stack {} - Stack completed with status {}'.format(
                stack.stack_name,
                stack.stack_status))
            complete = True

        time.sleep(check_interval)
