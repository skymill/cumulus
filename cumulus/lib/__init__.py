""" Cumulus init """
import config_handler
import logging.config

import bundler

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
        'lib.config_handler': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'lib.bundler': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
})


def main():
    """ Main function """
    config_handler.configure()
    bundler.build_bundles()
