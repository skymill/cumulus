""" Configuration management """
import logging
import sys
from ConfigParser import SafeConfigParser, NoOptionError

LOGGER = logging.getLogger('cumulus_bundle_handler')

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

CONFIG = {
    'region': None,
    'access-key-id': None,
    'secret-access-key': None,
    'bundle-extraction-paths': None,
    'bundle-bucket': None,
    'bundle-types': None,
    'environment': None,
    'version': None,
}

REQUIRED_OPTIONS = {
    'region': None,
    'access-key-id': None,
    'secret-access-key': None,
    'bundle-bucket': None,
    'bundle-types': None,
    'environment': None,
    'version': None
}

OPTIONAL_OPTIONS = {
    'bundle-extraction-paths': None,
    'log-level': None
}


if sys.platform in ['win32', 'cygwin']:
    CONFIG_PATH = 'C:\\cumulus\\conf\\metadata.conf'
else:
    CONFIG_PATH = '/etc/cumulus/metadata.conf'

if not ospath.exists(CONFIG_PATH):
    print('Error: Configuration file not found: {}'.format(CONFIG_PATH))
    sys.exit(1)

CONF_FILE = SafeConfigParser()
CONF_FILE.read(CONFIG_PATH)

# Parse required options
section = 'metadata'
for option in REQUIRED_OPTIONS:
    try:
        CONFIG[option] = CONF_FILE.get(section, option)
    except NoOptionError:
        LOGGER.error('Missing required option {} in {}'.format(
            option, CONFIG_PATH))
        sys.exit(1)

# Parse optional options
for option in OPTIONAL_OPTIONS:
    try:
        CONFIG[option] = CONF_FILE.get(section, option)
    except NoOptionError:
        pass


def get(option):
    """ Get configuration option

    :type option: str
    :param option: Option name to get
    :returns: option
    """
    if option in CONFIG:
        return CONFIG[option]
