""" Bundler init """
import argparse

import bundle


def main():
    """ Main function """
    parser = argparse.ArgumentParser(
        description='SCT Bundler')
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
    parser.add_argument(
        '-v', '--version',
        required=True,
        help='Version string')
    args = parser.parse_args()

    # Create the bundle
    bundle_obj = bundle.Bundle(
        args.base,
        args.environment,
        args.version)
    bundle_obj.create_and_upload(args.instance_type)
