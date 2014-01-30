""" Cumulus Deployment Suite

The MIT License (MIT)

Copyright (c) 2013 Sebastian Dahlgren & Skymill Solutions

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
            deployment_manager.undeploy()

        if config_handler.args.validate_templates:
            deployment_manager.validate_templates()

        if config_handler.args.events:
            deployment_manager.list_events()

    except Exception as error:
        logger.error(error)
        raise
