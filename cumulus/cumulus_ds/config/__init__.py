""" Configuration management """
import logging

from cumulus_ds.config import config_file
from cumulus_ds.config import command_line_options
from cumulus_ds.exceptions import ConfigurationException

LOGGER = logging.getLogger(__name__)

CONF = config_file.configure(command_line_options.ARGS.config)
ENVIRONMENT = command_line_options.ARGS.environment


def get_config():
    """ Returns the configuration object

    :returns: dict
    """
    return CONF


def get_environment():
    """ Returns the environment name

    :returns: str or None
    """
    return ENVIRONMENT


def get_bundle_path_rewrites(bundle):
    """ Returns a dict with all path rewrites

    :type bundle: str
    :param bundle: Bundle name
    :returns: dict
    """
    try:
        return CONF['bundles'][bundle]['path-rewrites']
    except KeyError:
        return {}


def get_bundle_paths(bundle):
    """ Returns a list of bundle paths for a given bundle

    :type bundle: str
    :param bundle: Bundle name
    :returns: list
    """
    try:
        return CONF['bundles'][bundle]['paths']
    except KeyError:
        LOGGER.error('No paths defined for bundle "{}"'.format(bundle))
        raise ConfigurationException(
            'No paths defined for bundle "{}"'.format(bundle))


def get_bundles():
    """ Returns a list of bundles"""
    try:
        bundles = CONF['environments'][ENVIRONMENT]['bundles']
    except KeyError:
        LOGGER.warning(
            'No bundles found for environment {}'.format(ENVIRONMENT))
        return None

    # Check that the bundles are configured
    for bundle in bundles:
        if not bundle:
            bundles.remove(bundle)
            continue

        if bundle not in CONF['bundles']:
            bundles.remove(bundle)
            LOGGER.warning(
                'No matching configuration for bundle "{}"!'.format(bundle))

    return bundles


def get_environment_option(option_name):
    """ Returns version number

    :returns: str
    """
    try:
        return CONF['environments'][ENVIRONMENT][option_name]
    except KeyError:
        LOGGER.error('No option {} in environment {}'.format(
            option_name, ENVIRONMENT))
        return None


def get_log_level():
    """ Returns the log level

    :returns: str
    """
    try:
        return CONF['general']['log-level']
    except KeyError:
        return 'DEBUG'


def get_post_bundle_hook(bundle):
    """ Returns the post bundle hook command or None

    :type bundle: str
    :param bundle: Bundle name
    :returns: str or None
    """
    try:
        return CONF['bundles'][bundle]['post-bundle-hook']
    except KeyError:
        return None


def get_post_deploy_hook():
    """ Returns the post deploy hook command or None

    :returns: str or None
    """
    try:
        return CONF['environments'][ENVIRONMENT]['post-deploy-hook']
    except KeyError:
        return None


def get_pre_built_bundle_path(bundle):
    """ Return the path to the pre-built bundle

    :type bundle: str
    :param bundle: Bundle name
    :returns: str -- Path to the pre-built bundle
    """
    try:
        return str(CONF['bundles'][bundle]['pre-built-bundle'])
    except KeyError:
        LOGGER.error('No pre-built bundle path found for "{}"'.format(bundle))
        raise ConfigurationException(
            'No pre-built bundle path found for "{}"'.format(bundle))


def get_pre_deploy_hook():
    """ Returns the pre deploy hook command or None

    :returns: str or None
    """
    try:
        return CONF['environments'][ENVIRONMENT]['pre-deploy-hook']
    except KeyError:
        return None


def get_pre_bundle_hook(bundle):
    """ Returns the pre bundle hook command or None

    :type bundle: str
    :param bundle: Bundle name
    :returns: str or None
    """
    try:
        return CONF['bundles'][bundle]['pre-bundle-hook']
    except KeyError:
        return None


def get_stack_disable_rollback(stack):
    """ See if we should disable rollback

    :type stack: str
    :param stack: Stack name
    :returns: bool -- Disable rollback?
    """
    try:
        return CONF['stacks'][stack]['disable-rollback']
    except KeyError:
        raise ConfigurationException(
            'Stack template not found in configuration')


def get_stack_parameters(stack):
    """ Return the stack parameters

    :type stack: str
    :param stack: Stack name
    :returns: list -- All stack parameters
    """
    try:
        return CONF['stacks'][stack]['parameters']
    except KeyError:
        return []


def get_stack_tags(stack):
    """ Return the stack tags

    :type stack: str
    :param stack: Stack name
    :returns: list -- All stack tags
    """
    try:
        return CONF['stacks'][stack]['tags']
    except KeyError:
        return None


def get_stack_template(stack):
    """ Return the path to the stack template

    :type stack: str
    :param stack: Stack name
    :returns: str -- Stack template path
    """
    try:
        return CONF['stacks'][stack]['template']
    except KeyError:
        raise ConfigurationException(
            'Stack template not found in configuration for stack {}'.format(
                stack))


def get_stack_timeout_in_minutes(stack):
    """ Return stack creation timeout

    :type stack: str
    :param stack: Stack name
    :returns: int -- Stack creation timeout in minutes
    """
    try:
        timeout = int(CONF['stacks'][stack]['timeout-in-minutes'])
    except KeyError:
        raise ConfigurationException(
            'Stack timeout not found in configuration')

    if timeout == 0:
        return None
    return timeout


def get_stacks():
    """ Returns a list of stacks """
    try:
        return CONF['stacks'].keys()
    except KeyError:
        LOGGER.warning(
            'No stacks found for environment {}'.format(ENVIRONMENT))
        return None


def has_pre_built_bundle(bundle):
    """ Checks wether or not the bundle has a pre-built-bundle flag

    :type bundle: str
    :param bundle: Bundle name
    :returns: bool -- True if there is a pre-built-bundle
    """
    if 'pre-built-bundle' in CONF['bundles'][bundle]:
        return True
    return False
