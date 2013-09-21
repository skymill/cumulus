""" Configuration handler """
import os.path
import sys
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

from logger import logger

CONF_FILES = [
    os.path.expanduser('~/.skymill-cloud-tools/.skymill-cloud-tools.conf'),
    '/etc/skymill-cloud-tools/skymill-cloud-tools.conf'
]

# Read config file
exists = False
for conf_file in CONF_FILES:
    if os.path.exists(conf_file):
        exists = True
if not exists:
    logger.error('Missing config files: {}'.format(' or '.join(CONF_FILES)))
    sys.exit(1)
config = SafeConfigParser()
config.read(CONF_FILES)


def get(environment, option):
    """ Get an environment option

    :type environment: str
    :type option: str
    :returns: str -- Option value
    """
    try:
        return config.get(
            'environment: {}'.format(environment),
            option)
    except NoSectionError:
        logger.error('Missing config section "environment: {}"'.format(
            environment))
        sys.exit(1)
    except NoOptionError:
        logger.error('Missing config option "{}"'.format(option))
        sys.exit(1)
    except Exception:
        logger.exception('Unknown error occurred when getting config option')
        sys.exit(1)
