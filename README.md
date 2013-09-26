# Cumulus

Cumulus is a deployment tool used to deploy and maintain environments built with AWS CloudFormation. Cumulus will help you bundle your code and configuration and unpack the bundle to new instances on CloudFormation.

## Basic concepts

Cumulus is built around three main concepts:

- An **environment** references a whole environment and all it's CF stacks. It holds together information about the AWS account, which stacks to deploy and in which version.
- A **stack** is simply a CloudFormation stack.
- And a **bundle** is a `tar.bz2` file with code and configuration to unpack to instances.

## Requirements

Cumulus requires Python 2.7 and `boto`. Please install requirements with

    sudo pip install -r cumulus/requirements.txt

## Configuration

### Cumulus configuration

All configuration is read form `/etc/cumulus.conf`, `~/.cumulus.conf` and , `./cumulus.conf` in order. This is an example configuration:

    [environment: stage]
    access-key-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    bucket: se.skymill.bundles
    region: eu-west-1
    stacks: full
    bundles: webserver, database
    version: 1.0.0-SNAPSHOT

    [stack: full]
    template: /Users/sebastian/tmp/hosts/webserver.json
    disable-rollback: true
    parameters:
        version = 1.1.0,
        test tag=my test value ,
         key= value

    [bundle: webserver]
    paths:
        /Users/sebastian/tmp/hosts/webserver,
        /Users/sebastian/tmp/code/wordpress

    [bundle: database]
    paths: /Users/sebastian/tmp/hosts/database

All configuration options are required to be set except `parameters` for bundles.

### CloudFormation configuration

To save some space in this document, please find the example AWS CloudFormation template [here](https://github.com/skymill/cumulus/blob/master/cumulus/docs/cloudformation-template-example.json)

## Deployment workflow

First off you need to create a bundle. Run

    cumulus --environment production --bundle

This will bundle and upload all your software to AWS S3. The next step is to update CloudFormation. That is done with the `--deploy` command:

    cumulus --environment production --deploy

Cumulus will create or update the CloudFormation stacks as needed.

## Environment specific configuration

To have files that should only be included in specific environments, prefix them with `__cumulus-environment__filename`. So for example: `__cumulus-production__nginx.conf` is the `nginx.conf` for the `production` environment.

## Release notes

**0.2.3 (2013-09-26)**

- [Symbolic links should be dereferenced in bundles #19](https://github.com/skymill/cumulus/issues/19)
- [Current directory is added to bundle #18](https://github.com/skymill/cumulus/issues/18)

**0.2.2 (2013-09-25)**

- [Mismatch in metadata and cumulus_bundle_handler.py #16](https://github.com/skymill/cumulus/issues/16)
- Various bug fixes in the bundle handler system

**0.2.1 (2013-09-25)**

- [Cumulus CF namespace conflicts with some rules #15](https://github.com/skymill/cumulus/issues/15)

**0.2.0 (2013-09-24)**

- [Custom parameters in CloudFormation #14](https://github.com/skymill/cumulus/issues/14)
- [Expand ~ in config template & bundle paths #12](https://github.com/skymill/cumulus/issues/12)
- [Read the bucket name from configuration in CF template #11](https://github.com/skymill/cumulus/issues/11)
- [Exception when building non-configured bundle #13](https://github.com/skymill/cumulus/issues/13)

**0.1.1 (2013-09-23)**

- [Prefixes for prefixed files is not removed in bundle #9](https://github.com/skymill/cumulus/issues/9)

**0.1.0 (2013-09-23)**

Initial release with some basic functions and concepts.

- Basic bundling and stack management features implemented
