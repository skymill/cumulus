""" Bundler init """

import argparse

import bundle


def main():
    """ Main function """
    parser = argparse.ArgumentParser(
        description='STS Bundler')
    parser.add_argument(
        '-b', '--base',
        required=True,
        help='Base path to include in the bundle')
    parser.add_argument(
        '-e', '--environment',
        required=True,
        help='Environment to bundle for')
    parser.add_argument(
        '-i', '--instance-type',
        default=None,
        help='Instance type to bundle. All will be bundled by default')
    args = parser.parse_args()

    # Create the bundle
    bundle_obj = bundle.Bundle(args.base, args.environment)
    bundle_obj.create(args.instance_type)
