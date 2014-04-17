""" Command line options for Cumulus DS """
import argparse


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
    help='Path to configuration file. Can be a comma separated list of files.')
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
    '--redeploy',
    action='count',
    help='Undeploy and deploy the stack(s). Implies bundling.')
ACTIONS_AG.add_argument(
    '--events',
    action='count',
    help='List events for the stack')
ACTIONS_AG.add_argument(
    '--list',
    action='count',
    help='List stacks for each environment')
ACTIONS_AG.add_argument(
    '--outputs',
    action='count',
    help='Show output for all stacks')
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
