""" Configuration management """
import logging
import sys
from ConfigParser import SafeConfigParser

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

from cumulus_ds.config import config_file
from cumulus_ds.config.command_line_options import PARSER as parser
from cumulus_ds.exceptions import ConfigurationException

LOGGER = logging.getLogger(__name__)


class Configuration:
    environment = None
    config = None
    args = None

    def __init__(self):
        """ Constructor """
        self._parse_command_line_options()
        self._parse_configuration_file()
        self.environment = self.args.environment

    def _parse_command_line_options(self):
        """ Parse the command line options and populate self.args """
        self.args = parser.parse_args()

        # Make the stacks prettier
        if self.args.stacks:
            self.args.stacks = [s.strip() for s in self.args.stacks.split(',')]

        if self.args.cumulus_version:
            settings_conf = SafeConfigParser()
            settings_conf.read(
                ospath.realpath(
                    '{}/../settings.conf'.format(ospath.dirname(__file__))))
            print('Cumulus version {}'.format(
                settings_conf.get('general', 'version')))
            sys.exit(0)
        elif not self.args.environment:
            raise ConfigurationException('--environment is required')

    def _parse_configuration_file(self):
        """ Parse the configuration file """
        self.config = config_file.configure(self.args)

    def get_environment(self):
        """ Returns the environment name

        :returns: str
        """
        return unicode(self.environment)

    def get_bundle_path_rewrites(self, bundle):
        """ Returns a dict with all path rewrites

        :type bundle: str
        :param bundle: Bundle name
        :returns: dict
        """
        try:
            return self.config['bundles'][bundle]['path-rewrites']
        except KeyError:
            return []

    def get_bundle_paths(self, bundle):
        """ Returns a list of bundle paths for a given bundle

        :type bundle: str
        :param bundle: Bundle name
        :returns: list
        """
        try:
            return self.config['bundles'][bundle]['paths']
        except KeyError:
            LOGGER.error('No paths defined for bundle "{}"'.format(bundle))
            raise ConfigurationException(
                'No paths defined for bundle "{}"'.format(bundle))

    def get_bundles(self):
        """ Returns a list of bundles"""
        try:
            bundles = self.config['environments'][self.environment]['bundles']
        except KeyError:
            LOGGER.warning(
                'No bundles found for environment {}'.format(self.environment))
            return None

        # Check that the bundles are configured
        for bundle in bundles:
            if not bundle:
                bundles.remove(bundle)
                continue

            if bundle not in self.config['bundles']:
                bundles.remove(bundle)
                LOGGER.warning(
                    'No matching configuration for bundle "{}"!'.format(bundle))

        return bundles

    def get_environment_option(self, option_name):
        """ Returns version number

        :returns: str
        """
        try:
            return self.config['environments'][self.environment][option_name]
        except KeyError:
            LOGGER.error('No option {} in environment {}'.format(
                option_name, self.environment))
            return None

    def get_log_level(self):
        """ Returns the log level

        :returns: str
        """
        try:
            return self.config['general']['log-level']
        except KeyError:
            return 'INFO'

    def get_post_bundle_hook(self, bundle):
        """ Returns the post bundle hook command or None

        :type bundle: str
        :param bundle: Bundle name
        :returns: str or None
        """
        try:
            return self.config['bundles'][bundle]['post-bundle-hook']
        except KeyError:
            return None

    def get_post_deploy_hook(self):
        """ Returns the post deploy hook command or None

        :returns: str or None
        """
        try:
            return self.config[
                'environments'][self.environment]['post-deploy-hook']
        except KeyError:
            return None

    def get_pre_built_bundle_path(self, bundle):
        """ Return the path to the pre-built bundle

        :type bundle: str
        :param bundle: Bundle name
        :returns: str -- Path to the pre-built bundle
        """
        try:
            return str(self.config['bundles'][bundle]['pre-built-bundle'])
        except KeyError:
            LOGGER.error('No pre-built bundle path found for "{}"'.format(
                bundle))
            raise ConfigurationException(
                'No pre-built bundle path found for "{}"'.format(bundle))

    def get_pre_deploy_hook(self):
        """ Returns the pre deploy hook command or None

        :returns: str or None
        """
        try:
            return self.config[
                'environments'][self.environment]['pre-deploy-hook']
        except KeyError:
            return None

    def get_pre_bundle_hook(self, bundle):
        """ Returns the pre bundle hook command or None

        :type bundle: str
        :param bundle: Bundle name
        :returns: str or None
        """
        try:
            return self.config['bundles'][bundle]['pre-bundle-hook']
        except KeyError:
            return None

    def get_stack_disable_rollback(self, stack):
        """ See if we should disable rollback

        :type stack: str
        :param stack: Stack name
        :returns: bool -- Disable rollback?
        """
        try:
            return self.config['stacks'][stack]['disable-rollback']
        except KeyError:
            raise ConfigurationException(
                'Stack template not found in configuration')

    def get_stack_parameters(self, stack):
        """ Return the stack parameters

        :type stack: str
        :param stack: Stack name
        :returns: list -- All stack parameters
        """
        try:
            return self.config['stacks'][stack]['parameters']
        except KeyError:
            return []

    def get_stack_tags(self, stack):
        """ Return the stack tags

        :type stack: str
        :param stack: Stack name
        :returns: list -- All stack tags
        """
        try:
            return self.config['stacks'][stack]['tags']
        except KeyError:
            return None

    def get_stack_template(self, stack):
        """ Return the path to the stack template

        :type stack: str
        :param stack: Stack name
        :returns: str -- Stack template path
        """
        try:
            return self.config['stacks'][stack]['template']
        except KeyError:
            raise ConfigurationException(
                'Stack template not found in configuration for stack {}'.format(
                    stack))

    def get_stack_timeout_in_minutes(self, stack):
        """ Return stack creation timeout

        :type stack: str
        :param stack: Stack name
        :returns: int -- Stack creation timeout in minutes
        """
        try:
            timeout = int(self.config['stacks'][stack]['timeout-in-minutes'])
        except KeyError:
            raise ConfigurationException(
                'Stack timeout not found in configuration')

        if timeout == 0:
            return None
        return timeout

    def get_stacks(self):
        """ Returns a list of stacks """
        try:
            return self.config['stacks'].keys()
        except KeyError:
            LOGGER.warning(
                'No stacks found for environment {}'.format(self.environment))
            return None

    def has_pre_built_bundle(self, bundle):
        """ Checks wether or not the bundle has a pre-built-bundle flag

        :type bundle: str
        :param bundle: Bundle name
        :returns: bool -- True if there is a pre-built-bundle
        """
        if 'pre-built-bundle' in self.config['bundles'][bundle]:
            return True
        return False


CONFIG = Configuration()
