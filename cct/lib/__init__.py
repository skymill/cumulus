""" Cumulus init """
import json
import config_handler


def main():
    """ Main function """
    config = config_handler.Configuration()
    print json.dumps(config.get_config(), indent=4)
