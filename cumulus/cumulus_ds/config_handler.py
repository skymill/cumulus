""" Configuration handler """
import argparse
import logging
import os
import os.path
import sys
from ConfigParser import SafeConfigParser, NoOptionError

from exceptions import ConfigurationException

logger = logging.getLogger(__name__)

# Get settings.conf
settings = SafeConfigParser()
settings.read(
    os.path.realpath('{}/settings.conf'.format(os.path.dirname(__file__))))

environment = None
args = None

# Initial configuration object
conf = {
    'general': {},
    'environments': {},
    'stacks': {},
    'bundles': {}
}

# Options per section
# [(option, required)]
general_options = [
    ('log-level', False)
]
stack_options = [
    ('template', True),
    ('disable-rollback', True),
    ('parameters', False),
    ('timeout-in-minutes', False),
    ('tags', False)
]
bundle_options = [
    ('paths', True),
    ('path-rewrites', False),
    ('pre-bundle-hook', False),
    ('post-bundle-hook', False),
    ('pre-built-bundle', False)
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


def command_line_options():
    """ Parse command line options """
    global args
    global environment

    # Read arguments from the command line
    parser = argparse.ArgumentParser(
        description='Cumulus cloud management tool')
    general_ag = parser.add_argument_group('General options')
    general_ag.add_argument(
        '-e', '--environment',
        help='Environment to use')
    general_ag.add_argument(
        '-s', '--stacks',
        help=(
            'Comma separated list of stacks to deploy. '
            'Default behavior is to deploy all stacks for an environment'))
    general_ag.add_argument(
        '--version',
        help=(
            'Environment version number. '
            'Overrides the version value from the configuration file'))
    general_ag.add_argument(
        '--parameters',
        help=(
            'CloudFormation parameters. On the form: '
            'stack_name:parameter_name=value,stack_name=parameter_name=value'
        ))
    general_ag.add_argument(
        '--config',
        help='Path to configuration file.')
    general_ag.add_argument(
        '--cumulus-version',
        action='count',
        help='Print cumulus version number')
    general_ag.add_argument(
        '--force',
        type=bool,
        ddefault=False,
        help='Skip any safety questions')
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
        '--events',
        action='count',
        help='List events for the stack')
    actions_ag.add_argument(
        '--list',
        action='count',
        help='List stacks for each environment')
    actions_ag.add_argument(
        '--validate-templates',
        action='count',
        help='Validate all templates for the environment')
    actions_ag.add_argument(
        '--undeploy',
        action='count',
        help=(
            'Undeploy (delete) all stacks in the environment. '
            'Use --force to skip the safety question.'))
    args = parser.parse_args()

    # Make the stacks prettier
    if args.stacks:
        args.stacks = [s.strip() for s in args.stacks.split(',')]

    if args.cumulus_version:
        print('Cumulus version {}'.format(settings.get('general', 'version')))
        sys.exit(0)
    elif not args.environment:
        raise ConfigurationException('--environment is required')

    environment = args.environment


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


def get_bundle_path_rewrites(bundle):
    """ Returns a dict with all path rewrites

    :type bundle: str
    :param bundle: Bundle name
    :returns: dict
    """
    try:
        return conf['bundles'][bundle]['path-rewrites']
    except KeyError:
        return {}


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
        raise ConfigurationException(
            'No paths defined for bundle "{}"'.format(bundle))


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
        if not bundle:
            bundles.remove(bundle)
            continue

        if bundle not in conf['bundles']:
            bundles.remove(bundle)
            logger.warning(
                'No matching configuration for bundle "{}"!'.format(bundle))

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


def get_log_level():
    """ Returns the log level

    :returns: str
    """
    try:
        return conf['general']['log-level']
    except KeyError:
        return 'DEBUG'


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


def get_pre_built_bundle_path(bundle):
    """ Return the path to the pre-built bundle

    :type bundle: str
    :param bundle: Bundle name
    :returns: str -- Path to the pre-built bundle
    """
    try:
        return str(conf['bundles'][bundle]['pre-built-bundle'])
    except KeyError:
        logger.error('No pre-built bundle path found for "{}"'.format(bundle))
        raise ConfigurationException(
            'No pre-built bundle path found for "{}"'.format(bundle))


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
        raise ConfigurationException(
            'Stack template not found in configuration')


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


def get_stack_tags(stack):
    """ Return the stack tags

    :type stack: str
    :param stack: Stack name
    :returns: list -- All stack tags
    """
    try:
        return conf['stacks'][stack]['tags']
    except KeyError:
        return None


def get_stack_template(stack):
    """ Return the path to the stack template

    :type stack: str
    :param stack: Stack name
    :returns: str -- Stack template path
    """
    try:
        return conf['stacks'][stack]['template']
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
        timeout = int(conf['stacks'][stack]['timeout-in-minutes'])
    except KeyError:
        raise ConfigurationException(
            'Stack timeout not found in configuration')

    if timeout == 0:
        return None
    return timeout


def get_stacks():
    """ Returns a list of stacks """
    try:
        return conf['environments'][environment]['stacks']
    except KeyError:
        logger.warning(
            'No stacks found for environment {}'.format(environment))
        return None


def has_pre_built_bundle(bundle):
    """ Checks wether or not the bundle has a pre-built-bundle flag

    :type bundle: str
    :param bundle: Bundle name
    :returns: bool -- True if there is a pre-built-bundle
    """
    if 'pre-built-bundle' in conf['bundles'][bundle]:
        return True
    return False


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
            config_files = [os.path.expanduser(args.config)]
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
        raise ConfigurationException(
            'No configuration file found. Looked for {}'.format(
                ', '.join(config_files)))

    config = SafeConfigParser()
    config.read(config_files)

    _populate_general(config)
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
            if env != environment:
                continue

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
                            item = item.strip()

                            # If --stacks has been used,
                            # do only add those stacks
                            if args.stacks and item not in args.stacks:
                                continue

                            stacks.append('{}-{}'.format(environment, item))
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
                        raise ConfigurationException(
                            'Missing required option {}'.format(option))


def _populate_general(config):
    """ Populate the general config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section == 'general':
            conf['general'] = {}

            for option, required in general_options:
                try:
                    if option == 'log-level':
                        log_level = config.get(section, option).upper()

                        log_levels = [
                            'DEBUG',
                            'INFO',
                            'WARNING',
                            'ERROR'
                        ]

                        if log_level not in log_levels:
                            logger.warning(
                                (
                                    'Invalid log level "{}". '
                                    'Using default log level.'
                                ).format(log_level))
                            log_level = 'DEBUG'

                        conf['general'][option] = log_level
                    else:
                        conf['general'][option] = config.get(section, option)
                except NoOptionError:
                    if required:
                        raise ConfigurationException(
                            'Missing required option {}'.format(option))


def _populate_stacks(config):
    """ Populate the stacks config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section.startswith('stack: '):
            stack = section.split(': ')[1]

            # If --stacks has been used, do only add those stacks
            if args.stacks and stack not in args.stacks:
                continue

            stack = '{}-{}'.format(environment, section.split(': ')[1])

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
                                .split('\n')
                            if not raw_parameters[0]:
                                raw_parameters.pop(0)

                            parameters = []
                            for parameter in raw_parameters:
                                key, value = parameter.split('=')
                                parameters.append((key.strip(), value.strip()))
                            conf['stacks'][stack][option] = parameters
                        except ValueError:
                            raise ConfigurationException(
                                'Error parsing parameters for stack {}'.format(
                                    stack))
                    elif option == 'tags':
                        try:
                            raw_tags = config.get(section, option)\
                                .split('\n')
                            if not raw_tags[0]:
                                raw_tags.pop(0)

                            tags = {}
                            for tag in raw_tags:
                                key, value = tag.split('=')
                                tags[key.strip()] = value.strip()
                            conf['stacks'][stack][option] = tags
                        except ValueError:
                            raise ConfigurationException(
                                'Error parsing tags for stack {}'.format(
                                    stack))
                    elif option == 'timeout-in-minutes':
                        conf['stacks'][stack][option] = config.getint(
                            section, option)
                    else:
                        conf['stacks'][stack][option] = config.get(
                            section, option)
                except NoOptionError:
                    if required:
                        raise ConfigurationException(
                            'Missing required option {}'.format(
                                option))

                    if option == 'timeout-in-minutes':
                        conf['stacks'][stack][option] = 0

            # Add command line parameters
            try:
                if args.parameters:
                    if not 'parameters' in conf['stacks'][stack]:
                        conf['stacks'][stack]['parameters'] = []

                    for raw_parameter in args.parameters.split(','):
                        stack_name, keyvalue = raw_parameter.split(':')
                        key, value = keyvalue.split('=')
                        if stack_name == stack:
                            conf['stacks'][stack]['parameters'].append(
                                (key, value))
            except ValueError:
                raise ConfigurationException('Error parsing --parameters')


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
                        lines = config.get(section, option).strip().split('\n')
                        paths = []
                        for path in lines:
                            paths.append(os.path.expanduser(path.strip()))
                        conf['bundles'][bundle]['paths'] = paths
                    elif option == 'path-rewrites':
                        conf['bundles'][bundle]['path-rewrites'] = []
                        lines = config.get(section, option).strip().split('\n')

                        for line in lines:
                            try:
                                target, destination = line.split('->')
                            except ValueError:
                                raise ConfigurationException(
                                    'Invalid path-rewrites for '
                                    'bundle {}'.format(bundle))

                            # Clean the target and destination from initial /
                            if target[0] == '/':
                                target = target[1:]
                            if destination[0] == '/':
                                destination = destination[1:]

                            conf['bundles'][bundle]['path-rewrites'].append({
                                'target': target.strip(),
                                'destination': destination.strip()
                            })

                    else:
                        conf['bundles'][bundle][option] = config.get(
                            section, option)
                except NoOptionError:
                    if (option == 'paths' and
                            config.has_option(section, 'pre-built-bundle')):
                        continue

                    if required:
                        raise ConfigurationException(
                            'Missing required option {}'.format(option))
