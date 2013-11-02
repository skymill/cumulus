""" Cumulus init """
import config_handler
import logging

import bundle_manager
import deployment_manager
from exceptions import ConfigurationException, HookExecutionException

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':
            '%(asctime)s - cumulus - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'lib.bundle_manager': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'lib.config_handler': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'lib.connection_handler': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'lib.deployment_manager': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
})

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    try:
        config_handler.command_line_options()
        config_handler.configure()
    except ConfigurationException as error:
        logger.error(error)
        raise

    if config_handler.args.bundle:
        try:
            bundle_manager.build_bundles()
        except HookExecutionException as error:
            logger.error(error)
            raise

    if config_handler.args.deploy:
        bundle_manager.build_bundles()
        deployment_manager.deploy()

    if config_handler.args.deploy_without_bundling:
        deployment_manager.deploy()

    if config_handler.args.list:
        deployment_manager.list_stacks()

    if config_handler.args.undeploy:
        deployment_manager.undeploy()

    if config_handler.args.validate_templates:
        deployment_manager.validate_templates()

    if config_handler.args.events:
        deployment_manager.list_events()
