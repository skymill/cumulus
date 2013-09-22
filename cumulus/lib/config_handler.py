""" Configuration handler """
import argparse
import os
import os.path
import sys
from ConfigParser import SafeConfigParser, NoOptionError

import logging
logger = logging.getLogger(__name__)


class Configuration:
    """ Configuration object """
    environment = None
    config = {
        'environments': {},
        'stacks': {},
        'bundles': {}
    }

    # [(option, required)]
    stack_options = [('template', True)]
    bundle_options = [('paths', True)]
    env_options = [
        ('access-key-id', True),
        ('secret-access-key', True),
        ('bucket', True),
        ('region', True),
        ('stacks', True),
        ('bundles', True),
        ('version', True),
    ]

    def __init__(self):
        """ Constructor """
        self._read_global_configuration_file()
        self._read_command_line_args()

    def get_config(self):
        """ Returns the configuration object

        :returns: dict
        """
        return self.config

    def get_environment(self):
        """ Returns the environment name

        :returns: str or None
        """
        return self.environment

    def get_bundle_paths(self, bundle):
        """ Returns a list of bundle paths for a given bundle

        :type bundle: str
        :param bundle: Bundle name
        :returns: list
        """
        try:
            return self.config['bundles'][bundle]['paths']
        except KeyError:
            return None

    def get_bundles(self):
        """ Returns a list of bundles"""
        try:
            return self.config['environments'][self.environment]['bundles']
        except KeyError:
            logger.warning(
                'No bundles found for environment {}'.format(self.environment))
            return None

    def get_environment_option(self, option_name):
        """ Returns version number

        :returns: str
        """
        try:
            return self.config['environments'][self.environment][option_name]
        except KeyError:
            logger.error('No option {} in environment {}'.format(
                option_name, self.environment))
            return None

    def _read_command_line_args(self):
        """ Read arguments from the command line """
        parser = argparse.ArgumentParser(
            description='Cumulus cloud management tool')
        parser.add_argument(
            '-e', '--environment',
            required=True,
            help='Environment to use')
        args = parser.parse_args()

        self.environment = args.environment

    def _read_global_configuration_file(self):
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
                self.config['environments'][env] = {}

                for option, required in self.env_options:
                    try:
                        if option == 'bundles':
                            bundles = []
                            for item in config.get(section, option).split(','):
                                bundles.append(item.strip())
                            self.config['environments'][env][option] = bundles
                        elif option == 'stacks':
                            stacks = []
                            for item in config.get(section, option).split(','):
                                stacks.append(item.strip())
                            self.config['environments'][env][option] = stacks
                        else:
                            self.config['environments'][env][option] = \
                                config.get(section, option)
                    except NoOptionError:
                        if required:
                            logger.error('Missing required option {}'.format(
                                option))
                            sys.exit(1)
                        else:
                            self.config['environments'][env][option] = None

        # Populate stacks
        for section in config.sections():
            if section.startswith('stack: '):
                stack = section.split(': ')[1]
                self.config['stacks'][stack] = {}

                for option, required in self.stack_options:
                    try:
                        self.config['stacks'][stack][option] = config.get(
                            section, option)
                    except NoOptionError:
                        if required:
                            logger.error('Missing required option {}'.format(
                                option))
                            sys.exit(1)
                        else:
                            self.config['environments'][stack][option] = None

        # Populate bundles
        for section in config.sections():
            if section.startswith('bundle: '):
                bundle = section.split(': ')[1]
                self.config['bundles'][bundle] = {}

                for option, required in self.bundle_options:
                    try:
                        raw_paths = config.get(section, option)\
                            .replace('\n', '')\
                            .split(',')
                        paths = []
                        for path in raw_paths:
                            paths.append(path.strip())

                        self.config['bundles'][bundle][option] = paths
                    except NoOptionError:
                        if required:
                            logger.error('Missing required option {}'.format(
                                option))
                            sys.exit(1)
                        else:
                            self.config['environments'][bundle][option] = None
