""" The deployment manager handles all deployments of CloudFormation stacks """
import logging
import subprocess

from cumulus_ds import config
from cumulus_ds import terminal_size
from cumulus_ds.helpers.stack import (
    delete_stack,
    ensure_stack,
    list_events_all_stacks,
    list_all_stacks,
    validate_templates_all_stacks)
from cumulus_ds.exceptions import HookExecutionException

LOGGER = logging.getLogger(__name__)

TERMINAL_WIDTH, _ = terminal_size.get_terminal_size()


def deploy():
    """ Ensure stack is up and running (create or update it) """
    # Run pre-deploy-hook
    _pre_deploy_hook()

    stack_names = config.get_stacks()

    if not stack_names:
        LOGGER.warning('No stacks configured, nothing to deploy')
        return

    for stack_name in stack_names:
        ensure_stack(
            stack_name,
            template=config.get_stack_template(stack_name),
            disable_rollback=config.get_stack_disable_rollback(
                stack_name),
            parameters=config.get_stack_parameters(stack_name),
            timeout_in_minutes=config.get_stack_timeout_in_minutes(
                stack_name),
            tags=config.get_stack_tags(stack_name))

    # Run post-deploy-hook
    _post_deploy_hook()


def list_events():
    """ List events """
    list_events_all_stacks()


def list_stacks():
    """ List stacks and their statuses """
    list_all_stacks()


def undeploy(force=False):
    """ Undeploy an environment

    :type force: bool
    :param force: Skip the safety question
    """
    message = (
        'This will DELETE all stacks in the environment. '
        'This action cannot be undone. '
        'Are you sure you want to do continue? [N/y] ')

    choice = 'yes'
    if not force:
        choice = raw_input(message).lower()
        if choice not in ['yes', 'y']:
            print('Skipping undeployment.')
            return None

    stacks = config.get_stacks()
    stacks.reverse()

    if not stacks:
        LOGGER.warning('No stacks to undeploy.')
        return None

    for stack in stacks:
        delete_stack(stack)


def validate_templates():
    """ Validate the template """
    validate_templates_all_stacks()


def _pre_deploy_hook():
    """ Execute a pre-deploy-hook """
    command = config.get_pre_deploy_hook()

    if not command:
        return None

    LOGGER.info('Running pre-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The pre-deploy-hook returned a non-zero exit code: {}'.format(
                error))


def _post_deploy_hook():
    """ Execute a post-deploy-hook """
    command = config.get_post_deploy_hook()

    if not command:
        return None

    LOGGER.info('Running post-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The post-deploy-hook returned a non-zero exit code: {}'.format(
                error))
