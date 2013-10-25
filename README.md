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
    pre-deploy-hook: /path/to/script
    post-deploy-hook: echo "Yay" > ~/test.log

    [stack: full]
    template: /Users/sebastian/tmp/hosts/webserver.json
    disable-rollback: true
    parameters:
        version = 1.1.0,
        test tag = my test value
        key = value

    [bundle: webserver]
    pre-bundle-hook: git clone git://git.example.com/my.git
    post-bundle-hook: rm -rf my
    paths:
        /Users/sebastian/tmp/hosts/webserver,
        /Users/sebastian/tmp/code/wordpress

    [bundle: database]
    pre-bundle-hook: /path/to/script
    paths: /Users/sebastian/tmp/hosts/database
    path-rewrites:
        /wordpress -> /var/www/wordpress
        /nginx -> /etc/nginx

All configuration options are required to be set except `parameters` for bundles.

### CloudFormation configuration

To save some space in this document, please find the example AWS CloudFormation template [here](https://github.com/skymill/cumulus/blob/master/cumulus/docs/cloudformation-template-example.json)

## Deployment workflow

All you need to do is to run the command below. This will bundle and upload all your software to AWS S3. It will then trigger an create or update at AWS CloudFormation.

    cumulus --environment production --deploy

## Environment specific configuration

To have files that should only be included in specific environments, prefix them with `__cumulus-environment__filename`. So for example: `__cumulus-production__nginx.conf` is the `nginx.conf` for the `production` environment.

## Release notes

**0.4.0 (2013-10-25)**

- [Path prefix in bundles #36](https://github.com/skymill/cumulus/issues/36)

**0.3.1 (2013-10-24)**

- [Error handling stack delete status #34](https://github.com/skymill/cumulus/issues/34)
- [Running `--deploy` on existing stack fails #35](https://github.com/skymill/cumulus/issues/35)
- [Initial stack creation fails when using `--deploy-without-bundling` #33](https://github.com/skymill/cumulus/issues/33)
- [Bundle type missing in Cumulus metadata #37](https://github.com/skymill/cumulus/issues/37)

**0.3.0 (2013-10-11)**

- [Write hooks for Cumulus deployments #26](https://github.com/skymill/cumulus/issues/26)
- [Wait until stack is done updating/creating #20](https://github.com/skymill/cumulus/issues/20)
- [Specify config file location as input parameter #30](https://github.com/skymill/cumulus/issues/30)
- [Set environment version as input parameter #28](https://github.com/skymill/cumulus/issues/28)
- [Make it possible to environment prefix whole directories #10](https://github.com/skymill/cumulus/issues/10)
- [Create shortcut for both bundling and deploying #27](https://github.com/skymill/cumulus/issues/27)
- [Ask before delete when running `--undeploy` #24](https://github.com/skymill/cumulus/issues/24)
- [Ensure that boto is available for cumulus bundle handler #25](https://github.com/skymill/cumulus/issues/25)
- [Remove skymill reference from JSON template #23](https://github.com/skymill/cumulus/issues/23)
- [Remove unnecessary stack name in metadata #22](https://github.com/skymill/cumulus/issues/22)
- [Remove unnecessary bundle-type in metadata #21](https://github.com/skymill/cumulus/issues/21)

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
