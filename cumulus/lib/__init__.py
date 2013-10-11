""" Cumulus init """
import config_handler
import logging.config

import bundle_manager
import deployment_manager

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':
            '%(asctime)s - cumulus - %(name)s - %(levelname)s - %(message)s'
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


def main():
    """ Main function """
    config_handler.configure()

    if config_handler.args.bundle:
        bundle_manager.build_bundles()

    if config_handler.args.deploy:
        for stack in config_handler.get_stacks():
            deployment_manager.ensure_stack(
                stack,
                config_handler.get_environment(),
                config_handler.get_stack_template(stack),
                disable_rollback=config_handler.get_stack_disable_rollback(
                    stack),
                parameters=config_handler.get_stack_parameters(stack))

    if config_handler.args.undeploy:
        deployment_manager.undeploy()

    if config_handler.args.validate_templates:
        deployment_manager.validate_templates()
