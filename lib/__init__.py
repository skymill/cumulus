""" Cumulus init """
import config_handler
import logging

import bundle_manager
import deployment_manager

config_handler.command_line_options()
config_handler.configure()

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':
            '%(asctime)s - cumulus - %(levelname)s - %(message)s'
        },
        'boto': {
            'format':
            '%(asctime)s - boto - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'boto': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'boto'
        }
    },
    'loggers': {
        '': {
            'handlers': ['boto'],
            'level': 'DEBUG',
            'propagate': True
        },
        'boto': {
            'handlers': ['boto'],
            'level': logging.CRITICAL,
            'propagate': False
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
}

# Set log level
logging_config['handlers']['default']['level'] = config_handler.get_log_level()

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


def main():
    """ Main function """
    try:
        if config_handler.args.bundle:
            bundle_manager.build_bundles()

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

    except Exception as error:
        logger.error(error)
        raise
