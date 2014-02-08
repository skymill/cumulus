""" Manage configuration file parsing """
import logging
import os
import os.path
from ConfigParser import SafeConfigParser, NoOptionError

from cumulus_ds.exceptions import ConfigurationException

LOGGER = logging.getLogger(__name__)

# Initial configuration object
CONF = {
    'general': {},
    'environments': {},
    'stacks': {},
    'bundles': {}
}

# Options per section
# [(option, required)]
GENERAL_OPTIONS = [
    ('log-level', False)
]
STACK_OPTIONS = [
    ('template', True),
    ('disable-rollback', True),
    ('parameters', False),
    ('timeout-in-minutes', False),
    ('tags', False)
]
BUNDLE_OPTIONS = [
    ('paths', True),
    ('path-rewrites', False),
    ('pre-bundle-hook', False),
    ('post-bundle-hook', False),
    ('pre-built-bundle', False)
]
ENV_OPTIONS = [
    ('access-key-id', True),
    ('secret-access-key', True),
    ('bucket', True),
    ('region', True),
    ('stacks', True),
    ('bundles', True),
    ('version', False),
    ('pre-deploy-hook', False),
    ('post-deploy-hook', False),
    ('stack-name-prefix', False),
    ('stack-name-suffix', False)
]


def configure(args):
    """ Populate the objects

    :type config_file: str or None
    :param config_file: Configuration file to read from
    """
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
            LOGGER.warning('Configuration file {} not found.'.format(
                os.path.expanduser(args.config)))

    # Read config file
    conf_file_found = False
    for conf_file in config_files:
        if os.path.exists(conf_file):
            conf_file_found = True
            LOGGER.info('Reading configuration from {}'.format(conf_file))
    if not conf_file_found:
        raise ConfigurationException(
            'No configuration file found. Looked for {}'.format(
                ', '.join(config_files)))

    config = SafeConfigParser()
    config.read(config_files)

    _populate_general(args, config)
    _populate_environments(args, config)
    _populate_stacks(args, config)
    _populate_bundles(args, config)

    return CONF


def _populate_environments(args, config):
    """ Populate the environments config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    section = 'environment: {}'.format(args.environment)
    environment = args.environment
    if not section in config.sections():
        raise ConfigurationException(
            'No configuration found for environment {}'.format(environment))

    CONF['environments'][environment] = {}

    for option, required in ENV_OPTIONS:
        try:
            if option == 'bundles':
                bundles = []
                for item in config.get(section, option).split(','):
                    bundles.append(item.strip())
                CONF['environments'][environment][option] = bundles
            elif option == 'stacks':
                stacks = []
                for item in config.get(section, option).split(','):
                    item = item.strip()

                    # If --stacks has been used,
                    # do only add those stacks
                    if args.stacks and item not in args.stacks:
                        continue

                    stacks.append('{}-{}'.format(
                        args.environment, item))
                CONF['environments'][environment][option] = stacks
            elif option == 'version':
                if args.version:
                    CONF['environments'][environment][option] = args.version
                else:
                    CONF['environments'][environment][option] = config.get(
                        section, option)
            else:
                CONF['environments'][environment][option] = \
                    config.get(section, option)
        except NoOptionError:
            if required:
                raise ConfigurationException(
                    'Missing required option {}'.format(option))


def _populate_general(args, config):
    """ Populate the general config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    section = 'general'
    if not section in config.sections():
        return None

    for option, required in GENERAL_OPTIONS:
        try:
            if option == 'log-level':
                log_level = config.get(section, option).upper()

                if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                    LOGGER.warning(
                        (
                            'Invalid log level "{}". Using default log level.'
                        ).format(log_level))
                    log_level = 'DEBUG'

                CONF['general'][option] = log_level
            else:
                CONF['general'][option] = config.get(section, option)
        except NoOptionError:
            if required:
                raise ConfigurationException(
                    'Missing required option {}'.format(option))


def _populate_stacks(args, config):
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

            stack = '{}-{}'.format(args.environment, section.split(': ')[1])

            # Prepend a stack name prefix
            if 'stack-name-prefix' in CONF['environments'][args.environment]:
                stack = '{}-{}'.format(
                    CONF['environments'][args.environment]['stack-name-prefix'],
                    stack)

            # Append a stack name suffix
            if 'stack-name-suffix' in CONF['environments'][args.environment]:
                stack = '{}-{}'.format(
                    stack,
                    CONF['environments'][args.environment]['stack-name-suffix'])

            CONF['stacks'][stack] = {}

            for option, required in STACK_OPTIONS:
                try:
                    if option == 'disable-rollback':
                        CONF['stacks'][stack][option] = config.getboolean(
                            section, option)
                    elif option == 'template':
                        CONF['stacks'][stack][option] = os.path.expanduser(
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
                            CONF['stacks'][stack][option] = parameters
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
                            CONF['stacks'][stack][option] = tags
                        except ValueError:
                            raise ConfigurationException(
                                'Error parsing tags for stack {}'.format(
                                    stack))
                    elif option == 'timeout-in-minutes':
                        CONF['stacks'][stack][option] = config.getint(
                            section, option)
                    else:
                        CONF['stacks'][stack][option] = config.get(
                            section, option)
                except NoOptionError:
                    if required:
                        raise ConfigurationException(
                            'Missing required option {}'.format(
                                option))

                    if option == 'timeout-in-minutes':
                        CONF['stacks'][stack][option] = 0

            # Add command line parameters
            try:
                if args.parameters:
                    if not 'parameters' in CONF['stacks'][stack]:
                        CONF['stacks'][stack]['parameters'] = []

                    for raw_parameter in args.parameters.split(','):
                        stack_name, keyvalue = raw_parameter.split(':')
                        key, value = keyvalue.split('=')
                        if stack_name == stack:
                            CONF['stacks'][stack]['parameters'].append(
                                (key, value))
            except ValueError:
                raise ConfigurationException('Error parsing --parameters')


def _populate_bundles(args, config):
    """ Populate the bundles config object

    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section.startswith('bundle: '):
            bundle = section.split(': ')[1]
            CONF['bundles'][bundle] = {}

            for option, required in BUNDLE_OPTIONS:
                try:
                    if option == 'paths':
                        lines = config.get(section, option).strip().split('\n')
                        paths = []
                        for path in lines:
                            paths.append(os.path.expanduser(path.strip()))
                        CONF['bundles'][bundle]['paths'] = paths
                    elif option == 'path-rewrites':
                        CONF['bundles'][bundle]['path-rewrites'] = []
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

                            CONF['bundles'][bundle]['path-rewrites'].append({
                                'target': target.strip(),
                                'destination': destination.strip()
                            })

                    else:
                        CONF['bundles'][bundle][option] = config.get(
                            section, option)
                except NoOptionError:
                    if (option == 'paths' and
                            config.has_option(section, 'pre-built-bundle')):
                        continue

                    if required:
                        raise ConfigurationException(
                            'Missing required option {}'.format(option))
