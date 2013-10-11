""" Configuration handler """
import argparse
import logging
import os
import os.path
import sys
from ConfigParser import SafeConfigParser, NoOptionError

logger = logging.getLogger(__name__)


# Get settings.conf
settings = SafeConfigParser()
settings.read(
    os.path.realpath('{}/settings.conf'.format(os.path.dirname(__file__))))

# Read arguments from the command line
parser = argparse.ArgumentParser(
    description='Cumulus cloud management tool')
general_ag = parser.add_argument_group('General options')
general_ag.add_argument(
    '-e', '--environment',
    help='Environment to use')
general_ag.add_argument(
    '--version',
    help=(
        'Environment version number. '
        'Overrides the version value from the configuration file'))
general_ag.add_argument(
    '--config',
    help='Path to configuration file.')
general_ag.add_argument(
    '--cumulus-version',
    action='count',
    help='Print cumulus version number')
actions_ag = parser.add_argument_group('Actions')
actions_ag.add_argument(
    '--bundle',
    action='count',
    help='Build and upload bundles to AWS S3')
actions_ag.add_argument(
    '--deploy',
    action='count',
    help='Bundle and deploy all stacks in the environment')
actions_ag.add_argument(
    '--deploy-without-bundling',
    action='count',
    help='Deploy all stacks in the environment, without bundling first')
actions_ag.add_argument(
    '--validate-templates',
    action='count',
    help='Validate all templates for the environment')
actions_ag.add_argument(
    '--undeploy',
    action='count',
    help='Undeploy (DELETE) all stacks in the environment')
args = parser.parse_args()

if args.cumulus_version:
    print('Cumulus version {}'.format(settings.get('general', 'version')))
    sys.exit(0)
elif not args.environment:
    print('--environment is required')
    sys.exit(1)

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
    ('disable-rollback', True),
    ('parameters', False)
]
bundle_options = [
    ('paths', True),
    ('pre-bundle-hook', False),
    ('post-bundle-hook', False)
]
env_options = [
    ('access-key-id', True),
    ('secret-access-key', True),
    ('bucket', True),
    ('region', True),
    ('stacks', True),
    ('bundles', True),
    ('version', False),
    ('pre-deploy-hook', False),
    ('post-deploy-hook', False)
]


def configure():
    """ Constructor """
    _read_configuration_files()


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
        logger.error('No paths defined for bundle "{}"'.format(bundle))
        sys.exit(1)


def get_bundles():
    """ Returns a list of bundles"""
    try:
        bundles = conf['environments'][environment]['bundles']
    except KeyError:
        logger.warning(
            'No bundles found for environment {}'.format(environment))
        return None

    # Check that the bundles are configured
    for bundle in bundles:
        if bundle not in conf['bundles']:
            logger.warning('No matching configuration for bundle "{}"!'.format(
                bundle))
            sys.exit(1)

    return bundles


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


def get_post_bundle_hook(bundle):
    """ Returns the post bundle hook command or None

    :type bundle: str
    :param bundle: Bundle name
    :returns: str or None
    """
    try:
        return conf['bundles'][bundle]['post-bundle-hook']
    except KeyError:
        return None


def get_post_deploy_hook():
    """ Returns the post deploy hook command or None

    :returns: str or None
    """
    try:
        return conf['environments'][environment]['post-deploy-hook']
    except KeyError:
        return None


def get_pre_deploy_hook():
    """ Returns the pre deploy hook command or None

    :returns: str or None
    """
    try:
        return conf['environments'][environment]['pre-deploy-hook']
    except KeyError:
        return None


def get_pre_bundle_hook(bundle):
    """ Returns the pre bundle hook command or None

    :type bundle: str
    :param bundle: Bundle name
    :returns: str or None
    """
    try:
        return conf['bundles'][bundle]['pre-bundle-hook']
    except KeyError:
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


def get_stack_parameters(stack):
    """ Return the stack parameters

    :type stack: str
    :param stack: Stack name
    :returns: list -- All stack parameters
    """
    try:
        return conf['stacks'][stack]['parameters']
    except KeyError:
        return []


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


def _read_configuration_files():
    """ Read global configuration file """
    config_files = [
        '/etc/cumulus.conf',
        os.path.expanduser('~/.cumulus.conf'),
        '{}/cumulus.conf'.format(os.curdir)
    ]

    # Add custom configuration file path
    if args.config:
        if os.path.exists(os.path.expanduser(args.config)):
            config_files.append(os.path.expanduser(args.config))
        else:
            logger.warning('Configuration file {} not found.'.format(
                os.path.expanduser(args.config)))

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

    _populate_environments(config)
    _populate_stacks(config)
    _populate_bundles(config)


def _populate_environments(config):
    """ Populate the environments config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
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
                    elif option == 'version':
                        if args.version:
                            conf['environments'][env][option] = args.version
                        else:
                            conf['environments'][env][option] = config.get(
                                section, option)
                    else:
                        conf['environments'][env][option] = \
                            config.get(section, option)
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)


def _populate_stacks(config):
    """ Populate the stacks config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section.startswith('stack: '):
            stack = section.split(': ')[1]
            conf['stacks'][stack] = {}

            for option, required in stack_options:
                try:
                    if option == 'disable-rollback':
                        conf['stacks'][stack][option] = config.getboolean(
                            section, option)
                    elif option == 'template':
                        conf['stacks'][stack][option] = os.path.expanduser(
                            config.get(section, option))
                    elif option == 'parameters':
                        try:
                            raw_parameters = config.get(section, option)\
                                .replace('\n', '')\
                                .split(',')
                            parameters = []
                            for parameter in raw_parameters:
                                key, value = parameter.split('=')
                                parameters.append((key.strip(), value.strip()))
                            conf['stacks'][stack][option] = parameters
                        except ValueError:
                            logger.error(
                                'Error parsing parameters for stack {}'.format(
                                    stack))
                            sys.exit(1)
                    else:
                        conf['stacks'][stack][option] = config.get(
                            section, option)
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)


def _populate_bundles(config):
    """ Populate the bundles config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section.startswith('bundle: '):
            bundle = section.split(': ')[1]
            conf['bundles'][bundle] = {}

            for option, required in bundle_options:
                try:
                    if option == 'paths':
                        raw_paths = config.get(section, option)\
                            .replace('\n', '')\
                            .split(',')
                        paths = []
                        for path in raw_paths:
                            paths.append(os.path.expanduser(path.strip()))
                        conf['bundles'][bundle]['paths'] = paths
                    else:
                        conf['bundles'][bundle][option] = config.get(
                            section, option)
                except NoOptionError:
                    if required:
                        logger.error('Missing required option {}'.format(
                            option))
                        sys.exit(1)
