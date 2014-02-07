""" Command line options for Cumulus DS """
import argparse
import os
import sys
from ConfigParser import SafeConfigParser

from cumulus_ds.exceptions import ConfigurationException

# Get settings.conf
SETTINGS = SafeConfigParser()
SETTINGS.read(
    os.path.realpath('{}/settings.conf'.format(os.path.dirname(__file__))))


# Read arguments from the command line
PARSER = argparse.ArgumentParser(
    description='Cumulus cloud management tool')
GENERAL_AG = PARSER.add_argument_group('General options')
GENERAL_AG.add_argument(
    '-e', '--environment',
    help='Environment to use')
GENERAL_AG.add_argument(
    '-s', '--stacks',
    help=(
        'Comma separated list of stacks to deploy. '
        'Default behavior is to deploy all stacks for an environment'))
GENERAL_AG.add_argument(
    '--version',
    help=(
        'Environment version number. '
        'Overrides the version value from the configuration file'))
GENERAL_AG.add_argument(
    '--parameters',
    help=(
        'CloudFormation parameters. On the form: '
        'stack_name:parameter_name=value,stack_name=parameter_name=value'
    ))
GENERAL_AG.add_argument(
    '--config',
    help='Path to configuration file.')
GENERAL_AG.add_argument(
    '--cumulus-version',
    action='count',
    help='Print cumulus version number')
GENERAL_AG.add_argument(
    '--force',
    default=False,
    action='store_true',
    help='Skip any safety questions')
ACTIONS_AG = PARSER.add_argument_group('Actions')
ACTIONS_AG.add_argument(
    '--bundle',
    action='count',
    help='Build and upload bundles to AWS S3')
ACTIONS_AG.add_argument(
    '--deploy',
    action='count',
    help='Bundle and deploy all stacks in the environment')
ACTIONS_AG.add_argument(
    '--deploy-without-bundling',
    action='count',
    help='Deploy all stacks in the environment, without bundling first')
ACTIONS_AG.add_argument(
    '--events',
    action='count',
    help='List events for the stack')
ACTIONS_AG.add_argument(
    '--list',
    action='count',
    help='List stacks for each environment')
ACTIONS_AG.add_argument(
    '--validate-templates',
    action='count',
    help='Validate all templates for the environment')
ACTIONS_AG.add_argument(
    '--undeploy',
    action='count',
    help=(
        'Undeploy (delete) all stacks in the environment. '
        'Use --force to skip the safety question.'))
ARGS = PARSER.parse_args()

# Make the stacks prettier
if ARGS.stacks:
    ARGS.stacks = [s.strip() for s in ARGS.stacks.split(',')]

if ARGS.cumulus_version:
    print('Cumulus version {}'.format(SETTINGS.get('general', 'version')))
    sys.exit(0)
elif not ARGS.environment:
    raise ConfigurationException('--environment is required')
