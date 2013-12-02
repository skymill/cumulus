""" Manager """
import json
import logging
import subprocess
import time
from datetime import datetime

import boto

import config_handler
import connection_handler
from exceptions import InvalidTemplateException, HookExecutionException

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
        for stack in config_handler.get_stacks():
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
            logger.info('Template {} is valid!'.format(template))


def _ensure_stack(
        stack_name, environment, template,
        disable_rollback=False, parameters=[]):
    """ Ensure stack is up and running (create or update it)

    :type stack_name: str
    :param stack_name: Stack name
    :type environment: str
    :param environment: Environment name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    :type parameters: list
    :param parameters: List of tuples with CF parameters
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    logger.info('Ensuring stack {} with template {}'.format(
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
            'CumulusEnvironment',
            config_handler.get_environment()
        ),
        (
            'CumulusVersion',
            config_handler.get_environment_option('version')
        )
    ]

    for parameter in cumulus_parameters + parameters:
        logger.debug(
            'Adding parameter {} with value {} to CF template'.format(
                parameter[0], parameter[1]))

    try:
        if _stack_exists(stack_name):
            logger.debug('Updating existing stack to version {}'.format(
                config_handler.get_environment_option('version')))

            if template[0:4] == 'http':
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'])
            else:
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'])

            _wait_for_stack_complete(stack_name, filter_type='UPDATE')
        else:
            logger.debug('Creating new stack with version {}'.format(
                config_handler.get_environment_option('version')))
            if template[0:4] == 'http':
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'])
            else:
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'])

        _wait_for_stack_complete(stack_name, filter_type='CREATE')

    except ValueError, error:
        raise InvalidTemplateException(
            'Malformatted template: {}'.format(error))
    except boto.exception.BotoServerError, error:
        raise


def _delete_stack(stack):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    logger.info('Deleting stack {}'.format(stack))
    connection.delete_stack(stack)
    _wait_for_stack_complete(stack, filter_type='DELETE')


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

    logger.info('Running pre-deploy-hook command: "{}"'.format(command))
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


def _print_event_log_title():
    """ Print event log title row on stdout """
    print((
        '{timestamp:<20} | {type:<45} | '
        '{logical_id:<42} | {status:<25}'.format(
            timestamp='Timestamp',
            type='Resource type',
            logical_id='Logical ID',
            status='Status')))
    print((
        '---------------------+---------------'
        '--------------------------------------+----'
        '----------------------------------+--------'
        '-------------------'))


def _post_deploy_hook():
    """ Execute a post-deploy-hook """
    command = config_handler.get_post_deploy_hook()

    if not command:
        return None

    logger.info('Running post-deploy-hook command: "{}"'.format(command))
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
            break

        if stack.stack_status in complete_statuses:
            logger.info('Stack {} - Stack completed with status {}'.format(
                stack.stack_name,
                stack.stack_status))
            complete = True
        else:
            if written_events == []:
                _print_event_log_title()

            for event in reversed(con.describe_stack_events(stack.stack_id)):
                if event.event_id in written_events:
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

        time.sleep(check_interval)
