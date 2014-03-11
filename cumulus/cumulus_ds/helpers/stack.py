""" Stack helpers """
import json
import logging
import sys
import time
from datetime import datetime, timedelta

import boto

from cumulus_ds import connection_handler
from cumulus_ds import terminal_size
from cumulus_ds.config import CONFIG as config
from cumulus_ds.exceptions import InvalidTemplateException

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

LOGGER = logging.getLogger(__name__)
CONNECTION = connection_handler.connect_cloudformation()
TERMINAL_WIDTH, _ = terminal_size.get_terminal_size()

# Valid statuses for instances that are actually running
# all statuses except (DELETE_COMPLETE)
RUNNING_STATUSES = [
    'CREATE_IN_PROGRESS',
    'CREATE_FAILED',
    'CREATE_COMPLETE',
    'ROLLBACK_IN_PROGRESS',
    'ROLLBACK_FAILED',
    'ROLLBACK_COMPLETE',
    'DELETE_IN_PROGRESS',
    'DELETE_FAILED',
    'UPDATE_IN_PROGRESS',
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
    'UPDATE_COMPLETE',
    'UPDATE_ROLLBACK_IN_PROGRESS',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
    'UPDATE_ROLLBACK_COMPLETE'
]


def delete_stack(stack):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    """
    LOGGER.info('Deleting stack {}'.format(stack))
    CONNECTION.delete_stack(stack)
    _wait_for_stack_complete(stack, filter_type='DELETE')


def ensure_stack(
        stack_name, parameters, template, tags=None, disable_rollback=False,
        timeout_in_minutes=None, capabilities=['CAPABILITY_IAM']):
    """ Ensure that a CloudFormation stack is running

    If the stack does not exist, it will be created. If the stack exists
    it will be updated.

    :type stack_name: str
    :param stack_name: Name of the stack to ensure
    :type parameters: list
    :param parameters: List of tuples with parameters and values
    :type template: str
    :parameter template: Template in JSON string or a HTTP URL
    :type tags: dict
    :param tags: Dict with keys and values
    :type disable_rollback: bool
    :param disable_rollback: Disable rollbacks of failed creates/updates
    :type timeout_in_minutes: int
    :parameter timeout_in_minutes: Timeout the stack creation after x minutes
    :type capabilities: list
    :parameter capabilities: The list of capabilities you want to allow in the
        stack. Currently, the only valid capability is 'CAPABILITY_IAM'
    """
    LOGGER.info('Ensuring stack {} with template {}'.format(
        stack_name, template))

    cumulus_parameters = [
        ('CumulusBundleBucket', config.get_environment_option('bucket')),
        ('CumulusEnvironment', config.get_environment()),
        ('CumulusVersion', config.get_environment_option('version'))
    ]

    for parameter in cumulus_parameters + parameters:
        LOGGER.debug(
            'Adding parameter "{}" with value "{}" to CF template'.format(
                parameter[0], parameter[1]))

    if timeout_in_minutes:
        LOGGER.debug('Will time out stack creation after {:d} minutes'.format(
            timeout_in_minutes))

    try:
        if stack_exists(stack_name):
            LOGGER.debug('Updating existing stack to version {}'.format(
                config.get_environment_option('version')))

            if template[0:4] == 'http':
                CONNECTION.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                CONNECTION.update_stack(
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
                config.get_environment_option('version')))
            if template[0:4] == 'http':
                CONNECTION.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                CONNECTION.create_stack(
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
        if (error.error_code == 'ValidationError' and
                error.error_message == 'No updates are to be performed.'):
            # Do not raise this exception if it is due to lack of updates
            # We do not want to fail any other stack updates after this
            # stack
            LOGGER.warning(
                'No CloudFormation updates are to be '
                'performed for {}'.format(stack_name))
            return

        LOGGER.error('Boto exception {}: {}'.format(
            error.error_code, error.error_message))
        return

    _print_stack_output(stack_name)


def get_stack_by_name(stack_name):
    """ Returns a stack given its name

    :type stack_name: str
    :param stack_name: Stack name
    :returns: stack or None
    """
    for stack in CONNECTION.list_stacks(RUNNING_STATUSES):
        if stack.stack_name == stack_name:
            return stack

    return None


def list_events_all_stacks():
    """ List events for all configured stacks """
    for stack_name in config.get_stacks():
        stack = get_stack_by_name(stack_name)

        if not stack:
            break

        _print_event_log_title()

        written_events = []
        for event in reversed(CONNECTION.describe_stack_events(stack.stack_id)):
            if event.event_id not in written_events:
                written_events.append(event.event_id)
                _print_event_log_event(event)


def list_all_stacks():
    """ List stacks and their statuses """
    cf_stacks = CONNECTION.list_stacks()

    for stack in config.get_stacks():
        stack_found = False
        for cf_stack in cf_stacks:
            if stack == cf_stack.stack_name:
                stack_found = True

        if stack_found:
            print('{:<30}{}'.format(stack, cf_stack.stack_status))
        else:
            print('{:<30}{}'.format(stack, 'NOT_RUNNING'))


def print_output_all_stacks():
    """ Print the output for all stacks """
    for stack in config.get_stacks():
        _print_stack_output(stack)


def stack_exists(stack_name):
    """ Check if a stack exists

    :type stack_name: str
    :param stack_name: Stack name
    :returns: bool
    """
    for stack in CONNECTION.list_stacks(RUNNING_STATUSES):
        if stack.stack_name == stack_name:
            return True

    return False


def validate_templates_all_stacks():
    """ Validate the template for all stacks"""
    for stack in config.get_stacks():
        template = config.get_stack_template(stack)

        result = CONNECTION.validate_template(_get_json_from_template(template))
        if result:
            LOGGER.info('Template {} is valid!'.format(template))


def _get_stack_outputs(stack_name_or_id):
    """ Get a list of stack output values

    :type stack_name_or_id: str
    :param stack_name_or_id: Stack name or id
    :returns: list -- List of (key, value)
    """
    try:
        stack = CONNECTION.describe_stacks(stack_name_or_id)[0]
    except IndexError:
        LOGGER.debug(
            'No stack with name or id {} found'.format(stack_name_or_id))
        return []

    return stack.outputs


def _get_json_from_template(template):
    """ Returns a JSON string given a template file path

    :type template: str
    :param template: Template path to use
    :returns: JSON object
    """
    template_path = ospath.expandvars(ospath.expanduser(template))
    LOGGER.debug('Parsing template file {}'.format(template_path))

    file_handle = open(template_path)
    json_data = json.dumps(json.loads(file_handle.read()))
    file_handle.close()

    return json_data


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

    row = '{timestamp:<19}'.format(
        timestamp=datetime.strftime(event.timestamp, '%Y-%m-%d %H:%M:%S'))
    row += ' | {type:<45}'.format(type=event.resource_type)
    row += ' | {logical_id:<42}'.format(logical_id=event.logical_resource_id)

    if TERMINAL_WIDTH >= 190:
        if event.resource_status_reason:
            reason = event.resource_status_reason
        else:
            reason = ''

        row += ' | {reason:<36}'.format(reason=reason)

    row += ' | {status:<33}'.format(status=status.replace('_', ' ').lower())

    print(row)


def _print_event_log_separator():
    """ Print separator line for the event log """
    row = '--------------------'  # Timestamp
    row += '+-----------------------------------------------'  # Resource type
    row += '+--------------------------------------------'  # Logical ID

    if TERMINAL_WIDTH >= 190:
        row += '+--------------------------------------'  # Reason

    row += '+--------------------------------'  # Status

    print(row)


def _print_event_log_title():
    """ Print event log title row on stdout """
    _print_event_log_separator()

    row = '{timestamp:<19}'.format(timestamp='Timestamp')
    row += ' | {type:<45}'.format(type='Resource type')
    row += ' | {logical_id:<42}'.format(logical_id='Logical ID')
    if TERMINAL_WIDTH >= 190:
        row += ' | {reason:<36}'.format(reason='Reason')
    row += ' | {status:<25}'.format(status='Status')

    print(row)

    _print_event_log_separator()


def _print_stack_output(stack_name_or_id):
    """ Print the stack output for a given stack

    :type stack_name_or_id: str
    :param stack_name_or_id: Stack name
    :returns: None
    """
    LOGGER.debug('Printing output for stack "{}"'.format(stack_name_or_id))
    outputs = _get_stack_outputs(stack_name_or_id)

    if not outputs:
        LOGGER.debug('No outputs found for stack "{}"'.format(stack_name_or_id))
        return

    print(
        '--------------------+----------------------------------'
        '-------------------------------------------------------'
        '------------------------------------')
    print('{key_title:<19} | {value_title:<45}'.format(
        key_title='Tag',
        value_title='Value'))
    print(
        '--------------------+----------------------------------'
        '-------------------------------------------------------'
        '------------------------------------')
    for output in outputs:
        print('{key:<19} | {value:<45}'.format(
            key=output.key,
            value=output.value))
    print(
        '--------------------+----------------------------------'
        '-------------------------------------------------------'
        '------------------------------------')


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

    written_events = []

    while not complete:
        stack = get_stack_by_name(stack_name)
        if not stack:
            _print_event_log_separator()
            break

        if not written_events:
            _print_event_log_title()

        for event in reversed(CONNECTION.describe_stack_events(stack.stack_id)):
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
