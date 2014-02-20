""" Command line options for CBH """
import argparse

PARSER = argparse.ArgumentParser(
    description='Cumulus Bundle Handler')
PARSER.add_argument(
    '--keep-old-files',
    action='count',
    help='Do not delete files from the previous deployment')
ARGS = PARSER.parse_args()
