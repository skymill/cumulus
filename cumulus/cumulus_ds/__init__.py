""" Cumulus Deployment Suite

APACHE LICENSE 2.0
Copyright 2013-2014 Skymill Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import config_handler
import logging

import bundle_manager
import deployment_manager

try:
    config_handler.command_line_options()
    config_handler.configure()
except Exception:
    raise

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
            'handlers': ['default'],
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
            deployment_manager.undeploy(force=config_handler.args.force)

        if config_handler.args.validate_templates:
            deployment_manager.validate_templates()

        if config_handler.args.events:
            deployment_manager.list_events()

    except Exception as error:
        logger.error(error)
        raise
