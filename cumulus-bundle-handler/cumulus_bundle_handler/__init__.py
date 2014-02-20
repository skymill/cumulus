""" Script downloading and unpacking Cumulus bundles for the host """
import logging
import logging.config
import os
import sys

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

# Configure logging
LOG_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': (
                '%(asctime)s - cumulus-bundle-handler - '
                '%(levelname)s - %(message)s'
            )
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '/var/log/cumulus-bundle-handler.log',
            'mode': 'a',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True
        },
        'cumulus_bundle_handler': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Change the log file path on Windows systems
if sys.platform in ['win32', 'cygwin']:
    if not ospath.exists('C:\\cumulus\\logs'):
        os.makedirs('C:\\cumulus\\logs')
    LOG_CONF['handlers']['file']['filename'] = \
        'C:\\cumulus\\logs\\cumulus-bundle-handler.log'
logging.config.dictConfig(LOG_CONF)

from cumulus_bundle_handler import config
from cumulus_bundle_handler import bundle_manager
from cumulus_bundle_handler import script_executor
from cumulus_bundle_handler.command_line_options import ARGS as args


# Read log level from the metadata.conf
if config.get('log-level'):
    LOG_CONF['handlers']['console']['level'] = config.get('log-level').upper()
    LOG_CONF['handlers']['file']['level'] = config.get('log-level').upper()

logging.config.dictConfig(LOG_CONF)
LOGGER = logging.getLogger('cumulus_bundle_handler')


def main():
    """ Main function """
    script_executor.run_init_scripts(kill=True, start=False, other=True)

    bundle_types = config.get('bundle-types').split(',')
    if not bundle_types:
        LOGGER.error('Missing "bundle-types" in metadata.conf')
        sys.exit(1)

    if args.keep_old_files:
        LOGGER.info('Keeping files from previous deployment')
    else:
        _remove_old_files()

    for bundle_type in bundle_types:
        bundle_manager.download_and_unpack_bundle(bundle_type.strip())

    script_executor.run_init_scripts(kill=False, start=True, other=True)

    LOGGER.info("Done updating host")


def _remove_old_files():
    """ Remove files from previous bundle """
    cache_file = '/var/local/cumulus-bundle-handler.cache'
    if sys.platform in ['win32', 'cygwin']:
        if not ospath.exists('C:\\cumulus\\cache'):
            os.makedirs('C:\\cumulus\\cache')
        cache_file = 'C:\\cumulus\\cache\\cumulus-bundle-handler.cache'

    if not ospath.exists(cache_file):
        LOGGER.info('No previous bundle files to clean up')
        return

    LOGGER.info('Removing old files and directories')

    with open(cache_file, 'r') as file_handle:
        for line in file_handle.readlines():
            line = line.replace('\n', '')

            if not ospath.exists(line):
                continue

            if ospath.isdir(line):
                try:
                    os.removedirs(line)
                    LOGGER.debug('Removing directory {}'.format(line))
                except OSError:
                    pass
            elif ospath.isfile(line):
                LOGGER.debug('Removing file {}'.format(line))
                os.remove(line)

                try:
                    os.removedirs(ospath.dirname(line))
                except OSError:
                    pass
            elif ospath.islink(line):
                LOGGER.debug('Removing link {}'.format(line))
                os.remove(line)

                try:
                    os.removedirs(ospath.dirname(line))
                except OSError:
                    pass
            else:
                LOGGER.warning('Unknown file type {}'.format(line))

    # Remove the cache file when done
    os.remove(cache_file)
