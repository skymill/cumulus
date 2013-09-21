""" Bundler init """
import argparse
import sys

import manager


def main():
    """ Main function """
    parser = argparse.ArgumentParser(
        description='Cumulus Cloud Tools Stack Manager')
    general_args = parser.add_argument_group(title='General')
    general_args.add_argument(
        '-s', '--stack',
        required=True,
        help='Stack name')
    general_args.add_argument(
        '-e', '--environment',
        required=True,
        help=(
            'Environment name. This corresponds to the environments'
            'configured in cumulus-cloud-tools.conf'))
    general_args.add_argument(
        '-t', '--template',
        help='Path to template file')
    general_args.add_argument(
        '--disable-rollback',
        action='count',
        help='Disable rollback when you are updating or creating stack')
    action_args = parser.add_argument_group(title='Actions')
    action_args.add_argument(
        '--list',
        action='count',
        help='List current stacks')
    action_args.add_argument(
        '--create',
        action='count',
        help='Create stack')
    action_args.add_argument(
        '--delete',
        action='count',
        help='Delete stack')
    action_args.add_argument(
        '--update',
        action='count',
        help='Update stack')
    action_args.add_argument(
        '--validate',
        action='count',
        help='Validate template')
    args = parser.parse_args()

    # Should we rollback on failure?
    if args.disable_rollback:
        disable_rollback = True
    else:
        disable_rollback = False

    # Handle actions
    if args.list:
        manager.list_stacks(args.environment)
    elif args.create:
        manager.create_stack(
            args.stack,
            args.environment,
            args.template,
            disable_rollback)
    elif args.delete:
        manager.delete_stack(args.stack, args.environment)
    elif args.update:
        manager.update_stack(
            args.stack,
            args.environment,
            args.template,
            disable_rollback)
    elif args.validate:
        manager.validate_template(args.environment, args.template)
    else:
        print('No action argument supplied')
        parser.print_usage()
        sys.exit(1)
