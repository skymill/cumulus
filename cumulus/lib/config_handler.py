""" Configuration handler """
import argparse
import logging
import os
import os.path
import sys
from ConfigParser import SafeConfigParser, NoOptionError

logger = logging.getLogger(__name__)

# Read arguments from the command line
parser = argparse.ArgumentParser(
    description='Cumulus cloud management tool')
general_ag = parser.add_argument_group('General options')
general_ag.add_argument(
    '-e', '--environment',
    required=True,
    help='Environment to use')
actions_ag = parser.add_argument_group('Actions')
actions_ag.add_argument(
    '--bundle',
    action='count',
    help='Build and upload bundles to AWS S3')
actions_ag.add_argument(
    '--deploy',
    action='count',
    help='Deploy all stacks in the environment')
actions_ag.add_argument(
    '--validate-templates',
    action='count',
    help='Validate all templates for the environment')
#actions_ag.add_argument(
#    '--undeploy',
#    action='count',
#    help='Undeploy (DELETE) all stacks in the environment')
args = parser.parse_args()

# Environment name
environment = args.environment

# Initial configuration object
conf = {
    'environments': {},
    'stacks': {},
    'bundles': {}
}

# Options per section
# [(option, required)]
stack_options = [
    ('template', True),
    ('disable-rollback', True)
]
bundle_options = [
    ('paths', True)
]
env_options = [
    ('access-key-id', True),
    ('secret-access-key', True),
    ('bucket', True),
    ('region', True),
    ('stacks', True),
    ('bundles', True),
    ('version', True),
]


def configure():
    """ Constructor """
    _read_global_configuration_file()


def get_config():
    """ Returns the configuration object

    :returns: dict
    """
    return conf


def get_environment():
    """ Returns the environment name

    :returns: str or None
    """
    return environment


def get_bundle_paths(bundle):
    """ Returns a list of bundle paths for a given bundle

    :type bundle: str
    :param bundle: Bundle name
    :returns: list
    """
    try:
        return conf['bundles'][bundle]['paths']
    except KeyError:
        return None


def get_bundles():
    """ Returns a list of bundles"""
    try:
        return conf['environments'][environment]['bundles']
    except KeyError:
        logger.warning(
            'No bundles found for environment {}'.format(environment))
        return None


def get_environment_option(option_name):
    """ Returns version number

    :returns: str
    """
    try:
        return conf['environments'][environment][option_name]
    except KeyError:
        logger.error('No option {} in environment {}'.format(
            option_name, environment))
        return None


def get_stack_disable_rollback(stack):
    """ See if we should disable rollback

    :type stack: str
    :param stack: Stack name
    :returns: bool -- Disable rollback?
    """
    try:
        return conf['stacks'][stack]['disable-rollback']
    except KeyError:
        logger.error('Stack template not found in configuration')
        sys.exit(1)


def get_stack_template(stack):
    """ Return the path to the stack template

    :type stack: str
    :param stack: Stack name
    :returns: str -- Stack template path
    """
    try:
        return conf['stacks'][stack]['template']
    except KeyError:
        logger.error('Stack template not found in configuration')
        sys.exit(1)


def get_stacks():
    """ Returns a list of stacks """
    try:
        return conf['environments'][environment]['stacks']
    except KeyError:
        logger.warning(
            'No stacks found for environment {}'.format(environment))
        return None


def _read_global_configuration_file():
    """ Read global configuration file """
    config_files = [
        '/etc/cumulus.conf',
        os.path.expanduser('~/.cumulus.conf'),
        '{}/cumulus.conf'.format(os.curdir)
    ]

    # Read config file
    conf_file_found = False
    for conf_file in config_files:
        if os.path.exists(conf_file):
            conf_file_found = True
            logger.info('Reading configuration from {}'.format(conf_file))
    if not conf_file_found:
        logger.error('No configuration file found. Looked for {}'.format(
            ', '.join(config_files)))
        sys.exit(1)

    config = SafeConfigParser()
    config.read(config_files)

    # Populate environments
    for section in config.sections():
        if section.startswith('environment: '):
            env = section.split(': ')[1]
            conf['environments'][env] = {}

            for option, required in env_options:
                try:
                    if option == 'bundles':
                        bundles = []
                        for item in config.get(section, option).split(','):
                            bundles.append(item.strip())
                        conf['environments'][env][option] = bundles
                    elif option == 'stacks':
                        stacks = []
                        for item in config.get(section, option).split(','):
                            stacks.append(item.strip())
                        conf['environments'][env][option] = stacks
                    else:
                        conf['environments'][env][option] = \
                            config.get(section, option)
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)
                    else:
                        conf['environments'][env][option] = None

    # Populate stacks
    for section in config.sections():
        if section.startswith('stack: '):
            stack = section.split(': ')[1]
            conf['stacks'][stack] = {}

            for option, required in stack_options:
                try:
                    if option == 'disable-rollback':
                        conf['stacks'][stack][option] = config.getboolean(
                            section, option)
                    else:
                        conf['stacks'][stack][option] = config.get(
                            section, option)
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)
                    else:
                        conf['environments'][stack][option] = None

    # Populate bundles
    for section in config.sections():
        if section.startswith('bundle: '):
            bundle = section.split(': ')[1]
            conf['bundles'][bundle] = {}

            for option, required in bundle_options:
                try:
                    raw_paths = config.get(section, option)\
                        .replace('\n', '')\
                        .split(',')
                    paths = []
                    for path in raw_paths:
                        paths.append(path.strip())

                    conf['bundles'][bundle][option] = paths
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)
                    else:
                        conf['environments'][bundle][option] = None
