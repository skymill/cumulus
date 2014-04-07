""" Manage configuration file parsing """
import logging
import os
import sys
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

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
    ('log-level', False),
    ('include', False)
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
    ('bucket', False),
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

    :type args: Namespace
    :param args: Parsed arguments from argparse
    :type config_file: str or None
    :param config_file: Configuration file to read from
    """
    # Add custom configuration file path
    config_files = []
    if args.config:
        for config in args.config:
            config = ospath.expanduser(config)
            if ospath.exists(config):
                config_files.append(config)
                LOGGER.info('Added "{}" to config file list'.format(config))
                continue
            LOGGER.warning('Configuration file {} not found.'.format(config))
    else:
        if sys.platform in ['win32', 'cygwin']:
            config_files.append('C:\\cumulus.conf')
            config_files.append(ospath.expanduser('~\\.cumulus.conf'))
            config_files.append('{}\\cumulus.conf'.format(os.curdir))
        else:
            config_files.append('/etc/cumulus.conf')
            config_files.append(ospath.expanduser('~/.cumulus.conf'))
            config_files.append('{}/cumulus.conf'.format(os.curdir))

    # Get the include option from the general section
    config_files = __get_include_files(config_files) + config_files

    # Read config file
    conf_file_found = False
    for conf_file in config_files:
        if ospath.exists(conf_file):
            conf_file_found = True
            LOGGER.info('Reading configuration from {}'.format(conf_file))
    if not conf_file_found:
        raise ConfigurationException(
            'No configuration file found. Looked for {}'.format(
                ', '.join(config_files)))

    config = SafeConfigParser()
    config.read(config_files)

    try:
        _populate_general(args, config)
        _populate_environments(args, config)
        _populate_stacks(args, config)
        _populate_bundles(args, config)
    except ConfigurationException:
        raise

    return CONF


def __get_include_files(config_files):
    """ Read the 'include' option in the 'general' section

    This will return a list of include files

    :type config_files: str
    :param config_files: List of configuration files to include
    :returns: list -- List of include config files
    """
    config = SafeConfigParser()
    config.read(config_files)

    try:
        return [
            ospath.expanduser(c.strip())
            for c in config.get('general', 'include').split(',')
        ]
    except NoOptionError:
        return []
    except NoSectionError:
        return []
    return []


def _populate_environments(args, config):
    """ Populate the environments config object

    :type args: Namespace
    :param args: Parsed arguments from argparse
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

    :type args: Namespace
    :param args: Parsed arguments from argparse
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
            elif option == 'include':
                # The include option is read earlier
                continue
            else:
                CONF['general'][option] = config.get(section, option)
        except NoOptionError:
            if required:
                raise ConfigurationException(
                    'Missing required option {}'.format(option))


def _populate_stacks(args, config):
    """ Populate the stacks config object

    :type args: Namespace
    :param args: Parsed arguments from argparse
    :type config: ConfigParser.read
    :param config: Config parser config object
    """
    for section in config.sections():
        if section.startswith('stack: '):
            stack = section.split(': ', 1)[1]

            # If --stacks has been used, do only add those stacks
            if args.stacks and stack not in args.stacks:
                continue

            stack = '{}-{}'.format(args.environment, stack)

            # Only add stacks that belong to the current environment
            if stack not in CONF['environments'][args.environment]['stacks']:
                continue

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
                        CONF['stacks'][stack][option] = ospath.expanduser(
                            config.get(section, option))
                    elif option == 'parameters':
                        try:
                            raw_parameters = config.get(section, option)\
                                .split('\n')
                            if not raw_parameters[0]:
                                raw_parameters.pop(0)

                            parameters = []
                            for parameter in raw_parameters:
                                key, value = parameter.split('=', 1)
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
                                key, value = tag.split('=', 1)
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
                        key, value = keyvalue.split('=', 1)
                        if stack_name == stack:
                            CONF['stacks'][stack]['parameters'].append(
                                (key, value))
            except ValueError:
                raise ConfigurationException('Error parsing --parameters')


def _populate_bundles(args, config):
    """ Populate the bundles config object

    :type args: Namespace
    :param args: Parsed arguments from argparse
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
                            paths.append(ospath.expanduser(path.strip()))
                        CONF['bundles'][bundle]['paths'] = paths
                    elif option == 'path-rewrites':
                        CONF['bundles'][bundle]['path-rewrites'] = []
                        lines = config.get(section, option).strip().split('\n')

                        for line in lines:
                            try:
                                target, destination = line.split('->', 1)
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
